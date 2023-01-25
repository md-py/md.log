import datetime

import pytest
import unittest.mock

import md.log


class TestPidRecordProcessor:
    def test_process(self) -> None:
        # arrange
        record = {'extra': {}}

        # act
        pid_record_processor = md.log.PidRecordProcessor()
        with unittest.mock.patch('os.getpid') as os_mock:
            os_mock.return_value = 42
            pid_record_processor.process(record=record)

        # assert
        assert 'pid' in record['extra']
        assert record['extra']['pid'] == 42


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
        channel = 'request'
        context = {'foo': 'bar'}
        message = 'log act'

        def process_1(record: dict) -> None:
            record['extra']['foo'] = 'bar'

        record_processor_1 = unittest.mock.Mock(spec=md.log.RecordProcessorInterface)
        record_processor_1.process = process_1
        record_processor_2 = unittest.mock.Mock(spec=md.log.RecordProcessorInterface)
        record_processor_3 = unittest.mock.Mock(spec=md.log.RecordProcessorInterface)
        handler_1 = unittest.mock.Mock(spec=md.log.HandlerInterface)
        handler_2 = unittest.mock.Mock(spec=md.log.HandlerInterface)
        handler_3 = unittest.mock.Mock(spec=md.log.HandlerInterface)

        record_processor_list = [record_processor_1, record_processor_2, record_processor_3]
        handler_list = [handler_1, handler_2, handler_3]

        now_datetime_scalar = '2023-01-18 16:45:43.481516'
        now_datetime_mock = unittest.mock.Mock(spec=datetime.datetime)
        now_datetime_mock.strftime.return_value = now_datetime_scalar

        record = {
            'date': now_datetime_mock,
            'channel': channel,
            'level': level,
            'message': message,
            'context': context,
            'extra': {'foo': 'bar'},
        }

        # act

        logger = md.log.Logger(
            name=channel,
            handler_list=handler_list,
            record_processor_list=record_processor_list,
        )

        assert hasattr(logger, method)
        logging_method = getattr(logger, method)

        kw = dict(message=message, context=context)
        if method == 'log':
            kw['level'] = level  # ... a lit bit dirty, but ok

        with unittest.mock.patch('datetime.datetime') as datetime_datetime_mock:
            datetime_datetime_mock.now.return_value = now_datetime_mock
            logging_method(**kw)

        # assert
        for handler in handler_list:
            handler.handle.assert_called_once_with(record=record)

        for record_processor in [record_processor_2, record_processor_3]:
            record_processor.process.assert_called_once_with(record=record)


class TestDefaultHandler:
    @pytest.mark.parametrize(
        'level', ['emergency', 'alert', 'critical', 'error', 'warning', 'notice', 'info', 'debug', 'custom-level']
    )
    def test_handle(self, level: str) -> None:
        # arrange
        filename = '/tmp/md.log'
        channel = 'request'
        date_format = '%Y-%m-%d %H:%M:%S.%f'
        record_format = '[{date!s}] {channel!s}.{level!s}: {message!s} {context!s} {extra!s}'
        context = {'foo': 'bar'}
        extra = {'bar': 'baz'}
        message = 'log act'

        now_datetime_scalar = '2023-01-18 16:45:43.481516'
        now_datetime_mock = unittest.mock.Mock(spec=datetime.datetime)
        now_datetime_mock.strftime.return_value = now_datetime_scalar

        # act
        with (
            unittest.mock.patch('builtins.open') as open_mock,
            # unittest.mock.patch('datetime.datetime') as datetime_datetime_mock,
        ):
            # datetime_datetime_mock.now.return_value = now_datetime_mock
            default_handler = md.log.DefaultHandler(
                filename=filename,
                record_format=record_format,
                date_format=date_format
            )
            default_handler.handle(record=dict(
                date=now_datetime_mock,
                channel=channel,
                level=level,
                message=message,
                context=context,
                extra=extra,
            ))

        # assert
        now_datetime_mock.strftime.assert_called_once_with(date_format)
        open_mock.assert_called_once_with(filename, 'a')
        open_mock.return_value.write.assert_called_once_with(
            f'[{now_datetime_scalar!s}] {channel!s}.{level!s}: {message!s}' + ' {"foo": "bar"} {"bar": "baz"}\n'
        )
        open_mock.return_value.flush.assert_called_once()
