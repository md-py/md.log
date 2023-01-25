import datetime

import pytest
import unittest.mock

import md.log


class TestLogger:
    @pytest.mark.parametrize('method,level', [
        ('emergency', 'emergency'),
        ('alert', 'alert'),
        ('critical', 'critical'),
        ('error', 'error'),
        ('warning', 'warning'),
        ('notice', 'notice'),
        ('info', 'info'),
        ('debug', 'debug'),
        ('log', 'custom-level'),
    ])
    def test_log(self, method: str, level: str) -> None:
        # arrange
        filename = '/tmp/md.log'
        channel = 'request'
        date_format = '%Y-%m-%d %H:%M:%S.%f'
        log_format = '[{date!s}] {channel!s}.{level!s}: {message!s} {context!s}'
        context = {'foo': 'bar'}
        message = 'log act'

        now_datetime_scalar = '2023-01-18 16:45:43.481516'
        now_datetime_mock = unittest.mock.Mock(spec=datetime.datetime)
        now_datetime_mock.strftime.return_value = now_datetime_scalar

        # act
        with (
            unittest.mock.patch('builtins.open') as open_mock,
            unittest.mock.patch('datetime.datetime') as datetime_datetime_mock,
        ):
            datetime_datetime_mock.now.return_value = now_datetime_mock
            logger = md.log.Logger(
                filename=filename,
                channel=channel,
                log_format=log_format,
                date_format=date_format,
            )

            assert hasattr(logger, method)
            logging_method = getattr(logger, method)

            kw = dict(message=message, context=context)
            if method == 'log': kw['level'] = level  # ... a lit bit dirty, but ok

            logging_method(**kw)

        # assert
        now_datetime_mock.strftime.assert_called_once_with(date_format)
        open_mock.assert_called_once_with(filename, 'a')
        open_mock.return_value.write.assert_called_once_with(
            f'[{now_datetime_scalar!s}] {channel!s}.{level!s}: {message!s}' + ' {"foo": "bar"}\n'
        )
        open_mock.return_value.flush.assert_called_once()
