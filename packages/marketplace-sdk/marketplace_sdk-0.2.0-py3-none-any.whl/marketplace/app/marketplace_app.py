"""This module contains all functionality for MarketPlace apps..

.. currentmodule:: marketplace.app.marketplace_app
.. moduleauthor:: Pablo de Andres, Pranjali Singh (Fraunhofer IWM)
"""


from urllib.parse import urljoin

from marketplace.app.data_sink_app import DataSinkApp
from marketplace.app.data_source_app import DataSourceApp
from marketplace.app.transformation_app import TransformationApp
from marketplace.app.utils import camel_to_snake, check_capability_availability


class MarketPlaceApp(DataSinkApp, DataSourceApp, TransformationApp):
    """Base MarketPlace app.

    Includes the heartbeat capability and extends the MarketPlace class
    to use the authentication mechanism.
    """

    def __init__(self, client_id, **kwargs):
        super().__init__(**kwargs)
        self.client_id = client_id
        # Must be run before the marketplace_host_url is updated to include the proxy.
        self.set_capabilities()
        self.marketplace_host_url = urljoin(
            self.marketplace_host_url, f"mp-api/proxy/{self.client_id}/"
        )

    def set_capabilities(self):
        """Query the platform to get the capabilities supported by a certain
        app."""
        app_service_path = f"application-service/applications/{self.client_id}"
        response = self.get(path=app_service_path).json()
        capability_info = response["capabilities"]
        self.capabilities = []
        for capability in capability_info:
            self.capabilities.append(camel_to_snake(capability["name"]))

    @check_capability_availability
    def heartbeat(self) -> str:
        """Check the heartbeat of the application.

        Returns:
            str: heartbeat
        """
        return self.get(path="heartbeat").text
