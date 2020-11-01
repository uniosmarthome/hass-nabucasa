"""Constants for the hass-uniocloud."""
CONFIG_DIR = ".cloud"

REQUEST_TIMEOUT = 10

MODE_PROD = "production"
MODE_DEV = "development"

STATE_CONNECTING = "connecting"
STATE_CONNECTED = "connected"
STATE_DISCONNECTED = "disconnected"

DISPATCH_REMOTE_CONNECT = "remote_connect"
DISPATCH_REMOTE_DISCONNECT = "remote_disconnect"
DISPATCH_REMOTE_BACKEND_UP = "remote_backend_up"
DISPATCH_REMOTE_BACKEND_DOWN = "remote_backend_down"

SERVERS = {
    "production": {
        "cognito_client_id": "66srmrqakinvc3fd8lh7gulm9g",
        "user_pool_id": "us-east-1_vzZfERFLP",
        "region": "us-east-1",
        "relayer": "wss://cloud.uniosmarthome.com/websocket",
        "google_actions_report_state_url": "https://remotestate.nabucasa.com",
        "subscription_info_url": (
            "https://cloud.uniosmarthome.com/payments/" "subscription_info"
        ),
        "cloudhook_create_url": "https://webhooks-api.nabucasa.com/generate",
        "remote_api_url": "https://cloud.uniosmarthome.com/remote",
        "alexa_access_token_url": "https://alexa-api.nabucasa.com/access_token",
        "account_link_url": "https://account-link.nabucasa.com",
        "voice_api_url": "https://voice-api.nabucasa.com",
        "thingtalk_url": "https://thingtalk-api.nabucasa.com",
        "acme_directory_server": "https://acme-v02.api.letsencrypt.org/directory",
    }
}

MESSAGE_EXPIRATION = """
It looks like your Home Assistant Cloud subscription has expired. Please check
your [account page](/config/cloud/account) to continue using the service.
"""

MESSAGE_AUTH_FAIL = """
You have been logged out of Home Assistant Cloud because we have been unable
to verify your credentials. Please [log in](/config/cloud) again to continue
using the service.
"""

MESSAGE_REMOTE_READY = """
Your remote access is now available.
You can manage your connectivity on the [Cloud Panel](/config/cloud) or with our [Portal](https://remote.nabucasa.com/).
"""

MESSAGE_REMOTE_SETUP = """
Unable to create a certificate. We will automatically retry it and notify you when it's available.
"""
