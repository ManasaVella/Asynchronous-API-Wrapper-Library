import asyncio
import logging
from typing import AsyncIterator, Any, Dict, Type, TypeVar
import aiohttp
from pydantic import BaseModel

from .exceptions import raise_for_status
from .utils import parse_link_header

logger = logging.getLogger("softnexis_git")
T = TypeVar("T", bound=BaseModel)

class AsyncClient:
    """Central engine orchestration for asynchronous connections to GitHub REST boundaries."""
    
    BASE_URL = "https://api.github.com"

    def __init__(self, token: str | None = None, session: aiohttp.ClientSession | None = None):
        self.token = token
        self._session = session
        self._own_session = False
        
        # State metrics updating continuously on every outgoing network trip
        self.rate_limit_limit: int | None = None
        self.rate_limit_remaining: int | None = None
        self.rate_limit_reset: int | None = None

    async def __aenter__(self):
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def _ensure_session(self) -> aiohttp.ClientSession:
        """Lazily creates a clear aiohttp session instance if one doesn't exist."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
            self._own_session = True
        return self._session

    def _get_headers(self) -> dict:
        """Constructs essential identity metadata payload parameters required by GitHub."""
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Softnexis-Evaluation-Client/1.0.0"
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _update_rate_limits(self, headers: aiohttp.CIMultiDictProxy[str]) -> None:
        """Parses response structural markers to synchronize state values."""
        try:
            if "X-RateLimit-Limit" in headers:
                self.rate_limit_limit = int(headers["X-RateLimit-Limit"])
                self.rate_limit_remaining = int(headers["X-RateLimit-Remaining"])
                self.rate_limit_reset = int(headers["X-RateLimit-Reset"])
        except (ValueError, TypeError):
            pass  # Fail silently to avoid breaking execution if headers shift format

    async def _request(self, method: str, endpoint: str, **kwargs) -> tuple[Any, dict]:
        """Low-level internal runner wrapping HTTP verbs, monitoring states, and trapping bad responses."""
        session = await self._ensure_session()
        url = endpoint if endpoint.startswith("http") else f"{self.BASE_URL}{endpoint}"
        headers = {**self._get_headers(), **kwargs.pop("headers", {})}

        async with session.request(method, url, headers=headers, **kwargs) as response:
            self._update_rate_limits(response.headers)
            
            try:
                data = await response.json()
            except aiohttp.ContentTypeError:
                data = {"message": await response.text()}

            if response.status >= 400:
                raise_for_status(response.status, data, dict(response.headers))

            return data, dict(response.headers)

    async def get(self, endpoint: str, model: Type[T], **kwargs) -> T:
        """Fetches a record component and returns an instantiated validation model."""
        data, _ = await self._request("GET", endpoint, **kwargs)
        return model.model_validate(data)

    async def get_paginated(self, endpoint: str, model: Type[T], per_page: int = 30) -> AsyncIterator[T]:
        """Asynchronously streams data sequentially across server pages using an iterator loop pattern."""
        separator = "&" if "?" in endpoint else "?"
        next_url = f"{endpoint}{separator}per_page={per_page}"
        
        while next_url:
            data, headers = await self._request("GET", next_url)

            if isinstance(data, list):
                for item in data:
                    yield model.model_validate(item)
            else:
                yield model.model_validate(data)

            # Extract direction pointers to verify if subsequent datasets are queued
            links = parse_link_header(headers.get("Link"))
            next_url = links.get("next")

    async def close(self) -> None:
        """Cleans up internal connection pools securely if self-managed."""
        if self._own_session and self._session and not self._session.closed:
            await self._session.close()