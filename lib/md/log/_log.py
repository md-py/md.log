import json
import datetime

import psr.log


__version__ = '1.1.0'
__author__ = 'https://md.land/md'
__all__ = (
    # Metadata
    '__version__',
    '__author__',
    # Implementation
    'Logger',
)


class Logger(psr.log.LoggerInterface):
    """
    Simplest PSR-3 (PHP Standard) logger implementation for Python.

    Example:

        # Main instance initialization with absolute path to log file
        logger = Logger(filename='/var/log/my-app.log')

        # Log some message
        logger.info('Client registration process started', context={'client_data': dict(client_dto)})
    """

    def __init__(
        self,
        filename: str,
        channel: str = None,
        log_format: str = None,
        date_format: str = None,
    ) -> None:
        self._stream = open(filename, 'a')
        self._channel = channel or 'app'
        self._log_format = log_format or '[{date!s}] {channel!s}.{level!s}: {message!s} {context!s}'
        self._date_format = date_format or '%Y-%m-%d %H:%M:%S.%f'

    def __del__(self) -> None:
        if not self._stream.closed:
            self._stream.close()

    def emergency(self, message: str, context: dict = None) -> None:
        self.log(level=psr.log.LogLevel.EMERGENCY, message=message, context=context)

    def alert(self, message: str, context: dict = None) -> None:
        self.log(level=psr.log.LogLevel.ALERT, message=message, context=context)

    def critical(self, message: str, context: dict = None) -> None:
        self.log(level=psr.log.LogLevel.CRITICAL, message=message, context=context)

    def error(self, message: str, context: dict = None) -> None:
        self.log(level=psr.log.LogLevel.ERROR, message=message, context=context)

    def warning(self, message: str, context: dict = None) -> None:
        self.log(level=psr.log.LogLevel.WARNING, message=message, context=context)

    def notice(self, message: str, context: dict = None) -> None:
        self.log(level=psr.log.LogLevel.NOTICE, message=message, context=context)

    def info(self, message: str, context: dict = None) -> None:
        self.log(level=psr.log.LogLevel.INFO, message=message, context=context)

    def debug(self, message: str, context: dict = None) -> None:
        self.log(level=psr.log.LogLevel.DEBUG, message=message, context=context)

    def log(self, level: str, message: str, context: dict = None) -> None:
        """ Writes a log message """
        self._stream.write(self._log_format.format(
            date=datetime.datetime.now().strftime(self._date_format),
            channel=self._channel,
            level=level,
            message=message,
            context=json.dumps(context) if context else '{}',
        ) + '\n')
        self._stream.flush()
