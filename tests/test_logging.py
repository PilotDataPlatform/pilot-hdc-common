# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.


import datetime as dt
import json
import logging
from logging import LogRecord
from logging import getLevelName

from common.logging.logging import AUDIT
from common.logging.logging import JsonFormatter
from common.logging.logging import Logger
from common.logging.logging import configure_logging
from common.logging.logging import extend_logger_class


class TestJsonFormatter:
    def test_format_converts_log_record_into_expected_json_string(self, fake):
        logger = fake.word()
        level = fake.pyint(0, 5) * 10
        message = fake.word()
        exception_message = fake.text()
        exception = Exception(exception_message)
        exc_info = (type(exception), exception, exception.__traceback__)
        details = fake.pydict(allowed_types=(str, int, float, bool))
        record = LogRecord(logger, level, '', 0, message, details, exc_info)
        asctime = dt.datetime.fromtimestamp(record.created, tz=dt.timezone.utc).isoformat()
        expected_string = json.dumps(
            {
                'asctime': asctime,
                'level': getLevelName(level),
                'logger': logger,
                'message': message,
                'exc_info': f'Exception: {exception_message}',
                'details': details,
            }
        )

        received_string = JsonFormatter().format(record)

        assert received_string == expected_string


class TestLogging:
    def test_configure_logging_calls_dict_configurator_with_expected_config(self, mocker, fake):
        mock = mocker.patch('logging.config.dictConfig')
        level = fake.pyint(0, 5) * 10
        expected_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'default': {'format': '%(asctime)s\t%(levelname)s\t' '[%(name)s]\t%(message)s'},
                'json': {'()': JsonFormatter},
            },
            'handlers': {
                'stdout': {
                    'formatter': 'default',
                    'class': 'logging.StreamHandler',
                    'stream': 'ext://sys.stdout',
                }
            },
            'loggers': {
                'pilot': {'handlers': ['stdout'], 'level': level},
                'asyncio': {'handlers': ['stdout'], 'level': level},
                'uvicorn': {'handlers': ['stdout'], 'level': level},
            },
        }

        configure_logging(level, 'non-existing')

        mock.assert_called_once_with(expected_config)

    def test_extend_logger_class_adds_audit_method_into_already_created_logger(self, mocker, fake):
        logger: Logger = logging.getLogger(fake.pystr())
        logger.setLevel(logging.INFO)
        log_method = mocker.spy(logger, '_log')
        message = fake.word()
        kwds = fake.pydict(allowed_types=(str, int, float, bool))

        extend_logger_class()
        logger.audit(message, **kwds)

        log_method.assert_called_once_with(AUDIT, message, args=(kwds,))
