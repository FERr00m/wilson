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
            self.page.add_init_script('''
                // Complete fingerprint spoofing bundle
                
                // 1. PluginArray spoofing (critical for sannysoft)
                const fakePlugins = [
                    { name: 'Chrome PDF Plugin', description: 'Portable Document Format', filename: 'internal-pdf-viewer' },
                    { name: 'Chrome PDF Viewer', description: 'Portable Document Format', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai' },
                    { name: 'Native Client', description: 'Native Client Executable', filename: 'internal-nacl-plugin' },
                    { name: 'WidevineCDM', description: 'Widevine Content Decryption Module', filename: 'widevinecdmadapter' },
                    { name: 'Flash Player', description: 'Shockwave Flash', filename: 'libpepflashplayer.so' }
                ];
                
                const pluginArray = {
                    length: fakePlugins.length,
                    item: function(index) { return fakePlugins[index] || null; },
                    namedItem: function(name) {
                        return fakePlugins.find(p => p.name === name) || null;
                    },
                    refresh: function() {}
                };
                
                // Fix PluginArray toStringTag for proper type detection
                Object.defineProperty(pluginArray, Symbol.toStringTag, {
                    get: function() { return 'PluginArray'; }
                });
                
                // Properly construct PluginArray prototype chain
                pluginArray.__proto__ = {
                    __proto__: Array.prototype,
                    constructor: function PluginArray() {}
                };
                
                Object.defineProperty(navigator, 'plugins', {
                    get: () => pluginArray,
                    configurable: true,
                    enumerable: true
                });
                
                // 2. Chrome object spoofing (fixes 'Chrome missing' failure)
                Object.defineProperty(window, 'chrome', {
                    get: function() {
                        return {
                            app: {},
                            webstore: {},
                            runtime: {},
                            loadTimes: function() {},
                            csi: function() {}
                        };
                    },
                    configurable: true,
                    enumerable: true
                });
                
                // 3. WebDriver protection
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                    configurable: true
                });
                
                // 4. Consistent language/platform
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                    configurable: true
                });
                Object.defineProperty(navigator, 'platform', {
                    get: () => 'Win32',
                    configurable: true
                });
                
                // 5. Fix Permission API
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
                
                // 6. WebGL spoofing profiles
                const webglProfiles = [
                  {
                    vendor: 'Intel Inc.',
                    renderer: 'Intel Iris OpenGL Engine'
                  },
                  {
                    vendor: 'NVIDIA Corporation',
                    renderer: 'NVIDIA GeForce RTX 3080/PCIe/SSE2'
                  },
                  {
                    vendor: 'ATI Technologies Inc.',
                    renderer: 'AMD Radeon RX 6800 XT'
                  }
                ];

                const randomProfile = webglProfiles[Math.floor(Math.random() * webglProfiles.length)];

                const originalGetParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                  if (parameter === 7937) return randomProfile.vendor;
                  if (parameter === 7938) return randomProfile.renderer;
                  return originalGetParameter.apply(this, [parameter]);
                };

                // 7. Canvas entropy
                const originalFillText = CanvasRenderingContext2D.prototype.fillText;
                CanvasRenderingContext2D.prototype.fillText = function(text, x, y, maxWidth) {
                  const offsetX = (Math.random() - 0.5) * 0.1;
                  const offsetY = (Math.random() - 0.5) * 0.1;
                  originalFillText.call(this, text, x + offsetX, y + offsetY, maxWidth);
                };

                const originalStrokeText = CanvasRenderingContext2D.prototype.strokeText;
                CanvasRenderingContext2D.prototype.strokeText = function(text, x, y, maxWidth) {
                  const offsetX = (Math.random() - 0.5) * 0.1;
                  const offsetY = (Math.random() - 0.5) * 0.1;
                  originalStrokeText.call(this, text, x + offsetX, y + offsetY, maxWidth);
                };
            ''')

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
            "description": "Perform action on current browser page. Actions: click (selector), fill (selector + value), select (selector + value), screenshot (base64 PNG), evaluate (JS code in value), scroll (value: up/down/top/bottom.",
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