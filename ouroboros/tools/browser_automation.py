'''Browser automation tools.'''

from __future__ import annotations

import json
import logging
import time
from typing import Any, Dict, List, Optional, Tuple

from playwright.sync_api import sync_playwright, Playwright, Browser, Page
from ouroboros.tools.registry import ToolContext, ToolEntry

logger = logging.getLogger(__name__)

_BROWSER_MANAGER = None


class BrowserManager:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def launch(self):
        if self.playwright is None:
            self.playwright = sync_playwright().start()
        if self.browser is None:
            self.browser = self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu'
                ]
            )
            self.context = self.browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
            )
            self.page = self.context.new_page()
            self._setup_spoofing()

    def _setup_spoofing(self):
        if self.page:
            self.page.add_init_script("""
                // Полная эмуляция navigator.plugins с 5 реалистичными плагинами
                const fakePlugins = [
                    {
                        name: 'Chrome PDF Plugin',
                        description: 'Portable Document Format',
                        filename: 'internal-pdf-viewer',
                        version: '131.0.0.0',
                        length: 0
                    },
                    {
                        name: 'Chrome PDF Viewer',
                        description: 'Portable Document Format',
                        filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai',
                        version: '131.0.0.0',
                        length: 0
                    },
                    {
                        name: 'Native Client',
                        description: 'Native Client Executable',
                        filename: 'internal-nacl-plugin',
                        version: '131.0.0.0',
                        length: 0
                    },
                    {
                        name: 'Widevine Content Decryption Module',
                        description: 'Widevine Content Decryption Module',
                        filename: 'widevinecdmadapter',
                        version: '4.10.2698.0',
                        length: 0
                    },
                    {
                        name: 'Shockwave Flash',
                        description: 'Adobe Flash Player',
                        filename: 'libpepflashplayer.so',
                        version: '32.0.0.468',
                        length: 0
                    }
                ];

                // Создаем финальный объект плагинов с правильными свойствами
                const pluginArray = {
                    0: fakePlugins[0],
                    1: fakePlugins[1],
                    2: fakePlugins[2],
                    3: fakePlugins[3],
                    4: fakePlugins[4],
                    length: fakePlugins.length,
                    item: function(index) { return this[index] || null; },
                    namedItem: function(name) { return fakePlugins.find(p => p.name === name) || null; },
                    refresh: function() {},
                    [Symbol.iterator]: function* () {
                        for (let i = 0; i < this.length; i++) {
                            yield this[i];
                        }
                    }
                };

                // Настройка прототипа для правильной типизации
                Object.setPrototypeOf(pluginArray, {
                    constructor: Array,
                    __proto__: Array.prototype
                });

                // Окончательная настройка navigator.plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: function() { return pluginArray; },
                    configurable: true,
                    enumerable: true
                });

                // Дополнительные настройки анти-детекции
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
                Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });
                Object.defineProperty(navigator, 'permissions', {
                    get: async () => ({
                        query: () => ({ state: 'denied' })
                    })
                });
            """)

    def close(self):
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def get_page(self) -> Page:
        if not self.page:
            self.launch()
        return self.page


_BROWSER_MANAGER = BrowserManager()


def _browse_page(ctx: ToolContext, url: str, output: str = 'text', timeout: int = 30000, wait_for: Optional[str] = None) -> str:
    try:
        page = _BROWSER_MANAGER.get_page()
        page.goto(url, timeout=timeout, wait_until='domcontentloaded')
        
        if wait_for:
            page.wait_for_selector(wait_for, timeout=timeout)

        if output == 'screenshot':
            img = page.screenshot(type='png')
            return json.dumps({"screenshot": img.hex()}, ensure_ascii=False)
        elif output == 'html':
            return page.content()
        elif output == 'markdown':
            return page.evaluate('document.body.innerText')
        else:
            return page.evaluate('document.body.innerText')[:10000]
    except Exception as e:
        logger.error("Failed to browse page: %s", str(e))
        return json.dumps({"error": str(e)}, ensure_ascii=False)


def _browser_action(ctx: ToolContext, action: str, selector: Optional[str] = None, value: Optional[str] = None, timeout: int = 5000) -> str:
    try:
        page = _BROWSER_MANAGER.get_page()
        if action == 'click':
            assert selector
            page.click(selector, timeout=timeout)
        elif action == 'fill':
            assert selector and value
            page.fill(selector, value, timeout=timeout)
        elif action == 'select':
            assert selector and value
            page.select_option(selector, value=value, timeout=timeout)
        elif action == 'screenshot':
            img = page.screenshot(type='png')
            return json.dumps({"screenshot": img.hex()}, ensure_ascii=False)
        elif action == 'evaluate':
            assert value
            result = page.evaluate(value)
            return json.dumps({"result": result}, ensure_ascii=False)
        elif action == 'scroll':
            assert value
            if value == 'top':
                page.evaluate('window.scrollTo(0, 0)')
            elif value == 'bottom':
                page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            elif value == 'up':
                page.evaluate('window.scrollBy(0, -300)')
            elif value == 'down':
                page.evaluate('window.scrollBy(0, 300)')
        return json.dumps({"status": "success"}, ensure_ascii=False)
    except Exception as e:
        logger.error("Browser action failed: %s", str(e))
        return json.dumps({"error": str(e)}, ensure_ascii=False)


def get_tools() -> List[ToolEntry]:
    return [
        ToolEntry("browse_page", {
            "name": "browse_page",
            "description": "Open a URL in headless browser. Returns page content as text, html, markdown, or screenshot (base64 PNG). Browser persists across calls within a task. For screenshots: use send_photo tool to deliver the image to owner.",
            "parameters": {
                "properties": {
                    "output": {
                        "description": "Output format (default: text)",
                        "enum": ["text", "html", "markdown", "screenshot"],
                        "type": "string"
                    },
                    "timeout": {
                        "description": "Page load timeout in ms (default: 30000)",
                        "type": "integer"
                    },
                    "url": {
                        "description": "URL to open",
                        "type": "string"
                    },
                    "wait_for": {
                        "description": "CSS selector to wait for before extraction",
                        "type": "string"
                    }
                },
                "required": ["url"],
                "type": "object"
            },
        }, _browse_page),
        ToolEntry("browser_action", {
            "name": "browser_action",
            "description": "Perform action on current browser page. Actions: click (selector), fill (selector + value), select (selector + value), screenshot (base64 PNG), evaluate (JS code in value), scroll (value: up/down/top/bottom).",
            "parameters": {
                "properties": {
                    "action": {
                        "description": "Action to perform",
                        "enum": ["click", "fill", "select", "screenshot", "evaluate", "scroll"],
                        "type": "string"
                    },
                    "selector": {
                        "description": "CSS selector for click/fill/select",
                        "type": "string"
                    },
                    "timeout": {
                        "description": "Action timeout in ms (default: 5000)",
                        "type": "integer"
                    },
                    "value": {
                        "description": "Value for fill/select, JS for evaluate, direction for scroll",
                        "type": "string"
                    }
                },
                "required": ["action"],
                "type": "object"
            },
        }, _browser_action),
    ]
