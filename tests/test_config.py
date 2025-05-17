import os
import pytest
from reviewscraper.config import Settings

def test_settings_from_env(monkeypatch):
    monkeypatch.setenv("PLACE_URL", "https://example.com")
    monkeypatch.setenv("STAR_FILTER", "3,5")
    monkeypatch.setenv("OUTPUT_PATH", "out.json")
    monkeypatch.setenv("HEADLESS", "false")

    cfg = Settings.from_env()
    assert cfg.place_url == "https://example.com"
    assert cfg.star_filter == [3, 5]
    assert cfg.output_path == "out.json"
    assert cfg.headless is False

def test_invalid_url():
    with pytest.raises(ValueError):
        Settings(place_url="not-a-url")
