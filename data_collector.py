import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import json
import logging
from datetime import datetime
import time
import random
from typing import List, Dict, Optional
from fake_useragent import UserAgent
import re
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='data_collector.log'
)

class DataCollector:
    def __init__(self):
        self.ua = UserAgent()
        self.collected_data = []
        
    def get_random_delay(self) -> float:
        return random.uniform(2, 5)
    
    async def collect_from_bing_search(self, locations: List[str]) -> List[Dict]:
        """Collect rental listings using Bing search"""
        listings = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(user_agent=self.ua.random)
            page = await context.new_page()
            try:
                for location in locations:
                    # Search for rental listings on multiple platforms
                    search_queries = [
                        f'"{location} rental apartments" site:apartments.com',
                        f'"{location} rental properties" site:zillow.com',
                        f'"{location} apartments for rent" site:rentalfast.ca',
                        f'"{location} rental listings" site:padmapper.com'
                    ]
                    
                    for query in search_queries:
                        try:
                            search_url = f'https://www.bing.com/search?q={query.replace(" ", "+")}'
                            await page.goto(search_url, wait_until='networkidle')
                            await asyncio.sleep(self.get_random_delay())
                            
                            # Click on search results to visit the actual rental sites
                            links = await page.query_selector_all('a[href*="apartments.com"], a[href*="zillow.com"], a[href*="rentalfast.ca"], a[href*="padmapper.com"]')
                            
                            for link in links[:3]:  # Limit to first 3 results per query
                                try:
                                    href = await link.get_attribute('href')
                                    if href and any(domain in href for domain in ['apartments.com', 'zillow.com', 'rentalfast.ca', 'padmapper.com']):
                                        await page.goto(href, wait_until='networkidle')
                                        await asyncio.sleep(self.get_random_delay())
                                        html_content = await page.content()
                                        
                                        # Parse based on the domain
                                        if 'apartments.com' in href:
                                            site_listings = self._parse_apartments_com(html_content, location)
                                        elif 'zillow.com' in href:
                                            site_listings = self._parse_zillow(html_content, location)
                                        elif 'rentalfast.ca' in href:
                                            site_listings = self._parse_rentalfast(html_content, location)
                                        elif 'padmapper.com' in href:
                                            site_listings = self._parse_padmapper(html_content, location)
                                        else:
                                            site_listings = self._parse_generic(html_content, location, href)
                                        
                                        listings.extend(site_listings)
                                except Exception as e:
                                    logging.warning(f"Error processing link {href}: {str(e)}")
                                    continue
                                    
                        except Exception as e:
                            logging.warning(f"Error processing search query '{query}': {str(e)}")
                            continue
                            
            finally:
                await browser.close()
        return listings

    async def collect_from_direct_sites(self, locations: List[str]) -> List[Dict]:
        """Collect from rental sites directly"""
        listings = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(user_agent=self.ua.random)
            page = await context.new_page()
            try:
                for location in locations:
                    # Try different URL patterns for each site
                    site_urls = [
                        (f'https://www.apartments.com/{location.replace(" ", "-").lower()}', 'apartments.com'),
                        (f'https://www.zillow.com/{location.replace(" ", "-").lower()}-rentals/', 'zillow.com'),
                        (f'https://www.rentalfast.ca/search?location={location.replace(" ", "+")}', 'rentalfast.ca'),
                        (f'https://www.padmapper.com/apartments/{location.replace(" ", "-").lower()}', 'padmapper.com')
                    ]
                    
                    for url, site in site_urls:
                        try:
                            await page.goto(url, wait_until='networkidle', timeout=30000)
                            await asyncio.sleep(self.get_random_delay())
                            html_content = await page.content()
                            
                            if site == 'apartments.com':
                                site_listings = self._parse_apartments_com(html_content, location)
                            elif site == 'zillow.com':
                                site_listings = self._parse_zillow(html_content, location)
                            elif site == 'rentalfast.ca':
                                site_listings = self._parse_rentalfast(html_content, location)
                            elif site == 'padmapper.com':
                                site_listings = self._parse_padmapper(html_content, location)
                            
                            listings.extend(site_listings)
                            logging.info(f"Collected {len(site_listings)} listings from {site} for {location}")
                            
                        except Exception as e:
                            logging.warning(f"Error collecting from {site} for {location}: {str(e)}")
                            continue
                            
            finally:
                await browser.close()
        return listings

    def _parse_generic(self, html_content: str, location: str, url: str) -> List[Dict]:
        """Generic parser for any rental site"""
        listings = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Try multiple common selectors
        selectors = [
            '.property-card', '.listing-card', '.apartment-card', '.rental-card',
            '.property-item', '.listing-item', '.apartment-item', '.rental-item',
            '[class*="property"]', '[class*="listing"]', '[class*="apartment"]', '[class*="rental"]'
        ]
        
        for selector in selectors:
            items = soup.select(selector)
            if items:
                for item in items:
                    try:
                        # Try to extract title and price with multiple selectors
                        title = self._extract_text(item, [
                            '.title', '.name', '.property-title', '.listing-title',
                            'h1', 'h2', 'h3', '[class*="title"]', '[class*="name"]'
                        ])
                        
                        price = self._extract_price_from_element(item, [
                            '.price', '.rent', '.property-price', '.listing-price',
                            '[class*="price"]', '[class*="rent"]'
                        ])
                        
                        if title and price:
                            listing = {
                                'id': len(listings) + 1,
                                'title': title,
                                'price': price,
                                'location': location,
                                'amenities': ['Contact for details'],
                                'description': f'Rental property in {location}',
                                'contact': {'name': 'Contact for details', 'phone': 'N/A', 'email': 'N/A'},
                                'source_website': url,
                                'availability_date': datetime.now().strftime('%Y-%m-%d'),
                                'collected_date': datetime.now().isoformat(),
                                'source': 'Generic Parser'
                            }
                            listings.append(listing)
                    except Exception as e:
                        continue
                break  # If we found items with this selector, stop trying others
                
        return listings

    def _extract_text(self, element, selectors: List[str]) -> Optional[str]:
        """Extract text using multiple selectors"""
        for selector in selectors:
            try:
                elem = element.select_one(selector)
                if elem:
                    text = elem.get_text().strip()
                    if text:
                        return text
            except:
                continue
        return None

    def _extract_price_from_element(self, element, selectors: List[str]) -> Optional[int]:
        """Extract price using multiple selectors"""
        for selector in selectors:
            try:
                elem = element.select_one(selector)
                if elem:
                    price_text = elem.get_text().strip()
                    price = self._extract_price(price_text)
                    if price:
                        return price
            except:
                continue
        return None

    def _parse_apartments_com(self, html_content: str, location: str) -> List[Dict]:
        listings = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Try multiple selectors for Apartments.com
        selectors = [
            '.placardContainer',
            '.property-card',
            '.apartment-card',
            '[class*="placard"]',
            '[class*="property"]'
        ]
        
        for selector in selectors:
            items = soup.select(selector)
            if items:
                for item in items:
                    try:
                        title = self._extract_text(item, [
                            '.property-title', '.title', '.name', 'h1', 'h2', 'h3'
                        ])
                        
                        price = self._extract_price_from_element(item, [
                            '.property-rent', '.price', '.rent', '[class*="price"]'
                        ])
                        
                        if title and price:
                            listing = {
                                'id': len(listings) + 1,
                                'title': title,
                                'price': price,
                                'location': location,
                                'amenities': ['Contact for details'],
                                'description': f'Apartment in {location}',
                                'contact': {'name': 'Contact Apartments.com', 'phone': 'N/A', 'email': 'N/A'},
                                'source_website': 'https://www.apartments.com',
                                'availability_date': datetime.now().strftime('%Y-%m-%d'),
                                'collected_date': datetime.now().isoformat(),
                                'source': 'Apartments.com'
                            }
                            listings.append(listing)
                    except Exception as e:
                        continue
                break
        return listings

    def _parse_padmapper(self, html_content: str, location: str) -> List[Dict]:
        listings = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        selectors = [
            '.listing-card',
            '.property-card',
            '.apartment-card',
            '[class*="listing"]',
            '[class*="property"]'
        ]
        
        for selector in selectors:
            items = soup.select(selector)
            if items:
                for item in items:
                    try:
                        title = self._extract_text(item, [
                            '.listing-title', '.title', '.name', 'h1', 'h2', 'h3'
                        ])
                        
                        price = self._extract_price_from_element(item, [
                            '.listing-price', '.price', '.rent', '[class*="price"]'
                        ])
                        
                        if title and price:
                            listing = {
                                'id': len(listings) + 1,
                                'title': title,
                                'price': price,
                                'location': location,
                                'amenities': ['Contact for details'],
                                'description': f'Rental in {location}',
                                'contact': {'name': 'Contact PadMapper', 'phone': 'N/A', 'email': 'N/A'},
                                'source_website': 'https://www.padmapper.com',
                                'availability_date': datetime.now().strftime('%Y-%m-%d'),
                                'collected_date': datetime.now().isoformat(),
                                'source': 'PadMapper'
                            }
                            listings.append(listing)
                    except Exception as e:
                        continue
                break
        return listings

    def _parse_rentalfast(self, html_content: str, location: str) -> List[Dict]:
        listings = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        selectors = [
            '.property-card',
            '.listing-card',
            '.apartment-card',
            '[class*="property"]',
            '[class*="listing"]'
        ]
        
        for selector in selectors:
            items = soup.select(selector)
            if items:
                for item in items:
                    try:
                        title = self._extract_text(item, [
                            '.property-title', '.title', '.name', 'h1', 'h2', 'h3'
                        ])
                        
                        price = self._extract_price_from_element(item, [
                            '.property-price', '.price', '.rent', '[class*="price"]'
                        ])
                        
                        if title and price:
                            listing = {
                                'id': len(listings) + 1,
                                'title': title,
                                'price': price,
                                'location': location,
                                'amenities': ['Contact for details'],
                                'description': f'Rental property in {location}',
                                'contact': {'name': 'Contact RentalFast', 'phone': 'N/A', 'email': 'N/A'},
                                'source_website': 'https://www.rentalfast.ca',
                                'availability_date': datetime.now().strftime('%Y-%m-%d'),
                                'collected_date': datetime.now().isoformat(),
                                'source': 'RentalFast'
                            }
                            listings.append(listing)
                    except Exception as e:
                        continue
                break
        return listings

    def _parse_zillow(self, html_content: str, location: str) -> List[Dict]:
        listings = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        selectors = [
            '.property-card',
            '.listing-card',
            '.apartment-card',
            '[class*="property"]',
            '[class*="listing"]'
        ]
        
        for selector in selectors:
            items = soup.select(selector)
            if items:
                for item in items:
                    try:
                        title = self._extract_text(item, [
                            '.property-title', '.title', '.name', 'h1', 'h2', 'h3'
                        ])
                        
                        price = self._extract_price_from_element(item, [
                            '.property-price', '.price', '.rent', '[class*="price"]'
                        ])
                        
                        if title and price:
                            listing = {
                                'id': len(listings) + 1,
                                'title': title,
                                'price': price,
                                'location': location,
                                'amenities': ['Contact for details'],
                                'description': f'Rental property in {location}',
                                'contact': {'name': 'Contact Zillow', 'phone': 'N/A', 'email': 'N/A'},
                                'source_website': 'https://www.zillow.com',
                                'availability_date': datetime.now().strftime('%Y-%m-%d'),
                                'collected_date': datetime.now().isoformat(),
                                'source': 'Zillow'
                            }
                            listings.append(listing)
                    except Exception as e:
                        continue
                break
        return listings
    
    def _extract_price(self, price_text: str) -> Optional[int]:
        if not price_text: return None
        # Remove all non-digit characters except decimal points
        cleaned = re.sub(r'[^\d.]', '', price_text)
        try:
            # Convert to float first, then to int
            price_float = float(cleaned)
            return int(price_float)
        except (ValueError, TypeError):
            return None
    
    async def collect_all_data(self, locations: List[str]) -> List[Dict]:
        all_listings = []
        print(f'Starting data collection for locations: {locations}')
        
        # Try both methods: direct site access and Bing search
        methods = [
            ('Direct Site Access', self.collect_from_direct_sites),
            ('Bing Search', self.collect_from_bing_search)
        ]
        
        for method_name, collection_method in methods:
            try:
                print(f'Collecting using {method_name}...')
                listings = await collection_method(locations)
                all_listings.extend(listings)
                print(f'Collected {len(listings)} listings using {method_name}')
            except Exception as e:
                print(f'Error with {method_name}: {str(e)}')
                continue
        
        unique_listings = self._remove_duplicates(all_listings)
        print(f'Total unique listings collected: {len(unique_listings)}')
        return unique_listings
    
    def _remove_duplicates(self, listings: List[Dict]) -> List[Dict]:
        seen = set()
        unique_listings = []
        for listing in listings:
            key = (listing.get('title', '').lower(), listing.get('location', '').lower())
            if key not in seen:
                seen.add(key)
                unique_listings.append(listing)
        return unique_listings
    
    def save_to_file(self, listings: List[Dict], filename: str = 'houseAds.txt'):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for listing in listings:
                    f.write(json.dumps(listing, ensure_ascii=False) + '\n')
            print(f'Saved {len(listings)} listings to {filename}')
        except Exception as e:
            print(f'Error saving to file: {str(e)}')

async def main():
    collector = DataCollector()
    locations = ['Toronto', 'New York', 'San Francisco']
    listings = await collector.collect_all_data(locations)
    collector.save_to_file(listings)
    print(f'Data collection complete! Collected {len(listings)} unique listings.')

if __name__ == '__main__':
    asyncio.run(main())
