"""
OpenSAFELY Projects Scraper
Scrapes approved projects from https://www.opensafely.org/approved-projects/
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from typing import List, Dict
from urllib.parse import urljoin


class OpenSAFELYScraper:
    """Scraper for OpenSAFELY approved projects"""

    def __init__(self):
        self.base_url = "https://www.opensafely.org"
        self.projects_url = f"{self.base_url}/approved-projects/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def fetch_page(self, url: str, retries: int = 3, delay: int = 2) -> str:
        """Fetch a page with retries"""
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return response.text
            except requests.exceptions.RequestException as e:
                if attempt < retries - 1:
                    print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    raise Exception(f"Failed to fetch {url} after {retries} attempts: {e}")

    def parse_projects_list(self, html: str) -> List[Dict[str, str]]:
        """Parse the projects list page and extract project information"""
        soup = BeautifulSoup(html, 'lxml')
        projects = []

        # Save HTML for debugging if no projects found
        debug_mode = True  # Set to False to disable debugging

        # Check if page might be JavaScript-rendered
        if 'react' in html.lower() or 'vue' in html.lower() or 'angular' in html.lower():
            print("⚠ WARNING: Page appears to use JavaScript frameworks.")
            print("   Projects may be loaded dynamically after page load.")
            print("   Consider using Selenium or Playwright for scraping.")

        # Check for common JavaScript indicators
        if len(html) < 10000 and ('__NEXT_DATA__' in html or 'root' in html):
            print("⚠ WARNING: Page appears to be a JavaScript app shell.")
            print("   The projects list may be loaded via AJAX/fetch.")

        # Try multiple parsing strategies

        # Strategy 1: Look for articles
        project_elements = soup.find_all('article')
        if project_elements:
            print(f"Found {len(project_elements)} <article> elements")

        # Strategy 2: Look for divs with 'project' in class name
        if not project_elements:
            project_elements = soup.find_all('div', class_=lambda x: x and 'project' in x.lower())
            if project_elements:
                print(f"Found {len(project_elements)} <div> elements with 'project' in class")

        # Strategy 3: Look for list items with 'project' in class
        if not project_elements:
            project_elements = soup.find_all('li', class_=lambda x: x and 'project' in x.lower())
            if project_elements:
                print(f"Found {len(project_elements)} <li> elements with 'project' in class")

        # Strategy 4: Look for any container with 'card' class
        if not project_elements:
            project_elements = soup.find_all(['div', 'article'], class_=lambda x: x and 'card' in x.lower())
            if project_elements:
                print(f"Found {len(project_elements)} card elements")

        # Strategy 5: Look for links with '/project' in href
        if not project_elements:
            print("No structured elements found. Looking for project links...")
            links = soup.find_all('a', href=lambda x: x and '/project' in x.lower())
            print(f"Found {len(links)} links with '/project' in href")

            for link in links:
                href = link.get('href')
                if not href:
                    continue

                project_url = urljoin(self.base_url, href)
                title = link.get_text(strip=True)

                # Skip empty titles or very short ones (likely navigation)
                if title and len(title) > 3:
                    projects.append({
                        'title': title,
                        'url': project_url,
                        'summary': ''
                    })
        else:
            # Parse structured project elements
            print(f"Parsing {len(project_elements)} project elements...")
            for element in project_elements:
                project = self.parse_project_element(element)
                if project:
                    projects.append(project)

        # Debug output if no projects found
        if not projects and debug_mode:
            print("\n" + "="*60)
            print("DEBUG: No projects found. Saving HTML for inspection...")
            with open('debug_page_output.html', 'w', encoding='utf-8') as f:
                f.write(html)
            print("Saved HTML to: debug_page_output.html")
            print(f"HTML length: {len(html)} characters")
            print(f"Page title: {soup.find('title').get_text() if soup.find('title') else 'No title found'}")

            # Show structure hints
            main_content = soup.find('main') or soup.find('div', id='content') or soup.find('body')
            if main_content:
                print("\nMain content structure:")
                children = [child.name for child in main_content.children if hasattr(child, 'name')]
                print(f"  Direct children: {children[:20]}")

                # Look for any headings
                headings = main_content.find_all(['h1', 'h2', 'h3', 'h4'])
                if headings:
                    print(f"\n  Found {len(headings)} headings:")
                    for h in headings[:5]:
                        print(f"    {h.name}: {h.get_text(strip=True)[:60]}")
            print("="*60 + "\n")

        return projects

    def parse_project_element(self, element) -> Dict[str, str]:
        """Parse a single project element"""
        project = {
            'title': '',
            'url': '',
            'summary': '',
            'description': '',
            'authors': '',
            'status': '',
            'date': ''
        }

        # Find title
        title_elem = element.find(['h1', 'h2', 'h3', 'h4'])
        if title_elem:
            project['title'] = title_elem.get_text(strip=True)

        # Find URL
        link = element.find('a', href=True)
        if link:
            project['url'] = urljoin(self.base_url, link['href'])

        # Find description/summary
        desc_elem = element.find('p')
        if desc_elem:
            project['summary'] = desc_elem.get_text(strip=True)

        # Get all text as description
        project['description'] = element.get_text(separator=' ', strip=True)

        return project if project['title'] else None

    def scrape_project_detail(self, url: str) -> Dict[str, str]:
        """Scrape detailed information from a project page"""
        try:
            html = self.fetch_page(url)
            soup = BeautifulSoup(html, 'lxml')

            detail = {
                'url': url,
                'title': '',
                'full_description': '',
                'authors': '',
                'status': '',
                'date': '',
                'topics': '',
                'raw_html': ''
            }

            # Extract title
            title = soup.find('h1')
            if title:
                detail['title'] = title.get_text(strip=True)

            # Extract main content
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
            if main_content:
                detail['full_description'] = main_content.get_text(separator='\n', strip=True)
                detail['raw_html'] = str(main_content)

            # Look for metadata
            meta_fields = ['author', 'status', 'date', 'topic']
            for field in meta_fields:
                meta = soup.find(['div', 'span', 'p'], class_=lambda x: x and field in x.lower())
                if meta:
                    detail[field + 's' if not field.endswith('s') else field] = meta.get_text(strip=True)

            return detail
        except Exception as e:
            print(f"Error scraping project detail {url}: {e}")
            return None

    def scrape_all_projects(self, include_details: bool = True) -> List[Dict[str, str]]:
        """Scrape all projects from the OpenSAFELY website"""
        print("Fetching projects list...")

        try:
            html = self.fetch_page(self.projects_url)
            projects = self.parse_projects_list(html)
            print(f"Found {len(projects)} projects")

            if include_details:
                print("Fetching detailed information for each project...")
                detailed_projects = []
                for i, project in enumerate(projects, 1):
                    print(f"Scraping project {i}/{len(projects)}: {project['title']}")
                    if project.get('url'):
                        detail = self.scrape_project_detail(project['url'])
                        if detail:
                            # Merge list info with detail info
                            project.update(detail)
                        time.sleep(1)  # Be polite, don't hammer the server
                    detailed_projects.append(project)
                projects = detailed_projects

            return projects
        except Exception as e:
            print(f"Error scraping projects: {e}")
            raise

    def save_projects(self, projects: List[Dict[str, str]], filename: str = "opensafely_projects.json"):
        """Save scraped projects to a JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(projects, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(projects)} projects to {filename}")


def main():
    """Main function to run the scraper"""
    scraper = OpenSAFELYScraper()

    try:
        projects = scraper.scrape_all_projects(include_details=True)
        scraper.save_projects(projects)
        print(f"\nSuccessfully scraped {len(projects)} projects!")

        # Print sample
        if projects:
            print("\nSample project:")
            print(json.dumps(projects[0], indent=2))
        else:
            print("\n" + "="*60)
            print("NO PROJECTS FOUND")
            print("="*60)
            print("\nPossible causes:")
            print("1. The website uses JavaScript to load projects dynamically")
            print("2. The HTML structure has changed since this scraper was written")
            print("3. The website is blocking automated requests")
            print("\nNext steps:")
            print("1. Check debug_page_output.html to see the actual HTML received")
            print("2. Try using the Selenium-based scraper:")
            print("   python scraper_selenium.py")
            print("3. Visit https://www.opensafely.org/approved-projects/ in your browser")
            print("   to verify projects are visible")
            print("="*60)

    except Exception as e:
        print(f"Scraping failed: {e}")
        print("\nYou may need to:")
        print("1. Check if the website is accessible")
        print("2. Adjust the scraper to match the actual page structure")
        print("3. Use a browser automation tool like Selenium if JavaScript is required")


if __name__ == "__main__":
    main()
