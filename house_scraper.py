import asyncio
from playwright.async_api import async_playwright
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

class IntelligentFilter:
    """Intelligent filter that adapts to different website structures."""
    
    def __init__(self):
        # Common variations for different filter types
        self.bedroom_keywords = [
            'bedroom', 'bedrooms', 'beds', 'bed', 'br', 'brs',
            'sleeping', 'room', 'rooms', 'studio'
        ]
        
        self.price_keywords = [
            'price', 'rent', 'cost', 'rate', 'monthly', 'per month',
            'min', 'max', 'from', 'to', 'range', 'budget'
        ]
        
        self.amenity_keywords = [
            'amenity', 'amenities', 'feature', 'features', 'included',
            'facility', 'facilities', 'perk', 'perks', 'bonus'
        ]
        
        self.location_keywords = [
            'location', 'address', 'area', 'neighborhood', 'district',
            'city', 'town', 'region', 'zone', 'vicinity'
        ]
    
    def find_filter_elements(self, page_content: str, filter_type: str) -> List[Dict]:
        """Find filter elements on the page based on keywords."""
        soup = BeautifulSoup(page_content, 'html.parser')
        elements = []
        
        if filter_type == 'bedrooms':
            keywords = self.bedroom_keywords
        elif filter_type == 'price':
            keywords = self.price_keywords
        elif filter_type == 'amenities':
            keywords = self.amenity_keywords
        elif filter_type == 'location':
            keywords = self.location_keywords
        else:
            return elements
        
        # Search for elements containing these keywords
        for keyword in keywords:
            # Find elements by text content
            text_elements = soup.find_all(text=re.compile(keyword, re.IGNORECASE))
            for elem in text_elements:
                parent = elem.parent
                if parent and parent.name:
                    elements.append({
                        'element': parent,
                        'keyword': keyword,
                        'text': elem.strip(),
                        'tag': parent.name,
                        'classes': parent.get('class', []),
                        'id': parent.get('id', ''),
                        'name': parent.get('name', '')
                    })
            
            # Find elements by attribute values
            attr_elements = soup.find_all(attrs={
                'class': re.compile(keyword, re.IGNORECASE)
            })
            for elem in attr_elements:
                elements.append({
                    'element': elem,
                    'keyword': keyword,
                    'text': elem.get_text().strip(),
                    'tag': elem.name,
                    'classes': elem.get('class', []),
                    'id': elem.get('id', ''),
                    'name': elem.get('name', '')
                })
        
        return elements
    
    def extract_numeric_value(self, text: str) -> Optional[int]:
        """Extract numeric value from text."""
        if not text:
            return None
        
        # Remove common non-numeric characters and extract numbers
        cleaned = re.sub(r'[^\d]', '', text)
        if cleaned:
            return int(cleaned)
        return None
    
    async def apply_intelligent_filters(self, page, filter_type: str, value, **kwargs):
        """Apply filters intelligently based on detected elements."""
        try:
            page_content = await page.content()
            elements = self.find_filter_elements(page_content, filter_type)
            
            if not elements:
                logging.warning(f"No {filter_type} filter elements found")
                return False
            
            # Sort elements by relevance (more specific keywords first)
            elements.sort(key=lambda x: len(x['keyword']), reverse=True)
            
            for elem_info in elements:
                element = elem_info['element']
                
                if filter_type == 'bedrooms':
                    success = await self._apply_bedroom_filter(page, element, value, elem_info)
                elif filter_type == 'price':
                    success = await self._apply_price_filter(page, element, value, elem_info, **kwargs)
                elif filter_type == 'amenities':
                    success = await self._apply_amenity_filter(page, element, value, elem_info)
                else:
                    continue
                
                if success:
                    logging.info(f"Successfully applied {filter_type} filter using {elem_info['keyword']}")
                    return True
            
            return False
            
        except Exception as e:
            logging.error(f"Error applying {filter_type} filter: {str(e)}")
            return False
    
    async def _apply_bedroom_filter(self, page, element, value, elem_info):
        """Apply bedroom filter intelligently."""
        try:
            # Try different approaches to set the value
            if element.name == 'select':
                # Find option with matching value
                options = element.find_all('option')
                for option in options:
                    option_text = option.get_text().strip().lower()
                    option_value = option.get('value', '')
                    
                    if (str(value) in option_text or 
                        str(value) in option_value or
                        any(keyword in option_text for keyword in self.bedroom_keywords if str(value) in option_text)):
                        await page.select_option(f"#{element.get('id')}", option_value)
                        return True
            
            elif element.name == 'input':
                # Try to fill the input
                input_id = element.get('id', '')
                input_name = element.get('name', '')
                
                if input_id:
                    await page.fill(f"#{input_id}", str(value))
                    return True
                elif input_name:
                    await page.fill(f"[name='{input_name}']", str(value))
                    return True
            
            return False
            
        except Exception as e:
            logging.error(f"Error applying bedroom filter: {str(e)}")
            return False
    
    async def _apply_price_filter(self, page, element, value, elem_info, **kwargs):
        """Apply price filter intelligently."""
        try:
            price_type = kwargs.get('price_type', 'min')  # 'min' or 'max'
            
            if element.name == 'input':
                input_id = element.get('id', '')
                input_name = element.get('name', '')
                input_placeholder = element.get('placeholder', '').lower()
                
                # Check if this is the right type of price input
                is_min_input = any(word in input_placeholder for word in ['min', 'from', 'low'])
                is_max_input = any(word in input_placeholder for word in ['max', 'to', 'high'])
                
                if (price_type == 'min' and is_min_input) or (price_type == 'max' and is_max_input):
                    if input_id:
                        await page.fill(f"#{input_id}", str(value))
                        return True
                    elif input_name:
                        await page.fill(f"[name='{input_name}']", str(value))
                        return True
            
            return False
            
        except Exception as e:
            logging.error(f"Error applying price filter: {str(e)}")
            return False
    
    async def _apply_amenity_filter(self, page, element, value, elem_info):
        """Apply amenity filter intelligently."""
        try:
            if element.name == 'input' and element.get('type') == 'checkbox':
                # Check if this checkbox matches the amenity
                checkbox_text = element.get_text().strip().lower()
                checkbox_id = element.get('id', '')
                checkbox_name = element.get('name', '')
                
                if any(amenity.lower() in checkbox_text for amenity in value):
                    if checkbox_id:
                        await page.check(f"#{checkbox_id}")
                        return True
                    elif checkbox_name:
                        await page.check(f"[name='{checkbox_name}']")
                        return True
            
            return False
            
        except Exception as e:
            logging.error(f"Error applying amenity filter: {str(e)}")
            return False

class BaseScraper:
    def __init__(self):
        self.ua = UserAgent()
        self.intelligent_filter = IntelligentFilter()
        
    def get_random_delay(self) -> float:
        """Generate a random delay between requests."""
        return random.uniform(3, 7)  # Increased delay for commercial use
        
    async def get_page_content(self, url: str, wait_for_selector: str = None) -> str:
        """Get page content using Playwright with JavaScript rendering."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=self.ua.random,
                viewport={'width': 1920, 'height': 1080}
            )
            page = await context.new_page()
            
            try:
                # Set additional headers
                await page.set_extra_http_headers({
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                })
                
                # Navigate to the page
                await page.goto(url, wait_until='networkidle')
                
                # Wait for specific selector if provided
                if wait_for_selector:
                    await page.wait_for_selector(wait_for_selector, timeout=10000)
                
                # Add random delay
                await asyncio.sleep(self.get_random_delay())
                
                # Get the rendered content
                content = await page.content()
                return content
                
            except Exception as e:
                logging.error(f"Error getting page content: {str(e)}")
                log_scraper_error(str(e))
                return ""
            finally:
                await browser.close()
    
    async def apply_intelligent_filters(self, page, min_price=None, max_price=None, num_bedrooms=None, **kwargs):
        """Apply filters intelligently to the page."""
        try:
            # Apply bedroom filter
            if num_bedrooms:
                await self.intelligent_filter.apply_intelligent_filters(
                    page, 'bedrooms', num_bedrooms
                )
            
            # Apply price filters
            if min_price:
                await self.intelligent_filter.apply_intelligent_filters(
                    page, 'price', min_price, price_type='min'
                )
            
            if max_price:
                await self.intelligent_filter.apply_intelligent_filters(
                    page, 'price', max_price, price_type='max'
                )
            
            # Wait for filters to take effect
            await asyncio.sleep(2)
            
        except Exception as e:
            logging.error(f"Error applying intelligent filters: {str(e)}")


class ZillowScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.zillow.com"
        
    async def search_rentals(self, location: str, min_price=None, max_price=None, num_bedrooms=None, **kwargs) -> List[Dict]:
        """Search Zillow rentals with intelligent filtering."""
        try:
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
            
            # For API calls, we can still use requests-like approach with Playwright
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent=self.ua.random,
                    viewport={'width': 1920, 'height': 1080}
                )
                page = await context.new_page()
                
                try:
                    # Set headers
                    await page.set_extra_http_headers({
                        'Accept': 'application/json',
                        'Content-Type': 'application/json',
                    })
                    
                    # Make the API request
                    full_url = f"{search_url}?{urlencode(params)}"
                    response = await page.goto(full_url, wait_until='networkidle')
                    
                    if response.status == 200:
                        data = await response.json()
                        listings = self._parse_zillow_response(data)
                        return listings
                    else:
                        logging.error(f"Zillow API returned status {response.status}")
                        return []
                        
                except Exception as e:
                    logging.error(f"Error with Zillow API request: {str(e)}")
                    return []
                finally:
                    await browser.close()
                    
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

class ApartmentsScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.apartments.com"
        
    async def search_rentals(self, location: str, min_price=None, max_price=None, num_bedrooms=None, **kwargs) -> List[Dict]:
        """Search Apartments.com listings with intelligent filtering."""
        try:
            search_url = f"{self.base_url}/{location.replace(' ', '-').lower()}"
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent=self.ua.random,
                    viewport={'width': 1920, 'height': 1080}
                )
                page = await context.new_page()
                
                try:
                    # Set headers
                    await page.set_extra_http_headers({
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                    })
                    
                    # Navigate to the page
                    await page.goto(search_url, wait_until='networkidle')
                    
                    # Wait for content to load
                    await page.wait_for_selector('.placardContainer', timeout=10000)
                    
                    # Apply intelligent filters
                    await self.apply_intelligent_filters(page, min_price, max_price, num_bedrooms)
                    
                    # Wait for filters to take effect
                    await asyncio.sleep(3)
                    
                    # Get the filtered content
                    html_content = await page.content()
                    
                    listings = self._parse_apartments_response(html_content)
                    return listings
                    
                except Exception as e:
                    logging.error(f"Error with Apartments.com scraping: {str(e)}")
                    return []
                finally:
                    await browser.close()
                    
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
                try:
                    title_elem = item.select_one('.property-title')
                    price_elem = item.select_one('.property-rent')
                    location_elem = item.select_one('.property-address')
                    link_elem = item.select_one('a')
                    
                    if title_elem and price_elem and location_elem and link_elem:
                        listing = {
                            'source': 'Apartments.com',
                            'title': title_elem.text.strip(),
                            'price': price_elem.text.strip(),
                            'location': location_elem.text.strip(),
                            'url': f"{self.base_url}{link_elem['href']}",
                            'scraped_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        listings.append(listing)
                except Exception as e:
                    logging.error(f"Error parsing individual listing: {str(e)}")
                    continue
        except Exception as e:
            logging.error(f"Error parsing Apartments.com response: {str(e)}")
            log_scraper_error(str(e))
        return listings

class PadMapperScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.padmapper.com"
        
    async def search_rentals(self, location: str, min_price=None, max_price=None, num_bedrooms=None, **kwargs) -> List[Dict]:
        """Search PadMapper listings with intelligent filtering."""
        try:
            search_url = f"{self.base_url}/apartments/{location.replace(' ', '-').lower()}"
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent=self.ua.random,
                    viewport={'width': 1920, 'height': 1080}
                )
                page = await context.new_page()
                
                try:
                    # Set headers
                    await page.set_extra_http_headers({
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                    })
                    
                    # Navigate to the page
                    await page.goto(search_url, wait_until='networkidle')
                    
                    # Wait for content to load
                    await page.wait_for_selector('.listing-card', timeout=10000)
                    
                    # Apply intelligent filters
                    await self.apply_intelligent_filters(page, min_price, max_price, num_bedrooms)
                    
                    # Wait for filters to take effect
                    await asyncio.sleep(3)
                    
                    # Get the filtered content
                    html_content = await page.content()
                    
                    listings = self._parse_padmapper_response(html_content)
                    return listings
                    
                except Exception as e:
                    logging.error(f"Error with PadMapper scraping: {str(e)}")
                    return []
                finally:
                    await browser.close()
                    
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
                try:
                    title_elem = item.select_one('.listing-title')
                    price_elem = item.select_one('.listing-price')
                    location_elem = item.select_one('.listing-location')
                    link_elem = item.select_one('a')
                    
                    if title_elem and price_elem and location_elem and link_elem:
                        listing = {
                            'source': 'PadMapper',
                            'title': title_elem.text.strip(),
                            'price': price_elem.text.strip(),
                            'location': location_elem.text.strip(),
                            'url': f"{self.base_url}{link_elem['href']}",
                            'scraped_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        listings.append(listing)
                except Exception as e:
                    logging.error(f"Error parsing individual listing: {str(e)}")
                    continue
        except Exception as e:
            logging.error(f"Error parsing PadMapper response: {str(e)}")
            log_scraper_error(str(e))
        return listings

class KijijiScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.kijiji.ca"
        
    async def search_rentals(self, location: str, min_price=None, max_price=None, num_bedrooms=None, **kwargs) -> List[Dict]:
        """Search Kijiji listings with intelligent filtering."""
        try:
            search_url = f"{self.base_url}/b-apartments-condos/{location}/c37l1700272"
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent=self.ua.random,
                    viewport={'width': 1920, 'height': 1080}
                )
                page = await context.new_page()
                
                try:
                    # Set headers
                    await page.set_extra_http_headers({
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                    })
                    
                    # Navigate to the page
                    await page.goto(search_url, wait_until='networkidle')
                    
                    # Wait for content to load
                    await page.wait_for_selector('.search-item', timeout=10000)
                    
                    # Apply intelligent filters
                    await self.apply_intelligent_filters(page, min_price, max_price, num_bedrooms)
                    
                    # Wait for filters to take effect
                    await asyncio.sleep(3)
                    
                    # Get the filtered content
                    html_content = await page.content()
                    
                    listings = self._parse_kijiji_response(html_content)
                    return listings
                    
                except Exception as e:
                    logging.error(f"Error with Kijiji scraping: {str(e)}")
                    return []
                finally:
                    await browser.close()
                    
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
                try:
                    title_elem = item.select_one('.title')
                    price_elem = item.select_one('.price')
                    location_elem = item.select_one('.location')
                    link_elem = item.select_one('a')
                    
                    if title_elem and price_elem and location_elem and link_elem:
                        listing = {
                            'source': 'Kijiji',
                            'title': title_elem.text.strip(),
                            'price': price_elem.text.strip(),
                            'location': location_elem.text.strip(),
                            'url': f"{self.base_url}{link_elem['href']}",
                            'scraped_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        listings.append(listing)
                except Exception as e:
                    logging.error(f"Error parsing individual listing: {str(e)}")
                    continue
        except Exception as e:
            logging.error(f"Error parsing Kijiji response: {str(e)}")
            log_scraper_error(str(e))
        return listings

class RentalScraperManager:
    def __init__(self):
        self.scrapers = {
            # 'zillow': ZillowScraper(),  # REMOVED due to API issues
            'apartments': ApartmentsScraper(),
            'padmapper': PadMapperScraper(),
            'kijiji': KijijiScraper()
        }

    async def search_all_sites(self, location: str, min_price=None, max_price=None, num_bedrooms=None, **kwargs) -> List[Dict]:
        """Search all supported sites for rental listings with intelligent filtering."""
        all_listings = []

        print(f"\n[INFO] Searching listings for location: {location}")
        print(f"[INFO] Filters -> Price: {min_price}-{max_price}, Beds: {num_bedrooms}\n")

        for site_name, scraper in self.scrapers.items():
            try:
                print(f"[DEBUG] Scraping from: {site_name}")
                listings = await scraper.search_rentals(
                    location,
                    min_price=min_price,
                    max_price=max_price,
                    num_bedrooms=num_bedrooms
                )
                print(f"[DEBUG] {site_name} returned {len(listings)} listings.")
                all_listings.extend(listings)
            except Exception as e:
                logging.error(f"Error searching {site_name}: {str(e)}")
                log_scraper_error(str(e))
                print(f"[ERROR] Failed scraping from {site_name}: {str(e)}")
                continue

        print(f"\n[INFO] Total listings collected: {len(all_listings)}\n")
        return all_listings

    def save_to_csv(self, listings: List[Dict], filename: str = 'rental_listings.csv'):
        """Save the scraped listings to a CSV file."""
        if not listings:
            logging.warning("No listings to save")
            print("[WARN] No listings to save.")
            return

        df = pd.DataFrame(listings)
        df.to_csv(filename, index=False)
        logging.info(f"Saved {len(listings)} listings to {filename}")
        print(f"[INFO] Saved {len(listings)} listings to {filename}")

async def main():
    # Example usage
    scraper_manager = RentalScraperManager()
    
    # Search for rentals in a specific location
    listings = await scraper_manager.search_all_sites(
        location="Toronto",
        min_price=1000,
        max_price=3000,
        num_bedrooms=2
    )
    
    # Save results
    scraper_manager.save_to_csv(listings)

if __name__ == "__main__":
    asyncio.run(main()) 