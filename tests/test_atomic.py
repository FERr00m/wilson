import os
import time
import pytest
from pathlib import Path
from supervisor.state import atomic_write_text, acquire_file_lock, release_file_lock


def test_atomic_write_text(tmp_path):
    test_file = tmp_path / "test.txt"
    atomic_write_text(test_file, "Hello, World!")
    assert test_file.read_text() == "Hello, World!"


def test_atomic_write_concurrent(tmp_path):
    file_path = tmp_path / "concurrent.txt"
    lock_path = tmp_path / "lock"

    def writer(process_id):
        for i in range(5):
            lock_fd = acquire_file_lock(lock_path, timeout_sec=2.0)
            try:
                current = file_path.read_text() if file_path.exists() else ""
                new_content = current + f"{process_id}={i}\n"
                atomic_write_text(file_path, new_content)
            finally:
                if lock_fd:
                    release_file_lock(lock_path, lock_fd)
            time.sleep(0.01)

    pid = os.fork()
    if pid == 0:
        writer(0)
        os._exit(0)
    else:
        writer(1)
        os.wait()

    content = file_path.read_text().splitlines()
    assert len(content) == 10
    assert set(content) == {f"0={i}" for i in range(5)} | {f"1={i}" for i in range(5)}