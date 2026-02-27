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
    
    def writer():
        for _ in range(5):
            atomic_write_text(file_path, f"{os.getpid()}\n", mode="append")
            time.sleep(0.01)
    
    # Fork to simulate concurrent processes
    pid = os.fork()
    if pid == 0:
        writer()
        os._exit(0)
    else:
        writer()
        os.wait()
    
    content = file_path.read_text().splitlines()
    assert len(content) == 10  # 5 writes from each process
    assert len(set(content)) == 2  # Only 2 unique PIDs