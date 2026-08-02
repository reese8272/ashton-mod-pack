"""The CurseForge file-id -> CDN path derivation is load-bearing with no other
check: a wrong split would 404 every CurseForge mod in the server build."""
from build_server_pack import curseforge_url


def test_cdn_path_split():
    meta = {"filename": "cupboard-1.21.1-3.9.jar",
            "update": {"curseforge": {"file-id": 5678901, "project-id": 1}}}
    assert curseforge_url(meta) == (
        "https://mediafilez.forgecdn.net/files/5678/901/cupboard-1.21.1-3.9.jar")


def test_leading_zero_tail_drops_and_name_is_quoted():
    meta = {"filename": "a b.jar",
            "update": {"curseforge": {"file-id": 5670001, "project-id": 1}}}
    assert curseforge_url(meta) == (
        "https://mediafilez.forgecdn.net/files/5670/1/a%20b.jar")
