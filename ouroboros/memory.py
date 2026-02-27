import logging
import pathlib
from typing import Dict, Any

log = logging.getLogger(__name__)

class Memory:
    def __init__(self, scratchpad: str, identity: str):
        self.scratchpad = scratchpad
        self.identity = identity

def load_identity() -> str:
    try:
        path = pathlib.Path("/content/drive/MyDrive/Ouroboros/memory/identity.md")
        return path.read_text(encoding="utf-8")
    except Exception as e:
        log.error("Failed to load identity.md", exc_info=True)
        return "# Identity Core\n\nPlaceholder for identity manifesto\n"

def load_scratchpad() -> str:
    try:
        path = pathlib.Path("/content/drive/MyDrive/Ouroboros/memory/scratchpad.md")
        return path.read_text(encoding="utf-8")
    except Exception as e:
        log.error("Failed to load scratchpad.md", exc_info=True)
        return "# Scratchpad\n\nPlaceholder for working memory\n"