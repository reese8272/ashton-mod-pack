"""verify_pack.py is CI's only gate: prove the real pack passes, and that each
guard actually fails on a synthetic broken pack (a guard that can't fail is no
guard at all)."""
import verify_pack


def test_real_pack_passes():
    assert verify_pack.main() == 0


def make_pack(root, metas=(), index_files=()):
    (root / "mods").mkdir(parents=True, exist_ok=True)
    for name, text in metas:
        (root / "mods" / name).write_text(text)
    (root / "index.toml").write_text(
        "".join(f'[[files]]\nfile = "{f}"\n' for f in index_files))
    kb = root / "config/defaultoptions"
    kb.mkdir(parents=True, exist_ok=True)
    (kb / "keybindings.txt").write_text(
        "\n".join(f"key_test{i}:NONE" for i in range(60)))


def test_curseforge_theft_detected(tmp_path, capsys):
    make_pack(tmp_path, metas=[("stolen.pw.toml",
        'name = "Stolen"\nfilename = "stolen-1.0.jar"\nside = "both"\n'
        "[update.curseforge]\nfile-id = 123\nproject-id = 456\n")])
    assert verify_pack.main(tmp_path) == 1
    assert "re-pointed to CurseForge" in capsys.readouterr().out


def test_per_player_file_at_root_detected(tmp_path, capsys):
    make_pack(tmp_path, index_files=["options.txt"])
    assert verify_pack.main(tmp_path) == 1
    assert "overwrite every player's settings" in capsys.readouterr().out


def test_runtime_state_under_config_detected(tmp_path, capsys):
    make_pack(tmp_path, index_files=["config/spark/activity.json"])
    assert verify_pack.main(tmp_path) == 1
    assert "per-player/runtime state under config/" in capsys.readouterr().out


def test_client_required_dep_cannot_be_server(tmp_path, capsys):
    make_pack(tmp_path, metas=[("lithostitched.pw.toml",
        'name = "Lithostitched"\nfilename = "lithostitched-1.7.13.jar"\n'
        'side = "server"\n')])
    assert verify_pack.main(tmp_path) == 1
    assert 'labelled side="server"' in capsys.readouterr().out
