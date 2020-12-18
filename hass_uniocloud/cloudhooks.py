"""Manage cloud cloudhooks."""
from typing import Dict, Any

import async_timeout

from . import cloud_api


class Cloudhooks:
    """Class to help manage cloudhooks."""

    def __init__(self, cloud):
        """Initialize cloudhooks."""
        self.cloud = cloud

        cloud.iot.register_on_connect(self.async_publish_cloudhooks)

    async def async_publish_cloudhooks(self) -> None:
        """Inform the Relayer of the cloudhooks that we support."""
        if not self.cloud.is_connected:
            return

        cloudhooks = self.cloud.client.cloudhooks
        await self.cloud.iot.async_send_message(
            "webhook-register",
            {"cloudhook_ids": [info["cloudhook_id"] for info in cloudhooks.values()]},
            expect_answer=False,
        )

    async def async_create(self, webhook_id: str, managed: bool) -> Dict[str, Any]:
        """Create a cloud webhook."""

        cloudhook_id = webhook_id
        cloudhook_url = "https://server.sni.uniosmarthome.com"

        try:
            remote_ui_url = self.cloud.async_remote_ui_url()
        except:
            pass
     
        hook = {
            "webhook_id": webhook_id,
            "cloudhook_id": cloudhook_id,
            "cloudhook_url": cloudhook_url,
            "managed": managed,
        }
 
        return hook

    async def async_delete(self, webhook_id: str) -> None:
        """Delete a cloud webhook."""
        
