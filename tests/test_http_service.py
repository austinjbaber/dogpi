"""Tests for explicit HttpService transport-failure behavior."""

import importlib
from urllib.error import URLError

import pytest

from services.http import HttpTransportError


http_service_module = importlib.import_module("services.http.HttpService")
HttpService = http_service_module.HttpService


def test_get_raises_transport_error_instead_of_returning_none(monkeypatch):
    def fail_request(*_args, **_kwargs):
        raise URLError("network is down")

    monkeypatch.setattr(http_service_module, "urlopen", fail_request)
    service = HttpService(base_url="https://example.test")

    with pytest.raises(HttpTransportError, match="network is down"):
        service.get("/forecast")
