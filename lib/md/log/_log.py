import json
import os
import datetime
import collections
import threading
import typing

import psr.log


# Metadata
__version__ = '3.0.0'
__author__ = 'https://md.land/md'
__all__ = (
    # Metadata
    '__version__',
    '__author__',
    # Contract
    'PatchInterface',
    'FormatExceptionPatch',
    'FormatInterface',
    'KeepInterface',
    # Implementation
    'PidPatch',
    'ThreadPidPatch',
    'KeepStream',
    'Format',
    'Logger',
)


# Contract
class PatchInterface:
    def patch(self, record: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        """ Modifies log record before handle """
        raise NotImplementedError


class FormatInterface:
    def format(self, record: typing.Dict[str, typing.Any]) -> str:
        raise NotImplementedError


class KeepInterface:
    def keep(self, record: typing.Dict[str, typing.Any]) -> None:
        """ Writes a log message """
        raise NotImplementedError


# Implementation
class PidPatch(PatchInterface):
    """ Adds process identifier to log record """
    def patch(self, record: typing.Dict[str, typing.Any]) -> dict:
        record['extra']['pid'] = os.getpid()
        return record


class ThreadPidPatch(PatchInterface):
    """ Adds process identifier to log record """
    def __init__(self) -> None:
        # assert py_ver >= 3.8
        import threading
        self.threading = threading

    def patch(self, record: typing.Dict[str, typing.Any]) -> dict:
        record['extra']['thread'] = threading.get_native_id()
        return record


class FormatExceptionPatch(PatchInterface):
    def __init__(self, level_set: set = None) -> None:
        import traceback
        self._traceback = traceback
        self._level_set = level_set or {
            psr.log.LEVEL_EMERGENCY,
            psr.log.LEVEL_ALERT,
            psr.log.LEVEL_CRITICAL,
            psr.log.LEVEL_ERROR,
            psr.log.LEVEL_WARNING,
            psr.log.LEVEL_NOTICE,
            psr.log.LEVEL_INFO,
            psr.log.LEVEL_DEBUG,
        }

    def patch(self, record: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        if 'exception' not in record['context']:
            return record

        exception = record['context']['exception']
        if not isinstance(exception, Exception):
            return record

        assert 'level' in record
        if record['level'] not in self._level_set:
            record['context']['exception'] = self._traceback.format_exception(
                type(exception),
                exception,
                None
            )
            return record

        record['context']['exception'] = self._traceback.format_exception(
            type(exception),
            exception,
            exception.__traceback__,
        )

        return record


class Format(FormatInterface):
    def __init__(self, record_format: str = None, date_format: str = None) -> None:
        self._record_format = record_format or '[{date!s}] {channel!s}.{level!s}: {message!s} {context!s} {extra!s}'
        self._date_format = date_format or '%Y-%m-%d %H:%M:%S.%f'

    def format(self, record: typing.Dict[str, typing.Any]) -> str:
        return self._record_format.format(
            date=record['date'].strftime(self._date_format),
            channel=record['channel'].lower(),
            level=record['level'].upper(),
            message=record['message'],
            context=json.dumps(record['context']) if record['context'] else '{}',
            extra=json.dumps(record['extra']) if record['extra'] else '{}',
        )

    def __repr__(self) -> str:
        return 'FormatRecord(' \
               f'record_format={self._record_format!r}, ' \
               f'date_format={self._date_format!r}' \
               ')'


class KeepStream(KeepInterface):
    def __init__(
        self,
        stream_list: typing.List[typing.IO],
        format_: FormatInterface = None
    ) -> None:
        self._format = format_ or Format()
        self._stream_list = stream_list

    def keep(self, record: typing.Dict[str, typing.Any]) -> None:
        """ Writes a log message """
        log = self._format.format(record=record)

        for stream in self._stream_list:
            stream.write(log + '\n')
            stream.flush()

    @classmethod
    def from_file(cls, filename_list: typing.List[str], format_: FormatInterface = None) -> 'KeepStream':
        assert isinstance(filename_list, list)
        return cls(
            stream_list=[open(filename, 'a') for filename in filename_list],
            format_=format_,
        )

    def __repr__(self) -> str:
        return f'StreamHandler(stream_list={self._stream_list!r}), format={self._format!r}'

    def __del__(self) -> None:
        if hasattr(self, '_stream_list'):
            for stream in self._stream_list:
                if not stream.closed:
                    stream.close()


class Logger(psr.log.LoggerInterface):
    def __init__(
        self,
        name: str = 'app',
        keep_list: typing.List[KeepInterface] = None,
        patch_list: typing.List[PatchInterface] = None,
    ) -> None:
        self._name = name
        self._keep_list = keep_list or []
        self._patch_list = patch_list or []
        assert len(self._keep_list) > 0, 'No keep action makes no sense'

    def __repr__(self) -> str:
        return 'Logger(' \
               f'name={self._name!r}, ' \
               f'keep_list={self._keep_list!r}, ' \
               f'patch_list={self._patch_list!r}' \
               ')'

    def emergency(self, message: str, context: dict = None) -> None:
        self.log(level=psr.log.LEVEL_EMERGENCY, message=message, context=context)

    def alert(self, message: str, context: dict = None) -> None:
        self.log(level=psr.log.LEVEL_ALERT, message=message, context=context)

    def critical(self, message: str, context: dict = None) -> None:
        self.log(level=psr.log.LEVEL_CRITICAL, message=message, context=context)

    def error(self, message: str, context: dict = None) -> None:
        self.log(level=psr.log.LEVEL_ERROR, message=message, context=context)

    def warning(self, message: str, context: dict = None) -> None:
        self.log(level=psr.log.LEVEL_WARNING, message=message, context=context)

    def notice(self, message: str, context: dict = None) -> None:
        self.log(level=psr.log.LEVEL_NOTICE, message=message, context=context)

    def info(self, message: str, context: dict = None) -> None:
        self.log(level=psr.log.LEVEL_INFO, message=message, context=context)

    def debug(self, message: str, context: dict = None) -> None:
        self.log(level=psr.log.LEVEL_DEBUG, message=message, context=context)

    def log(self, level: str, message: str, context: dict = None) -> None:
        """ Writes a log message """
        record = collections.OrderedDict(
            date=datetime.datetime.now(),
            channel=self._name,
            level=level,
            message=message,
            context=context or collections.OrderedDict(),
            extra=collections.OrderedDict(),
        )

        for patch in self._patch_list:
            patch.patch(record=record)

        for keep in self._keep_list:
            keep.keep(record=record)
