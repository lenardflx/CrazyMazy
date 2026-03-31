from __future__ import annotations

import client.state.app_data as app_data_module


def test_client_settings_persists_tutorial_completion(tmp_path, monkeypatch) -> None:
    (tmp_path / "data").mkdir()
    monkeypatch.setattr(app_data_module, "BASE_DIR", tmp_path)

    settings = app_data_module.ClientData()
    assert settings.get_tutorial() is False

    settings.set_tutorial(True)

    reloaded = app_data_module.ClientData()
    assert reloaded.get_tutorial() is True
