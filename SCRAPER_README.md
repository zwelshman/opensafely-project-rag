# OpenSAFELY Projects Scraper - Troubleshooting Guide

## Problem: Finding 0 Projects

If you're seeing "Found 0 projects" when running the scraper, this is likely due to one of the following reasons:

### 1. JavaScript-Rendered Content (Most Likely)

The OpenSAFELY website may use JavaScript frameworks (React, Vue, Next.js, etc.) to load projects dynamically. The basic `requests` library only fetches the initial HTML without executing JavaScript.

**Solution**: Use the Selenium-based scraper instead:

```bash
# Install Selenium
pip install selenium

# Install Chrome driver (choose one method):
# Method 1: Using webdriver-manager (easiest)
pip install webdriver-manager

# Method 2: Manual installation
# Download chromedriver from: https://chromedriver.chromium.org/
# Add to PATH

# Run the Selenium scraper
python scraper_selenium.py
```

### 2. Website Structure Changed

The HTML structure of the website may have changed since the scraper was written.

**Debugging steps**:

1. Run the scraper once to generate debug output:
   ```bash
   python scraper.py
   ```

2. Check the generated `debug_page_output.html` file to see the actual HTML structure

3. Look for:
   - How projects are wrapped (in `<article>`, `<div>`, `<li>` tags?)
   - What class names are used (e.g., `class="project-card"`)
   - Where project titles and links are located

4. Update the parsing logic in `scraper.py` (lines 46-144) to match the actual structure

### 3. Request Blocking

The website might be blocking automated requests.

**Solutions**:
- The scraper already uses browser-like headers
- Try adding delays between requests (already implemented)
- Use Selenium which mimics a real browser more closely

## Available Scrapers

### 1. scraper.py (Basic - Fast but may not work)

Uses `requests` + `BeautifulSoup4`. Works only if:
- Website content is in the initial HTML (not JavaScript-loaded)
- No advanced anti-bot protection

**Usage**:
```bash
python scraper.py
```

**Pros**: Fast, lightweight
**Cons**: Doesn't execute JavaScript

### 2. scraper_selenium.py (Advanced - More robust)

Uses Selenium WebDriver to load the page in an actual browser.

**Usage**:
```bash
python scraper_selenium.py
```

**Pros**: Executes JavaScript, handles dynamic content
**Cons**: Slower, requires browser driver installation

## Debugging Steps

1. **Check if website is accessible**:
   ```bash
   curl -I https://www.opensafely.org/approved-projects/
   ```

2. **Run test scraper**:
   ```bash
   python test_scraper.py
   ```

3. **Inspect debug output**:
   - `debug_page_output.html` - Raw HTML from requests
   - `debug_selenium_output.html` - Rendered HTML from Selenium

4. **Manual inspection**:
   - Visit https://www.opensafely.org/approved-projects/ in your browser
   - Right-click > "Inspect Element"
   - Look at the page source to see how projects are structured

## Quick Fix Workflow

```bash
# Step 1: Try the enhanced basic scraper
python scraper.py

# If 0 projects found, check debug output
cat debug_page_output.html | head -100

# Step 2: If page looks empty/minimal, try Selenium
pip install selenium webdriver-manager
python scraper_selenium.py

# Step 3: If still failing, check Selenium debug output
cat debug_selenium_output.html | grep -i "project"
```

## Common Issues

### "ModuleNotFoundError: No module named 'selenium'"

```bash
pip install selenium webdriver-manager
```

### "selenium.common.exceptions.WebDriverException: chromedriver not found"

```bash
# Install webdriver-manager to auto-download drivers
pip install webdriver-manager

# Or manually download from:
# Chrome: https://chromedriver.chromium.org/
# Firefox: https://github.com/mozilla/geckodriver/releases
```

### Selenium scraper finds 0 projects

The page might use lazy loading or have a complex structure. Try:

1. Check `debug_selenium_output.html` to see what Selenium captured
2. Increase wait time in `scraper_selenium.py` (line 89: `time.sleep(3)` → `time.sleep(5)`)
3. Update the CSS selectors based on actual page structure

## Need Help?

If you're still stuck:

1. Share the contents of `debug_page_output.html` (first 500 lines)
2. Provide the page title and any error messages
3. Check if projects are visible when you visit the URL in a normal browser

## Updating the Scraper

If the website structure has changed, you'll need to update the parsing logic:

1. **Identify project containers** in the HTML
2. **Update selectors** in `parse_projects_list()` method:
   ```python
   # Example: If projects are in <div class="approved-project">
   project_elements = soup.find_all('div', class_='approved-project')
   ```

3. **Test** with `python test_scraper.py`
