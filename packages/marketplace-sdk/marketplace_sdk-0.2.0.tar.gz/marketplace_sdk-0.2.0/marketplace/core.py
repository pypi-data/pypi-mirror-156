"""This module contains MarketPlaceClient to enable interaction with the MarketPlace.

.. currentmodule:: marketplace.core
.. moduleauthor:: Carl Simon Adorf <simon.adorf@epfl.ch>,
                  Pablo de Andres <pablo.de.andres@iwm.fraunhofer.de>
"""

import os
from urllib.parse import urljoin

import requests

from .version import __version__


class MarketPlaceClient:
    """Interact with the MarketPlace platform."""

    def __init__(self, marketplace_host_url=None, access_token=None):
        marketplace_host_url = marketplace_host_url or os.environ.get(
            "MP_HOST", "https://www.materials-marketplace.eu/"
        )
        access_token = access_token or os.environ["MP_ACCESS_TOKEN"]

        self.marketplace_host_url = marketplace_host_url
        self.access_token = access_token

    @property
    def default_headers(self):
        """Generate default headers to be used with every request."""
        return {
            "User-Agent": f"MarketPlace Python SDK {__version__}",
            "Authorization": f"Bearer {self.access_token}",
        }

    @property
    def url_userinfo(self):
        return (
            f"{self.marketplace_host_url}"
            "auth/realms/marketplace/protocol/openid-connect/userinfo"
        )

    @property
    def userinfo(self):
        userinfo = self.get(self.url_userinfo)
        userinfo.raise_for_status()
        return userinfo.json()

    def _request(self, op, path, **kwargs):
        kwargs.setdefault("headers", {}).update(self.default_headers)
        full_url = urljoin(self.marketplace_host_url, path)
        response = op(url=full_url, **kwargs)
        if response.status_code != 200:
            message = (
                f"Querying MarketPlace for {full_url} returned {response.status_code} "
                f"because: {response.text}."
                "Please check the host, client_id and token validity."
            )
            raise RuntimeError(message)
        return response

    def get(self, path: str, **kwargs):
        return self._request(requests.get, path, **kwargs)

    def post(self, path: str, **kwargs):
        return self._request(requests.post, path, **kwargs)

    def put(self, path: str, **kwargs):
        return self._request(requests.put, path, **kwargs)

    def delete(self, path: str, **kwargs):
        return self._request(requests.delete, path, **kwargs)
