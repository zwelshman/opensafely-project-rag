# OpenSAFELY Projects Scraper - Troubleshooting Guide

## Quick Start

Based on your situation, use one of these scripts:

### 1. **smart_scraper.py** - Try this first! ⭐
Automatically tries multiple methods:
```bash
python smart_scraper.py
```

### 2. **improved_scraper.py** - For the known structure
Uses knowledge about the page structure (projects with IDs like #project-200):
```bash
python improved_scraper.py
```

### 3. **parse_local_html.py** - If you have HTML saved
Parse from a saved HTML file:
```bash
# Manually save the page in your browser as 'opensafely_projects.html', then:
python parse_local_html.py opensafely_projects.html
```

### 4. **selenium_scraper.py** - For JavaScript-rendered pages
Requires Selenium and Chrome/Chromium:
```bash
# Install dependencies first:
pip install selenium

# Then run:
python selenium_scraper.py
```

### 5. **debug_scraper.py** - For detailed debugging
Shows detailed info about what's being fetched:
```bash
python debug_scraper.py
```

---

## Common Issues & Solutions

### Issue 1: "No projects found" but HTML was fetched

**Symptoms:**
```
Found 0 projects
Saved HTML to: debug_page_output.html
HTML length: 97388 characters
```

**Cause:** The page structure doesn't match what the scraper expects, OR the page requires JavaScript to render.

**Solutions:**

1. **Check if the HTML looks normal:**
   ```bash
   python parse_local_html.py debug_page_output.html
   ```

2. **If you see garbled/binary data:**
   - The HTML might be compressed wrong
   - Run the improved scraper which handles this better:
     ```bash
     python improved_scraper.py
     ```

3. **If the page is JavaScript-rendered:**
   - Use Selenium:
     ```bash
     pip install selenium
     python selenium_scraper.py
     ```

### Issue 2: Compressed/Garbled HTML

**Symptoms:**
```
Main content structure:
  Direct children: [None, 'q~5�s[��Ǚ^a�$�{p\x1f����ow��6;:}^�?\\�}��?\x1d�zybx&�܃4']
```

**Cause:** The HTML is gzip-compressed but not being decompressed properly.

**Solution:**
The `improved_scraper.py` handles encoding issues better. Also try:

```bash
# Check if the saved HTML is gzip compressed:
file debug_page_output.html

# If it says "gzip compressed", decompress it:
gunzip debug_page_output.html.gz

# Or let the parse script handle it:
python parse_local_html.py debug_page_output.html
```

### Issue 3: Proxy/Network errors

**Symptoms:**
```
403 Forbidden
ProxyError: Unable to connect to proxy
```

**Cause:** Network restrictions or the site blocking automated requests.

**Solutions:**

1. **Manual HTML save:**
   - Open https://www.opensafely.org/approved-projects/ in your browser
   - Right-click → "Save Page As" → save as `opensafely_projects.html`
   - Run: `python parse_local_html.py opensafely_projects.html`

2. **Check network:**
   ```bash
   curl -I https://www.opensafely.org/approved-projects/
   ```

3. **Try different headers:**
   Edit the `headers` in `improved_scraper.py` to match your browser

### Issue 4: Selenium not working

**Symptoms:**
```
✗ Failed to initialize Chrome driver
```

**Solutions:**

1. **Install Chrome/Chromium:**
   ```bash
   # Ubuntu/Debian:
   sudo apt-get update
   sudo apt-get install chromium-browser chromium-chromedriver

   # Mac:
   brew install chromium chromedriver
   ```

2. **Check chromedriver version:**
   ```bash
   chromedriver --version
   chrome --version  # Should be similar
   ```

3. **Use webdriver-manager (auto-downloads drivers):**
   ```bash
   pip install webdriver-manager
   ```

   Then modify `selenium_scraper.py` to use it (see Selenium docs).

---

## Understanding the Output

### Successful scrape:
```json
[
  {
    "title": "Project Title",
    "id": "project-200",
    "url": "https://www.opensafely.org/approved-projects/#project-200",
    "description": "Project description...",
    "authors": "Author names",
    "date": "2024-01-01",
    "status": "Active"
  }
]
```

### Debug files created:
- **debug_page_output.html** - The raw HTML fetched
- **debug_response.html** - Alternative debug output
- **selenium_page_output.html** - HTML after JavaScript rendering
- **opensafely_projects.json** - Final extracted projects

---

## Page Structure Reference

Based on the link https://www.opensafely.org/approved-projects/#project-200:

- Each project has an ID like: `project-1`, `project-2`, ... `project-200`
- Projects are on a single page with anchor links
- The page might be JavaScript-rendered (Next.js/React)

The scrapers look for:
1. Elements with `id="project-*"`
2. `<article>` tags
3. Divs/sections with "project" in the class name
4. Links containing "/project" or "#project-"

---

## Advanced Debugging

### 1. Check what structure the page actually has:

```bash
python debug_scraper.py
# Check the output and debug_response.html
```

### 2. Manually inspect the HTML:

```bash
# Save the page, then:
grep -i "project-200" debug_page_output.html | head -5
# This shows how project-200 is structured
```

### 3. Use browser DevTools:

1. Open https://www.opensafely.org/approved-projects/
2. Press F12 (open DevTools)
3. Go to "Network" tab
4. Refresh the page
5. Look for:
   - API calls returning JSON (might be an easier way to get data)
   - The HTML structure in "Elements" tab

### 4. Find the right selector:

```bash
# In browser console:
document.querySelectorAll('[id^="project-"]').length
# This tells you how many elements with IDs starting with "project-" exist
```

---

## Alternative: Use the API (if available)

Some sites have APIs that are easier to use:

```bash
# Try these URLs in your browser:
https://www.opensafely.org/api/projects
https://www.opensafely.org/api/approved-projects
https://api.opensafely.org/projects

# If one returns JSON, you can fetch it directly:
curl -o projects.json https://www.opensafely.org/api/projects
```

---

## Contact & Support

If none of these work:
1. Check the project README for updates
2. The page structure may have changed
3. You might need to adjust the scrapers based on the current HTML structure

## Summary of Tools

| Script | Use When | Requires |
|--------|----------|----------|
| `smart_scraper.py` | **Try first** - auto-detects method | Basic Python |
| `improved_scraper.py` | You know the structure | Basic Python |
| `parse_local_html.py` | You have HTML saved | Basic Python |
| `selenium_scraper.py` | Page needs JavaScript | Selenium + Chrome |
| `debug_scraper.py` | Need detailed diagnostics | Basic Python |
| `scraper.py` | Original basic scraper | Basic Python |
| `test_scraper.py` | Test connectivity | Basic Python |
