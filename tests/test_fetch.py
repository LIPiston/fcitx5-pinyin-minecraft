import os
import sys
import urllib.parse

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import fetch


def page(title, variant=None):
    entry = {"title": title}
    if variant is not None:
        entry["varianttitles"] = {"zh-cn": variant}
    return entry


class FakeWiki:
    """Replays canned API responses, one per requested gapcontinue value."""

    def __init__(self, responses):
        self.responses = responses
        self.urls = []

    def __call__(self, url):
        self.urls.append(url)
        params = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
        gapcontinue = params.get("gapcontinue", [""])[0]
        return self.responses[gapcontinue]


def test_get_all_titles_in_variant_follows_gapcontinue(monkeypatch, tmp_path):
    fake = FakeWiki({
        "": {
            "query": {"pages": {"1": page("草方块", "草方块")}},
            "continue": {"gapcontinue": "下一页", "continue": "-||"},
        },
        "下一页": {
            "query": {"pages": {"2": page("钻石", "钻石")}},
        },
    })
    monkeypatch.setattr(fetch, "fetch", fake)
    out = tmp_path / "titles.txt"

    fetch.get_all_titles_in_variant("https://wiki.example/api.php", str(out), "zh-cn")

    assert out.read_text().split("\n") == ["草方块", "钻石"]
    assert len(fake.urls) == 2
    assert "gapcontinue=" in fake.urls[1]


def test_get_all_titles_in_variant_requests_variant_titles_in_batch(monkeypatch, tmp_path):
    fake = FakeWiki({
        "": {"query": {"pages": {"1": page("草方块", "草方块")}}},
    })
    monkeypatch.setattr(fetch, "fetch", fake)
    out = tmp_path / "titles.txt"

    fetch.get_all_titles_in_variant("https://wiki.example/api.php", str(out), "zh-cn")

    assert len(fake.urls) == 1, "one request per page of results, not per title"
    params = urllib.parse.parse_qs(urllib.parse.urlparse(fake.urls[0]).query)
    assert params["action"] == ["query"]
    assert params["generator"] == ["allpages"]
    assert params["gaplimit"] == ["max"]
    assert params["inprop"] == ["varianttitles"]


def test_get_all_titles_in_variant_filters_by_original_title(monkeypatch, tmp_path):
    fake = FakeWiki({
        "": {"query": {"pages": {
            "1": page("Creeper", "苦力怕"),
            "2": page("Item/钻石", "物品/钻石"),
            "3": page("1.0", "1.0"),
        }}},
    })
    monkeypatch.setattr(fetch, "fetch", fake)
    out = tmp_path / "titles.txt"

    fetch.get_all_titles_in_variant("https://wiki.example/api.php", str(out), "zh-cn")

    assert out.read_text().split("\n") == ["物品/钻石"]


def test_get_all_titles_in_variant_keeps_page_order(monkeypatch, tmp_path):
    fake = FakeWiki({
        "": {
            "query": {"pages": {
                "9": page("钻石", "钻石"),
                "3": page("草方块", "草方块"),
                "7": page("红石", "红石"),
            }},
            "continue": {"gapcontinue": "b", "continue": "-||"},
        },
        "b": {"query": {"pages": {"1": page("下界", "下界")}}},
    })
    monkeypatch.setattr(fetch, "fetch", fake)
    out = tmp_path / "titles.txt"

    fetch.get_all_titles_in_variant("https://wiki.example/api.php", str(out), "zh-cn")

    assert out.read_text().split("\n") == ["钻石", "草方块", "红石", "下界"]


def test_get_all_titles_in_variant_falls_back_to_title_without_variant(monkeypatch, tmp_path):
    fake = FakeWiki({
        "": {"query": {"pages": {"1": page("草方块")}}},
    })
    monkeypatch.setattr(fetch, "fetch", fake)
    out = tmp_path / "titles.txt"

    fetch.get_all_titles_in_variant("https://wiki.example/api.php", str(out), "zh-cn")

    assert out.read_text().split("\n") == ["草方块"]


def test_get_all_titles_in_variant_writes_honoured_variant(monkeypatch, tmp_path):
    fake = FakeWiki({
        "": {"query": {"pages": {"1": page("紅石方塊", "红石方块")}}},
    })
    monkeypatch.setattr(fetch, "fetch", fake)
    out = tmp_path / "titles.txt"

    fetch.get_all_titles_in_variant("https://wiki.example/api.php", str(out), "zh-cn")

    assert out.read_text().split("\n") == ["红石方块"]
