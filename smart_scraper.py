"""
Smart OpenSAFELY Scraper
Automatically tries different scraping methods and chooses the best one
"""

import sys
import json
from pathlib import Path


def try_requests_scraper():
    """Try the regular requests-based scraper"""
    print("\n" + "=" * 60)
    print("METHOD 1: Requests-based scraper")
    print("=" * 60)

    try:
        from scraper import OpenSAFELYScraper
        scraper = OpenSAFELYScraper()
        html = scraper.fetch_page(scraper.projects_url)

        # Check if HTML looks valid
        if '<html' in html.lower() or '<body' in html.lower():
            projects = scraper.parse_projects_list(html)
            if projects:
                print(f"✓ Success! Found {len(projects)} projects")
                return projects, 'requests'
            else:
                print("⚠ HTML fetched but no projects found")
                # Save for debugging
                with open('debug_requests_output.html', 'w', encoding='utf-8') as f:
                    f.write(html)
                print("  Saved HTML to debug_requests_output.html")
                return None, 'requests_failed_parse'
        else:
            print("⚠ HTML doesn't look valid (might be compressed/encoded)")
            return None, 'requests_failed_invalid_html'

    except Exception as e:
        print(f"✗ Failed: {e}")
        return None, 'requests_failed_error'


def try_selenium_scraper():
    """Try the Selenium-based scraper"""
    print("\n" + "=" * 60)
    print("METHOD 2: Selenium scraper (JavaScript rendering)")
    print("=" * 60)

    try:
        from selenium_scraper import SeleniumScraper, SELENIUM_AVAILABLE

        if not SELENIUM_AVAILABLE:
            print("⚠ Selenium not installed")
            print("  Install with: pip install selenium")
            return None, 'selenium_not_installed'

        scraper = SeleniumScraper(headless=True)
        try:
            projects = scraper.scrape_projects()
            scraper.close()

            if projects:
                print(f"✓ Success! Found {len(projects)} projects")
                return projects, 'selenium'
            else:
                print("⚠ Selenium ran but found no projects")
                return None, 'selenium_no_projects'

        except Exception as e:
            scraper.close()
            raise e

    except Exception as e:
        print(f"✗ Failed: {e}")
        return None, 'selenium_failed'


def try_local_html():
    """Try parsing from a local HTML file"""
    print("\n" + "=" * 60)
    print("METHOD 3: Parse from local HTML file")
    print("=" * 60)

    possible_files = [
        'debug_page_output.html',
        'debug_requests_output.html',
        'selenium_page_output.html',
        'opensafely_projects.html',
        'approved_projects.html'
    ]

    for filename in possible_files:
        if Path(filename).exists():
            print(f"✓ Found local file: {filename}")
            try:
                from parse_local_html import parse_local_html
                projects = parse_local_html(filename)
                if projects:
                    print(f"✓ Success! Found {len(projects)} projects")
                    return projects, 'local_html'
                else:
                    print(f"⚠ Parsed {filename} but found no projects")
            except Exception as e:
                print(f"✗ Failed to parse {filename}: {e}")

    print("⚠ No local HTML files found")
    return None, 'no_local_files'


def try_api_approach():
    """Try to find and use an API endpoint"""
    print("\n" + "=" * 60)
    print("METHOD 4: Look for API endpoints")
    print("=" * 60)

    import requests

    # Common API patterns
    api_urls = [
        "https://www.opensafely.org/api/projects",
        "https://www.opensafely.org/api/approved-projects",
        "https://api.opensafely.org/projects",
    ]

    for url in api_urls:
        try:
            print(f"Trying: {url}")
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✓ Found API endpoint!")
                    print(f"  Response type: {type(data)}")

                    # Try to extract projects
                    projects = []
                    if isinstance(data, list):
                        projects = data
                    elif isinstance(data, dict):
                        # Try common keys
                        for key in ['projects', 'data', 'items', 'results']:
                            if key in data:
                                projects = data[key]
                                break

                    if projects:
                        print(f"✓ Success! Found {len(projects)} projects via API")
                        return projects, 'api'

                except json.JSONDecodeError:
                    print(f"  Response not JSON")

        except Exception as e:
            print(f"  Failed: {e}")

    print("⚠ No API endpoints found")
    return None, 'no_api'


def main():
    """Main function - tries all methods"""
    print("=" * 60)
    print("SMART OPENSAFELY SCRAPER")
    print("Trying multiple methods to scrape projects")
    print("=" * 60)

    methods = [
        ("Local HTML files", try_local_html),
        ("Requests scraper", try_requests_scraper),
        ("API endpoints", try_api_approach),
        ("Selenium scraper", try_selenium_scraper),
    ]

    projects = None
    method_used = None

    for method_name, method_func in methods:
        print(f"\n{'─' * 60}")
        print(f"Trying: {method_name}")
        print(f"{'─' * 60}")

        try:
            result, status = method_func()
            if result:
                projects = result
                method_used = method_name
                break
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            import traceback
            traceback.print_exc()

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    if projects:
        print(f"\n✓ SUCCESS!")
        print(f"  Method: {method_used}")
        print(f"  Projects found: {len(projects)}")

        # Save results
        output_file = 'opensafely_projects.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(projects, f, indent=2, ensure_ascii=False)
        print(f"  Saved to: {output_file}")

        # Show samples
        print("\nSample projects:")
        for i, project in enumerate(projects[:3], 1):
            title = project.get('title', 'No title')
            url = project.get('url', 'No URL')
            print(f"\n{i}. {title}")
            print(f"   URL: {url}")
            if project.get('summary'):
                summary = project['summary'][:100]
                print(f"   Summary: {summary}...")

        return 0

    else:
        print("\n✗ FAILED - Could not scrape projects using any method")
        print("\nTroubleshooting steps:")
        print("1. Check internet connectivity:")
        print("   curl -I https://www.opensafely.org/approved-projects/")
        print("\n2. Install Selenium for JavaScript rendering:")
        print("   pip install selenium")
        print("   # Also install Chrome/Chromium and chromedriver")
        print("\n3. Manually save the HTML:")
        print("   - Visit https://www.opensafely.org/approved-projects/ in a browser")
        print("   - Save page as 'opensafely_projects.html'")
        print("   - Run: python parse_local_html.py opensafely_projects.html")
        print("\n4. Check if there's an API:")
        print("   - Open browser DevTools (F12)")
        print("   - Go to Network tab")
        print("   - Load the projects page")
        print("   - Look for XHR/Fetch requests returning JSON")
        print("\n5. Run debug scripts for more info:")
        print("   python debug_scraper.py  # Detailed HTTP debugging")

        return 1


if __name__ == "__main__":
    sys.exit(main())
