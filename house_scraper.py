import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import random
from typing import List, Dict, Optional
import json
from urllib.parse import urlencode
import logging
from fake_useragent import UserAgent
import re
import difflib

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='scraper.log'
)

def log_scraper_error(error_msg):
    with open('scraper_errors.log', 'a', encoding='utf-8') as f:
        f.write(f"{datetime.now().isoformat()} - {error_msg}\n")

def log_user_feedback(feedback):
    with open('user_feedback.log', 'a', encoding='utf-8') as f:
        f.write(f"{datetime.now().isoformat()} - {feedback}\n")

class BaseScraper:
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
    def get_random_delay(self) -> float:
        """Generate a random delay between requests."""
        return random.uniform(3, 7)  # Increased delay for commercial use
        
    def rotate_user_agent(self):
        """Rotate user agent for each request."""
        self.session.headers.update({'User-Agent': self.ua.random})

class ZillowScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.zillow.com"
        
    def search_rentals(self, location: str, min_price=None, max_price=None, num_bedrooms=None, amenities=None, lifestyle=None, **kwargs) -> List[Dict]:
        """Search Zillow rentals with proper API endpoints and apply filters."""
        try:
            self.rotate_user_agent()
            time.sleep(self.get_random_delay())
            
            # Use Zillow's search API endpoint
            search_url = f"{self.base_url}/search/GetSearchPageState.htm"
            filter_state = {
                'isForSaleByAgent': {'value': False},
                'isForSaleForeclosure': {'value': False},
                'isAllHomes': {'value': True},
                'isMultiFamily': {'value': False},
                'isAuction': {'value': False},
                'isNewConstruction': {'value': False},
                'isForRent': {'value': True},
            }
            if min_price:
                filter_state['priceMin'] = {'value': min_price}
            if max_price:
                filter_state['priceMax'] = {'value': max_price}
            if num_bedrooms:
                filter_state['bedsMin'] = {'value': num_bedrooms}
            params = {
                'searchQueryState': json.dumps({
                    'pagination': {},
                    'mapBounds': {},
                    'regionSelection': [{'regionId': self._get_region_id(location)}],
                    'isMapVisible': True,
                    'filterState': filter_state
                })
            }
            
            response = self.session.get(search_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            listings = self._parse_zillow_response(data)
            # Post-filter for amenities/lifestyle if needed
            return self._post_filter(listings, amenities, lifestyle)
        except Exception as e:
            logging.error(f"Error scraping Zillow: {str(e)}")
            log_scraper_error(str(e))
            return []

    def _get_region_id(self, location: str) -> str:
        """Get Zillow region ID for a location."""
        # Simple hardcoded mapping for demo
        region_map = {
            'Toronto': '83728',
            'New York': '6181',
            'San Francisco': '20330',
            'Los Angeles': '12447',
            'Chicago': '17426',
        }
        return region_map.get(location, '')

    def _parse_zillow_response(self, data: Dict) -> List[Dict]:
        """Parse Zillow API response."""
        listings = []
        try:
            for item in data.get('searchResults', {}).get('listResults', []):
                listing = {
                    'source': 'Zillow',
                    'title': item.get('address'),
                    'price': item.get('price'),
                    'location': item.get('address'),
                    'bedrooms': item.get('beds'),
                    'bathrooms': item.get('baths'),
                    'square_feet': item.get('area'),
                    'url': f"{self.base_url}{item.get('detailUrl')}",
                    'scraped_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                listings.append(listing)
        except Exception as e:
            logging.error(f"Error parsing Zillow response: {str(e)}")
            log_scraper_error(str(e))
        return listings

    def _post_filter(self, listings, amenities, lifestyle):
        if not amenities and not lifestyle:
            return listings
        filtered = []
        for l in listings:
            match = True
            # Amenities: fuzzy/partial match
            if amenities:
                l_amenities = [a.lower() for a in l.get('amenities', [])]
                for a in amenities:
                    found = False
                    for la in l_amenities:
                        if a.lower() in la or la in a.lower() or difflib.get_close_matches(a.lower(), [la], n=1, cutoff=0.7):
                            found = True
                            break
                    if not found:
                        match = False
                        break
            # Lifestyle: fuzzy/partial match in title/location/description
            if match and lifestyle:
                lifestyle_keywords = [k.strip().lower() for k in lifestyle.split(',')]
                text = (l.get('title','') + ' ' + l.get('location','') + ' ' + l.get('description','')).lower()
                if not any(k in text or difflib.get_close_matches(k, text.split(), n=1, cutoff=0.7) for k in lifestyle_keywords):
                    match = False
            if match:
                filtered.append(l)
        return filtered

class ApartmentsScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.apartments.com"
        
    def search_rentals(self, location: str, min_price=None, max_price=None, num_bedrooms=None, amenities=None, lifestyle=None, **kwargs) -> List[Dict]:
        """Search Apartments.com listings with all filters."""
        try:
            self.rotate_user_agent()
            time.sleep(self.get_random_delay())
            
            search_url = f"{self.base_url}/{location.replace(' ', '-').lower()}"
            response = self.session.get(search_url)
            response.raise_for_status()
            
            listings = self._parse_apartments_response(response.text)
            # Post-filter for price, bedrooms, amenities, lifestyle
            filtered = []
            for l in listings:
                match = True
                if min_price and l.get('price'):
                    try:
                        price = int(re.sub(r'[^0-9]', '', str(l['price'])))
                        if price < min_price:
                            match = False
                    except:
                        pass
                if max_price and l.get('price'):
                    try:
                        price = int(re.sub(r'[^0-9]', '', str(l['price'])))
                        if price > max_price:
                            match = False
                    except:
                        pass
                if num_bedrooms and l.get('bedrooms'):
                    try:
                        if int(l['bedrooms']) < num_bedrooms:
                            match = False
                    except:
                        pass
                # Amenities/lifestyle
                if match:
                    l_amenities = [a.lower() for a in l.get('amenities', [])]
                    if amenities:
                        for a in amenities:
                            if a.lower() not in l_amenities:
                                match = False
                                break
                if match and lifestyle:
                    lifestyle_keywords = [k.strip().lower() for k in lifestyle.split(',')]
                    text = (l.get('title','') + ' ' + l.get('location','') + ' ' + l.get('description','')).lower()
                    if not any(k in text for k in lifestyle_keywords):
                        match = False
                if match:
                    filtered.append(l)
            return filtered
        except Exception as e:
            logging.error(f"Error scraping Apartments.com: {str(e)}")
            log_scraper_error(str(e))
            return []

    def _parse_apartments_response(self, html_content: str) -> List[Dict]:
        """Parse Apartments.com HTML response."""
        listings = []
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            for item in soup.select('.placardContainer'):
                listing = {
                    'source': 'Apartments.com',
                    'title': item.select_one('.property-title').text.strip(),
                    'price': item.select_one('.property-rent').text.strip(),
                    'location': item.select_one('.property-address').text.strip(),
                    'url': f"{self.base_url}{item.select_one('a')['href']}",
                    'scraped_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                listings.append(listing)
        except Exception as e:
            logging.error(f"Error parsing Apartments.com response: {str(e)}")
            log_scraper_error(str(e))
        return listings

class PadMapperScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.padmapper.com"
        
    def search_rentals(self, location: str, min_price=None, max_price=None, num_bedrooms=None, amenities=None, lifestyle=None, **kwargs) -> List[Dict]:
        """Search PadMapper listings with all filters."""
        try:
            self.rotate_user_agent()
            time.sleep(self.get_random_delay())
            
            search_url = f"{self.base_url}/apartments/{location.replace(' ', '-').lower()}"
            response = self.session.get(search_url)
            response.raise_for_status()
            
            listings = self._parse_padmapper_response(response.text)
            # Post-filter for price, bedrooms, amenities, lifestyle
            filtered = []
            for l in listings:
                match = True
                if min_price and l.get('price'):
                    try:
                        price = int(re.sub(r'[^0-9]', '', str(l['price'])))
                        if price < min_price:
                            match = False
                    except:
                        pass
                if max_price and l.get('price'):
                    try:
                        price = int(re.sub(r'[^0-9]', '', str(l['price'])))
                        if price > max_price:
                            match = False
                    except:
                        pass
                if num_bedrooms and l.get('bedrooms'):
                    try:
                        if int(l['bedrooms']) < num_bedrooms:
                            match = False
                    except:
                        pass
                # Amenities/lifestyle
                if match:
                    l_amenities = [a.lower() for a in l.get('amenities', [])]
                    if amenities:
                        for a in amenities:
                            if a.lower() not in l_amenities:
                                match = False
                                break
                if match and lifestyle:
                    lifestyle_keywords = [k.strip().lower() for k in lifestyle.split(',')]
                    text = (l.get('title','') + ' ' + l.get('location','') + ' ' + l.get('description','')).lower()
                    if not any(k in text for k in lifestyle_keywords):
                        match = False
                if match:
                    filtered.append(l)
            return filtered
        except Exception as e:
            logging.error(f"Error scraping PadMapper: {str(e)}")
            log_scraper_error(str(e))
            return []

    def _parse_padmapper_response(self, html_content: str) -> List[Dict]:
        """Parse PadMapper HTML response."""
        listings = []
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            for item in soup.select('.listing-card'):
                listing = {
                    'source': 'PadMapper',
                    'title': item.select_one('.listing-title').text.strip(),
                    'price': item.select_one('.listing-price').text.strip(),
                    'location': item.select_one('.listing-location').text.strip(),
                    'url': f"{self.base_url}{item.select_one('a')['href']}",
                    'scraped_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                listings.append(listing)
        except Exception as e:
            logging.error(f"Error parsing PadMapper response: {str(e)}")
            log_scraper_error(str(e))
        return listings

class KijijiScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.kijiji.ca"
        
    def search_rentals(self, location: str, min_price=None, max_price=None, num_bedrooms=None, amenities=None, lifestyle=None, **kwargs) -> List[Dict]:
        """Search Kijiji listings with all filters."""
        try:
            self.rotate_user_agent()
            time.sleep(self.get_random_delay())
            
            search_url = f"{self.base_url}/b-apartments-condos/{location}/c37l1700272"
            response = self.session.get(search_url)
            response.raise_for_status()
            
            listings = self._parse_kijiji_response(response.text)
            # Post-filter for price, bedrooms, amenities, lifestyle
            filtered = []
            for l in listings:
                match = True
                if min_price and l.get('price'):
                    try:
                        price = int(re.sub(r'[^0-9]', '', str(l['price'])))
                        if price < min_price:
                            match = False
                    except:
                        pass
                if max_price and l.get('price'):
                    try:
                        price = int(re.sub(r'[^0-9]', '', str(l['price'])))
                        if price > max_price:
                            match = False
                    except:
                        pass
                if num_bedrooms and l.get('bedrooms'):
                    try:
                        if int(l['bedrooms']) < num_bedrooms:
                            match = False
                    except:
                        pass
                # Amenities/lifestyle
                if match:
                    l_amenities = [a.lower() for a in l.get('amenities', [])]
                    if amenities:
                        for a in amenities:
                            if a.lower() not in l_amenities:
                                match = False
                                break
                if match and lifestyle:
                    lifestyle_keywords = [k.strip().lower() for k in lifestyle.split(',')]
                    text = (l.get('title','') + ' ' + l.get('location','') + ' ' + l.get('description','')).lower()
                    if not any(k in text for k in lifestyle_keywords):
                        match = False
                if match:
                    filtered.append(l)
            return filtered
        except Exception as e:
            logging.error(f"Error scraping Kijiji: {str(e)}")
            log_scraper_error(str(e))
            return []

    def _parse_kijiji_response(self, html_content: str) -> List[Dict]:
        """Parse Kijiji HTML response."""
        listings = []
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            for item in soup.select('.search-item'):
                listing = {
                    'source': 'Kijiji',
                    'title': item.select_one('.title').text.strip(),
                    'price': item.select_one('.price').text.strip(),
                    'location': item.select_one('.location').text.strip(),
                    'url': f"{self.base_url}{item.select_one('a')['href']}",
                    'scraped_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                listings.append(listing)
        except Exception as e:
            logging.error(f"Error parsing Kijiji response: {str(e)}")
            log_scraper_error(str(e))
        return listings

class RentalScraperManager:
    def __init__(self):
        self.scrapers = {
            'zillow': ZillowScraper(),
            'apartments': ApartmentsScraper(),
            'padmapper': PadMapperScraper(),
            'kijiji': KijijiScraper()
        }
        
    def search_all_sites(self, location: str, min_price=None, max_price=None, num_bedrooms=None, amenities=None, lifestyle=None, **kwargs) -> List[Dict]:
        """Search all supported sites for rental listings with all filters."""
        all_listings = []
        
        for site_name, scraper in self.scrapers.items():
            try:
                logging.info(f"Searching {site_name} for {location}")
                listings = scraper.search_rentals(
                    location,
                    min_price=min_price,
                    max_price=max_price,
                    num_bedrooms=num_bedrooms,
                    amenities=amenities,
                    lifestyle=lifestyle
                )
                all_listings.extend(listings)
                logging.info(f"Found {len(listings)} listings on {site_name}")
            except Exception as e:
                logging.error(f"Error searching {site_name}: {str(e)}")
                log_scraper_error(str(e))
                continue
                
        return all_listings
    
    def save_to_csv(self, listings: List[Dict], filename: str = 'rental_listings.csv'):
        """Save the scraped listings to a CSV file."""
        if not listings:
            logging.warning("No listings to save")
            return

        df = pd.DataFrame(listings)
        df.to_csv(filename, index=False)
        logging.info(f"Saved {len(listings)} listings to {filename}")

def main():
    # Example usage
    scraper_manager = RentalScraperManager()
    
    # Search for rentals in a specific location
    listings = scraper_manager.search_all_sites(
        location="Toronto",
        min_price=1000,
        max_price=3000,
        num_bedrooms=2
    )
    
    # Save results
    scraper_manager.save_to_csv(listings)

if __name__ == "__main__":
    main() 