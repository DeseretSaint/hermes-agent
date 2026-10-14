"""Regression: UV_LINK_MODE must survive pm's no_config env isolation.

pm strips ambient UV_* settings before handing the environment to uv
(pm/index_config.py::is_forwarded + pm/environment.py::_base_environment) so a
mirror can't re-resolve a --locked runtime. UV_LINK_MODE is a filesystem knob
(hardlink vs copy out of uv's cache), not an index redirect, so it is safe to
forward — and it must be, because on proot with --link2symlink (Omalauncher on
Android) uv's cache hardlinks become symlinks that then fail with "failed to
hardlink file ... Operation not permitted (os error 1)", breaking the runtime
sync. Without forwarding, a caller's UV_LINK_MODE=copy never reaches the
failing `uv sync`.
"""


def test_uv_link_mode_is_forwarded():
    from pm.index_config import is_forwarded

    assert is_forwarded("UV_LINK_MODE"), (
        "UV_LINK_MODE must be forwarded into pm's uv child so copy mode can be "
        "forced where hardlinks fail (proot --link2symlink)"
    )


def test_uv_link_mode_survives_base_environment():
    """_base_environment keeps UV_LINK_MODE (it is in the forwarded set).

    Note: index-redirect stripping (UV_INDEX_URL etc.) is applied separately in
    PythonEnvironment._run when no_config=True, not in _base_environment itself.
    This test pins only the forwarding behavior the fix relies on.
    """
    from pm.environment import _base_environment

    env = {
        "UV_LINK_MODE": "copy",
        "UV_CACHE_DIR": "/some/cache",  # not in the forwarded set: dropped
        "PATH": "/usr/bin",
    }
    out = _base_environment(env)
    assert out.get("UV_LINK_MODE") == "copy"
    assert "UV_CACHE_DIR" not in out
