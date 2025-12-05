"""
Test script for the OpenSAFELY scraper
Tests basic functionality and connectivity
"""

import sys
from scraper import OpenSAFELYScraper


def test_scraper():
    """Test the scraper functionality"""
    print("Testing OpenSAFELY Scraper...")
    print("=" * 50)

    # Initialize scraper
    print("\n1. Initializing scraper...")
    scraper = OpenSAFELYScraper()
    print("   ✓ Scraper initialized")

    # Test connection
    print("\n2. Testing connection to OpenSAFELY...")
    try:
        html = scraper.fetch_page(scraper.projects_url)
        print(f"   ✓ Successfully fetched page ({len(html)} bytes)")
        print(f"   First 200 characters: {html[:200]}")

        # Try to parse
        print("\n3. Parsing projects list...")
        projects = scraper.parse_projects_list(html)
        print(f"   ✓ Found {len(projects)} projects")

        if projects:
            print("\n4. Sample project:")
            import json
            print(json.dumps(projects[0], indent=2))

            print("\n✓ All tests passed!")
            print(f"\nTo scrape all projects, run: python scraper.py")
            return True
        else:
            print("\n⚠ Warning: No projects found. The page structure might have changed.")
            print("   You may need to adjust the parser in scraper.py")
            return False

    except Exception as e:
        print(f"   ✗ Error: {e}")
        print("\nTroubleshooting:")
        print("- Check your internet connection")
        print("- The website might be blocking automated requests")
        print("- Try running: curl -I https://www.opensafely.org/approved-projects/")
        print("- You may need to adjust headers in scraper.py")
        return False


if __name__ == "__main__":
    success = test_scraper()
    sys.exit(0 if success else 1)
