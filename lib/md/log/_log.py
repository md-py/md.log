import json
import os
import datetime
import typing

import psr.log


# Metadata
__version__ = '2.0.0'
__author__ = 'https://md.land/md'
__all__ = (
    # Metadata
    '__version__',
    '__author__',
    # Contract
    'RecordProcessorInterface',
    'HandlerInterface',
    # Implementation
    'PidRecordProcessor',
    'DefaultHandler',
    'Logger',
)


# Public contracts
class RecordProcessorInterface:
    def process(self, record: dict) -> dict:
        """ Modifies log record before handle """
        raise NotImplementedError


class HandlerInterface:
    def handle(self, record: dict) -> None:
        raise NotImplementedError


# Out-of-box implementation
class PidRecordProcessor(RecordProcessorInterface):
    """ Adds process identifier to log record """

    def process(self, record: dict) -> dict:
        record['extra']['pid'] = os.getpid()
        return record


class DefaultHandler(HandlerInterface):
    def __init__(self, filename: str, record_format: str = None, date_format: str = None) -> None:
        self._record_format = record_format or '[{date!s}] {channel!s}.{level!s}: {message!s} {context!s} {extra!s}'
        self._date_format = date_format or '%Y-%m-%d %H:%M:%S.%f'
        self._filename = filename

        self._stream = open(self._filename, 'a')

    def __repr__(self) -> str:
        return 'DefaultHandler(' \
               f'filename={self._filename!r}, ' \
               f'record_format={self._record_format!r}, ' \
               f'date_format={self._date_format!r}' \
               ')'

    def handle(self, record: dict) -> None:
        """ Writes a log message """
        self._stream.write(self._record_format.format(
            date=record['date'].strftime(self._date_format),
            channel=record['channel'].lower(),
            level=record['level'].upper(),
            message=record['message'],
            context=json.dumps(record['context']) if record['context'] else '{}',
            extra=json.dumps(record['extra']) if record['extra'] else '{}',
        ) + '\n')
        self._stream.flush()

    def __del__(self) -> None:
        if hasattr(self, '_stream') and not self._stream.closed:
            self._stream.close()


# Main API
class Logger(psr.log.LoggerInterface):
    """
    PSR-3 (PHP Standard) logger implementation for Python.

    Example:

        # Main instance initialization with absolute path to log file
        logger = Logger(handler_list=[DefaultHandler(filename='/var/log/my-app.log')]

        # Log some message
        logger.info('Client registration process started', context={'client_data': dict(client_dto)})
    """

    def __init__(
        self,
        name: str = 'app',
        handler_list: typing.List[HandlerInterface] = None,
        record_processor_list: typing.List[RecordProcessorInterface] = None,
    ) -> None:
        self._name = name
        self._handler_list = handler_list or []
        self._record_processor_list = record_processor_list or []
        assert len(self._handler_list) > 0, 'Logger without handler makes no sense'

    def __repr__(self) -> str:
        return 'Logger(' \
               f'name={self._name!r}, ' \
               f'record_processor_list={self._record_processor_list!r}, ' \
               f'handler_list={self._handler_list!r}' \
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
        record = {
            'date': datetime.datetime.now(),
            'channel': self._name,
            'level': level,
            'message': message,
            'context': context,
            'extra': {},
        }

        for record_processor in self._record_processor_list:
            record_processor.process(record=record)

        for handler in self._handler_list:
            handler.handle(record=record)
