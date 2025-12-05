"""
Selenium-based scraper for OpenSAFELY projects
Use this if the site requires JavaScript rendering
"""

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("Selenium not installed. Install with: pip install selenium")

from bs4 import BeautifulSoup
import json
import time


class SeleniumScraper:
    """Scraper using Selenium for JavaScript-rendered content"""

    def __init__(self, headless=True):
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium is required for this scraper")

        self.headless = headless
        self.driver = None

    def setup_driver(self):
        """Setup Chrome driver with appropriate options"""
        chrome_options = Options()

        if self.headless:
            chrome_options.add_argument('--headless')

        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            print("✓ Chrome driver initialized")
        except Exception as e:
            print(f"✗ Failed to initialize Chrome driver: {e}")
            print("\nTroubleshooting:")
            print("1. Install Chrome/Chromium browser")
            print("2. Install chromedriver: ")
            print("   - Linux: sudo apt-get install chromium-chromedriver")
            print("   - Mac: brew install chromedriver")
            print("   - Or download from: https://chromedriver.chromium.org/")
            raise

    def fetch_page(self, url, wait_for_selector=None, wait_time=10):
        """Fetch page and wait for JavaScript to render"""
        if not self.driver:
            self.setup_driver()

        print(f"\nFetching: {url}")
        self.driver.get(url)

        # Wait for page to load
        if wait_for_selector:
            try:
                print(f"Waiting for selector: {wait_for_selector}")
                WebDriverWait(self.driver, wait_time).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, wait_for_selector))
                )
                print("✓ Page loaded")
            except Exception as e:
                print(f"⚠ Timeout waiting for selector: {e}")
        else:
            # Just wait a bit for JS to execute
            time.sleep(3)

        # Get the rendered HTML
        html = self.driver.page_source

        # Save for debugging
        with open('selenium_page_output.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"✓ Saved rendered HTML to selenium_page_output.html ({len(html)} chars)")

        return html

    def scrape_projects(self, url="https://www.opensafely.org/approved-projects/"):
        """Scrape projects from OpenSAFELY"""
        print("=" * 60)
        print("SELENIUM SCRAPER")
        print("=" * 60)

        # Fetch the page
        # Try waiting for common project container selectors
        selectors_to_try = [
            'article',
            '.project',
            '[class*="project"]',
            'main',
            '#__next'  # Next.js app root
        ]

        html = None
        for selector in selectors_to_try:
            try:
                html = self.fetch_page(url, wait_for_selector=selector, wait_time=5)
                break
            except:
                continue

        if not html:
            # Fallback: just load and wait
            html = self.fetch_page(url)

        # Parse the HTML
        soup = BeautifulSoup(html, 'lxml')

        print("\n" + "=" * 60)
        print("ANALYZING RENDERED PAGE")
        print("=" * 60)

        # Basic info
        print(f"\nPage title: {soup.title.string if soup.title else 'No title'}")
        print(f"HTML length: {len(html)} characters")

        # Structure
        print("\nPage structure:")
        print(f"  Articles: {len(soup.find_all('article'))}")
        print(f"  Divs: {len(soup.find_all('div'))}")
        print(f"  Links: {len(soup.find_all('a'))}")

        # Try to find projects
        projects = []

        # Strategy 1: Articles
        articles = soup.find_all('article')
        if articles:
            print(f"\n✓ Found {len(articles)} articles")
            for article in articles:
                project = self.parse_project_element(article)
                if project:
                    projects.append(project)

        # Strategy 2: Divs with project class
        if not projects:
            project_divs = soup.find_all('div', class_=lambda x: x and 'project' in x.lower())
            if project_divs:
                print(f"\n✓ Found {len(project_divs)} project divs")
                for div in project_divs:
                    project = self.parse_project_element(div)
                    if project:
                        projects.append(project)

        # Strategy 3: Links
        if not projects:
            links = soup.find_all('a', href=lambda x: x and 'project' in x.lower())
            if links:
                print(f"\n✓ Found {len(links)} project links")
                for link in links:
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    if text and len(text) > 10:  # Filter out short navigation links
                        projects.append({
                            'title': text,
                            'url': href if href.startswith('http') else f"https://www.opensafely.org{href}",
                            'summary': ''
                        })

        # Strategy 4: Use Selenium to find elements directly
        if not projects:
            print("\nTrying direct Selenium element search...")
            try:
                # Try to find project elements
                elements = self.driver.find_elements(By.CSS_SELECTOR, 'article, [class*="project"], [class*="card"]')
                print(f"Found {len(elements)} potential project elements")

                for element in elements[:20]:  # Limit to first 20
                    try:
                        text = element.text
                        if len(text) > 50:  # Has substantial content
                            # Try to find title
                            title_elem = element.find_element(By.CSS_SELECTOR, 'h1, h2, h3, h4')
                            title = title_elem.text if title_elem else text.split('\n')[0]

                            # Try to find link
                            try:
                                link_elem = element.find_element(By.TAG_NAME, 'a')
                                url = link_elem.get_attribute('href')
                            except:
                                url = ''

                            if title:
                                projects.append({
                                    'title': title,
                                    'url': url,
                                    'summary': text[:200]
                                })
                    except:
                        continue

            except Exception as e:
                print(f"✗ Selenium search failed: {e}")

        print(f"\n✓ Extracted {len(projects)} projects")

        return projects

    def parse_project_element(self, element):
        """Parse a project from a BeautifulSoup element"""
        project = {}

        # Get title
        title = element.find(['h1', 'h2', 'h3', 'h4'])
        if title:
            project['title'] = title.get_text(strip=True)
        else:
            # Try to get first significant text
            text = element.get_text(strip=True)
            if text:
                lines = [l for l in text.split('\n') if len(l) > 10]
                if lines:
                    project['title'] = lines[0]

        # Get URL
        link = element.find('a', href=True)
        if link:
            href = link['href']
            if not href.startswith('http'):
                href = f"https://www.opensafely.org{href}"
            project['url'] = href

        # Get summary
        paras = element.find_all('p')
        if paras:
            project['summary'] = ' '.join(p.get_text(strip=True) for p in paras[:2])

        return project if project.get('title') else None

    def save_projects(self, projects, filename='opensafely_projects.json'):
        """Save projects to JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(projects, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved to {filename}")

    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            print("✓ Browser closed")


def main():
    """Main function"""
    if not SELENIUM_AVAILABLE:
        print("Please install Selenium: pip install selenium")
        return

    scraper = SeleniumScraper(headless=True)

    try:
        projects = scraper.scrape_projects()

        if projects:
            scraper.save_projects(projects)
            print(f"\n✓ Successfully scraped {len(projects)} projects!")

            print("\nSample projects:")
            for i, project in enumerate(projects[:3], 1):
                print(f"\n{i}. {project.get('title', 'No title')}")
                print(f"   URL: {project.get('url', 'No URL')}")
                if project.get('summary'):
                    print(f"   Summary: {project['summary'][:100]}...")
        else:
            print("\n✗ No projects found")
            print("Check selenium_page_output.html to see what was rendered")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        scraper.close()


if __name__ == "__main__":
    main()
