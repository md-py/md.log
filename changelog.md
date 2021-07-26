# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

## [1.0.0] - 2020-09-26

- Basic `psr.log:^1` implementation

[2.0.0]: https://github.com/md-py/md.log/releases/tag/2.0.0
[1.0.0]: https://github.com/md-py/md.log/releases/tag/1.0.0
