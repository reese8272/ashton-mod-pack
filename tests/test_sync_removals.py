"""Regression for the sync-deletes-bumped-mods bug.

A version bump arrives as add(new jar) + remove(old jar), but both names map to
the SAME slug-named metadata file -- the removal step must never unlink the
freshly updated mod, and server-only mods must never be diffed against a client
instance at all.
"""
import pathlib

from sync_from_instance import client_facing, plan_removals


def test_version_bump_is_not_a_removal(tmp_path):
    meta = tmp_path / "foo.pw.toml"
    meta.write_text('name = "Foo"\nfilename = "foo-2.0.jar"\nside = "both"\n')
    # Pack state AFTER the add step: only the new jar name maps to the meta.
    real, bumped = plan_removals(["foo-1.0.jar"], {"foo-2.0.jar": (meta, "both")})
    assert real == []
    assert bumped == ["foo-1.0.jar"]


def test_genuine_removal_is_planned(tmp_path):
    meta = tmp_path / "gone.pw.toml"
    meta.write_text('name = "Gone"\nfilename = "gone-1.0.jar"\nside = "both"\n')
    real, bumped = plan_removals(["gone-1.0.jar"], {"gone-1.0.jar": (meta, "both")})
    assert real == [("gone-1.0.jar", meta)]
    assert bumped == []


def test_server_only_mods_never_diffed_against_client_instance():
    mods = {
        "clientmod.jar": (pathlib.Path("a.pw.toml"), "client"),
        "bothmod.jar": (pathlib.Path("b.pw.toml"), "both"),
        "servermod.jar": (pathlib.Path("c.pw.toml"), "server"),
    }
    visible = client_facing(mods)
    assert "servermod.jar" not in visible
    assert set(visible) == {"clientmod.jar", "bothmod.jar"}
