import collections
import datetime

import pytest
import unittest.mock

import psr.log
import md.log


class TestPidPatch:
    def test_patch(self) -> None:
        # arrange
        record = {'extra': {}}

        # act
        pid_patch = md.log.PidPatch()
        with unittest.mock.patch('os.getpid') as os_mock:
            os_mock.return_value = 42
            pid_patch.patch(record=record)

        # assert
        assert 'pid' in record['extra']
        assert record['extra']['pid'] == 42


class TestThreadPidPatch:
    def test_patch(self) -> None:
        # arrange
        record = {'extra': {}}

        # act
        with unittest.mock.patch('threading.get_native_id') as threading_mock:
            pid_patch = md.log.ThreadPidPatch()
            threading_mock.return_value = 42
            pid_patch.patch(record=record)

        # assert
        assert 'thread' in record['extra']
        assert record['extra']['thread'] == 42


class TestFormatExceptionPatch:
    def test_patch(self) -> None:  # white/positive
        # arrange
        try:
            raise RuntimeError()
        except RuntimeError as e:
            exception = e

        record = {
            'level': psr.log.LEVEL_DEBUG,
            'context': {'exception': exception}
        }

        # act
        with unittest.mock.patch('traceback.format_exception') as traceback_format_exception_mock:
            traceback_format_exception_mock.return_value = 'Traceback (Mock)'
            format_exception_patch = md.log.FormatExceptionPatch(level_set={
                psr.log.LEVEL_DEBUG,
            })
            format_exception_patch.patch(record=record)

        # assert
        traceback_format_exception_mock.assert_called_once_with(
            type(exception),
            exception,
            exception.__traceback__
        )
        assert record['context']['exception'] == 'Traceback (Mock)'

    def test_patch_wrong_exception_in_context(self) -> None:  # white/negative
        # arrange
        record = {
            'level': psr.log.LEVEL_DEBUG,
            'context': {'exception': 'something else'}
        }

        # act
        with unittest.mock.patch('traceback.format_exception') as traceback_format_exception_mock:
            format_exception_patch = md.log.FormatExceptionPatch(level_set={
                psr.log.LEVEL_DEBUG,
            })
            format_exception_patch.patch(record=record)

        # assert
        traceback_format_exception_mock.assert_not_called()
        assert record['context']['exception'] == 'something else'  # not changed

    def test_patch_ignores_level(self) -> None:  # white/negative
        # arrange
        try:
            raise RuntimeError('exception message')
        except RuntimeError as e:
            exception = e

        record = {
            'level': psr.log.LEVEL_DEBUG,
            'context': {'exception': exception}
        }

        # act
        with unittest.mock.patch('traceback.format_exception') as traceback_format_exception_mock:
            traceback_format_exception_mock.return_value = ['RuntimeError: exception message\n']
            format_exception_patch = md.log.FormatExceptionPatch(level_set={
                psr.log.LEVEL_CRITICAL,
            })
            format_exception_patch.patch(record=record)

        # assert
        traceback_format_exception_mock.assert_called_once_with(
            type(exception),
            exception,
            None
        )
        assert record['context']['exception'] == ['RuntimeError: exception message\n']

    def test_patch_without_exception_in_context(self) -> None:  # white/negative
        # arrange
        record = {
            'level': psr.log.LEVEL_DEBUG,
            'context': {}
        }

        # act
        with unittest.mock.patch('traceback.format_exception') as traceback_format_exception_mock:
            format_exception_patch = md.log.FormatExceptionPatch(level_set={
                psr.log.LEVEL_DEBUG,
            })
            format_exception_patch.patch(record=record)

        # assert
        traceback_format_exception_mock.assert_not_called()
        assert record['context'] == {}  # not changed


class TestFormat:
    @pytest.mark.parametrize(
        'level', ['emergency', 'alert', 'critical', 'error', 'warning', 'notice', 'info', 'debug', 'custom-level']
    )
    def test_format(self, level: str) -> None:
        # arrange
        channel = 'request'
        date_format = '%Y-%m-%d %H:%M:%S.%f'
        record_format = '[{date!s}] {channel!s}.{level!s}: {message!s} {context!s} {extra!s}'
        context = {'foo': 'bar'}
        extra = {'bar': 'baz'}
        message = 'log act'

        # act
        now_datetime_scalar = '2023-01-18 16:45:43.481516'
        now_datetime_mock = unittest.mock.Mock(spec=datetime.datetime)
        now_datetime_mock.strftime.return_value = now_datetime_scalar

        format_ = md.log.Format(
            record_format=record_format,
            date_format=date_format,
        )

        log = format_.format(record=collections.OrderedDict(
            date=now_datetime_mock,
            channel=channel,
            level=level,
            message=message,
            context=context,
            extra=extra,
        ))

        # assert
        now_datetime_mock.strftime.assert_called_once_with(date_format)
        assert log == f'[{now_datetime_scalar!s}] {channel!s}.{level.upper()!s}: {message!s}' + ' {"foo": "bar"} {"bar": "baz"}'


class TestKeepStream:
    @pytest.mark.parametrize(
        'level', ['emergency', 'alert', 'critical', 'error', 'warning', 'notice', 'info', 'debug', 'custom-level']
    )
    def test_handle(self, level: str) -> None:
        # arrange
        filename = '/tmp/md.log'
        channel = 'request'
        context = {'foo': 'bar'}
        extra = {'bar': 'baz'}
        message = 'log act'

        now_datetime_scalar = '2023-01-18 16:45:43.481516'
        now_datetime_mock = unittest.mock.Mock(spec=datetime.datetime)

        result_log = (  # actually, dummy example
            f'[{now_datetime_scalar!s}] {channel!s}.{level.upper()!s}: {message!s}'
            ' {"foo": "bar"} {"bar": "baz"}'
        )

        format_ = unittest.mock.Mock(spec=md.log.FormatInterface)
        format_.format.return_value = result_log

        # act
        with unittest.mock.patch('builtins.open') as open_mock:
            default_keep = md.log.KeepStream.from_file(
                filename_list=[filename],
                format_=format_,
            )
            default_keep.keep(record=dict(
                date=now_datetime_mock,
                channel=channel,
                level=level,
                message=message,
                context=context,
                extra=extra,
            ))

        # assert
        open_mock.assert_called_once_with(filename, 'a')
        open_mock.return_value.write.assert_called_once_with(result_log + '\n')
        open_mock.return_value.flush.assert_called_once()


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

        patch_1 = unittest.mock.Mock(spec=md.log.PatchInterface)
        patch_1.patch = process_1
        patch_2 = unittest.mock.Mock(spec=md.log.PatchInterface)
        patch_3 = unittest.mock.Mock(spec=md.log.PatchInterface)
        keep_1 = unittest.mock.Mock(spec=md.log.KeepInterface)
        keep_2 = unittest.mock.Mock(spec=md.log.KeepInterface)
        keep_3 = unittest.mock.Mock(spec=md.log.KeepInterface)

        patch_list = [patch_1, patch_2, patch_3]
        keep_list = [keep_1, keep_2, keep_3]

        now_datetime_scalar = '2023-01-18 16:45:43.481516'
        now_datetime_mock = unittest.mock.Mock(spec=datetime.datetime)
        now_datetime_mock.strftime.return_value = now_datetime_scalar

        record = collections.OrderedDict(
            date=now_datetime_mock,
            channel=channel,
            level=level,
            message=message,
            context=context,
            extra=collections.OrderedDict(foo='bar'),
        )

        # act
        logger = md.log.Logger(
            name=channel,
            keep_list=keep_list,
            patch_list=patch_list,
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
        for keep in keep_list:
            keep.keep.assert_called_once_with(record=record)

        for patch in [patch_2, patch_3]:
            patch.patch.assert_called_once_with(record=record)
