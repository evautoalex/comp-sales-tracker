"""
EV Auto Comp Sales Tracker - VIN Scraper
Multi-strategy scraper that extracts Tesla and Rivian VINs from dealer websites.
"""

import re
import json
import time
import logging
import requests
from bs4 import BeautifulSoup
from config import DEALERS, VIN_PATTERN, TESLA_VIN_PREFIXES, RIVIAN_VIN_PREFIXES

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}


def classify_vin(vin):
    """Classify a VIN as Tesla, Rivian, or unknown."""
    vin = vin.upper()
    for prefix in TESLA_VIN_PREFIXES:
        if vin.startswith(prefix):
            return 'tesla'
    for prefix in RIVIAN_VIN_PREFIXES:
        if vin.startswith(prefix):
            return 'rivian'
    return None


def extract_vins_from_text(text):
    """Extract all valid VINs from raw text."""
    vins = set(re.findall(VIN_PATTERN, text.upper()))
    tesla_vins = set()
    rivian_vins = set()
    for vin in vins:
        make = classify_vin(vin)
        if make == 'tesla':
            tesla_vins.add(vin)
        elif make == 'rivian':
            rivian_vins.add(vin)
    return tesla_vins, rivian_vins


def scrape_dealerinspire(site_config, make_filter):
    """
    Scrape DealerInspire/Dealer.com platform sites.
    These sites typically have VINs in data attributes and page source.
    Handles pagination via ?start=N parameter.
    """
    all_vins_text = ""
    base_url = site_config['url'] + make_filter
    page = 0
    max_pages = 20  # Safety limit

    while page < max_pages:
        url = base_url if page == 0 else f"{base_url}&start={page * 25}"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            all_vins_text += resp.text

            # Check if there's a next page
            soup = BeautifulSoup(resp.text, 'html.parser')
            # Look for pagination indicators
            next_link = soup.find('a', class_=re.compile(r'next|pagination.*next', re.I))
            if not next_link and page > 0:
                break
            if page > 0 and f'start={page * 25}' not in resp.text:
                break
            page += 1
            time.sleep(1)  # Be respectful
        except Exception as e:
            logger.warning(f"Error fetching {url}: {e}")
            break

    return all_vins_text


def scrape_dealersocket(site_config, make_filter):
    """
    Scrape DealerSocket platform sites (e.g., Kentson).
    Similar approach but different URL patterns.
    """
    all_vins_text = ""
    url = site_config['url'] + make_filter
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        all_vins_text += resp.text

        # Try to find API endpoint for full inventory
        soup = BeautifulSoup(resp.text, 'html.parser')
        # Look for script tags with inventory data
        for script in soup.find_all('script'):
            if script.string and ('vin' in script.string.lower() or 'VIN' in script.string):
                all_vins_text += script.string

        # Try common API patterns
        api_patterns = [
            site_config['url'].rstrip('/') + '/api/inventory' + make_filter,
            site_config['url'].rstrip('/') + '/inventory.json' + make_filter,
        ]
        for api_url in api_patterns:
            try:
                api_resp = requests.get(api_url, headers=HEADERS, timeout=15)
                if api_resp.status_code == 200:
                    all_vins_text += api_resp.text
            except:
                pass

    except Exception as e:
        logger.warning(f"Error fetching {url}: {e}")

    return all_vins_text


def scrape_recharged(site_config, make_filter):
    """Scrape Recharged.com - custom React app with API."""
    all_vins_text = ""
    url = site_config['url'] + make_filter
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        all_vins_text += resp.text

        # Try their API endpoint
        api_urls = [
            f"https://recharged.com/api/vehicles{make_filter}",
            f"https://recharged.com/api/v1/vehicles{make_filter}",
        ]
        for api_url in api_urls:
            try:
                api_resp = requests.get(api_url, headers={**HEADERS, 'Accept': 'application/json'}, timeout=15)
                if api_resp.status_code == 200:
                    all_vins_text += api_resp.text
            except:
                pass

    except Exception as e:
        logger.warning(f"Error fetching {url}: {e}")

    return all_vins_text


def scrape_generic(site_config, make):
    """
    Generic scraper for sites without a known platform.
    Tries multiple strategies to find VINs.
    """
    all_vins_text = ""
    base_url = site_config['url']

    # Strategy 1: Try the main page
    try:
        resp = requests.get(base_url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        all_vins_text += resp.text

        soup = BeautifulSoup(resp.text, 'html.parser')

        # Strategy 2: Find links to vehicle detail pages and scrape them
        detail_links = set()
        for a in soup.find_all('a', href=True):
            href = a['href']
            if any(kw in href.lower() for kw in ['vehicle', 'inventory', 'detail', 'car', 'listing']):
                if make.lower() in href.lower() or make.lower() in a.get_text().lower():
                    full_url = href if href.startswith('http') else base_url.rstrip('/') + '/' + href.lstrip('/')
                    detail_links.add(full_url)

        # Strategy 3: Look for embedded JSON data
        for script in soup.find_all('script'):
            if script.string:
                if 'vin' in script.string.lower() or 'inventory' in script.string.lower():
                    all_vins_text += script.string

        # Strategy 4: Check for common API patterns
        domain = base_url.rstrip('/')
        api_patterns = [
            f"{domain}/api/inventory",
            f"{domain}/api/vehicles",
            f"{domain}/inventory.json",
            f"{domain}/api/v1/inventory",
            f"{domain}/wp-json/inventory/v1/vehicles",
        ]
        for api_url in api_patterns:
            try:
                api_resp = requests.get(api_url, headers={**HEADERS, 'Accept': 'application/json'}, timeout=10)
                if api_resp.status_code == 200 and len(api_resp.text) > 100:
                    all_vins_text += api_resp.text
                    logger.info(f"Found API at {api_url}")
            except:
                pass

        # Scrape detail pages (limit to avoid being blocked)
        for link in list(detail_links)[:50]:
            try:
                detail_resp = requests.get(link, headers=HEADERS, timeout=15)
                if detail_resp.status_code == 200:
                    all_vins_text += detail_resp.text
                time.sleep(0.5)
            except:
                pass

    except Exception as e:
        logger.warning(f"Error fetching {base_url}: {e}")

    return all_vins_text


def scrape_ever_cars(site_config, make_filter):
    """Scrape Ever Cars - modern React ecommerce platform."""
    all_vins_text = ""
    url = site_config['url'] + make_filter
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        all_vins_text += resp.text

        # Try API patterns
        api_urls = [
            f"https://www.evercars.com/api/cars{make_filter}",
            f"https://www.evercars.com/api/v1/listings{make_filter}",
            f"https://api.evercars.com/vehicles{make_filter}",
        ]
        for api_url in api_urls:
            try:
                api_resp = requests.get(api_url, headers={**HEADERS, 'Accept': 'application/json'}, timeout=15)
                if api_resp.status_code == 200:
                    all_vins_text += api_resp.text
            except:
                pass

    except Exception as e:
        logger.warning(f"Error fetching {url}: {e}")

    return all_vins_text


# Map platform names to scraping functions
PLATFORM_SCRAPERS = {
    'dealerinspire': scrape_dealerinspire,
    'dealersocket': scrape_dealersocket,
    'custom_recharged': scrape_recharged,
    'custom_ever': scrape_ever_cars,
}


def scrape_dealer(dealer_key, dealer_config):
    """Scrape all sites for a single dealer, collecting Tesla and Rivian VINs."""
    all_tesla_vins = set()
    all_rivian_vins = set()

    for site in dealer_config['sites']:
        platform = site.get('platform', 'generic')
        scraper_fn = PLATFORM_SCRAPERS.get(platform)

        for make, make_filter, vin_set in [
            ('Tesla', site.get('tesla_filter', ''), all_tesla_vins),
            ('Rivian', site.get('rivian_filter', ''), all_rivian_vins),
        ]:
            logger.info(f"Scraping {dealer_config['name']} for {make} ({site['url']})")

            if scraper_fn:
                raw_text = scraper_fn(site, make_filter)
            else:
                raw_text = scrape_generic(site, make)

            tesla_vins, rivian_vins = extract_vins_from_text(raw_text)
            all_tesla_vins.update(tesla_vins)
            all_rivian_vins.update(rivian_vins)

            logger.info(f"  Found {len(tesla_vins)} Tesla, {len(rivian_vins)} Rivian VINs")
            time.sleep(2)  # Rate limiting between requests

    return {
        'tesla': sorted(all_tesla_vins),
        'rivian': sorted(all_rivian_vins),
    }


def scrape_all_dealers():
    """Scrape all configured dealers and return results."""
    results = {}
    for dealer_key, dealer_config in DEALERS.items():
        try:
            results[dealer_key] = scrape_dealer(dealer_key, dealer_config)
            results[dealer_key]['name'] = dealer_config['name']
            results[dealer_key]['is_us'] = dealer_config.get('is_us', False)
            logger.info(
                f"â {dealer_config['name']}: "
                f"{len(results[dealer_key]['tesla'])} Tesla, "
                f"{len(results[dealer_key]['rivian'])} Rivian"
            )
        except Exception as e:
            logger.error(f"â Failed to scrape {dealer_config['name']}: {e}")
            results[dealer_key] = {
                'name': dealer_config['name'],
                'is_us': dealer_config.get('is_us', False),
                'tesla': [],
                'rivian': [],
                'error': str(e),
            }

    return results


if __name__ == '__main__':
    results = scrape_all_dealers()
    print(json.dumps(results, indent=2))
