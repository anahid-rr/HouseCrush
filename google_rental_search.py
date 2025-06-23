#!/usr/bin/env python3
"""
Google Custom Search API Integration for Rental Search
This module uses Google Custom Search API to search for rental listings in real-time.
Uses the official Google Custom Search JSON API endpoint.
"""

import os
import json
import logging
import requests
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleRentalSearch:
    def __init__(self):
        """Initialize Google Custom Search API client."""
        self.api_key = os.getenv('GOOGLE_API_KEY')
        self.search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
        self.api_url = "https://www.googleapis.com/customsearch/v1"
        
        if not self.api_key:
            logger.warning("GOOGLE_API_KEY not found in environment variables")
        if not self.search_engine_id:
            logger.warning("GOOGLE_SEARCH_ENGINE_ID not found in environment variables")
        
        if self.api_key and self.search_engine_id:
            logger.info("Google Custom Search API client initialized successfully")
        else:
            logger.error("Google Custom Search API not properly configured")

    def search_rentals(self, location: str, min_price: Optional[int] = None, 
                      max_price: Optional[int] = None, bedrooms: Optional[int] = None,
                      amenities: Optional[List[str]] = None, lifestyle: Optional[str] = None) -> List[Dict]:
        """
        Search for rental listings using Google Custom Search API.
        
        Args:
            location: City or area to search
            min_price: Minimum price filter
            max_price: Maximum price filter
            bedrooms: Number of bedrooms required
            amenities: List of required amenities
            lifestyle: Lifestyle preferences (e.g., near a park)
            
        Returns:
            List of rental listings with structured data
        """
        if not self.api_key or not self.search_engine_id:
            logger.error("Google Custom Search API not properly configured")
            return []

        try:
            # Build search query
            query = self._build_search_query(location, min_price, max_price, bedrooms, amenities, lifestyle)
            logger.info(f"Searching Google Custom Search with query: {query}")

            # Validate query
            if not query or len(query.strip()) == 0:
                logger.error("Empty or invalid search query")
                return []

            # Prepare the API request
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': query,
                'num': 10,  # Number of results (max 10 per request for free tier)
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

    def _build_search_query(self, location: str, min_price: Optional[int] = None,
                           max_price: Optional[int] = None, bedrooms: Optional[int] = None,
                           amenities: Optional[List[str]] = None, lifestyle: Optional[str] = None) -> str:
        """Build a search query for rental listings."""
        # Define the sites to search
        target_sites = [
            "apartments.com",
            "zillow.com",
            "kijiji.ca"
        ]
        site_query = " OR ".join([f"site:{site}" for site in target_sites])
        
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
            query_parts.append(f"({' OR '.join(bedroom_terms)})")
        
        # Add amenities filter
        if amenities:
            amenities_text = ' AND '.join([f'"{amenity}"' for amenity in amenities[:3]])
            query_parts.append(f"({amenities_text})")
            
        # Add lifestyle filter
        if lifestyle:
            query_parts.append(f'"{lifestyle}"')
        
        # Join and clean the query
        query = " ".join(query_parts)
        return " ".join(query.split())  # Remove extra whitespace

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
            r'\$([0-9,]+)\s*rent'
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    price_str = match.group(1).replace(',', '')
                    return int(price_str)
                except (ValueError, TypeError):
                    continue
        
        return None

    def _extract_bedrooms_from_text(self, text: str) -> Optional[int]:
        """Extract number of bedrooms from text."""
        # First try to extract from "beds/baths" format
        bed_bath_match = self._extract_from_bed_bath_format(text)
        if bed_bath_match and bed_bath_match.get('bedrooms'):
            return bed_bath_match['bedrooms']
        
        # Look for bedroom patterns with various formats
        patterns = [
            # Standard bedroom patterns
            r'(\d+)\s*(?:bed|bedroom|br)',
            r'(\d+)\s*bedroom',
            r'(\d+)\s*br',
            # Handle "beds" format
            r'(\d+)\s*beds?',
            # Handle "beds/baths" format (e.g., "2 bed/bath")
            r'(\d+)\s*bed/bath',
            # Handle "2+" notation
            r'(\d+)\+\s*(?:bed|bedroom|br|beds?)',
            # Handle "2+ bed/bath" format
            r'(\d+)\+\s*bed/bath',
            # Handle standalone "2+" when context suggests bedrooms
            r'(\d+)\+',  # This is more general, will be validated in context
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    bedroom_count = int(match.group(1))
                    # For the general "2+" pattern, validate it's in a bedroom context
                    if pattern == r'(\d+)\+':
                        # Check if the surrounding text suggests this is about bedrooms
                        context_start = max(0, match.start() - 20)
                        context_end = min(len(text), match.end() + 20)
                        context = text[context_start:context_end].lower()
                        bedroom_indicators = ['bed', 'bedroom', 'br', 'room', 'apartment', 'unit', 'suite']
                        if not any(indicator in context for indicator in bedroom_indicators):
                            continue
                    return bedroom_count
                except (ValueError, TypeError):
                    continue
        
        return None

    def _extract_bathrooms_from_text(self, text: str) -> Optional[int]:
        """Extract number of bathrooms from text."""
        # First try to extract from "beds/baths" format
        bed_bath_match = self._extract_from_bed_bath_format(text)
        if bed_bath_match and bed_bath_match.get('bathrooms'):
            return bed_bath_match['bathrooms']
        
        # Look for bathroom patterns with various formats
        patterns = [
            # Standard bathroom patterns
            r'(\d+)\s*(?:bath|bathroom|ba)',
            r'(\d+)\s*bathroom',
            r'(\d+)\s*ba',
            # Handle "baths" format
            r'(\d+)\s*baths?',
            # Handle "beds/baths" format (e.g., "2 bed/1 bath")
            r'(\d+)\s*bath',  # This will catch "1 bath" in "2 bed/1 bath"
            # Handle "2+" notation
            r'(\d+)\+\s*(?:bath|bathroom|ba|baths?)',
            # Handle standalone "2+" when context suggests bathrooms
            r'(\d+)\+',  # This is more general, will be validated in context
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    bathroom_count = int(match.group(1))
                    # For the general "2+" pattern, validate it's in a bathroom context
                    if pattern == r'(\d+)\+':
                        # Check if the surrounding text suggests this is about bathrooms
                        context_start = max(0, match.start() - 20)
                        context_end = min(len(text), match.end() + 20)
                        context = text[context_start:context_end].lower()
                        bathroom_indicators = ['bath', 'bathroom', 'ba', 'washroom', 'toilet']
                        if not any(indicator in context for indicator in bathroom_indicators):
                            continue
                    return bathroom_count
                except (ValueError, TypeError):
                    continue
        
        return None

    def _extract_from_bed_bath_format(self, text: str) -> Optional[Dict]:
        """Extract both bedroom and bathroom counts from 'beds/baths' format patterns."""
        # Patterns for "beds/baths" format
        patterns = [
            r'(\d+)\s*(?:bed|beds?)\s*/\s*(\d+)\s*(?:bath|baths?)',  # "2 bed/1 bath"
            r'(\d+)\s*(?:bedroom|bedrooms?)\s*/\s*(\d+)\s*(?:bathroom|bathrooms?)',  # "2 bedroom/1 bathroom"
            r'(\d+)\s*br\s*/\s*(\d+)\s*ba',  # "2 br/1 ba"
            r'(\d+)\+\s*(?:bed|beds?)\s*/\s*(\d+)\s*(?:bath|baths?)',  # "2+ bed/1 bath"
            r'(\d+)\+\s*(?:bedroom|bedrooms?)\s*/\s*(\d+)\s*(?:bathroom|bathrooms?)',  # "2+ bedroom/1 bathroom"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    bedrooms = int(match.group(1))
                    bathrooms = int(match.group(2))
                    return {'bedrooms': bedrooms, 'bathrooms': bathrooms}
                except (ValueError, TypeError):
                    continue
        
        return None

    def _extract_amenities_from_text(self, text: str) -> List[str]:
        """Extract amenities from text."""
        # Common amenities to look for
        amenities = [
            'parking', 'gym', 'pool', 'balcony', 'laundry', 'dishwasher',
            'air conditioning', 'heating', 'elevator', 'doorman', 'storage',
            'bike storage', 'rooftop', 'terrace', 'garden', 'pet friendly'
        ]
        
        found_amenities = []
        for amenity in amenities:
            if re.search(r'\b' + re.escape(amenity) + r'\b', text, re.IGNORECASE):
                found_amenities.append(amenity.title())
        
        return found_amenities

    def _extract_source_website(self, url: str) -> str:
        """Extract source website name from URL."""
        # Extract domain from URL
        domain_match = re.search(r'https?://(?:www\.)?([^/]+)', url)
        if domain_match:
            domain = domain_match.group(1)
            # Map common domains to friendly names
            domain_mapping = {
                'zillow.com': 'Zillow',
                'apartments.com': 'Apartments.com',
                'rent.com': 'Rent.com',
                'padmapper.com': 'PadMapper',
                'rentfaster.ca': 'RentFaster',
                'kijiji.ca': 'Kijiji',
                'craigslist.org': 'Craigslist',
                'realtor.com': 'Realtor.com',
                'rentals.ca': 'Rentals.ca',
                'viewit.ca': 'Viewit.ca'
            }
            return domain_mapping.get(domain, domain)
        
        return 'Google Search'

    def _extract_contact_info(self, text: str) -> Dict:
        """Extract contact information from text."""
        contact = {
            'name': 'Contact for details',
            'phone': 'N/A',
            'email': 'N/A'
        }
        
        # Look for phone numbers
        phone_match = re.search(r'(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})', text)
        if phone_match:
            contact['phone'] = phone_match.group(1)
        
        # Look for email addresses
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        if email_match:
            contact['email'] = email_match.group(0)
        
        return contact

    def _calculate_match_percentage(self, title: str, snippet: str, location: str) -> int:
        """Calculate match percentage based on search criteria."""
        score = 0
        text = (title + " " + snippet).lower()
        location_lower = location.lower()
        
        # Location match (30 points)
        if location_lower in text:
            score += 30
        
        # Price indication (25 points)
        if any(word in text for word in ['rent', 'month', '$']):
            score += 25
        
        # Property type indication (20 points)
        if any(word in text for word in ['apartment', 'condo', 'house', 'unit', 'suite']):
            score += 20
        
        # Bedroom/Bathroom indication (15 points) - enhanced to catch various formats
        bedroom_indicators = ['bed', 'bedroom', 'br', 'beds']
        bathroom_indicators = ['bath', 'bathroom', 'ba', 'baths']
        bed_bath_indicators = ['bed/bath', 'beds/baths']
        
        if any(indicator in text for indicator in bedroom_indicators + bathroom_indicators + bed_bath_indicators):
            score += 15
        
        # Availability indication (10 points)
        if any(word in text for word in ['available', 'now', 'immediate', 'vacant']):
            score += 10
        
        return min(score, 100)

    def _save_search_results(self, response_data: Dict, location: str, listings: List[Dict]):
        """Save the complete search results to a JSON file."""
        try:
            results_dir = 'results'
            os.makedirs(results_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(results_dir, f'google_rental_search_results_{location}_{timestamp}.json')
            
            # Create search results summary
            search_results = {
                'search_summary': {
                    'location': location,
                    'total_listings_found': len(listings),
                    'search_timestamp': datetime.now().isoformat(),
                    'source': 'Google Custom Search API'
                },
                'listings': listings,
                'raw_response': response_data
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(search_results, f, ensure_ascii=False, indent=4)
            
            logger.info(f"Successfully saved search results to {file_path}")

        except Exception as e:
            logger.error(f"Error saving search results to file: {e}")

    def get_api_status(self) -> Dict:
        """Get the status of the Google Custom Search API connection."""
        if not self.api_key or not self.search_engine_id:
            return {
                'available': False,
                'api_key_set': bool(self.api_key),
                'search_engine_id_set': bool(self.search_engine_id),
                'status': 'API key or Search Engine ID not set'
            }
        
        try:
            # Test API connection with a simple request
            test_params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': 'test',
                'num': 1,
                'searchType': 'searchTypeUndefined'
            }
            
            response = requests.get(
                self.api_url,
                params=test_params,
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    'available': True,
                    'api_key_set': True,
                    'search_engine_id_set': True,
                    'status': 'Connected (Google Custom Search)'
                }
            else:
                return {
                    'available': False,
                    'api_key_set': True,
                    'search_engine_id_set': True,
                    'status': f'API Error: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'available': False,
                'api_key_set': True,
                'search_engine_id_set': True,
                'status': f'Connection Error: {str(e)}'
            }

# Global instance
google_search = GoogleRentalSearch()

def search_rentals_with_google(location: str, min_price: Optional[int] = None,
                              max_price: Optional[int] = None, bedrooms: Optional[int] = None,
                              amenities: Optional[List[str]] = None, lifestyle: Optional[str] = None) -> List[Dict]:
    """Convenience function to search rentals using Google Custom Search API."""
    return google_search.search_rentals(location, min_price, max_price, bedrooms, amenities, lifestyle)

def get_google_status() -> Dict:
    """Get Google Custom Search API status."""
    return google_search.get_api_status() 