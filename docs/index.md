# Documentation
## Overview

md.log is the simplest [psr.log](../psr.log) contract implementation component 
that provides API to perform application logging.

## Architecture overview

[![Architecture overview][architecture-overview]][architecture-overview]

## Installation

```sh
pip install md.log --index-url https://source.md.land/python/
```

## Usage example

```python3
import md.log
if __name__ == '__main__':
    logger = md.log.Logger(filename='/dev/stderr')
    # act
    logger.emergency('Application log', {'context-example': 42})
    logger.alert('Application log', {'context-example': 42})
    logger.critical('Application log', {'context-example': 42})
    logger.error('Application log', {'context-example': 42})
    logger.warning('Application log', {'context-example': 42})
    logger.notice('Application log', {'context-example': 42})
    logger.info('Application log', {'context-example': 42})
    logger.debug('Application log', {'context-example': 42})
    
    logger.log(level='custom-level', message='Application log', context={'context-example': 42})
```

Will log:

```
[2023-01-19 17:23:17.403825] app.emergency: Application log {"context-example": 42}
[2023-01-19 17:23:17.404138] app.alert: Application log {"context-example": 42}
[2023-01-19 17:23:17.404974] app.critical: Application log {"context-example": 42}
[2023-01-19 17:23:17.405162] app.error: Application log {"context-example": 42}
[2023-01-19 17:23:17.405231] app.warning: Application log {"context-example": 42}
[2023-01-19 17:23:17.405291] app.notice: Application log {"context-example": 42}
[2023-01-19 17:23:17.405347] app.info: Application log {"context-example": 42}
[2023-01-19 17:23:17.405410] app.debug: Application log {"context-example": 42}
[2023-01-19 17:23:17.405462] app.custom-level: Application log {"context-example": 42}
```

### Change channel name

By default, logger channel name is `app`, to change it 
provide `channel` parameter into logger constructor, for example:

```python3
import md.log
if __name__ == '__main__':
    logger = md.log.Logger(filename='/dev/stderr', channel='operation')
    logger.info('example log')
```

Will log:

```
[2023-01-25 13:48:05.010372] operation.info: example log {}
```

### Change log format

By default, logger record format is `[{date!s}] {channel!s}.{level!s}: {message!s} {context!s}`, 
to change it provide `log_format` parameter into logger constructor, for example:
 
```python3
import md.log
if __name__ == '__main__':
    logger = md.log.Logger(
        filename='/dev/stderr', 
        log_format='<{date!s}> ({channel!s}) [{level!s}] {message!s} {context!s}'
    )
    logger.info('example log')
```

Will log:

```
<2023-01-25 13:50:47.976986> (app) [info] example log {}
```

### Change log date format

By default, logger record date format is `%Y-%m-%d %H:%M:%S.%f`, 
to change it provide `date_format` parameter into logger constructor, for example:

```python3
import md.log
if __name__ == '__main__':
    logger = md.log.Logger(filename='/dev/stderr', date_format='%Y/%m/%d %H.%M.%S')
    logger.info('example log')
```

Will log:

```
[2023/01/25 13.53.10] app.info: example log {}
```

[architecture-overview]: _static/architecture.class-diagram.svg
