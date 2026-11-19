import os
import shutil
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "install.sh"


def run(*args, home, **env):
    return subprocess.run(
        ["sh", str(SCRIPT), *args], capture_output=True, text=True,
        env={**os.environ, "HOME": str(home), "XDG_DATA_HOME": "", **env},
    )


def test_install_script_is_posix_sh():
    assert subprocess.run(["sh", "-n", str(SCRIPT)]).returncode == 0
    if shutil.which("shellcheck"):
        result = subprocess.run(["shellcheck", "-s", "sh", str(SCRIPT)], capture_output=True, text=True)
        assert result.returncode == 0, result.stdout


def test_help_and_unknown_option(tmp_path):
    assert "--uninstall" in run("--help", home=tmp_path).stdout
    result = run("--bogus", home=tmp_path)
    assert result.returncode == 1 and "unknown option" in result.stderr


def test_uninstall_keeps_history_and_foreign_links(tmp_path):
    data = tmp_path / ".local/share/http-term"
    (data / "venv/bin").mkdir(parents=True)
    (data / "venv/bin/:http").touch()
    (data / "history.sqlite").touch()
    bin_dir = tmp_path / ".local/bin"
    bin_dir.mkdir(parents=True)
    (bin_dir / ":http").symlink_to(data / "venv/bin/:http")
    (bin_dir / "http-term").symlink_to(data / "venv/bin/http-term")

    result = run("--uninstall", home=tmp_path)
    assert result.returncode == 0, result.stderr
    assert not (data / "venv").exists() and not (bin_dir / ":http").is_symlink()
    assert not (bin_dir / "http-term").is_symlink()
    assert (data / "history.sqlite").exists()

    # A :http installed some other way (pipx, brew…) is not ours to remove.
    (bin_dir / ":http").symlink_to("/somewhere/else/:http")
    run("--uninstall", home=tmp_path)
    assert (bin_dir / ":http").is_symlink()
