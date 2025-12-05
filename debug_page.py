"""Debug script to fetch and analyze the OpenSAFELY projects page HTML structure"""

import requests
from bs4 import BeautifulSoup

url = "https://www.opensafely.org/approved-projects/"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

print(f"Fetching {url}...")
try:
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    html = response.text
    print(f"✓ Page fetched successfully ({len(html)} characters)")

    soup = BeautifulSoup(html, 'lxml')

    # Save the raw HTML for inspection
    with open('debug_page.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("✓ Saved raw HTML to debug_page.html")

    # Analyze structure
    print("\n" + "="*60)
    print("PAGE STRUCTURE ANALYSIS")
    print("="*60)

    # Check for articles
    articles = soup.find_all('article')
    print(f"\n<article> tags: {len(articles)}")
    if articles:
        print(f"  First article classes: {articles[0].get('class')}")
        print(f"  First article preview: {str(articles[0])[:200]}...")

    # Check for divs with 'project' in class
    project_divs = soup.find_all('div', class_=lambda x: x and 'project' in x.lower())
    print(f"\n<div> with 'project' in class: {len(project_divs)}")
    if project_divs:
        print(f"  First div classes: {project_divs[0].get('class')}")
        print(f"  First div preview: {str(project_divs[0])[:200]}...")

    # Check for list items with 'project' in class
    project_lis = soup.find_all('li', class_=lambda x: x and 'project' in x.lower())
    print(f"\n<li> with 'project' in class: {len(project_lis)}")
    if project_lis:
        print(f"  First li classes: {project_lis[0].get('class')}")
        print(f"  First li preview: {str(project_lis[0])[:200]}...")

    # Check for links with '/project' in href
    project_links = soup.find_all('a', href=lambda x: x and '/project' in x.lower())
    print(f"\n<a> with '/project' in href: {len(project_links)}")
    if project_links:
        for i, link in enumerate(project_links[:5], 1):
            print(f"  {i}. {link.get('href')} - {link.get_text(strip=True)[:50]}...")

    # Look for common container patterns
    print("\n" + "-"*60)
    print("COMMON CONTAINERS:")
    print("-"*60)

    # Check main content areas
    main = soup.find('main')
    if main:
        print(f"\n<main> found, classes: {main.get('class')}")
        print(f"  Children tags: {[child.name for child in main.children if hasattr(child, 'name')][:10]}")

    # Check for sections
    sections = soup.find_all('section')
    print(f"\n<section> tags: {len(sections)}")
    if sections:
        for i, section in enumerate(sections[:3], 1):
            print(f"  Section {i} classes: {section.get('class')}")
            print(f"  Section {i} id: {section.get('id')}")

    # Check all unique element types
    all_tags = set([tag.name for tag in soup.find_all()])
    print(f"\nAll unique HTML tags in page: {sorted(all_tags)}")

    # Check page title
    title = soup.find('title')
    if title:
        print(f"\nPage title: {title.get_text()}")

    # Check h1/h2 headings
    headings = soup.find_all(['h1', 'h2', 'h3'])
    print(f"\nHeadings found: {len(headings)}")
    for i, h in enumerate(headings[:5], 1):
        print(f"  {h.name}: {h.get_text(strip=True)[:60]}")

    print("\n" + "="*60)
    print("DEBUG COMPLETE")
    print("="*60)
    print("Check debug_page.html for full HTML content")

except requests.exceptions.RequestException as e:
    print(f"✗ Error fetching page: {e}")
except Exception as e:
    print(f"✗ Error analyzing page: {e}")
    import traceback
    traceback.print_exc()
