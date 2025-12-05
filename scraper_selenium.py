"""
OpenSAFELY Projects Scraper using Selenium
Use this if the website loads projects via JavaScript

Installation:
    pip install selenium
    # Also install a browser driver (e.g., chromedriver, geckodriver)
    # Or use selenium-wire which includes drivers
"""

import json
import time
from typing import List, Dict

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException
except ImportError:
    print("ERROR: Selenium is not installed.")
    print("Install it with: pip install selenium")
    print("You may also need to install a browser driver (chromedriver, geckodriver, etc.)")
    exit(1)


class SeleniumOpenSAFELYScraper:
    """Scraper using Selenium to handle JavaScript-rendered content"""

    def __init__(self, headless: bool = True):
        """
        Initialize the Selenium scraper

        Args:
            headless: Run browser in headless mode (no GUI)
        """
        self.base_url = "https://www.opensafely.org"
        self.projects_url = f"{self.base_url}/approved-projects/"
        self.headless = headless
        self.driver = None

    def _init_driver(self):
        """Initialize the Selenium WebDriver"""
        if self.driver:
            return

        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )

        try:
            self.driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            print(f"Failed to initialize Chrome driver: {e}")
            print("\nTrying Firefox...")
            try:
                from selenium.webdriver.firefox.options import Options as FirefoxOptions
                firefox_options = FirefoxOptions()
                if self.headless:
                    firefox_options.add_argument("--headless")
                self.driver = webdriver.Firefox(options=firefox_options)
            except Exception as e2:
                print(f"Failed to initialize Firefox driver: {e2}")
                raise Exception(
                    "Could not initialize any browser driver. "
                    "Please install chromedriver or geckodriver."
                )

    def scrape_projects_list(self) -> List[Dict[str, str]]:
        """Scrape the projects list page"""
        self._init_driver()
        projects = []

        try:
            print(f"Loading {self.projects_url}...")
            self.driver.get(self.projects_url)

            # Wait for page to load - adjust selector based on actual page
            # Try multiple strategies
            wait = WebDriverWait(self.driver, 10)

            # Give JavaScript time to render
            time.sleep(3)

            # Save page source for debugging
            page_source = self.driver.page_source
            with open('debug_selenium_output.html', 'w', encoding='utf-8') as f:
                f.write(page_source)
            print("Saved page source to: debug_selenium_output.html")

            # Try different selectors to find projects
            selectors = [
                (By.TAG_NAME, "article"),
                (By.CSS_SELECTOR, "[class*='project']"),
                (By.CSS_SELECTOR, "[class*='card']"),
                (By.XPATH, "//a[contains(@href, '/project')]"),
            ]

            elements = []
            for by, selector in selectors:
                try:
                    elements = self.driver.find_elements(by, selector)
                    if elements:
                        print(f"Found {len(elements)} elements using {by}={selector}")
                        break
                except Exception as e:
                    continue

            if not elements:
                print("⚠ No project elements found with any selector")
                print(f"Page title: {self.driver.title}")
                print(f"Page source length: {len(page_source)} characters")
                return projects

            # Extract project information
            for element in elements:
                try:
                    # Try to find title and link
                    title_element = element.find_element(By.TAG_NAME, "h1") if element.tag_name != "a" else element
                    if not title_element:
                        title_element = element.find_element(By.TAG_NAME, "h2")
                    if not title_element:
                        title_element = element.find_element(By.TAG_NAME, "h3")

                    title = title_element.text.strip() if hasattr(title_element, 'text') else element.text.strip()

                    # Get link
                    if element.tag_name == 'a':
                        url = element.get_attribute('href')
                    else:
                        link_element = element.find_element(By.TAG_NAME, "a")
                        url = link_element.get_attribute('href') if link_element else ""

                    if title and url:
                        projects.append({
                            'title': title,
                            'url': url,
                            'summary': ''
                        })
                except Exception as e:
                    # Skip elements that don't match expected structure
                    continue

            print(f"Extracted {len(projects)} projects")

        except TimeoutException:
            print("Timeout waiting for page to load")
        except Exception as e:
            print(f"Error scraping projects: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.driver:
                self.driver.quit()

        return projects

    def scrape_all_projects(self, include_details: bool = False) -> List[Dict[str, str]]:
        """Scrape all projects"""
        projects = self.scrape_projects_list()

        if include_details and projects:
            print(f"\nFetching details for {len(projects)} projects...")
            # TODO: Implement detail scraping if needed
            print("(Detail scraping not yet implemented for Selenium version)")

        return projects

    def save_projects(self, projects: List[Dict[str, str]], filename: str = "opensafely_projects.json"):
        """Save projects to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(projects, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(projects)} projects to {filename}")


def main():
    """Main function"""
    print("OpenSAFELY Selenium Scraper")
    print("="*60)
    print("This scraper uses Selenium to handle JavaScript-rendered content")
    print("="*60 + "\n")

    scraper = SeleniumOpenSAFELYScraper(headless=True)

    try:
        projects = scraper.scrape_all_projects(include_details=False)

        if projects:
            scraper.save_projects(projects)
            print(f"\n✓ Successfully scraped {len(projects)} projects!")
            print("\nSample project:")
            print(json.dumps(projects[0], indent=2))
        else:
            print("\n⚠ No projects found.")
            print("Check debug_selenium_output.html to see the page source")

    except Exception as e:
        print(f"\n✗ Scraping failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
