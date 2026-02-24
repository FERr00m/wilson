from playwright.sync_api import sync_playwright, BrowserContext
import random
import string

class BrowserAutomation:
    def __init__(self):
        self.context = None
        self.browser = None

    def launch(self, url, headless=True):
        playwright = sync_playwright().start()
        self.browser = playwright.chromium.launch(
            headless=headless,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--window-size=1920,1080',
                '--use-gl=swiftshader',
                '--enable-features=VizDisplayCompositor'
            ]
        )
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            locale='en-US'
        )
        page = self.context.new_page()
        page.goto(url)
        return page

    def spoof_webgl(self, page):
        # Dynamic WebGL spoofing with realistic GPU profiles
        gpu_profiles = [
            ('NVIDIA Corporation', 'NVIDIA GeForce RTX 4090/PCIe/SSE2'),
            ('Intel Inc.', 'Intel Iris OpenGL Engine'),
            ('AMD', 'AMD Radeon Pro 5500 XT')
        ]
        vendor, renderer = random.choice(gpu_profiles)

        page.add_init_script(f"""
        Object.defineProperty(WebGLRenderingContext.prototype, 'getParameter', {{
            value: function(parameter) {{
                if (parameter === 0x1F00) return '{vendor}'; // VENDOR
                if (parameter === 0x1F01) return '{renderer}'; // RENDERER
                return getParameter.toString().apply(this, arguments);
            }}
        }});
        """)

    def spoof_canvas(self, page):
        # Add natural variation to canvas rendering
        noise = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        page.add_init_script(f"""
        const originalGetContext = HTMLCanvasElement.prototype.getContext;
        HTMLCanvasElement.prototype.getContext = function(type) {{
            const context = originalGetContext.call(this, type);
            if (type === '2d' && context) {{
                const originalFillText = context.fillText;
                context.fillText = function(text, x, y) {{
                    // Add entropy through subtle pixel variations
                    const offsetX = {random.uniform(0.1, 0.5)};
                    const offsetY = {random.uniform(0.1, 0.5)};
                    originalFillText.call(this, text, x + offsetX, y + offsetY);
                }};
            }}
            return context;
        }};
        """)

    def humanize_behavior(self, page):
        # Simulate realistic human interaction patterns
        page.add_init_script("""
        // Mouse movement simulation
        window.humanMouse = {{
            lastX: 0,
            lastY: 0,
            move: function(x, y) {{
                this.lastX = x;
                this.lastY = y;
            }}
        }};
        
        // Click delay simulation
        const originalClick = HTMLElement.prototype.click;
        HTMLElement.prototype.click = function() {{
            const delay = Math.random() * 150 + 50;
            setTimeout(() => originalClick.apply(this), delay);
        }};
        """)

    def close(self):
        if self.browser:
            self.browser.close()
        if hasattr(self, 'playwright') and self.playwright:
            self.playwright.stop()