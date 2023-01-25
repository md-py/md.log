# Documentation
## Overview

md.log is advanced [psr.log 2](../psr.log) contract implementation component 
that provides API to perform application logging. Inspired by `monolog` 
(that inspired by monolog).

## Architecture overview

[![Architecture overview][architecture-overview]][architecture-overview]

## Installation

```sh
pip install md.log --index-url https://source.md.land/python/
```

## Usage

The basic usage case is writing log entries into a log file:

```python3
#!/usr/bin/env python3
import md.log


if __name__ == '__main__':
    # arrange
    logger = md.log.Logger(keep_list=[
        md.log.KeepStream.from_file(filename_list=['/tmp/my-app.log'])
    ])

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

```
# cat /tmp/my-app.log
[2023-01-18 17:23:17.403825] app.EMERGENCY: Application log {"context-example": 42}
[2023-01-18 17:23:17.404138] app.ALERT: Application log {"context-example": 42}
[2023-01-18 17:23:17.404974] app.CRITICAL: Application log {"context-example": 42}
[2023-01-18 17:23:17.405162] app.ERROR: Application log {"context-example": 42}
[2023-01-18 17:23:17.405231] app.WARNING: Application log {"context-example": 42}
[2023-01-18 17:23:17.405291] app.NOTICE: Application log {"context-example": 42}
[2023-01-18 17:23:17.405347] app.INFO: Application log {"context-example": 42}
[2023-01-18 17:23:17.405410] app.DEBUG: Application log {"context-example": 42}
[2023-01-18 17:23:17.405462] app.CUSTOM-LEVEL: Application log {"context-example": 42}
```

### Keep action

`md.log.KeepInterface` contract designed to keep log entry, 
it could be used to save to a file, or send via some protocol 
to somewhere (e.g. `elasticsearch`).

#### Keep to stream

`md.log.KeepStream` is implementation of `md.log.KeepInterface` contract out of box, 
designed to keep log entry to a stream (e.g. saving to a file).

##### keep into files configuration

```python3
md.log.KeepStream.from_file(filename_list=['/tmp/my-app.log'])
md.log.KeepStream.from_file(filename_list=['/tmp/my-app.log', '/dev/stderr'])
```

##### keep into already opened streams configuration 

This method could be useful when few loggers uses one stream, 
but it probably may block writing.

```python3
import md.log

stream_1 = open('/tmp/my-app.log', 'a')
stream_2 = open('/dev/stderr', 'a')
keep_stream = md.log.KeepStream(stream_list=[stream_1, stream_2])

# ... somewhere later:
md.log.Logger(name='request', keep_list=[keep_stream])
md.log.Logger(name='authorization', keep_list=[keep_stream])
md.log.Logger(name='form', keep_list=[keep_stream])
md.log.Logger(name='templating', keep_list=[keep_stream])
# etc ...
```

##### log format configuration

`md.log.KeepStream` constructor and `from_file` method takes optional
`format_: FormatInterface` parameter, that manages log entry format.
By default `md.log.Format` instance is used with default *record* and *date* formats. 
See [...] for more details.

### Format action

`md.log.FormatInterface` is a contract designed to format 
intermediate log entry (represented as `collection.OrderedDict` in runtime)
into a string, that will be handled (saved, sent, etc) 
by related `md.log.KeepInterface` action. 

Typically, this format action is injected into related `md.log.KeepInterface`
implementation and called on `keep` action is invoked, but by design this action 
may be reused in any other place to format internal structure to a string.

#### Format configuration

```python3
import md.log

# change only record format
format_ = md.log.Format(  
  record_format='<{date!s}> {channel!s}.{level!s}: {message!s} {context!s} {extra!s}',
)
# change only record datetime format
format_ = md.log.Format(        
  date_format='%Y-%m-%d %H:%M:%S',  # without microseconds
)
# change both
format_ = md.log.Format(  
  record_format='<{date!s}> {channel!s}.{level!s}: {message!s} {context!s} {extra!s}',
  date_format='%Y-%m-%d %H:%M:%S',  # without microseconds for example
)

# ... then somewhere later:

keep_stream = md.log.KeepStream.from_file(
    filename_list=['/dev/stderr'],
    format_=format_,
)

logger = md.log.Logger(keep_list=[keep_stream])
```

### Patch action

`md.log.PatchInterface` contract is designed to modify record 
until it kept by `md.log.KeepInterface`, typically it adds some extra 
data into log context or modifies some data 
of it (e.g. [FormatExceptionPatch](#format-exception-patch)).

#### Pid patch

`md.log.PidPatch` component adds current process id into each log entry context,
for example:

```python3
import md.log

if __name__ == '__main__':
    keep_stream = md.log.KeepStream.from_file(filename_list=['/dev/stderr'])
    pid_patch = md.log.PidPatch()
    
    logger = md.log.Logger(
        keep_list=[keep_stream], 
        patch_list=[pid_patch]
    )
    
    logger.debug('example log')
```

Will log:

```
[2023-01-25 12:51:55.955180] app.debug: example log {} {"pid": 42}
```

#### Thread pid patch

`md.log.ThreadPidPatch` component as just as `md.log.PidPatch`, but 
adds current thread id into each log entry context, for example:

```python3
import md.log

if __name__ == '__main__':
    keep_stream = md.log.KeepStream.from_file(filename_list=['/dev/stderr'])
    thread_pid_patch = md.log.ThreadPidPatch()
    
    logger = md.log.Logger(
        keep_list=[keep_stream], 
        patch_list=[thread_pid_patch]
    )
    
    logger.debug('example log')
```

Will log:

```
[2023-01-25 12:51:55.955180] app.debug: example log {} {"thread": 42}
```

#### Format exception patch

`md.log.FormatExceptionPatch` component converts caught exception instance
into string representation with traceback, when it's provided in log context, 
for example:

```python3
import md.log

if __name__ == '__main__':
    keep_stream = md.log.KeepStream.from_file(filename_list=['/dev/stderr'])
    format_exception_patch = md.log.FormatExceptionPatch()
    
    logger = md.log.Logger(
        keep_list=[keep_stream], 
        patch_list=[format_exception_patch]
    )
    
    try:
        raise RuntimeError()
    except RuntimeError as e:
        logger.error('Exception occurred', context={'exception': e})
```

Will log 

```
[2023-01-24 19:14:15.192289] app.error: Exception occurred {"exception": ["Traceback (most recent call last):\n", "  File \".../demo.py\", line 13, in <module>\n    raise RuntimeError()\n", "RuntimeError\n"]} {}
```

By default, traceback included for all standard log levels,
if custom level required to be enabled, or traceback should be omitted for some level,
new resolved level set should be provided in constructor, for example:

```python3
import psr.log
import md.log

md.log.FormatExceptionPatch(level_set={
    psr.log.LEVEL_EMERGENCY,
    psr.log.LEVEL_ALERT,
    psr.log.LEVEL_CRITICAL,
    'custom-level'
})
```


## Comparison

| -               | md.log | logging         | logbook         | monolog (php)   |
|-----------------|--------|-----------------|-----------------|-----------------|
| Logger          | Logger | Logger          | Logger          | Logger          |
| Handler         | Keep   | Handler         | Handler         | Handler         |
| RecordProcessor | Patch  | RecordProcessor | RecordProcessor | RecordProcessor |
| Formatter       | Format | Formatter       | Formatter       | Formatter       |

[architecture-overview]: _static/architecture.class-diagram.svg
