"""
Improved OpenSAFELY scraper based on known page structure
Projects use IDs like: #project-1, #project-2, etc.
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from typing import List, Dict
from urllib.parse import urljoin
import time


class ImprovedOpenSAFELYScraper:
    """Improved scraper targeting the actual page structure"""

    def __init__(self):
        self.base_url = "https://www.opensafely.org"
        self.projects_url = f"{self.base_url}/approved-projects/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }

    def fetch_page(self, url: str) -> str:
        """Fetch page content"""
        print(f"Fetching: {url}")
        response = requests.get(url, headers=self.headers, timeout=30)
        response.raise_for_status()

        # Ensure proper decoding
        if response.encoding is None or response.encoding == 'ISO-8859-1':
            response.encoding = response.apparent_encoding

        print(f"✓ Fetched {len(response.text)} characters")
        return response.text

    def parse_projects(self, html: str) -> List[Dict]:
        """Parse projects from HTML"""
        soup = BeautifulSoup(html, 'lxml')
        projects = []

        print("\n" + "=" * 60)
        print("PARSING PROJECTS")
        print("=" * 60)

        # Save HTML for debugging
        with open('debug_page_output.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"\nSaved HTML to: debug_page_output.html")
        print(f"HTML length: {len(html)} characters")
        print(f"Page title: {soup.title.string if soup.title else 'No title found'}")

        # Strategy 1: Look for elements with ID matching "project-*"
        print("\n1. Looking for elements with ID 'project-*'...")
        project_elements = soup.find_all(id=re.compile(r'^project-\d+$'))
        print(f"   Found {len(project_elements)} elements with project IDs")

        if project_elements:
            for elem in project_elements:
                project = self.parse_project_element(elem)
                if project:
                    projects.append(project)
            print(f"   ✓ Parsed {len(projects)} projects from ID elements")
            return projects

        # Strategy 2: Look for any element with ID containing "project"
        print("\n2. Looking for elements with ID containing 'project'...")
        project_elements = soup.find_all(id=re.compile(r'project', re.IGNORECASE))
        print(f"   Found {len(project_elements)} elements")

        if project_elements:
            for elem in project_elements:
                project = self.parse_project_element(elem)
                if project:
                    projects.append(project)
            print(f"   ✓ Parsed {len(projects)} projects")
            return projects

        # Strategy 3: Look for structured elements (article, section, div with project class)
        print("\n3. Looking for structured elements...")

        selectors = [
            ('article', None),
            ('section', lambda x: x and 'project' in ' '.join(x).lower()),
            ('div', lambda x: x and 'project' in ' '.join(x).lower()),
            ('li', lambda x: x and 'project' in ' '.join(x).lower()),
        ]

        for tag, class_filter in selectors:
            elements = soup.find_all(tag, class_=class_filter) if class_filter else soup.find_all(tag)
            print(f"   {tag}: {len(elements)} elements")

            if elements:
                for elem in elements:
                    project = self.parse_project_element(elem)
                    if project and project not in projects:  # Avoid duplicates
                        projects.append(project)

        if projects:
            print(f"   ✓ Parsed {len(projects)} projects from structured elements")
            return projects

        # Strategy 4: Look in main content area
        print("\n4. Analyzing main content structure...")
        main = soup.find('main') or soup.find('div', id='main') or soup.find('body')

        if main:
            print(f"   Main content: <{main.name}>")

            # Get all direct children
            children = [c for c in main.children if hasattr(c, 'name') and c.name]
            print(f"   Direct children: {len(children)}")

            # Look for repeating patterns
            tag_counts = {}
            for child in children:
                tag = child.name
                classes = ' '.join(child.get('class', []))
                key = f"{tag}.{classes}" if classes else tag
                tag_counts[key] = tag_counts.get(key, 0) + 1

            print("\n   Tag patterns:")
            for tag, count in sorted(tag_counts.items(), key=lambda x: -x[1])[:10]:
                print(f"      {tag}: {count}")

            # If there are many similar elements, they might be projects
            for tag_pattern, count in tag_counts.items():
                if count > 10:  # Likely a list of items
                    print(f"\n   Found repeating pattern: {tag_pattern} ({count} items)")

                    # Try to extract these as projects
                    tag_name, *class_parts = tag_pattern.split('.')
                    class_name = '.'.join(class_parts) if class_parts else None

                    if class_name:
                        elements = main.find_all(tag_name, class_=class_name.split())
                    else:
                        elements = main.find_all(tag_name)

                    for elem in elements:
                        project = self.parse_project_element(elem)
                        if project:
                            projects.append(project)

                    if projects:
                        print(f"   ✓ Extracted {len(projects)} projects")
                        return projects

        # Strategy 5: Look for links with project in the URL
        print("\n5. Looking for project links...")
        all_links = soup.find_all('a', href=True)
        project_links = []

        for link in all_links:
            href = link.get('href', '')
            text = link.get_text(strip=True)

            # Look for patterns like /project/*, /projects/*, or #project-*
            if re.search(r'/(project|approved-project)', href, re.IGNORECASE) or re.match(r'#project-\d+', href):
                if text and len(text) > 10:  # Filter out short navigation text
                    project_links.append(link)

        print(f"   Found {len(project_links)} project links")

        if project_links:
            for link in project_links:
                href = link.get('href')
                text = link.get_text(strip=True)

                # Try to find parent container with more info
                parent = link.find_parent(['article', 'div', 'li', 'section'])
                if parent:
                    project = self.parse_project_element(parent)
                else:
                    project = {
                        'title': text,
                        'url': urljoin(self.base_url, href) if not href.startswith('#') else f"{self.projects_url}{href}",
                        'id': href,
                    }

                if project and project not in projects:
                    projects.append(project)

            print(f"   ✓ Extracted {len(projects)} projects from links")

        return projects

    def parse_project_element(self, element) -> Dict:
        """Parse a single project element"""
        project = {
            'title': '',
            'description': '',
            'url': '',
            'id': '',
            'authors': '',
            'date': '',
            'status': '',
            'lead_organisation': '',
            'keywords': []
        }

        # Get ID
        elem_id = element.get('id', '')
        if elem_id:
            project['id'] = elem_id
            project['url'] = f"{self.projects_url}#{elem_id}"

        # Get title - try different heading levels
        title = element.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if title:
            project['title'] = title.get_text(strip=True)

        # If no title in heading, try to get from first significant text or link
        if not project['title']:
            link = element.find('a')
            if link:
                project['title'] = link.get_text(strip=True)

        # Get description - look for paragraphs or description elements
        desc_elem = element.find('p') or element.find(class_=re.compile(r'(desc|summary|abstract)', re.IGNORECASE))
        if desc_elem:
            project['description'] = desc_elem.get_text(strip=True)
        else:
            # Get all text as fallback
            text = element.get_text(separator=' ', strip=True)
            # Remove title from text
            if project['title']:
                text = text.replace(project['title'], '', 1)
            project['description'] = text[:500]  # Limit length

        # Look for metadata fields
        metadata_fields = {
            'author': 'authors',
            'date': 'date',
            'status': 'status',
            'organisation': 'lead_organisation',
            'organization': 'lead_organisation',
            'keyword': 'keywords',
            'tag': 'keywords'
        }

        for search_term, field_name in metadata_fields.items():
            # Look for elements with class or attribute containing the search term
            meta_elem = element.find(class_=re.compile(search_term, re.IGNORECASE))
            if meta_elem:
                value = meta_elem.get_text(strip=True)
                if field_name == 'keywords':
                    project[field_name].extend([k.strip() for k in value.split(',')])
                else:
                    project[field_name] = value

        # Look for links
        link = element.find('a', href=True)
        if link and not project['url']:
            href = link['href']
            if not href.startswith('#'):
                project['url'] = urljoin(self.base_url, href)

        # Only return if we have at least a title
        return project if project['title'] else None

    def scrape_all_projects(self) -> List[Dict]:
        """Main scraping method"""
        try:
            html = self.fetch_page(self.projects_url)
            projects = self.parse_projects(html)
            return projects
        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return []

    def save_projects(self, projects: List[Dict], filename='opensafely_projects.json'):
        """Save projects to JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(projects, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Saved {len(projects)} projects to {filename}")


def main():
    """Main function"""
    print("=" * 60)
    print("IMPROVED OPENSAFELY SCRAPER")
    print("=" * 60)

    scraper = ImprovedOpenSAFELYScraper()
    projects = scraper.scrape_all_projects()

    if projects:
        scraper.save_projects(projects)

        print("\n" + "=" * 60)
        print(f"SUCCESS: Found {len(projects)} projects!")
        print("=" * 60)

        print("\nSample projects:")
        for i, project in enumerate(projects[:3], 1):
            print(f"\n{i}. {project.get('title', 'No title')}")
            print(f"   ID: {project.get('id', 'N/A')}")
            print(f"   URL: {project.get('url', 'N/A')}")
            if project.get('description'):
                desc = project['description'][:150]
                print(f"   Description: {desc}...")
            if project.get('authors'):
                print(f"   Authors: {project['authors']}")

        return 0
    else:
        print("\n" + "=" * 60)
        print("FAILED: No projects found")
        print("=" * 60)
        print("\nCheck debug_page_output.html to see the HTML structure")
        print("You may need to use: python parse_local_html.py debug_page_output.html")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
