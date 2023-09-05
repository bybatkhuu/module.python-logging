# -*- coding: utf-8 -*-

## Standard libraries
import os
import json
import logging
from typing import Union

## Third-party libraries
import yaml
from pydantic import validate_call
from loguru._logger import Logger
from loguru import logger

## Internal modules
from ._handler import InterceptHandler
from .rotation import RotationChecker
from .schema import LoggerConfigPM
from .sink import std_sink
from .format import json_format
from .filter import (
    use_all_filter,
    use_std_filter,
    use_file_filter,
    use_file_err_filter,
    use_file_json_filter,
    use_file_json_err_filter,
)
from ._utils import create_dir


class LoggerLoader:
    """LoggerLoader class for setting up loguru logger.

    Attributes:
        _CONFIGS_DIR     (str           ): Default configs directory. Defaults to '${PWD}/configs'.
        _CONFIG_FILENAME (str           ): Default logger config filename. Defaults to 'logger.yml'.

        handlers_map     (dict          ): Registered logger handlers map as dictionary.
        configs_dir      (str           ): Logger configs directory.
        config_filename  (str           ): Logger config filename.
        config           (LoggerConfigPM): Logger config as <class 'LoggerConfigPM'>.

    Methods:
        load()                      : Load logger handlers based on logger config.
        remove_handler()            : Remove all handlers or specific handler by name or id from logger.
        update_config()             : Update logger config with new config.
        _load_config_file()         : Load logger config from file.
        _check_env()                : Check environment variables for logger config.
        _add_stream_std_handler()   : Add std stream handler to logger.
        _add_file_log_handler()     : Add log file handler to logger.
        _add_file_err_handler()     : Add error log file handler to logger.
        _add_file_json_handler()    : Add json log file handler to logger.
        _add_file_json_err_handler(): Add json error log file handler to logger.
        add_custom_handler()        : Add custom handler to logger.
        _load_intercept_handlers()  : Load intercept handlers to catch third-pary modules log or mute them.
    """

    _CONFIGS_DIR = os.path.join(os.getcwd(), "configs")
    _CONFIG_FILENAME = "logger.yml"

    def __init__(
        self,
        configs_dir: str = _CONFIGS_DIR,
        config_filename: str = _CONFIG_FILENAME,
        load_config_file: bool = True,
        config: Union[dict, LoggerConfigPM, None] = None,
        auto_load: bool = False,
    ):
        """LoggerLoader constructor method.

        Args:
            configs_dir      (str,                               optional): Logger configs directory. Defaults to LoggerLoader._CONFIGS_DIR.
            config_filename  (str,                               optional): Logger config filename. Defaults to LoggerLoader._CONFIG_FILENAME.
            load_config_file (bool,                              optional): Indicates whether to load logger config file or not. Defaults to True.
            config           (Union[dict, LoggerConfigPM, None], optional): New logger config to update loaded config. Defaults to None.
            auto_load        (bool,                              optional): Indicates whether to load logger handlers or not. Defaults to False.
        """

        self.handlers_map: dict = {"default": 0}
        self.configs_dir = configs_dir
        self.config_filename = config_filename
        self.config = LoggerConfigPM()

        if load_config_file:
            self._load_config_file()

        if config:
            self.update_config(config=config)

        if auto_load:
            self.load()

    def load(self) -> Logger:
        """Load logger handlers based on logger config.

        Returns:
            Logger: Main loguru logger instance.
        """

        self.remove_handler()

        self._check_env()

        if self.config.stream.std_handler.enabled:
            self._add_stream_std_handler()

        if self.config.file.log_handlers.enabled:
            self._add_file_log_handler()
            self._add_file_err_handler()

        if self.config.file.json_handlers.enabled:
            self._add_file_json_handler()
            self._add_file_json_err_handler()

        self._load_intercept_handlers()

        return logger

    @validate_call
    def remove_handler(
        self, handler: Union[str, None] = None, handler_type: str = "NAME"
    ):
        """Remove all handlers or specific handler by name or id from logger.

        Raises:
            ValueError: The `handler_type` argument value '{handler_type}' is invalid, must be 'NAME' or 'ID'!

        Args:
            handler     (str, optional): Handler name or id to remove. Defaults to None.
            hadler_type (int, optional): Handler type to remove, must be 'NAME' or 'ID'. Defaults to 'name'.
        """

        if handler:
            handler_type = handler_type.strip().upper()
            if handler_type == "NAME":
                if handler in self.handlers_map:
                    _handler_id = self.handlers_map[handler]
                    logger.remove(_handler_id)
                    self.handlers_map.pop(handler)
                    return
            elif handler_type == "ID":
                if handler in self.handlers_map.values():
                    logger.remove(handler)
                    for _handler_name, _handler_id in self.handlers_map.items():
                        if handler == _handler_id:
                            self.handlers_map.pop(_handler_name)
                    return
            else:
                raise ValueError(
                    f"`handler_type` argument value '{handler_type}' is invalid, must be 'NAME' or 'ID'!"
                )

        logger.remove()
        self.handlers_map.clear()

    @validate_call
    def update_config(self, config: Union[dict, LoggerConfigPM]):
        """Update logger config with new config.

        Args:
            config (Union[dict, LoggerConfigPM], required): New logger config to update loaded config.

        Raises:
            Exception: Failed to load `config` argument into <class 'LoggerConfigPM'>.
        """

        try:
            if isinstance(config, dict):
                _config_dict = self.config.model_dump()
                _config_dict.update(config)
                self.config = LoggerConfigPM(**_config_dict)
            elif isinstance(config, LoggerConfigPM):
                self.config = config
        except Exception:
            logger.critical(
                "Failed to load `config` argument into <class 'LoggerConfigPM'>."
            )
            raise

    def _load_config_file(self):
        """Load logger config from file."""

        _config_file_format = "YAML"
        if self.config_filename.lower().endswith((".yml", ".yaml")):
            _config_file_format = "YAML"
        if self.config_filename.lower().endswith(".json"):
            _config_file_format = "JSON"
        # elif self.config_filename.lower().endswith(".toml"):
        #     _config_file_format = "TOML"

        _config_path = os.path.abspath(
            os.path.join(self.configs_dir, self.config_filename)
        )

        ## Loading config from file, if it's exits:
        if os.path.isfile(_config_path):
            if _config_file_format == "YAML":
                try:
                    with open(_config_path, "r", encoding="utf-8") as _config_file:
                        _new_config_dict = yaml.safe_load(_config_file)["logger"]
                        _config_dict = self.config.model_dump()
                        _config_dict.update(_new_config_dict)
                        self.config = LoggerConfigPM(**_config_dict)
                except Exception:
                    logger.critical(
                        f"Failed to load '{_config_path}' yaml config file."
                    )
                    raise
            elif _config_file_format == "JSON":
                try:
                    with open(_config_path, "r", encoding="utf-8") as _config_file:
                        _new_config_dict = json.load(_config_file)["logger"]
                        _config_dict = self.config.model_dump()
                        _config_dict.update(_new_config_dict)
                        self.config = LoggerConfigPM(**_config_dict)
                except Exception:
                    logger.critical(
                        f"Failed to load '{_config_path}' json config file."
                    )
                    raise
            # elif _config_file_format == "TOML":
            #     try:
            #         import toml

            #         with open(_config_path, "r", encoding="utf-8") as _config_file:
            #             _new_config_dict = toml.load(_config_file)["logger"]
            #             _config_dict = self.config.model_dump()
            #             _config_dict.update(_new_config_dict)
            #             self.config = LoggerConfigPM(**_config_dict)
            #     except Exception:
            #         logger.critical(
            #             f"Failed to load '{_config_path}' toml config file."
            #         )
            #         raise

    def _check_env(self):
        """Check environment variables for logger config."""

        ## Checking environment for DEBUG option:
        _is_debug = False
        _ENV = str(os.getenv("ENV")).strip().lower()
        _DEBUG = str(os.getenv("DEBUG")).strip().lower()
        if (
            (_DEBUG == "true")
            or (_DEBUG == "1")
            or ((_ENV == "development") and ((_DEBUG == "none") or (_DEBUG == "")))
        ):
            _is_debug = True

        if _is_debug and (self.config.level != "TRACE"):
            self.config.level = "DEBUG"

        if self.config.level == "TRACE":
            self.config.use_diagnose = True

        if self.config.stream.use_icon:
            self.config.stream.format_str = self.config.stream.format_str.replace(
                "level_short:<5", "level.icon:<4"
            )

        # if self.config.stream.use_color:
        #     ## Checking terminal could support xterm colors:
        #     _TERM = str(os.getenv("TERM")).strip()
        #     if not "xterm" in _TERM:
        #         self.config.stream.use_color = False

    def _add_stream_std_handler(self) -> int:
        """Add std stream handler to logger.

        Returns:
            int: Handler id.
        """

        return self.add_custom_handler(handler_name="STREAM.STD", filter=use_std_filter)

    def _add_file_log_handler(self) -> int:
        """Add log file handler to logger.

        Returns:
            int: Handler id.
        """

        return self.add_custom_handler(handler_name="FILE", filter=use_file_filter)

    def _add_file_err_handler(self) -> int:
        """Add error log file handler to logger.

        Returns:
            int: Handler id.
        """

        _handler_id = self.add_custom_handler(
            handler_name="FILE_ERR",
            sink=self.config.file.log_handlers.err_path,
            level="WARNING",
            filter=use_file_err_filter,
        )
        return _handler_id

    def _add_file_json_handler(self) -> int:
        """Add json log file handler to logger.

        Returns:
            int: Handler id.
        """

        _kwargs = {
            "sink": self.config.file.json_handlers.log_path,
            "filter": use_file_json_filter,
            "serialize": True,
        }
        if self.config.file.json_handlers.use_custom:
            _kwargs["format"] = json_format
            _kwargs["serialize"] = False

        _handler_id = self.add_custom_handler(handler_name="FILE.JSON", **_kwargs)
        return _handler_id

    def _add_file_json_err_handler(self) -> int:
        """Add json error log file handler to logger.

        Returns:
            int: Handler id.
        """

        _kwargs = {
            "sink": self.config.file.json_handlers.err_path,
            "level": "WARNING",
            "filter": use_file_json_err_filter,
            "serialize": True,
        }
        if self.config.file.json_handlers.use_custom:
            _kwargs["format"] = json_format
            _kwargs["serialize"] = False

        _handler_id = self.add_custom_handler(
            handler_name="FILE.JSON_ERR",
            **_kwargs,
        )
        return _handler_id

    @validate_call
    def add_custom_handler(self, handler_name: str, **kwargs) -> int:
        """Add custom handler to logger.

        Args:
            handler_name (str): Handler name/type to add logger.

        Raises:
            ValueError: Custom handler '{handler_name}' already exists in logger!
            ValueError: The `sink` argument is required for custom handler!

        Returns:
            int: Handler id.
        """

        if handler_name in self.handlers_map:
            raise ValueError(
                f"Custom handler '{handler_name}' already exists in logger!"
            )

        _handler_id = None
        try:
            handler_name = handler_name.strip().upper()

            if "level" not in kwargs:
                kwargs["level"] = self.config.level

            if "filter" not in kwargs:
                kwargs["filter"] = use_all_filter

            if "backtrace" not in kwargs:
                kwargs["backtrace"] = self.config.use_backtrace

            if "diagnose" not in kwargs:
                kwargs["diagnose"] = self.config.use_diagnose

            if handler_name.startswith("STREAM"):
                if "sink" not in kwargs:
                    kwargs["sink"] = std_sink

                if "format" not in kwargs:
                    kwargs["format"] = self.config.stream.format_str

                if "colorize" not in kwargs:
                    kwargs["colorize"] = self.config.stream.use_color
            elif handler_name.startswith("FILE"):
                kwargs["enqueue"] = True

                if "sink" not in kwargs:
                    kwargs["sink"] = self.config.file.log_handlers.log_path

                if isinstance(kwargs["sink"], str):
                    _log_path = kwargs["sink"]
                    if not os.path.isabs(_log_path):
                        _log_path = os.path.abspath(
                            os.path.join(self.config.file.logs_dir, _log_path)
                        )

                    if "{app_name}" in _log_path:
                        _log_path = _log_path.format(app_name=self.config.app_name)

                    _logs_dir, _ = os.path.split(_log_path)
                    create_dir(create_dir=_logs_dir)
                    kwargs["sink"] = _log_path

                if "format" not in kwargs:
                    kwargs["format"] = self.config.file.log_handlers.format_str

                if "rotation" not in kwargs:
                    kwargs["rotation"] = RotationChecker(
                        rotate_size=self.config.file.rotate_size,
                        rotate_time=self.config.file.rotate_time,
                    ).should_rotate

                if "retention" not in kwargs:
                    kwargs["retention"] = self.config.file.backup_count

                if "encoding" not in kwargs:
                    kwargs["encoding"] = self.config.file.encoding

            if "sink" not in kwargs:
                raise ValueError(
                    f"The `sink` argument is required for custom handler '{handler_name}'!"
                )

            _handler_id = logger.add(**kwargs)
        except Exception:
            logger.critical(f"Failed to add custom handler '{handler_name}' to logger!")
            raise

        self.handlers_map[handler_name] = _handler_id
        return _handler_id

    def _load_intercept_handlers(self):
        """Load intercept handlers to catch third-pary modules log or mute them."""

        _intercept_handler = InterceptHandler()

        ## Intercepting all logs from standard (root logger) logging:
        logging.basicConfig(handlers=[_intercept_handler], level=0, force=True)

        _intercepted_modules = set()
        _muted_modules = set()

        if self.config.intercept.auto_load.enabled:
            for _module_name in list(logging.root.manager.loggerDict.keys()):
                if self.config.intercept.auto_load.only_base:
                    _module_name = _module_name.split(".")[0]

                if (_module_name not in _intercepted_modules) and (
                    _module_name not in self.config.intercept.auto_load.ignore_modules
                ):
                    _logger = logging.getLogger(_module_name)
                    _logger.handlers = [_intercept_handler]
                    _intercepted_modules.add(_module_name)

        for _include_module_name in self.config.intercept.include_modules:
            _logger = logging.getLogger(_include_module_name)
            _logger.handlers = [_intercept_handler]

            if _include_module_name not in _intercepted_modules:
                _intercepted_modules.add(_include_module_name)

        for _mute_module_name in self.config.intercept.mute_modules:
            _logger = logging.getLogger(_mute_module_name)
            _logger.handlers = []
            # _logger.propagate = False
            # _logger.disabled = True

            if _mute_module_name in _intercepted_modules:
                _intercepted_modules.remove(_mute_module_name)

            if _mute_module_name not in _muted_modules:
                _muted_modules.add(_mute_module_name)

        logger.trace(
            f"Intercepted modules: {list(_intercepted_modules)}; Muted modules: {list(_muted_modules)};"
        )

    ### ATTRIBUTES ###
    ## handlers_map ##
    @property
    def handlers_map(self) -> Union[dict, None]:
        try:
            return self.__handlers_map
        except AttributeError:
            return None

    @handlers_map.setter
    def handlers_map(self, handlers_map: dict):
        if not isinstance(handlers_map, dict):
            raise TypeError(
                f"The `handlers_map` attribute type {type(handlers_map)} is invalid, must be <dict>!."
            )

        self.__handlers_map = handlers_map

    ## handlers_map ##

    ## configs_dir ##
    @property
    def configs_dir(self) -> str:
        try:
            return self.__configs_dir
        except AttributeError:
            return LoggerLoader._CONFIGS_DIR

    @configs_dir.setter
    def configs_dir(self, configs_dir: str):
        if not isinstance(configs_dir, str):
            raise TypeError(
                f"The `configs_dir` attribute type {type(configs_dir)} is invalid, must be a <str>!"
            )

        configs_dir = configs_dir.strip()
        if configs_dir == "":
            raise ValueError("The `configs_dir` attribute value is empty!")

        self.__configs_dir = configs_dir

    ## configs_dir ##

    ## config_filename ##
    @property
    def config_filename(self) -> str:
        try:
            return self.__config_filename
        except AttributeError:
            return LoggerLoader._CONFIG_FILENAME

    @config_filename.setter
    def config_filename(self, config_filename: str):
        if not isinstance(config_filename, str):
            raise TypeError(
                f"The `config_filename` attribute type {type(config_filename)} is invalid, must be a <str>!"
            )

        config_filename = config_filename.strip()
        if config_filename == "":
            raise ValueError("The `config_filename` attribute value is empty!")

        if (not config_filename.lower().endswith((".yml", ".yaml"))) and (
            not config_filename.lower().endswith(".json")
        ):
            if not config_filename.lower().endswith(".toml"):
                raise NotImplementedError(
                    f"The `config_filename` attribute value '{config_filename}' is invalid, TOML file format is not supported yet!"
                )

            raise ValueError(
                f"The `config_filename` attribute value '{config_filename}' is invalid, must be a file with '.yml', '.yaml' or '.json' extension!"
            )

        self.__config_filename = config_filename

    ## config_filename ##

    ## config ##
    @property
    def config(self) -> Union[LoggerConfigPM, None]:
        try:
            return self.__config
        except AttributeError:
            return None

    @config.setter
    def config(self, config: LoggerConfigPM):
        if not isinstance(config, LoggerConfigPM):
            raise TypeError(
                f"The `config` attribute type {type(config)} is invalid, must be a <class 'LoggerConfigPM'>!"
            )

        self.__config = config

    ## config ##
    ### ATTRIBUTES ###
