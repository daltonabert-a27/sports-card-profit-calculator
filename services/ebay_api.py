"""eBay Browse API client for searching active listings."""

import base64
import threading
import requests


class EbayApiClient:
    SANDBOX_AUTH_URL = "https://api.sandbox.ebay.com/identity/v1/oauth2/token"
    PRODUCTION_AUTH_URL = "https://api.ebay.com/identity/v1/oauth2/token"
    SANDBOX_BROWSE_URL = "https://api.sandbox.ebay.com/buy/browse/v1"
    PRODUCTION_BROWSE_URL = "https://api.ebay.com/buy/browse/v1"

    # Trading Cards category ID on eBay
    TRADING_CARDS_CATEGORY = "261328"

    def __init__(self, client_id: str, client_secret: str, environment: str = "PRODUCTION"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.environment = environment.upper()
        self._token: str | None = None

    @property
    def auth_url(self) -> str:
        if self.environment == "SANDBOX":
            return self.SANDBOX_AUTH_URL
        return self.PRODUCTION_AUTH_URL

    @property
    def browse_url(self) -> str:
        if self.environment == "SANDBOX":
            return self.SANDBOX_BROWSE_URL
        return self.PRODUCTION_BROWSE_URL

    def get_app_token(self) -> str:
        """Get OAuth2 application access token using client credentials grant."""
        credentials = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()

        response = requests.post(
            self.auth_url,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Basic {credentials}",
            },
            data={
                "grant_type": "client_credentials",
                "scope": "https://api.ebay.com/oauth/api_scope",
            },
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
        self._token = data["access_token"]
        return self._token

    def _ensure_token(self):
        if self._token is None:
            self.get_app_token()

    def search_items(
        self,
        query: str,
        category_id: str | None = None,
        limit: int = 25,
        sort: str = "price",
    ) -> list[dict]:
        """Search active eBay listings via Browse API.

        Note: This returns ACTIVE listings only, not sold/completed items.
        The Browse API does not support sold item data.
        """
        self._ensure_token()

        params = {
            "q": query,
            "limit": min(limit, 200),
            "sort": sort,
        }
        if category_id:
            params["category_ids"] = category_id

        response = requests.get(
            f"{self.browse_url}/item_summary/search",
            headers={
                "Authorization": f"Bearer {self._token}",
                "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
                "Content-Type": "application/json",
            },
            params=params,
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()

        items = []
        for item in data.get("itemSummaries", []):
            price_val = item.get("price", {})
            items.append({
                "item_id": item.get("itemId", ""),
                "title": item.get("title", ""),
                "price": float(price_val.get("value", 0)),
                "currency": price_val.get("currency", "USD"),
                "condition": item.get("condition", ""),
                "item_url": item.get("itemWebUrl", ""),
                "image_url": item.get("image", {}).get("imageUrl", ""),
                "seller": item.get("seller", {}).get("username", ""),
                "buying_options": item.get("buyingOptions", []),
            })

        return items

    def search_items_async(self, query: str, callback, category_id: str | None = None,
                           limit: int = 25, error_callback=None):
        """Search items in a background thread to avoid freezing the GUI."""
        def _worker():
            try:
                results = self.search_items(query, category_id, limit)
                callback(results)
            except Exception as e:
                if error_callback:
                    error_callback(str(e))

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()
