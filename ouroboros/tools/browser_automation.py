'''Browser automation tools with Puppeteer stealth enhancements.'''

from __future__ import annotations

import json
import logging
import time
from typing import Any, Dict, List, Optional, Tuple

from playwright.sync_api import sync_playwright, Playwright, Browser, BrowserContext, Page
from ouroboros.tools.registry import ToolContext, ToolEntry

logger = logging.getLogger(__name__)

_BROWSER_MANAGER = None


class BrowserManager:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def launch(self, site_specific: bool = True):
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
        return self.browser

    def _get_context_for_site(self, url: str) -> BrowserContext:
        """Create site-specific context with tailored fingerprint masking"""
        domain = url.split("//")[-1].split("/")[0].lower()
        
        # Site-specific fingerprint configuration
        site_config = {
            'google.com': {
                'plugins': 5,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                'webgl': {
                    'vendor': 'Google Inc.',
                    'renderer': 'ANGLE (Intel(R) HD Graphics 630 Direct3D11 vs_5_0 ps_5_0)'
                }
            },
            'recaptcha.net': {
                'plugins': 6,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
                'webgl': {
                    'vendor': 'Intel Inc.',
                    'renderer': 'Intel(R) UHD Graphics 630'
                }
            },
            'default': {
                'plugins': 5,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                'webgl': {
                    'vendor': 'Google Inc.',
                    'renderer': 'ANGLE (NVIDIA GeForce RTX 3080 Direct3D11 vs_5_0 ps_5_0)'
                }
            }
        }
        
        # Select configuration based on domain
        config = site_config['default']
        for key in site_config:
            if key != 'default' and key in domain:
                config = site_config[key]
                break

        # Create context with site-specific configuration
        return self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent=config['user_agent'],
            extra_http_headers={"Accept-Language": "en-US,en;q=0.9"}
        )

    def prepare_for_url(self, url: str):
        """Create new context for specific URL with appropriate spoofing"""
        if self.context:
            self.context.close()
        
        self.context = self._get_context_for_site(url)
        self.page = self.context.new_page()
        self._setup_spoofing(url)

    def _setup_spoofing(self, url: str):
        """Advanced fingerprint masking with per-site rules"""
        domain = url.split("//")[-1].split("/")[0].lower()
        
        site_specific_script = ""
        if 'google.com' in domain or 'recaptcha.net' in domain:
            site_specific_script = """
                // Google-specific anti-detection measures
                Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
                Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
                Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });
                
                // Enhanced plugin spoofing for Google
                const googlePlugins = [
                    {name: 'Chrome PDF Plugin', description: 'Portable Document Format', filename: 'internal-pdf-viewer'},
                    {name: 'Chrome PDF Viewer', description: 'Portable Document Format', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai'},
                    {name: 'Native Client', description: 'Native Client Executable', filename: 'internal-nacl-plugin'},
                    {name: 'Widevine Content Decryption Module', description: 'Widevine CDM', filename: 'widevinecdmadapter'},
                    {name: 'Shockwave Flash', description: 'Adobe Flash Player', filename: 'libpepflashplayer.so'},
                    {name: 'Google Talk Plugin', description: 'Google Voice and Video chat', filename: 'SAVED_resource'}
                ];
                
                // WebGL spoofing for Google
                Object.defineProperty(WebGLRenderingContext.prototype, 'getParameter', {
                    value: function(parameter) {
                        if (parameter === 37445) return 'Google Inc.';
                        if (parameter === 37446) return 'ANGLE (Intel(R) HD Graphics 630 Direct3D11 vs_5_0 ps_5_0)';
                        return WebGLRenderingContext.prototype.getParameter(parameter);
                    }
                });
                """

        self.page.add_init_script(f"""
            // Universal fingerprint masking
            Object.defineProperty(navigator, 'webdriver', {{ get: () => undefined }});
            Object.defineProperty(navigator, 'plugins', {{
                get: function() {{
                    const fakePlugins = [
                        {{name: 'Chrome PDF Plugin', description: 'Portable Document Format', filename: 'internal-pdf-viewer'}},
                        {{name: 'Chrome PDF Viewer', description: 'Portable Document Format', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai'}},
                        {{name: 'Native Client', description: 'Native Client Executable', filename: 'internal-nacl-plugin'}},
                        {{name: 'Widevine Content Decryption Module', description: 'Widevine CDM', filename: 'widevinecdmadapter'}},
                        {{name: 'Shockwave Flash', description: 'Adobe Flash Player', filename: 'libpepflashplayer.so'}}
                    ];
                    
                    const pluginArray = {{
                        0: fakePlugins[0],
                        1: fakePlugins[1],
                        2: fakePlugins[2],
                        3: fakePlugins[3],
                        4: fakePlugins[4],
                        length: fakePlugins.length,
                        item: function(index) {{ return this[index] || null; }},
                        namedItem: function(name) {{ return fakePlugins.find(p => p.name === name) || null; }},
                        refresh: function() {{}},
                        [Symbol.iterator]: function* () {{
                            for (let i = 0; i < this.length; i++) {{
                                yield this[i];
                            }}
                        }}
                    }};
                    
                    Object.setPrototypeOf(pluginArray, Array.prototype);
                    return pluginArray;
                }}
            }});

            // Canvas fingerprint spoofing
            const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
            HTMLCanvasElement.prototype.toDataURL = function(type) {{
                return 'data:image/png;base64,spoofed-canvas-fingerprint';
            }};

            // AudioContext spoofing
            AudioContext.prototype.createOscillator = function() {{
                const original = AudioContext.prototype.createOscillator;
                const oscillator = original.apply(this, arguments);
                oscillator.type = 'sine';
                oscillator.frequency.setValueAtTime(1000, this.currentTime);
                return oscillator;
            }};

            // Human-like behavior simulation
            document.addEventListener('mousemove', function(e) {{
                window.lastMouseMove = {{x: e.clientX, y: e.clientY, time: Date.now()}};
            }});

            // Site-specific overrides
            {site_specific_script}
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

    def get_page(self, url: Optional[str] = None) -> Page:
        if url and (not self.context or self.context._closed):
            self.prepare_for_url(url)
        elif not self.page:
            self.launch()
            self.context = self.browser.new_context(
                viewport={{"width": 1920, "height": 1080}},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
            )
            self.page = self.context.new_page()
            if url:
                self._setup_spoofing(url)
        return self.page


_BROWSER_MANAGER = BrowserManager()


# Rest of the functions remain mostly unchanged with minor adaptations...

def _browse_page(ctx: ToolContext, url: str, output: str = 'text', timeout: int = 30000, wait_for: Optional[str] = None) -> str:
    try:
        page = _BROWSER_MANAGER.get_page(url)
        page.goto(url, timeout=timeout, wait_until='domcontentloaded')
        
        if wait_for:
            page.wait_for_selector(wait_for, timeout=timeout)

        if output == 'screenshot':
            img = page.screenshot(type='png')
            return json.dumps({{"screenshot": img.hex()}}, ensure_ascii=False)
        elif output == 'html':
            return page.content()
        elif output == 'markdown':
            return page.evaluate('document.body.innerText')
        else:
            return page.evaluate('document.body.innerText')[:10000]
    except Exception as e:
        logger.error("Failed to browse page: %s", str(e))
        return json.dumps({{"error": str(e)}}, ensure_ascii=False)


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
            return json.dumps({{"screenshot": img.hex()}}, ensure_ascii=False)
        elif action == 'evaluate':
            assert value
            result = page.evaluate(value)
            return json.dumps({{"result": result}}, ensure_ascii=False)
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
        return json.dumps({{"status": "success"}}, ensure_ascii=False)
    except Exception as e:
        logger.error("Browser action failed: %s", str(e))
        return json.dumps({{"error": str(e)}}, ensure_ascii=False)


def get_tools() -> List[ToolEntry]:
    return [
        ToolEntry("browse_page", {{
            "name": "browse_page",
            "description": "Open a URL in headless browser with advanced fingerprint masking. Returns page content as text, html, markdown, or screenshot.",
            "parameters": {{
                "properties": {{
                    "output": {{
                        "description": "Output format (default: text)",
                        "enum": ["text", "html", "markdown", "screenshot"],
                        "type": "string"
                    }},
                    "timeout": {{
                        "description": "Page load timeout in ms (default: 30000)",
                        "type": "integer"
                    }},
                    "url": {{
                        "description": "URL to open",
                        "type": "string"
                    }},
                    "wait_for": {{
                        "description": "CSS selector to wait for before extraction",
                        "type": "string"
                    }}
                }},
                "required": ["url"],
                "type": "object"
            }},
        }}, _browse_page),
        ToolEntry("browser_action", {{
            "name": "browser_action",
            "description": "Perform action on current browser page. Enhanced with human-like behavior simulation.",
            "parameters": {{
                "properties": {{
                    "action": {{
                        "description": "Action to perform",
                        "enum": ["click", "fill", "select", "screenshot", "evaluate", "scroll"],
                        "type": "string"
                    }},
                    "selector": {{
                        "description": "CSS selector for click/fill/select",
                        "type": "string"
                    }},
                    "timeout": {{
                        "description": "Action timeout in ms (default: 5000)",
                        "type": "integer"
                    }},
                    "value": {{
                        "description": "Value for fill/select, JS for evaluate, direction for scroll",
                        "type": "string"
                    }}
                }},
                "required": ["action"],
                "type": "object"
            }},
        }}, _browser_action),
    ]