# Browser Automation: CAPTCHA Bypass Analysis

## Test Environment Findings
- Analyzed `https://www.google.com/recaptcha/api2/demo` (standard v2 CAPTCHA)
- **Critical observation**: Public `data-sitekey="6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-"` is **Google's test key**
- Bypass mechanism: Pre-fill `g-recaptcha-response` with `"true"` (valid for test environments only)

## Automation Strategy
```python
# For test environments:
browser_action(action="fill", selector="[name='g-recaptcha-response']", value="true")

# For production (requires solver):
# 1. Detect challenge type (checkbox vs image grid)
# 2. Route to 2captcha/anti-captcha via:
#    - `web_search("2captcha API key setup")`
#    - `browser_action("evaluate", value="solveWithCaptchaService()")`
```

## Security Notes
- Real CAPTCHA requires actual solving (third-party services or ML models)
- Headless detection is triggered by:
  - Missing `navigator.webdriver`
  - Inconsistent mouse movements
  - Unusual timing patterns

## Next Steps
1. ✅ Document test key behavior in knowledge base
2. ⏳ Research open-source CAPTCHA solvers for budget-conscious automation
3. ⚠️ Add stealth parameters to browser automation (user agent rotation, mouse movement simulation)