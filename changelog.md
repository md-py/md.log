# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.2.0] - 2023-01-25
### Added 

- `md.log.SerializationFormat` component implemented to use any log 
  entry serialization (e.g. JSON) 
- add `PidPatch`, `ThreadPidPatch`, `FormatExceptionPatch` components instance representation

### Changed

- internal documentation remastering
  added usage examples, components specification.

### Fixed

- `Format`, `KeepStream` components instance representation fixed

## [3.1.0] - 2023-01-25
### Changed

- enhancement: remove string case cast from log entry format:
  record entry elements will not be modified in custom format.

## [3.0.0] - 2022-01-18
### Changed

- internal logger record type changed from `dict` to `collections.OrderedDict`

#### Backward compatibility breaking change

- `RecordProcessorInterface` renamed to `PatchInterface`
  - method `process` renamed to `patch`
- `HandlerInterface` renamed to `KeepInterface`
  - method `handle` renamed to `keep`
- `DefaultHandler` renamed to `KeepStream`
  - constructor signature changed from
    `(self, filename: str, record_format: str = None, date_format: str = None) -> None`
    to `(self, stream_list: typing.List[typing.IO], format_: FormatInterface = None) -> None`
  - method `handle` renamed to `keep`
- `Logger` signatuge changed from
  `(self, name: str = 'app', handler_list: typing.List[HandlerInterface] = None, record_processor_list: typing.List[RecordProcessorInterface] = None) -> None`
  to `(self, name: str = 'app', keep_list: typing.List[KeepInterface] = None, patch_list: typing.List[PatchInterface] = None) -> None`

### Added

- `FormatInterface` contact extracted out from `DefaultHandler` to render a message
- `Format` message render implementation extracted out from `DefaultHandler`
- `PidPatch` adds process id that calls `log` method into log message context
- `ThreadPidPatch` adds thread process id that calls `log` method into log message context
- `FormatExceptionPatch` renders exception traceback for configured log levels, when 
  exception provided in log context. (eg. `record['context']['exception']`)

## [2.1.0] - 2023-01-25
### Changed

- enhancement: remove string case cast from log entry format:
  record entry elements will not be modified in custom format.

## [2.0.0] - 2022-07-27 

### Changed
#### Backward compatibility breaking change

- Logger contract `psr.log` switched from `>=1.*` to `>=2.*`
- md.log.Logger constructor signature changed
  from: `(self, filename: str, channel: str = None, log_format: str = None, date_format: str = None) -> None:`
  to: `(self, name: str = 'app', handler_list: typing.List[HandlerInterface] = None, record_processor_list: typing.List[RecordProcessorInterface] = None) -> None`
- md.log.Logger record flush logic moved to default record processor implementation

### Added

- logger handler component (contract and default implementation)
- record processor component (contract and default implementation)

## [1.1.0] - 2023-01-25
### Changed

- enhancement: remove string case cast from log entry format:
  record entry elements will not be modified in custom format.

## [1.0.0] - 2020-09-26

- Basic `psr.log:^1` implementation

[3.2.0]: https://github.com/md-py/md.log/releases/tag/3.2.0
[3.1.0]: https://github.com/md-py/md.log/releases/tag/3.1.0
[3.0.0]: https://github.com/md-py/md.log/releases/tag/3.0.0
[2.1.0]: https://github.com/md-py/md.log/releases/tag/2.1.0
[2.0.0]: https://github.com/md-py/md.log/releases/tag/2.0.0
[1.1.0]: https://github.com/md-py/md.log/releases/tag/1.1.0
[1.0.0]: https://github.com/md-py/md.log/releases/tag/1.0.0
