# beans_logging

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/bybatkhuu/module.python-logging/2.build-publish.yml?logo=GitHub)](https://github.com/bybatkhuu/module.python-logging/actions/workflows/2.build-publish.yml)
[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/bybatkhuu/module.python-logging?logo=GitHub)](https://github.com/bybatkhuu/module.python-logging/releases)
[![PyPI](https://img.shields.io/pypi/v/beans-logging?logo=PyPi)](https://pypi.org/project/beans-logging)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/beans-logging?logo=Python)](https://docs.conda.io/en/latest/miniconda.html)

`beans_logging` is a python package for simple logger and easily managing logging modules.

It is a `Loguru` based custom logging package for python projects.

## Features

- Main **logger** based on **Loguru** logging - <https://pypi.org/project/loguru>
- Logging to **log files** (all, error, json)
- **Pre-defined** logging configs and handlers
- **Colorful** logging
- Auto **intercepting** and **muting** modules
- Load config from **YAML** or **JSON** file
- Custom options as a **config**
- Custom logging **formats**
- **Multiprocess** compatibility (Linux, macOS - 'fork')
- Add custom **handlers**
- **FastAPI** HTTP access logging **middleware**
- **Base** logging module

---

## Installation

### 1. Prerequisites

- **Python (>= v3.8)**
- **PyPi (>= v23)**

### 2. Install beans-logging package

Choose one of the following methods to install the package **[A ~ F]**:

**A.** [**RECOMMENDED**] Install from **PyPi**

```sh
# Install or upgrade beans-logging package:
pip install -U beans-logging
```

**B.** Install latest version from **GitHub**

```sh
# Install package by git:
pip install git+https://github.com/bybatkhuu/module.python-logging.git
```

**C.** Install from **pre-built release** files

1. Download **`.whl`** or **`.tar.gz`** file from **releases** - <https://github.com/bybatkhuu/module.python-logging/releases>
2. Install with pip:

```sh
# Install from .whl file:
pip install ./beans_logging-[VERSION]-py3-none-any.whl
# Or install from .tar.gz file:
pip install ./beans_logging-[VERSION].tar.gz
```

**D.** Install from **source code** by building package

```sh
# Clone repository by git:
git clone https://github.com/bybatkhuu/module.python-logging.git beans_logging
cd ./beans_logging

# Install python build tool:
pip install -U pip build

# Build python package:
python -m build

_VERSION=$(./scripts/get-version.sh)

# Install from .whl file:
pip install ./dist/beans_logging-${_VERSION}-py3-none-any.whl
# Or install from .tar.gz file:
pip install ./dist/beans_logging-${_VERSION}.tar.gz
```

**E.** Install with pip editable **development mode** (from source code)

```sh
# Clone repository by git:
git clone https://github.com/bybatkhuu/module.python-logging.git beans_logging
cd ./beans_logging

# Install with editable development mode:
pip install -e .
```

**F.** Manually add to **PYTHONPATH** (not recommended)

```sh
# Clone repository by git:
git clone https://github.com/bybatkhuu/module.python-logging.git beans_logging
cd ./beans_logging

# Install python dependencies:
pip install -r ./requirements.txt

# Add current path to PYTHONPATH:
export PYTHONPATH="${PWD}:${PYTHONPATH}"
```

## Usage/Examples

To use `beans_logging`, import the `logger` instance from the `beans_logging.auto` package:

```python
from beans_logging.auto import logger
```

You can call logging methods directly from the `logger` instance:

```python
logger.info("Logging info.")
```

### **Simple**

[**`configs/logger.yml`**](https://github.com/bybatkhuu/module.python-logging/blob/main/examples/simple/configs/logger.yml):

```yml
logger:
  app_name: "my-app"
  level: "TRACE"
  file:
    log_handlers:
      enabled: true
    json_handlers:
      enabled: true
```

[**`main.py`**](https://github.com/bybatkhuu/module.python-logging/blob/main/examples/simple/main.py):

```python
from beans_logging.auto import logger


logger.trace("Tracing...")
logger.debug("Debugging...")
logger.info("Logging info.")
logger.success("Success.")
logger.warning("Warning something.")
logger.error("Error occured.")
logger.critical("CRITICAL ERROR.")

def divide(a, b):
    _result = a / b
    return _result

def nested(c):
    try:
        divide(5, c)
    except ZeroDivisionError as err:
        logger.error(err)
        raise

try:
    nested(0)
except Exception as err:
    logger.exception("Show me, what value is wrong:")
```

Run the [**`examples/simple`**](https://github.com/bybatkhuu/module.python-logging/tree/main/examples/simple):

```sh
cd ./examples/simple

python ./main.py
```

**Output**:

```txt
[2023-09-01 09:00:00.384 +09:00 | TRACE | beans_logging._base:478]: Intercepted modules: ['concurrent', 'concurrent.futures', 'asyncio']; Muted modules: [];
[2023-09-01 09:00:00.384 +09:00 | TRACE | __main__:7]: Tracing...
[2023-09-01 09:00:00.385 +09:00 | DEBUG | __main__:8]: Debugging...
[2023-09-01 09:00:00.385 +09:00 | INFO  | __main__:9]: Logging info.
[2023-09-01 09:00:00.385 +09:00 | OK    | __main__:10]: Success.
[2023-09-01 09:00:00.385 +09:00 | WARN  | __main__:11]: Warning something.
[2023-09-01 09:00:00.385 +09:00 | ERROR | __main__:12]: Error occured.
[2023-09-01 09:00:00.386 +09:00 | CRIT  | __main__:13]: CRITICAL ERROR.
[2023-09-01 09:00:00.386 +09:00 | ERROR | __main__:25]: division by zero
[2023-09-01 09:00:00.386 +09:00 | ERROR | __main__:32]: Show me, what value is wrong:
Traceback (most recent call last):

> File "/home/user/workspaces/projects/beans_logging/examples/simple/./main.py", line 30, in <module>
    nested(0)
    └ <function nested at 0x10802a4c0>

  File "/home/user/workspaces/projects/beans_logging/examples/simple/./main.py", line 23, in nested
    divide(5, c)
    │         └ 0
    └ <function divide at 0x1052f31f0>

  File "/home/user/workspaces/projects/beans_logging/examples/simple/./main.py", line 17, in divide
    _result = a / b
              │   └ 0
              └ 5

ZeroDivisionError: division by zero
```

### **Advanced (FastAPI)**

[**`configs/logger.yml`**](https://github.com/bybatkhuu/module.python-logging/blob/main/examples/advanced/configs/logger.yml):

```yaml
logger:
  app_name: "fastapi-app"
  level: "TRACE"
  use_diagnose: false
  stream:
    use_color: true
    use_icon: false
    format_str: "[<c>{time:YYYY-MM-DD HH:mm:ss.SSS Z}</c> | <level>{level_short:<5}</level> | <w>{name}:{line}</w>]: <level>{message}</level>"
    std_handler:
      enabled: true
  file:
    logs_dir: "./logs"
    rotate_size: 10000000 # 10MB
    rotate_time: "00:00:00"
    backup_count: 90
    log_handlers:
      enabled: true
      format_str: "[{time:YYYY-MM-DD HH:mm:ss.SSS Z} | {level_short:<5} | {name}:{line}]: {message}"
      log_path: "{app_name}.std.all.log"
      err_path: "{app_name}.std.err.log"
    json_handlers:
      enabled: true
      use_custom: false
      log_path: "json/{app_name}.json.all.log"
      err_path: "json/{app_name}.json.err.log"
  intercept:
    auto_load:
      enabled: true
      only_base: false
      ignore_modules: []
    include_modules: []
    mute_modules: ["uvicorn.access", "uvicorn.error"]
  extra:
    http_std_debug_format: '<n>[{request_id}]</n> {client_host} {user_id} "<u>{method} {url_path}</u> HTTP/{http_version}"'
    http_std_msg_format: '<n><w>[{request_id}]</w></n> {client_host} {user_id} "<u>{method} {url_path}</u> HTTP/{http_version}" {status_code} {content_length}B {response_time}ms'
    http_file_enabled: true
    http_log_path: "http/{app_name}.http.access.log"
    http_err_path: "http/{app_name}.http.err.log"
    http_json_enabled: true
    http_json_path: "json.http/{app_name}.json.http.access.log"
    http_json_err_path: "json.http/{app_name}.json.http.err.log"
```

[**`.env`**](https://github.com/bybatkhuu/module.python-logging/blob/main/examples/advanced/.env):

```sh
ENV=development
DEBUG=true
```

[**`logger.py`**](https://github.com/bybatkhuu/module.python-logging/blob/main/examples/advanced/logger.py):

```python
from beans_logging import Logger, LoggerLoader
from beans_logging.fastapi import add_http_file_handler, add_http_file_json_handler


logger_loader = LoggerLoader()
logger: Logger = logger_loader.load()

if logger_loader.config.extra.http_file_enabled:
    add_http_file_handler(
        logger_loader=logger_loader,
        log_path=logger_loader.config.extra.http_log_path,
        err_path=logger_loader.config.extra.http_err_path,
    )

if logger_loader.config.extra.http_json_enabled:
    add_http_file_json_handler(
        logger_loader=logger_loader,
        log_path=logger_loader.config.extra.http_json_path,
        err_path=logger_loader.config.extra.http_json_err_path,
    )
```

[**`app.py`**](https://github.com/bybatkhuu/module.python-logging/blob/main/examples/advanced/app.py):

```python
from typing import Union
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse

load_dotenv()

from beans_logging.fastapi import HttpAccessLogMiddleware

from logger import logger, logger_loader
from __version__ import __version__


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Preparing to startup...")
    logger.success("Finished preparation to startup.")
    logger.info(f"API version: {__version__}")

    yield
    logger.info("Praparing to shutdown...")
    logger.success("Finished preparation to shutdown.")

app = FastAPI(lifespan=lifespan, version=__version__)
app.add_middleware(
    HttpAccessLogMiddleware,
    has_proxy_headers=True,
    debug_format=logger_loader.config.extra.http_std_debug_format,
    msg_format=logger_loader.config.extra.http_std_msg_format,
)

@app.get("/")
def root():
    return {"Hello": "World"}
```

Run the [**`examples/advanced`**](https://github.com/bybatkhuu/module.python-logging/tree/main/examples/advanced):

```sh
cd ./examples/advanced
# Install python dependencies for examples:
pip install -r ./requirements.txt

uvicorn app:app --host=0.0.0.0 --port=8000
```

**Output**:

```txt
[2023-09-01 12:37:38.569 +09:00 | TRACE | beans_logging._base:499]: Intercepted modules: ['watchfiles.watcher', 'asyncio', 'watchfiles', 'concurrent', 'dotenv', 'concurrent.futures', 'fastapi', 'dotenv.main', 'uvicorn', 'watchfiles.main']; Muted modules: ['uvicorn.error', 'uvicorn.access'];
[2023-09-01 12:37:38.579 +09:00 | INFO  | uvicorn.server:76]: Started server process [22599]
[2023-09-01 12:37:38.579 +09:00 | INFO  | uvicorn.lifespan.on:46]: Waiting for application startup.
[2023-09-01 12:37:38.579 +09:00 | INFO  | app:21]: Preparing to startup...
[2023-09-01 12:37:38.580 +09:00 | OK    | app:22]: Finished preparation to startup.
[2023-09-01 12:37:38.580 +09:00 | INFO  | app:23]: API version: 0.0.1-000000
[2023-09-01 12:37:38.580 +09:00 | INFO  | uvicorn.lifespan.on:60]: Application startup complete.
[2023-09-01 12:37:38.582 +09:00 | INFO  | uvicorn.server:218]: Uvicorn running on http://0.0.0.0:9000 (Press CTRL+C to quit)
[2023-09-01 12:37:48.487 +09:00 | DEBUG | anyio._backends._asyncio:807]: [0b9f972939054a58ba10e7a39a12bd21] 127.0.0.1 - "GET / HTTP/1.1"
[2023-09-01 12:37:48.488 +09:00 | OK    | anyio._backends._asyncio:807]: [0b9f972939054a58ba10e7a39a12bd21] 127.0.0.1 - "GET / HTTP/1.1" 200 17B 0.5ms
^C[2023-09-01 12:37:51.845 +09:00 | INFO  | uvicorn.server:264]: Shutting down
[2023-09-01 12:37:51.949 +09:00 | INFO  | uvicorn.lifespan.on:65]: Waiting for application shutdown.
[2023-09-01 12:37:51.951 +09:00 | INFO  | app:26]: Praparing to shutdown...
[2023-09-01 12:37:51.952 +09:00 | OK    | app:27]: Finished preparation to shutdown.
[2023-09-01 12:37:51.952 +09:00 | INFO  | uvicorn.lifespan.on:76]: Application shutdown complete.
[2023-09-01 12:37:51.953 +09:00 | INFO  | uvicorn.server:86]: Finished server process [22599]
```

---

## Running Tests

To run tests, run the following command:

```sh
# Install python test dependencies:
pip install -r ./requirements.test.txt

# Run tests:
python -m pytest -v
```

## Environment Variables

You can use the following environment variables inside [**`.env.example`**](https://github.com/bybatkhuu/module.python-logging/blob/main/.env.example) file:

```sh
ENV=development
DEBUG=true

BEANS_LOGGING_DISABLE_DEFAULT=false
BEANS_LOGGING_CONFIG_PATH="./configs/logger.yml"
BEANS_LOGGING_DIR="./logs"
```

## Configuration

You can use the following configuration template [**`logger.yml`**](https://github.com/bybatkhuu/module.python-logging/blob/main/templates/configs/logger.yml): file:

```yaml
logger:
  # app_name: "app"
  level: "INFO"
  use_diagnose: false
  stream:
    use_color: true
    use_icon: false
    format_str: "[<c>{time:YYYY-MM-DD HH:mm:ss.SSS Z}</c> | <level>{level_short:<5}</level> | <w>{name}:{line}</w>]: <level>{message}</level>"
    std_handler:
      enabled: true
  file:
    logs_dir: "./logs"
    rotate_size: 10000000 # 10MB
    rotate_time: "00:00:00"
    backup_count: 90
    log_handlers:
      enabled: false
      format_str: "[{time:YYYY-MM-DD HH:mm:ss.SSS Z} | {level_short:<5} | {name}:{line}]: {message}"
      log_path: "{app_name}.std.all.log"
      err_path: "{app_name}.std.err.log"
    json_handlers:
      enabled: false
      use_custom: false
      log_path: "{app_name}.json.all.log"
      err_path: "{app_name}.json.err.log"
  intercept:
    auto_load:
      enabled: true
      only_base: false
      ignore_modules: []
    include_modules: []
    mute_modules: []
  extra:
```

## Documentation

- [docs](https://github.com/bybatkhuu/module.python-logging/blob/main/docs/README.md)
- [scripts](https://github.com/bybatkhuu/module.python-logging/blob/main/docs/scripts/README.md)

---

## References

- <https://github.com/Delgan/loguru>
- <https://loguru.readthedocs.io/en/stable/api/logger.html>
- <https://loguru.readthedocs.io/en/stable/resources/recipes.html>
