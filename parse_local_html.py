"""
Parse OpenSAFELY projects from a locally saved HTML file
Useful when you've already fetched the HTML and need to debug parsing
"""

import sys
import json
from bs4 import BeautifulSoup
from pathlib import Path


def parse_local_html(html_path: str):
    """Parse projects from a local HTML file"""
    print("=" * 60)
    print(f"PARSING LOCAL HTML: {html_path}")
    print("=" * 60)

    # Read the HTML file
    try:
        with open(html_path, 'rb') as f:
            content = f.read()

        print(f"\nFile size: {len(content)} bytes")
        print(f"First 50 bytes: {content[:50]}")

        # Check if it's gzip compressed
        if content[:2] == b'\x1f\x8b':
            print("⚠ File appears to be gzip compressed. Decompressing...")
            import gzip
            content = gzip.decompress(content)
            print(f"Decompressed size: {len(content)} bytes")

        # Decode to string
        try:
            html = content.decode('utf-8')
        except UnicodeDecodeError:
            print("⚠ UTF-8 decode failed, trying latin-1...")
            html = content.decode('latin-1')

        print(f"HTML length: {len(html)} characters")
        print(f"First 200 chars:\n{html[:200]}\n")

    except FileNotFoundError:
        print(f"✗ Error: File not found: {html_path}")
        return None
    except Exception as e:
        print(f"✗ Error reading file: {e}")
        import traceback
        traceback.print_exc()
        return None

    # Parse with BeautifulSoup
    print("\nParsing HTML...")
    soup = BeautifulSoup(html, 'lxml')

    # Basic structure analysis
    print(f"Page title: {soup.title.string if soup.title else 'No title'}")
    print(f"\nStructure:")
    print(f"  <article> tags: {len(soup.find_all('article'))}")
    print(f"  <div> tags: {len(soup.find_all('div'))}")
    print(f"  <a> tags: {len(soup.find_all('a'))}")
    print(f"  <main> tags: {len(soup.find_all('main'))}")

    # Look for projects
    print("\n" + "=" * 60)
    print("SEARCHING FOR PROJECTS")
    print("=" * 60)

    projects = []

    # Strategy 1: Look for articles
    articles = soup.find_all('article')
    print(f"\nStrategy 1: Articles - Found {len(articles)}")
    if articles:
        for article in articles[:3]:
            print(f"  Sample: {article.get_text(strip=True)[:100]}")

    # Strategy 2: Look for divs with 'project' class
    project_divs = soup.find_all('div', class_=lambda x: x and 'project' in x.lower())
    print(f"\nStrategy 2: Divs with 'project' class - Found {len(project_divs)}")
    if project_divs:
        for div in project_divs[:3]:
            classes = div.get('class', [])
            print(f"  Sample: {classes} - {div.get_text(strip=True)[:100]}")

    # Strategy 3: Look for links with '/project' or '/projects' in href
    all_links = soup.find_all('a', href=True)
    project_links = [a for a in all_links if 'project' in a.get('href', '').lower()]
    print(f"\nStrategy 3: Links with 'project' in href - Found {len(project_links)}")
    if project_links:
        for link in project_links[:5]:
            href = link.get('href')
            text = link.get_text(strip=True)
            print(f"  {href} - {text[:50]}")

    # Strategy 4: Look for common CMS patterns
    print("\nStrategy 4: CMS patterns")

    # WordPress
    wp_posts = soup.find_all('article', class_=lambda x: x and 'post' in x.lower())
    print(f"  WordPress posts: {len(wp_posts)}")

    # Card patterns
    cards = soup.find_all('div', class_=lambda x: x and 'card' in x.lower())
    print(f"  Card elements: {len(cards)}")

    # List items
    list_items = soup.find_all('li', class_=lambda x: x and any(word in x.lower() for word in ['project', 'item', 'post']))
    print(f"  List items: {len(list_items)}")

    # Strategy 5: Check for JavaScript-rendered content
    print("\nStrategy 5: JavaScript framework detection")
    next_data = soup.find('script', id='__NEXT_DATA__')
    react_root = soup.find('div', id='root') or soup.find('div', id='__next')

    if next_data:
        print("  ✓ Found Next.js data!")
        try:
            data = json.loads(next_data.string)
            print(f"  Next.js data keys: {list(data.keys())}")
            # Try to extract projects from Next.js data
            props = data.get('props', {})
            page_props = props.get('pageProps', {})
            print(f"  Page props keys: {list(page_props.keys())}")

            # Look for common data structures
            for key in ['projects', 'items', 'posts', 'data']:
                if key in page_props:
                    print(f"  ✓ Found '{key}' in pageProps!")
                    items = page_props[key]
                    if isinstance(items, list):
                        print(f"    Contains {len(items)} items")
                        if items:
                            print(f"    First item keys: {list(items[0].keys()) if isinstance(items[0], dict) else 'not a dict'}")

        except json.JSONDecodeError as e:
            print(f"  ✗ Failed to parse Next.js data: {e}")

    elif react_root:
        print("  ⚠ React root found but content is likely client-rendered")
        print("  You may need to use a headless browser (Selenium/Playwright)")

    # Strategy 6: Look at main content structure
    print("\nStrategy 6: Main content analysis")
    main = soup.find('main') or soup.find('div', id='main') or soup.find('div', class_='main')

    if main:
        print(f"  Found main content area: <{main.name}>")
        children = [c for c in main.children if hasattr(c, 'name')]
        print(f"  Direct children: {len(children)}")

        # Look at structure
        for i, child in enumerate(children[:10]):
            tag = child.name
            classes = ' '.join(child.get('class', []))
            text_preview = child.get_text(strip=True)[:60]
            print(f"    [{i}] <{tag}> class='{classes}'")
            if text_preview:
                print(f"        {text_preview}")

    # Try to extract projects using best available method
    print("\n" + "=" * 60)
    print("ATTEMPTING EXTRACTION")
    print("=" * 60)

    extracted_projects = []

    # Prioritize methods
    if next_data:
        print("\nUsing Next.js data extraction...")
        # Already parsed above, use that data if found
        try:
            data = json.loads(next_data.string)
            page_props = data.get('props', {}).get('pageProps', {})

            # Try different keys
            for key in ['projects', 'items', 'posts', 'data', 'allProjects']:
                if key in page_props and isinstance(page_props[key], list):
                    extracted_projects = page_props[key]
                    print(f"✓ Extracted {len(extracted_projects)} projects from '{key}'")
                    break
        except:
            pass

    elif articles:
        print("\nUsing article extraction...")
        for article in articles:
            project = {}

            # Get title
            title = article.find(['h1', 'h2', 'h3', 'h4'])
            if title:
                project['title'] = title.get_text(strip=True)

            # Get link
            link = article.find('a', href=True)
            if link:
                project['url'] = link.get('href')

            # Get description
            desc = article.find('p')
            if desc:
                project['summary'] = desc.get_text(strip=True)

            if project.get('title'):
                extracted_projects.append(project)

        print(f"✓ Extracted {len(extracted_projects)} projects from articles")

    elif project_links:
        print("\nUsing link extraction...")
        for link in project_links:
            project = {
                'title': link.get_text(strip=True),
                'url': link.get('href'),
                'summary': ''
            }
            if project['title']:
                extracted_projects.append(project)

        print(f"✓ Extracted {len(extracted_projects)} projects from links")

    # Save results
    if extracted_projects:
        output_file = 'extracted_projects.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(extracted_projects, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Saved {len(extracted_projects)} projects to {output_file}")

        print("\nSample project:")
        print(json.dumps(extracted_projects[0], indent=2))
    else:
        print("\n✗ No projects could be extracted")
        print("\nRecommendations:")
        print("  1. Check if the page requires JavaScript rendering")
        print("  2. Try using Selenium/Playwright for dynamic content")
        print("  3. Inspect the HTML manually in debug_response.html")
        print("  4. Look for API endpoints that return JSON data")

    return extracted_projects


if __name__ == "__main__":
    if len(sys.argv) > 1:
        html_path = sys.argv[1]
    else:
        # Try common filenames
        possible_files = [
            'debug_page_output.html',
            'debug_response.html',
            'opensafely_projects.html',
            'approved_projects.html'
        ]

        html_path = None
        for filename in possible_files:
            if Path(filename).exists():
                html_path = filename
                print(f"Found HTML file: {filename}")
                break

        if not html_path:
            print("Usage: python parse_local_html.py <path_to_html_file>")
            print("\nOr save HTML to one of these filenames:")
            for f in possible_files:
                print(f"  - {f}")
            sys.exit(1)

    projects = parse_local_html(html_path)

    if projects:
        print(f"\n✓ Successfully extracted {len(projects)} projects!")
    else:
        print("\n✗ No projects extracted")
        sys.exit(1)
