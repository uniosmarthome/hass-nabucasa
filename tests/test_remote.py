"""Test remote sni handler."""
import asyncio
from datetime import timedelta
from tests.async_mock import patch, Mock

import pytest

from hass_uniocloud.const import (
    DISPATCH_REMOTE_BACKEND_DOWN,
    DISPATCH_REMOTE_BACKEND_UP,
    DISPATCH_REMOTE_CONNECT,
    DISPATCH_REMOTE_DISCONNECT,
)
from hass_uniocloud.remote import RemoteUI, SubscriptionExpired
from hass_uniocloud.utils import utcnow

from .common import MockAcme, MockSnitun


@pytest.fixture(autouse=True)
def ignore_context():
    """Ignore ssl context."""
    with patch(
        "hass_uniocloud.remote.RemoteUI._create_context", return_value=None
    ) as context:
        yield context


@pytest.fixture
def acme_mock():
    """Mock ACME client."""
    with patch("hass_uniocloud.remote.AcmeHandler", new_callable=MockAcme) as acme:
        yield acme


@pytest.fixture
def valid_acme_mock(acme_mock):
    """Mock ACME client with valid cert."""
    acme_mock.common_name = "test.dui.unio.cloud"
    acme_mock.expire_date = utcnow() + timedelta(days=60)
    return acme_mock


@pytest.fixture
async def snitun_mock():
    """Mock ACME client."""
    with patch("hass_uniocloud.remote.SniTunClientAioHttp", MockSnitun()) as snitun:
        yield snitun


def test_init_remote(auth_cloud_mock):
    """Init remote object."""
    RemoteUI(auth_cloud_mock)

    assert len(auth_cloud_mock.mock_calls) == 2


async def test_load_backend_exists_cert(
    auth_cloud_mock, valid_acme_mock, mock_cognito, aioclient_mock, snitun_mock
):
    """Initialize backend."""
    valid = utcnow() + timedelta(days=1)
    auth_cloud_mock.remote_api_url = "https://test.local/api"
    remote = RemoteUI(auth_cloud_mock)

    aioclient_mock.post(
        "https://test.local/api/register_instance",
        json={
            "domain": "test.dui.unio.cloud",
            "email": "test@uniocloud.com",
            "server": "rest-remote.unio.cloud",
        },
    )
    aioclient_mock.post(
        "https://test.local/api/snitun_token",
        json={
            "token": "test-token",
            "server": "rest-remote.unio.cloud",
            "valid": valid.timestamp(),
            "throttling": 400,
        },
    )

    assert not remote.is_connected
    await remote.start()
    assert remote.snitun_server == "rest-remote.unio.cloud"
    assert remote.instance_domain == "test.dui.unio.cloud"

    assert not valid_acme_mock.call_issue
    assert valid_acme_mock.init_args == (
        auth_cloud_mock,
        "test.dui.unio.cloud",
        "test@uniocloud.com",
    )
    assert valid_acme_mock.call_hardening
    assert snitun_mock.call_start
    assert snitun_mock.init_args == (auth_cloud_mock.client.aiohttp_runner, None)
    assert snitun_mock.init_kwarg == {
        "snitun_server": "rest-remote.unio.cloud",
        "snitun_port": 443,
    }

    await asyncio.sleep(0.1)
    assert snitun_mock.call_connect
    assert snitun_mock.connect_args[0] == b"test-token"
    assert snitun_mock.connect_args[3] == 400
    assert remote.is_connected

    assert remote._acme_task
    assert remote._reconnect_task

    assert auth_cloud_mock.client.mock_dispatcher[0][0] == DISPATCH_REMOTE_BACKEND_UP
    assert auth_cloud_mock.client.mock_dispatcher[1][0] == DISPATCH_REMOTE_CONNECT


async def test_load_backend_not_exists_cert(
    auth_cloud_mock, acme_mock, mock_cognito, aioclient_mock, snitun_mock
):
    """Initialize backend."""
    valid = utcnow() + timedelta(days=1)
    auth_cloud_mock.remote_api_url = "https://test.local/api"
    remote = RemoteUI(auth_cloud_mock)

    aioclient_mock.post(
        "https://test.local/api/register_instance",
        json={
            "domain": "test.dui.unio.cloud",
            "email": "test@uniocloud.com",
            "server": "rest-remote.unio.cloud",
        },
    )
    aioclient_mock.post(
        "https://test.local/api/snitun_token",
        json={
            "token": "test-token",
            "server": "rest-remote.unio.cloud",
            "valid": valid.timestamp(),
            "throttling": 400,
        },
    )

    acme_mock.set_false()
    await remote.start()
    await asyncio.sleep(0.1)

    assert remote.snitun_server == "rest-remote.unio.cloud"
    assert acme_mock.call_issue
    assert acme_mock.init_args == (
        auth_cloud_mock,
        "test.dui.unio.cloud",
        "test@uniocloud.com",
    )
    assert acme_mock.call_hardening
    assert snitun_mock.call_start
    assert snitun_mock.init_args == (auth_cloud_mock.client.aiohttp_runner, None)
    assert snitun_mock.init_kwarg == {
        "snitun_server": "rest-remote.unio.cloud",
        "snitun_port": 443,
    }

    assert snitun_mock.call_connect
    assert snitun_mock.connect_args[0] == b"test-token"
    assert snitun_mock.connect_args[3] == 400

    assert remote._acme_task
    assert remote._reconnect_task


async def test_load_and_unload_backend(
    auth_cloud_mock, valid_acme_mock, mock_cognito, aioclient_mock, snitun_mock
):
    """Initialize backend."""
    valid = utcnow() + timedelta(days=1)
    auth_cloud_mock.remote_api_url = "https://test.local/api"
    remote = RemoteUI(auth_cloud_mock)

    aioclient_mock.post(
        "https://test.local/api/register_instance",
        json={
            "domain": "test.dui.unio.cloud",
            "email": "test@uniocloud.com",
            "server": "rest-remote.unio.cloud",
        },
    )
    aioclient_mock.post(
        "https://test.local/api/snitun_token",
        json={
            "token": "test-token",
            "server": "rest-remote.unio.cloud",
            "valid": valid.timestamp(),
            "throttling": 400,
        },
    )

    await remote.start()
    await asyncio.sleep(0.1)

    assert remote.snitun_server == "rest-remote.unio.cloud"
    assert not valid_acme_mock.call_issue
    assert valid_acme_mock.init_args == (
        auth_cloud_mock,
        "test.dui.unio.cloud",
        "test@uniocloud.com",
    )
    assert valid_acme_mock.call_hardening
    assert snitun_mock.call_start
    assert not snitun_mock.call_stop
    assert snitun_mock.init_args == (auth_cloud_mock.client.aiohttp_runner, None)
    assert snitun_mock.init_kwarg == {
        "snitun_server": "rest-remote.unio.cloud",
        "snitun_port": 443,
    }

    assert remote._acme_task
    assert remote._reconnect_task

    await remote.stop()
    await asyncio.sleep(0.1)

    assert snitun_mock.call_stop

    assert not remote._acme_task
    assert not remote._reconnect_task

    assert auth_cloud_mock.client.mock_dispatcher[-1][0] == DISPATCH_REMOTE_BACKEND_DOWN


async def test_load_backend_exists_wrong_cert(
    auth_cloud_mock, valid_acme_mock, mock_cognito, aioclient_mock, snitun_mock
):
    """Initialize backend."""
    valid = utcnow() + timedelta(days=1)
    auth_cloud_mock.remote_api_url = "https://test.local/api"
    remote = RemoteUI(auth_cloud_mock)

    aioclient_mock.post(
        "https://test.local/api/register_instance",
        json={
            "domain": "test.dui.unio.cloud",
            "email": "test@uniocloud.com",
            "server": "rest-remote.unio.cloud",
        },
    )
    aioclient_mock.post(
        "https://test.local/api/snitun_token",
        json={
            "token": "test-token",
            "server": "rest-remote.unio.cloud",
            "valid": valid.timestamp(),
            "throttling": 400,
        },
    )

    valid_acme_mock.common_name = "wrong.dui.unio.cloud"
    await remote.load_backend()
    await asyncio.sleep(0.1)

    assert remote.snitun_server == "rest-remote.unio.cloud"
    assert valid_acme_mock.call_reset
    assert valid_acme_mock.init_args == (
        auth_cloud_mock,
        "test.dui.unio.cloud",
        "test@uniocloud.com",
    )
    assert valid_acme_mock.call_hardening
    assert snitun_mock.call_start
    assert snitun_mock.init_args == (auth_cloud_mock.client.aiohttp_runner, None)
    assert snitun_mock.init_kwarg == {
        "snitun_server": "rest-remote.unio.cloud",
        "snitun_port": 443,
    }

    assert snitun_mock.call_connect
    assert snitun_mock.connect_args[0] == b"test-token"
    assert snitun_mock.connect_args[3] == 400


async def test_call_disconnect(
    auth_cloud_mock, acme_mock, mock_cognito, aioclient_mock, snitun_mock
):
    """Initialize backend."""
    valid = utcnow() + timedelta(days=1)
    auth_cloud_mock.remote_api_url = "https://test.local/api"
    remote = RemoteUI(auth_cloud_mock)

    aioclient_mock.post(
        "https://test.local/api/register_instance",
        json={
            "domain": "test.dui.unio.cloud",
            "email": "test@uniocloud.com",
            "server": "rest-remote.unio.cloud",
        },
    )
    aioclient_mock.post(
        "https://test.local/api/snitun_token",
        json={
            "token": "test-token",
            "server": "rest-remote.unio.cloud",
            "valid": valid.timestamp(),
            "throttling": 400,
        },
    )

    assert not remote.is_connected
    await remote.load_backend()
    await asyncio.sleep(0.1)
    assert remote.is_connected

    await remote.disconnect()
    assert snitun_mock.call_disconnect
    assert not remote.is_connected
    assert auth_cloud_mock.client.mock_dispatcher[-1][0] == DISPATCH_REMOTE_DISCONNECT


async def test_load_backend_no_autostart(
    auth_cloud_mock, valid_acme_mock, mock_cognito, aioclient_mock, snitun_mock
):
    """Initialize backend."""
    valid = utcnow() + timedelta(days=1)
    auth_cloud_mock.remote_api_url = "https://test.local/api"
    remote = RemoteUI(auth_cloud_mock)

    aioclient_mock.post(
        "https://test.local/api/register_instance",
        json={
            "domain": "test.dui.unio.cloud",
            "email": "test@uniocloud.com",
            "server": "rest-remote.unio.cloud",
        },
    )
    aioclient_mock.post(
        "https://test.local/api/snitun_token",
        json={
            "token": "test-token",
            "server": "rest-remote.unio.cloud",
            "valid": valid.timestamp(),
            "throttling": 400,
        },
    )

    auth_cloud_mock.client.prop_remote_autostart = False
    await remote.load_backend()
    await asyncio.sleep(0.1)

    assert remote.snitun_server == "rest-remote.unio.cloud"
    assert not valid_acme_mock.call_issue
    assert valid_acme_mock.call_hardening
    assert snitun_mock.call_start

    assert not snitun_mock.call_connect

    await remote.connect()

    assert snitun_mock.call_connect
    assert snitun_mock.connect_args[0] == b"test-token"
    assert snitun_mock.connect_args[3] == 400
    assert auth_cloud_mock.client.mock_dispatcher[-1][0] == DISPATCH_REMOTE_CONNECT


async def test_get_certificate_details(
    auth_cloud_mock, acme_mock, mock_cognito, aioclient_mock, snitun_mock
):
    """Initialize backend."""
    valid = utcnow() + timedelta(days=1)
    auth_cloud_mock.remote_api_url = "https://test.local/api"
    remote = RemoteUI(auth_cloud_mock)

    assert remote.certificate is None

    aioclient_mock.post(
        "https://test.local/api/register_instance",
        json={
            "domain": "test.dui.unio.cloud",
            "email": "test@uniocloud.com",
            "server": "rest-remote.unio.cloud",
        },
    )
    aioclient_mock.post(
        "https://test.local/api/snitun_token",
        json={
            "token": "test-token",
            "server": "rest-remote.unio.cloud",
            "valid": valid.timestamp(),
            "throttling": 400,
        },
    )

    auth_cloud_mock.client.prop_remote_autostart = False
    await remote.load_backend()
    await asyncio.sleep(0.1)
    assert remote.certificate is None

    acme_mock.common_name = "test"
    acme_mock.expire_date = valid
    acme_mock.fingerprint = "ffff"

    certificate = remote.certificate
    assert certificate.common_name == "test"
    assert certificate.expire_date == valid
    assert certificate.fingerprint == "ffff"


async def test_certificate_task_no_backend(
    loop, auth_cloud_mock, acme_mock, mock_cognito, aioclient_mock, snitun_mock
):
    """Initialize backend."""
    valid = utcnow() + timedelta(days=1)
    auth_cloud_mock.remote_api_url = "https://test.local/api"
    remote = RemoteUI(auth_cloud_mock)

    aioclient_mock.post(
        "https://test.local/api/register_instance",
        json={
            "domain": "test.dui.unio.cloud",
            "email": "test@uniocloud.com",
            "server": "rest-remote.unio.cloud",
        },
    )
    aioclient_mock.post(
        "https://test.local/api/snitun_token",
        json={
            "token": "test-token",
            "server": "rest-remote.unio.cloud",
            "valid": valid.timestamp(),
            "throttling": 400,
        },
    )

    acme_mock.expire_date = valid

    with patch("hass_uniocloud.utils.next_midnight", return_value=0), patch(
        "random.randint", return_value=0
    ):
        remote._acme_task = loop.create_task(remote._certificate_handler())
        await asyncio.sleep(0.1)
        assert acme_mock.call_issue
        assert snitun_mock.call_start


async def test_certificate_task_renew_cert(
    loop, auth_cloud_mock, acme_mock, mock_cognito, aioclient_mock, snitun_mock
):
    """Initialize backend."""
    valid = utcnow() + timedelta(days=1)
    auth_cloud_mock.remote_api_url = "https://test.local/api"
    remote = RemoteUI(auth_cloud_mock)

    aioclient_mock.post(
        "https://test.local/api/register_instance",
        json={
            "domain": "test.dui.unio.cloud",
            "email": "test@uniocloud.com",
            "server": "rest-remote.unio.cloud",
        },
    )
    aioclient_mock.post(
        "https://test.local/api/snitun_token",
        json={
            "token": "test-token",
            "server": "rest-remote.unio.cloud",
            "valid": valid.timestamp(),
            "throttling": 400,
        },
    )

    acme_mock.expire_date = utcnow() + timedelta(days=-40)

    with patch("hass_uniocloud.utils.next_midnight", return_value=0), patch(
        "random.randint", return_value=0
    ):
        remote._acme_task = loop.create_task(remote._certificate_handler())

        await remote.load_backend()
        await asyncio.sleep(0.1)
        assert acme_mock.call_issue
