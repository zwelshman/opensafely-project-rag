"""
Debug script for OpenSAFELY scraper
Helps diagnose HTML parsing issues
"""

import requests
from bs4 import BeautifulSoup
import json
import sys


def debug_html_fetch(url: str):
    """Fetch and debug HTML content"""
    print("=" * 60)
    print("DEBUGGING HTML FETCH")
    print("=" * 60)

    # Headers that accept various encodings
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
    }

    print(f"\n1. Fetching URL: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"   Status Code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"   Content-Encoding: {response.headers.get('Content-Encoding', 'N/A')}")
        print(f"   Content-Length: {len(response.content)} bytes")
        print(f"   Text Length: {len(response.text)} characters")

        # Check if content is properly decoded
        print("\n2. Content Check:")
        print(f"   First 200 chars of text: {response.text[:200]}")

        # Check for common HTML markers
        has_html = '<html' in response.text.lower()
        has_doctype = '<!doctype' in response.text.lower()
        has_body = '<body' in response.text.lower()

        print(f"   Contains <html>: {has_html}")
        print(f"   Contains <!DOCTYPE>: {has_doctype}")
        print(f"   Contains <body>: {has_body}")

        if not (has_html or has_body):
            print("\n   ⚠ WARNING: Content doesn't look like HTML!")
            print("   This might be compressed or binary data.")

            # Try to check raw bytes
            print(f"\n   First 50 bytes (raw): {response.content[:50]}")

            # Check if it's gzip
            if response.content[:2] == b'\x1f\x8b':
                print("   ⚠ Content appears to be gzip compressed!")
                import gzip
                try:
                    decompressed = gzip.decompress(response.content)
                    print(f"   Decompressed length: {len(decompressed)}")
                    print(f"   Decompressed preview: {decompressed[:200]}")
                    response._content = decompressed
                    response.encoding = 'utf-8'
                    print("\n   ✓ Successfully decompressed!")
                except Exception as e:
                    print(f"   ✗ Failed to decompress: {e}")

        # Parse HTML
        print("\n3. Parsing HTML...")
        soup = BeautifulSoup(response.text, 'lxml')

        print(f"   Page title: {soup.title.string if soup.title else 'No title found'}")

        # Check main structure
        print("\n4. HTML Structure:")
        print(f"   <html> tags: {len(soup.find_all('html'))}")
        print(f"   <head> tags: {len(soup.find_all('head'))}")
        print(f"   <body> tags: {len(soup.find_all('body'))}")
        print(f"   <main> tags: {len(soup.find_all('main'))}")
        print(f"   <article> tags: {len(soup.find_all('article'))}")
        print(f"   <div> tags: {len(soup.find_all('div'))}")

        # Look for project-related elements
        print("\n5. Looking for project elements...")

        # Try different selectors
        selectors = [
            ('article', None),
            ('div', lambda x: x and 'project' in x.lower()),
            ('li', lambda x: x and 'project' in x.lower()),
            ('div', lambda x: x and 'card' in x.lower()),
            ('a', lambda x: x and '/project' in str(x).lower()),
        ]

        for tag, class_filter in selectors:
            if class_filter:
                elements = soup.find_all(tag, class_=class_filter)
                print(f"   {tag} with class containing 'project': {len(elements)}")
            else:
                elements = soup.find_all(tag)
                print(f"   {tag} elements: {len(elements)}")

        # Look for links
        all_links = soup.find_all('a', href=True)
        project_links = [a for a in all_links if '/project' in a.get('href', '').lower()]
        print(f"\n   Total <a> tags: {len(all_links)}")
        print(f"   Links with '/project' in href: {len(project_links)}")

        if project_links:
            print("\n   Sample project links:")
            for link in project_links[:5]:
                print(f"      - {link.get('href')} : {link.get_text(strip=True)[:50]}")

        # Check for common CMS/framework indicators
        print("\n6. Framework Detection:")
        has_nextjs = bool(soup.find(id='__next') or soup.find(id='__NEXT_DATA__'))
        has_react = bool(soup.find('div', id='root') or soup.find('div', {'data-reactroot': True}))
        has_vue = bool(soup.find('div', id='app', attrs={'data-v-': True}))

        print(f"   Next.js: {has_nextjs}")
        print(f"   React: {has_react}")
        print(f"   Vue.js: {has_vue}")

        if has_nextjs or has_react:
            print("\n   ⚠ This appears to be a JavaScript-rendered site!")
            print("   You may need to use Selenium or similar to get the rendered content.")

        # Save debug output
        print("\n7. Saving debug files...")

        with open('debug_response.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("   ✓ Saved to: debug_response.html")

        with open('debug_structure.txt', 'w', encoding='utf-8') as f:
            f.write(f"URL: {url}\n")
            f.write(f"Status: {response.status_code}\n")
            f.write(f"Content-Type: {response.headers.get('Content-Type')}\n\n")
            f.write(soup.prettify()[:5000])
        print("   ✓ Saved to: debug_structure.txt")

        # Try to extract any visible text
        body = soup.find('body')
        if body:
            visible_text = body.get_text(separator='\n', strip=True)
            print(f"\n   Body text length: {len(visible_text)} characters")
            print(f"   First 500 chars of body text:")
            print("   " + visible_text[:500].replace('\n', '\n   '))

        return response.text, soup

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def analyze_project_structure(soup):
    """Analyze the structure to find projects"""
    print("\n" + "=" * 60)
    print("ANALYZING PROJECT STRUCTURE")
    print("=" * 60)

    # Get main content area
    main = soup.find('main') or soup.find('div', id='main') or soup.find('body')

    if not main:
        print("Could not find main content area!")
        return []

    print(f"\nMain content area: <{main.name}>")
    print(f"Direct children: {len(list(main.children))}")

    # Look at the structure
    for i, child in enumerate(list(main.children)[:20]):
        if hasattr(child, 'name') and child.name:
            classes = child.get('class', [])
            class_str = '.'.join(classes) if classes else 'no-class'
            text_preview = child.get_text(strip=True)[:50] if hasattr(child, 'get_text') else ''
            print(f"  [{i}] <{child.name}> class={class_str}")
            if text_preview:
                print(f"      Text: {text_preview}")

    return []


if __name__ == "__main__":
    url = "https://www.opensafely.org/approved-projects/"

    print("OpenSAFELY Projects Scraper - Debug Mode")
    print("This script will help diagnose HTML parsing issues\n")

    html, soup = debug_html_fetch(url)

    if soup:
        analyze_project_structure(soup)
        print("\n" + "=" * 60)
        print("Debug complete! Check the following files:")
        print("  - debug_response.html : Full HTML response")
        print("  - debug_structure.txt : Parsed structure preview")
        print("=" * 60)
    else:
        print("\nFailed to fetch or parse HTML")
        sys.exit(1)
