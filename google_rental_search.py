#!/usr/bin/env python3
"""
Google Custom Search API Integration for Rental Listings
This module provides functionality to search for rental listings using Google Custom Search API.
"""

import requests
import json
import logging
import os
import re
from datetime import datetime
from typing import List, Optional, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleRentalSearch1:
    def __init__(self):
        """Initialize Google Custom Search API client."""
        self.api_key = os.getenv('GOOGLE_API_KEY')
        self.search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
        self.api_url = 'https://www.googleapis.com/customsearch/v1'
        
        if not self.api_key or not self.search_engine_id:
            logger.warning("Google Custom Search API not properly configured. Set GOOGLE_API_KEY and GOOGLE_SEARCH_ENGINE_ID environment variables.")

    def search_rentals(self, location: str, min_price: Optional[int] = None, 
                      max_price: Optional[int] = None, bedrooms: Optional[int] = None,
                      amenities: Optional[List[str]] = None, lifestyle: Optional[str] = None) -> List[Dict]:
        """
        Search for rental listings using Google Custom Search API.
        """
        if not self.api_key or not self.search_engine_id:
            logger.error("Google Custom Search API not properly configured")
            return []

        try:
            # Build search query
            query = self._build_search_query1(location, min_price, max_price, bedrooms, amenities, lifestyle)
            
            # If query is empty (invalid location), return empty results
            if not query or len(query.strip()) == 0:
                logger.warning(f"Invalid location '{location}' provided. Returning empty results.")
                return []
            
            logger.info(f"Searching Google Custom Search with query: {query}")

            # Prepare the API request
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': query,
                'num': 10,  # Number of results
                'safe': 'active',
                'lr': 'lang_en',  # Language restriction
                'sort': 'date'  # Sort by date (most recent first)
            }

            # Validate parameters before making request
            for key, value in params.items():
                if value is None or (isinstance(value, str) and len(value.strip()) == 0):
                    logger.error(f"Invalid parameter {key}: {value}")
                    return []

            # Make API request
            response = requests.get(
                self.api_url,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                self._save_response_to_file(result)
                listings = self._parse_google_response(result, location)
                
                logger.info(f"Found {len(listings)} rental listings with Google Custom Search")
                
                # Save the complete search results
                if listings:
                    self._save_search_results(result, location, listings)
                
                return listings
            else:
                logger.error(f"API request failed with status {response.status_code}: {response.text}")
                return []

        except Exception as e:
            logger.error(f"Error searching rentals: {e}")
            return []

    def _save_response_to_file(self, response_data: Dict):
        """Save the full Google Custom Search JSON response to a file for debugging."""
        try:
            results_dir = 'results'
            os.makedirs(results_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(results_dir, f'google_custom_search_response_{timestamp}.json')
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(response_data, f, ensure_ascii=False, indent=4)
            
            logger.info(f"Successfully saved Google Custom Search response to {file_path}")

        except Exception as e:
            logger.error(f"Error saving Google Custom Search response to file: {e}")

    def _build_search_query1(self, location: str, min_price: Optional[int] = None,
                           max_price: Optional[int] = None, bedrooms: Optional[int] = None,
                           amenities: Optional[List[str]] = None, lifestyle: Optional[str] = None) -> str:
        """Build a search query for rental listings."""
        # Define the sites to search
        target_sites = [
            "apartments.com",
            "zillow.com",
            "padmapper.com",
            "kijiji.ca"
        ]
        site_query = " OR ".join([f"site:{site}" for site in target_sites])
        
        # Validate location - if it's not a proper city name, return empty query
        if not location or not self._is_valid_city_name(location):
            logger.warning(f"Invalid location provided: '{location}'. Location must be a valid city name.")
            return ""  # Return empty query to get no results
        
        # Build query parts
        query_parts = [f"rental apartments {location}", f"({site_query})"]
        
        # Add price filters
        if min_price and max_price:
            query_parts.append(f'"${min_price}..${max_price}"')
        elif min_price:
            query_parts.append(f'price > ${min_price}')
        elif max_price:
            query_parts.append(f'price < ${max_price}')
        
        # Add bedroom filter
        if bedrooms:
            bedroom_terms = [f'"{bedrooms} bedroom"', f'"{bedrooms} bed"']
            query_parts.append(f"({' AND '.join(bedroom_terms)})")
        
        # Add amenities filter
        if amenities:
            amenities_text = ' OR '.join([f'"{amenity}"' for amenity in amenities[:3]])
            query_parts.append(f"({amenities_text})")
            
        # Add lifestyle filter
        if lifestyle:
            if isinstance(lifestyle, list):
                # Handle list of lifestyle keywords
                lifestyle_terms = [f'"{keyword}"' for keyword in lifestyle[:3]]  # Limit to 3 keywords
                query_parts.append(f"({' OR '.join(lifestyle_terms)})")
            else:
                # Handle single lifestyle string (backward compatibility)
                query_parts.append(f'"{lifestyle}"')
        
        # Join and clean the query
        query = " ".join(query_parts)
        return " ".join(query.split())  # Remove extra whitespace

    def _is_valid_city_name(self, location: str) -> bool:
        """Validate if the location is a proper city name."""
        if not location or not location.strip():
            return False
        
        location = location.strip()
        
        # Reject if it's just a number (like "2300")
        if location.isdigit():
            return False
        
        # Reject if it starts with $ and is followed by numbers (like "$2300")
        if location.startswith('$') and location[1:].isdigit():
            return False
        
        # Reject if it's too short (likely not a city name)
        if len(location) <= 2:
            return False
        
        # Reject if it contains only numbers and special characters
        if not any(c.isalpha() for c in location):
            return False
        
        # Reject common non-city terms
        invalid_terms = ['price', 'rent', 'apartment', 'house', 'bedroom', 'bathroom', 'sqft', 'sq ft']
        location_lower = location.lower()
        if any(term in location_lower for term in invalid_terms):
            return False
        
        return True

    def _parse_google_response(self, response: Dict, location: str) -> List[Dict]:
        """Parse Google Custom Search response into structured rental listings."""
        listings = []
        
        try:
            # Extract search results
            if 'items' in response:
                for i, item in enumerate(response['items']):
                    listing = self._extract_listing_from_item(item, location, i + 1)
                    if listing:
                        listings.append(listing)
                        
            # Save the complete search results
            if listings:
                self._save_search_results(response, location, listings)
                    
        except Exception as e:
            logger.error(f"Error parsing Google Custom Search response: {e}")
            listings = []

        return listings

    def _extract_listing_from_item(self, item: Dict, location: str, index: int) -> Optional[Dict]:
        """Extract rental listing information from a Google search result item."""
        try:
            title = item.get('title', '')
            link = item.get('link', '')
            snippet = item.get('snippet', '')
            pagemap = item.get('pagemap', {})

            # --- Start: Quality Gates ---
            
            # Gate 1: Skip listings that are clearly off-market or unavailable
            off_market_keywords = ['off-market', 'no longer available', 'not for rent', 'rental history']
            full_text_lower = (title + " " + snippet).lower()
            if any(keyword in full_text_lower for keyword in off_market_keywords):
                logger.info(f"Skipping off-market listing: {title}")
                return None

            # Gate 2: Skip pages that are search results, not individual listings
            title_lower = title.lower()
            
            # Pattern for generic search phrases like "Apartments for Rent"
            generic_patterns = [
                r'apartments\s+for\s+rent',
                r'condos\s+for\s+rent',
                r'homes\s+for\s+rent',
                r'houses\s+for\s+rent',
                r'rentals\s+in\s+'
            ]
            
            # Pattern to identify a specific street address (to protect real listings)
            address_pattern = r'\d+\s+[a-z0-9\s]+(st|street|ave|avenue|rd|road|blvd|dr|ln|ct)\b'
            
            is_generic = any(re.search(p, title_lower) for p in generic_patterns)
            has_address = re.search(address_pattern, title_lower)
            
            # If the title looks generic AND does NOT have a specific address, skip it.
            if is_generic and not has_address:
                logger.info(f"Skipping search results page (generic title): {title}")
                return None

            # Also, check for titles that list a large number of rentals
            if re.search(r'^\d{1,3}(,\d{3})*\s+rentals', title_lower):
                logger.info(f"Skipping search results page (lists rentals): {title}")
                return None

            if re.search(r'rentals\s+from\s+c?\$', title_lower):
                logger.info(f"Skipping search results page (rentals from...): {title}")
                return None
            
            # --- End: Quality Gates ---

            # --- Start: Data Extraction ---
            
            price = None
            bedrooms = None
            bathrooms = None
            amenities = []
            description = snippet
            listing_url = link  # Default to the main link

            # Prioritize structured data from pagemap for accuracy
            offer_data = pagemap.get('offer', [{}])[0]
            product_data = pagemap.get('product', [{}])[0]
            apartment_data = pagemap.get('apartment', [{}])[0]
            metatags = pagemap.get('metatags', [{}])[0]
            event_data = pagemap.get('event', [{}])[0]

            # 1. Find the best URL
            if 'url' in offer_data:
                listing_url = offer_data['url']
            elif 'og:url' in metatags:
                listing_url = metatags['og:url']
            elif 'url' in event_data:
                listing_url = event_data['url']

            # 2. Extract price from structured data
            if 'price' in offer_data:
                price = self._extract_price_from_text(f"${offer_data['price']}")
            elif 'price' in product_data:
                price = self._extract_price_from_text(f"${product_data['price']}")

            # 3. Extract bedrooms/bathrooms from structured data
            if 'numberofbedrooms' in apartment_data:
                bedrooms = apartment_data['numberofbedrooms']
            if 'numberofbathrooms' in apartment_data:
                bathrooms = apartment_data['numberofbathrooms']

            # --- Fallback to parsing text if structured data is incomplete ---
            
            if price is None:
                price = self._extract_price_from_text(full_text_lower)
            
            if bedrooms is None:
                bedrooms = self._extract_bedrooms_from_text(full_text_lower)

            if bathrooms is None:
                bathrooms = self._extract_bathrooms_from_text(full_text_lower)
            
            amenities = self._extract_amenities_from_text(full_text_lower)
            
            # --- End: Data Extraction ---

            source_website = self._extract_source_website(link)
            match_percentage = self._calculate_match_percentage(title, snippet, location)
            contact = self._extract_contact_info(snippet)
            
            listing = {
                'id': index,
                'title': title,
                'price': price,
                'location': location,
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'amenities': amenities,
                'description': description,
                'match_percentage': match_percentage,
                'contact': contact,
                'source_website': source_website,
                'listing_url': listing_url, # Use the more specific URL
                'availability_date': datetime.now().strftime('%Y-%m-%d'),
                'features': [],
                'images': []
            }
            
            return listing
            
        except Exception as e:
            logger.error(f"Error extracting listing from item: {e}")
            return None

    def _extract_price_from_text(self, text: str) -> Optional[int]:
        """Extract price from text."""
        # Look for price patterns like $1500, $1,500, $1500/month, etc.
        price_patterns = [
            r'\$([0-9,]+)(?:\s*\/\s*month)?',
            r'([0-9,]+)\s*\/\s*month',
            r'rent\s*\$([0-9,]+)',
            r'\$([0-9,]+)\s*rent',
            r'for\s*\$([0-9,]+)',  # "for $1500"
            r'at\s*\$([0-9,]+)',   # "at $1500"
            r'listed\s*at\s*\$([0-9,]+)',  # "listed at $1500"
            r'price\s*\$([0-9,]+)',  # "price $1500"
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    # Remove commas and convert to integer
                    price_str = match.group(1).replace(',', '')
                    price = int(price_str)
                    
                    # Validate reasonable price range (between $500 and $10,000)
                    if 500 <= price <= 10000:
                        return price
                except (ValueError, IndexError):
                    continue
        
        return None

    def _extract_bedrooms_from_text(self, text: str) -> Optional[int]:
        """Extract number of bedrooms from text."""
        # Look for bedroom patterns
        bedroom_patterns = [
            r'(\d+)\s*bedroom',
            r'(\d+)\s*br\b',
            r'(\d+)\s*bed',
            r'(\d+)\s*bedroom\s*apartment',
            r'(\d+)\s*bedroom\s*unit',
        ]
        
        for pattern in bedroom_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    bedrooms = int(match.group(1))
                    # Validate reasonable range (1-10 bedrooms)
                    if 1 <= bedrooms <= 10:
                        return bedrooms
                except (ValueError, IndexError):
                    continue
        
        # Try to extract from bed/bath format like "2 bed, 1 bath"
        bed_bath_match = self._extract_from_bed_bath_format(text)
        if bed_bath_match and bed_bath_match.get('bedrooms'):
            return bed_bath_match['bedrooms']
        
        return None

    def _extract_bathrooms_from_text(self, text: str) -> Optional[int]:
        """Extract number of bathrooms from text."""
        # Look for bathroom patterns
        bathroom_patterns = [
            r'(\d+)\s*bathroom',
            r'(\d+)\s*ba\b',
            r'(\d+)\s*bath',
            r'(\d+)\s*full\s*bath',
            r'(\d+)\s*half\s*bath',
        ]
        
        for pattern in bathroom_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    bathrooms = int(match.group(1))
                    # Validate reasonable range (1-10 bathrooms)
                    if 1 <= bathrooms <= 10:
                        return bathrooms
                except (ValueError, IndexError):
                    continue
        
        # Try to extract from bed/bath format like "2 bed, 1 bath"
        bed_bath_match = self._extract_from_bed_bath_format(text)
        if bed_bath_match and bed_bath_match.get('bathrooms'):
            return bed_bath_match['bathrooms']
        
        return None

    def _extract_from_bed_bath_format(self, text: str) -> Optional[Dict]:
        """Extract bedrooms and bathrooms from common formats like '2 bed, 1 bath'."""
        # Pattern for "X bed, Y bath" format
        pattern = r'(\d+)\s*bed[,\s]+(\d+)\s*bath'
        match = re.search(pattern, text, re.IGNORECASE)
        
        if match:
            try:
                bedrooms = int(match.group(1))
                bathrooms = int(match.group(2))
                
                # Validate reasonable ranges
                if 1 <= bedrooms <= 10 and 1 <= bathrooms <= 10:
                    return {'bedrooms': bedrooms, 'bathrooms': bathrooms}
            except (ValueError, IndexError):
                pass
        
        return None

    def _extract_amenities_from_text(self, text: str) -> List[str]:
        """Extract amenities from text."""
        amenities = []
        
        # Common amenities to look for
        amenity_keywords = [
            'parking', 'gym', 'pool', 'washer', 'dryer', 'dishwasher', 'balcony',
            'air conditioning', 'heating', 'furnished', 'unfurnished', 'pet friendly',
            'no pets', 'elevator', 'doorman', 'security', 'storage', 'parking',
            'garage', 'outdoor space', 'rooftop', 'terrace', 'garden', 'fireplace',
            'hardwood floors', 'carpet', 'central air', 'window ac', 'utilities included'
        ]
        
        text_lower = text.lower()
        for amenity in amenity_keywords:
            if amenity in text_lower:
                amenities.append(amenity.title())
        
        return amenities[:5]  # Limit to 5 amenities

    def _extract_source_website(self, url: str) -> str:
        """Extract the source website from URL."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Map domains to friendly names
            domain_mapping = {
                'apartments.com': 'Apartments.com',
                'zillow.com': 'Zillow',
                'kijiji.ca': 'Kijiji',
                'rent.com': 'Rent.com',
                'apartmentfinder.com': 'Apartment Finder',
                'rentals.com': 'Rentals.com'
            }
            
            return domain_mapping.get(domain, domain)
        except:
            return 'Unknown'

    def _extract_contact_info(self, text: str) -> Dict:
        """Extract contact information from text."""
        contact = {
            'name': 'Contact for details',
            'phone': 'N/A',
            'email': 'N/A'
        }
        
        # Look for phone numbers
        phone_pattern = r'\(?(\d{3})\)?[\s.-]?(\d{3})[\s.-]?(\d{4})'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            contact['phone'] = f"({phone_match.group(1)}) {phone_match.group(2)}-{phone_match.group(3)}"
        
        # Look for email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact['email'] = email_match.group(0)
        
        return contact

    def _calculate_match_percentage(self, title: str, snippet: str, location: str) -> int:
        """Calculate a match percentage based on location relevance."""
        full_text = (title + " " + snippet).lower()
        location_lower = location.lower()
        
        # Simple scoring based on location mentions
        if location_lower in full_text:
            return 85
        elif any(word in full_text for word in location_lower.split()):
            return 75
        else:
            return 60

    def _save_search_results(self, response_data: Dict, location: str, listings: List[Dict]):
        """Save the processed search results to a JSON file."""
        try:
            results_dir = 'results'
            os.makedirs(results_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(results_dir, f'google_rental_search_results_{location}_{timestamp}.json')
            
            # Create a comprehensive results object
            results = {
                'search_metadata': {
                    'location': location,
                    'timestamp': timestamp,
                    'total_results_found': len(listings),
                    'search_source': 'Google Custom Search API'
                },
                'listings': listings,
                'raw_response': response_data
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=4)
            
            logger.info(f"Successfully saved {len(listings)} rental listings to {file_path}")

        except Exception as e:
            logger.error(f"Error saving search results to file: {e}")

    def get_api_status(self) -> Dict:
        """Get the status of the Google Custom Search API configuration."""
        if not self.api_key:
            return {
                'available': False,
                'status': 'API key not configured',
                'message': 'Set GOOGLE_API_KEY environment variable'
            }
        
        if not self.search_engine_id:
            return {
                'available': False,
                'status': 'Search engine ID not configured',
                'message': 'Set GOOGLE_SEARCH_ENGINE_ID environment variable'
            }
        
        return {
            'available': True,
            'status': 'Configured and ready',
            'message': 'Google Custom Search API is properly configured'
        }

# Global instance
google_rental_search = GoogleRentalSearch()

def search_rentals_with_google(location: str, min_price: Optional[int] = None,
                              max_price: Optional[int] = None, bedrooms: Optional[int] = None,
                              amenities: Optional[List[str]] = None, lifestyle: Optional[str] = None) -> List[Dict]:
    """Search for rental listings using Google Custom Search API."""
    return google_rental_search.search_rentals(location, min_price, max_price, bedrooms, amenities, lifestyle)

def get_google_status() -> Dict:
    """Get the status of the Google Custom Search API."""
    return google_rental_search.get_api_status()

def is_relevant_url(url: str) -> bool:
    url = url.lower()
    # US ZIP and Canadian Postal Code
    zip_pattern = re.compile(r'\b\d{5}(?:-\d{4})?\b|\b[a-z]\d[a-z][ -]?\d[a-z]\d\b')
    # Unit or apartment numbers like unit-5b or #202
    unit_pattern = re.compile(r'(unit[- ]?\d+[a-z]?)|(#\d+)', re.IGNORECASE)
    # Street names heuristic
    street_pattern = re.compile(
        r'\b\w+(?:-|_)?(?:ave|avenue|st|street|road|rd|blvd|drive|dr|way|lane|ln|court|ct|place|pl)\b', 
        re.IGNORECASE
    )
    # 3D virtual tours
    threed_pattern = re.compile(
        r'(3d|three[-_]?d|threed|virtual[-_]?tour|threedtours|matterport)', 
        re.IGNORECASE
    )
    return any([
        zip_pattern.search(url),
        unit_pattern.search(url),
        street_pattern.search(url),
        threed_pattern.search(url)
    ])

def extract_filtered_rental_links(data):
    results = []
    for item in data.get("raw_response", {}).get("items", []):
        pagemap = item.get("pagemap", {})
        title = item.get("title", "No Title")
        snippet = item.get("snippet", "")
        metatags = pagemap.get("metatags", [{}])
        image = None
        description = snippet  # fallback if no meta description
        # Attempt to get image
        if "cse_image" in pagemap and pagemap["cse_image"]:
            image = pagemap["cse_image"][0].get("src")
        # Attempt to get better description
        if metatags and isinstance(metatags, list):
            description = metatags[0].get("description", description)
        urls_to_check = []
        # Event > url
        for event in pagemap.get("Event", []):
            url = event.get("url")
            if url:
                urls_to_check.append(url)
        # metatags > og:url
        for tag in metatags:
            og_url = tag.get("og:url")
            if og_url:
                urls_to_check.append(og_url)
        # Filter relevant URLs and build results
        for url in urls_to_check:
            if is_relevant_url(url):
                results.append({
                    "title": title,
                    "desc": description,
                    "image": image,
                    "url": url
                })
    return results

def load_and_filter_saved_results(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return extract_filtered_rental_links(data) 