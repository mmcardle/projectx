from django.db.utils import OperationalError

from projectx.common.management.commands.check_db_connection import (
    Command as CheckDbConnection,
)


def test_check_db_connection(mocker):
    connection = mocker.patch("projectx.common.management.commands.check_db_connection.connection")

    CheckDbConnection().handle()

    assert connection.mock_calls == [
        mocker.call.ensure_connection(),
    ]


def test_check_db_connection_operational_error(mocker):
    mocker.patch("projectx.common.management.commands.check_db_connection.time")

    connection = mocker.patch(
        "projectx.common.management.commands.check_db_connection.connection",
    )
    connection.ensure_connection.side_effect = [OperationalError, None]

    CheckDbConnection().handle()

    assert connection.mock_calls == [
        mocker.call.ensure_connection(),
        mocker.call.ensure_connection(),
    ]
