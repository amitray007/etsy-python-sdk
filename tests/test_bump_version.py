"""Tests for scripts/bump_version.py — version arithmetic and the
.bumpversion.cfg sync that keeps it consistent with _version.py.
"""

import sys
from pathlib import Path

import pytest

# scripts/ is not a package; put it on the path so we can import the tool.
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import bump_version  # noqa: E402


# --------------------------------------------------------------------------- #
# bump_version — arithmetic
# --------------------------------------------------------------------------- #
class TestBumpVersion:
    @pytest.mark.parametrize(
        "current,bump_type,expected",
        [
            ("1.1.10", "patch", "1.1.11"),
            ("1.1.10", "minor", "1.2.0"),
            ("1.1.10", "major", "2.0.0"),
            ("0.0.0", "patch", "0.0.1"),
            ("9.9.9", "major", "10.0.0"),
        ],
    )
    def test_bump(self, current, bump_type, expected):
        assert bump_version.bump_version(current, bump_type) == expected

    def test_invalid_bump_type_raises(self):
        with pytest.raises(ValueError):
            bump_version.bump_version("1.0.0", "sideways")

    def test_malformed_version_raises(self):
        with pytest.raises(ValueError):
            bump_version.parse_version("1.0")


# --------------------------------------------------------------------------- #
# sync_bumpversion_cfg
# --------------------------------------------------------------------------- #
class TestSyncBumpversionCfg:
    def _cfg(self, tmp_path, current="1.0.19"):
        p = tmp_path / ".bumpversion.cfg"
        p.write_text(
            f"[bumpversion]\n"
            f"current_version = {current}\n"
            f"commit = True\n\n"
            f"[bumpversion:file:etsy_python/_version.py]\n"
            f"search = __version__ = \"{{current_version}}\"\n"
        )
        return p

    def test_updates_current_version(self, tmp_path):
        cfg = self._cfg(tmp_path, "1.0.19")
        assert bump_version.sync_bumpversion_cfg(cfg, "1.1.10") is True
        assert "current_version = 1.1.10" in cfg.read_text()
        assert "1.0.19" not in cfg.read_text()

    def test_only_touches_current_version_line(self, tmp_path):
        # The bumpversion:file section also references the version via a
        # template; that line must be left alone.
        cfg = self._cfg(tmp_path, "1.0.19")
        bump_version.sync_bumpversion_cfg(cfg, "1.1.10")
        content = cfg.read_text()
        assert 'search = __version__ = "{current_version}"' in content
        assert content.count("1.1.10") == 1  # only the current_version line

    def test_missing_file_returns_false(self, tmp_path):
        assert bump_version.sync_bumpversion_cfg(tmp_path / "nope.cfg", "1.1.10") is False

    def test_no_current_version_line_raises(self, tmp_path):
        p = tmp_path / ".bumpversion.cfg"
        p.write_text("[bumpversion]\ncommit = True\n")
        with pytest.raises(ValueError):
            bump_version.sync_bumpversion_cfg(p, "1.1.10")

    def test_idempotent(self, tmp_path):
        cfg = self._cfg(tmp_path, "1.1.10")
        bump_version.sync_bumpversion_cfg(cfg, "1.1.10")
        assert "current_version = 1.1.10" in cfg.read_text()


# --------------------------------------------------------------------------- #
# Integration: write_version + sync leave the repo consistent
# --------------------------------------------------------------------------- #
class TestWriteAndSyncConsistency:
    def test_both_files_end_on_same_version(self, tmp_path):
        vfile = tmp_path / "_version.py"
        vfile.write_text('__version__ = "1.1.10"')
        cfg = tmp_path / ".bumpversion.cfg"
        cfg.write_text("[bumpversion]\ncurrent_version = 1.1.10\n")

        new = bump_version.bump_version(bump_version.read_version(vfile), "patch")
        bump_version.write_version(vfile, new)
        bump_version.sync_bumpversion_cfg(cfg, new)

        assert bump_version.read_version(vfile) == "1.1.11"
        assert f"current_version = {new}" in cfg.read_text()
