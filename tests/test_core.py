import os
import tempfile

from src.motx_os_bridge.core.memory import MemoryManager
from src.motx_os_bridge.core.security import SecurityManager
from src.motx_os_bridge.plugins.filesystem import FileSystemPlugin
from src.motx_os_bridge.plugins.advanced_filesystem import AdvancedFileSystemPlugin


def test_memory_manager_stores_and_returns_history(tmp_path):
    history_path = tmp_path / "history.json"
    memory = MemoryManager(history_file=history_path)
    entry = memory.store({'type': 'TEST'}, 'ok')
    assert isinstance(entry, dict)
    history = memory.get_history()
    assert len(history) == 1
    assert history[0]['task'] == {'type': 'TEST'}
    assert history[0]['result'] == 'ok'


def test_security_manager_blocks_delete_system_file():
    security = SecurityManager()
    allowed, reason, _ = security.validate({'type': 'DELETE_SYSTEM_FILE'})
    assert allowed is False
    assert reason is not None

    allowed2, reason2, _ = security.validate({'type': 'CREATE_FOLDER'})
    assert allowed2 is True
    assert reason2 is None


def test_security_manager_requires_confirmation_for_sensitive_task():
    security = SecurityManager()
    allowed, reason, needs_confirmation = security.validate({'type': 'FILE_DELETE', 'path': 'C:/Users/test.txt'})
    assert allowed is False
    assert needs_confirmation is True
    assert "Confirmation" in reason or "confirmation" in reason


def test_filesystem_create_and_list_folder(tmp_path):
    plugin = FileSystemPlugin()
    folder = tmp_path / "sample"
    result = plugin.create_folder(str(folder))
    assert "Dossier créé" in result
    assert folder.exists() and folder.is_dir()


def test_memory_manager_persists_history(tmp_path):
    history_file = tmp_path / "history.json"
    manager = MemoryManager(history_file=history_file)

    manager.store({'type': 'PERSIST'}, 'ok')
    assert history_file.exists()

    reloaded = MemoryManager(history_file=history_file)
    assert any(entry['task']['type'] == 'PERSIST' for entry in reloaded.history)


def test_advanced_filesystem_copy_and_list(tmp_path):
    adv = AdvancedFileSystemPlugin()
    src_file = tmp_path / "input.txt"
    dst_file = tmp_path / "copied.txt"
    src_file.write_text("test", encoding="utf-8")

    result_copy = adv.copy_file(str(src_file), str(dst_file))
    assert "Fichier copié" in result_copy
    assert dst_file.exists()

    result_list = adv.list_files(str(tmp_path))
    assert "input.txt" in result_list
    assert "copied.txt" in result_list
