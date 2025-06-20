#!/usr/bin/env python3
"""
Perplexity API Integration for Rental Search
This module uses Perplexity API to search for rental listings in real-time.
Uses the official API endpoint: https://api.perplexity.ai/chat/completions
"""

import os
import json
import logging
import requests
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerplexityRentalSearch:
    def __init__(self):
        """Initialize Perplexity API client."""
        self.api_key = os.getenv('PERPLEXITY_API_KEY')
        self.api_url = "https://api.perplexity.ai/chat/completions"
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        } if self.api_key else {}
        
        if not self.api_key:
            logger.warning("PERPLEXITY_API_KEY not found in environment variables")
        else:
            logger.info("Perplexity API client initialized successfully")

    def search_rentals(self, location: str, min_price: Optional[int] = None, 
                      max_price: Optional[int] = None, bedrooms: Optional[int] = None) -> List[Dict]:
        """
        Search for rental listings using Perplexity API.
        
        Args:
            location: City or area to search
            min_price: Minimum price filter
            max_price: Maximum price filter
            bedrooms: Number of bedrooms required
            
        Returns:
            List of rental listings with structured data
        """
        if not self.api_key:
            logger.error("Perplexity API key not available")
            return []

        try:
            # Build search query
            query = self._build_search_query(location, min_price, max_price, bedrooms)
            logger.info(f"Searching with query: {query}")

            # Prepare the API request
            payload = {
                "model": "sonar-medium-online",  # Using the online model for real-time search
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a rental property search assistant. Search for rental listings and return the results in a structured JSON format. Include property details like title, price, location, bedrooms, bathrooms, amenities, and contact information when available."
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                "max_tokens": 2000,
                "temperature": 0.1
            }

            # Make API request
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                listings = self._parse_api_response(result, location)
                logger.info(f"Found {len(listings)} rental listings")
                return listings
            else:
                logger.error(f"API request failed with status {response.status_code}: {response.text}")
                return []

        except Exception as e:
            logger.error(f"Error searching rentals: {e}")
            return []

    def _build_search_query(self, location: str, min_price: Optional[int] = None,
                           max_price: Optional[int] = None, bedrooms: Optional[int] = None) -> str:
        """Build a comprehensive search query for rental listings."""
        query_parts = [f"Find rental apartments for rent in {location}"]
        
        # Add price filters
        if min_price and max_price:
            query_parts.append(f"with price range ${min_price}-${max_price}")
        elif min_price:
            query_parts.append(f"with minimum price ${min_price}")
        elif max_price:
            query_parts.append(f"with maximum price ${max_price}")
        
        # Add bedroom filter
        if bedrooms:
            query_parts.append(f"with {bedrooms} bedroom(s)")
        
        # Add specific sources and format request
        query_parts.append("Search on rental websites like apartments.com, zillow.com, rentalfast.ca, and padmapper.com")
        query_parts.append("Return the results as a JSON array with each listing containing: title, price (as number), location, bedrooms (as number), bathrooms (as number), amenities (as array), description, contact info, and source website URL")
        query_parts.append("If you find multiple listings, return them all. If no specific listings are found, provide a summary of available rental information for the area.")
        
        return " ".join(query_parts)

    def _parse_api_response(self, response: Dict, location: str) -> List[Dict]:
        """Parse Perplexity API response into structured rental listings."""
        listings = []
        
        try:
            # Extract the content from the response
            if 'choices' in response and len(response['choices']) > 0:
                content = response['choices'][0]['message']['content']
                
                # Try to extract JSON from the response
                listings = self._extract_json_from_content(content, location)
                
                # If no JSON found, try to extract from text
                if not listings:
                    listings = self._extract_from_text_content(content, location)
                
                # If still no listings, create a fallback
                if not listings:
                    listings = self._create_fallback_listing(content, location)
                    
            else:
                logger.warning("No choices found in API response")
                
        except Exception as e:
            logger.error(f"Error parsing API response: {e}")
            listings = []

        return listings

    def _extract_json_from_content(self, content: str, location: str) -> List[Dict]:
        """Extract JSON listings from API response content."""
        listings = []
        
        try:
            import re
            
            # Look for JSON arrays or objects in the content
            json_patterns = [
                r'\[.*?\]',  # JSON arrays
                r'\{.*?\}',  # JSON objects
            ]
            
            for pattern in json_patterns:
                matches = re.findall(pattern, content, re.DOTALL)
                for match in matches:
                    try:
                        data = json.loads(match)
                        if isinstance(data, list):
                            for item in data:
                                if self._is_valid_listing(item):
                                    listings.append(self._normalize_listing(item, location))
                        elif self._is_valid_listing(data):
                            listings.append(self._normalize_listing(data, location))
                    except json.JSONDecodeError:
                        continue

        except Exception as e:
            logger.error(f"Error extracting JSON from content: {e}")

        return listings

    def _extract_from_text_content(self, content: str, location: str) -> List[Dict]:
        """Extract rental information from text content using patterns."""
        listings = []
        
        try:
            import re
            
            # Common patterns for rental listings in text
            patterns = [
                # Pattern: "Property Name" - $X,XXX/month
                r'"([^"]+)"\s*-\s*\$([0-9,]+)/month',
                # Pattern: Property Name: $X,XXX
                r'([^:]+):\s*\$([0-9,]+)',
                # Pattern: $X,XXX - Property Name
                r'\$([0-9,]+)\s*-\s*([^,\n]+)',
                # Pattern: Property Name at $X,XXX
                r'([^$]+)\s+at\s+\$([0-9,]+)',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    if len(match) == 2:
                        title, price_str = match
                        price = self._extract_price(price_str)
                        if price and title.strip():
                            listing = {
                                'id': len(listings) + 1,
                                'title': title.strip(),
                                'price': price,
                                'location': location,
                                'amenities': ['Contact for details'],
                                'description': f'Rental property in {location}',
                                'contact': {'name': 'Contact for details', 'phone': 'N/A', 'email': 'N/A'},
                                'source_website': 'Perplexity Search',
                                'availability_date': datetime.now().strftime('%Y-%m-%d'),
                                'collected_date': datetime.now().isoformat(),
                                'source': 'Perplexity API'
                            }
                            listings.append(listing)

        except Exception as e:
            logger.error(f"Error extracting from text content: {e}")

        return listings

    def _create_fallback_listing(self, content: str, location: str) -> List[Dict]:
        """Create a fallback listing when structured data cannot be extracted."""
        try:
            # Extract any price information from the content
            import re
            price_match = re.search(r'\$([0-9,]+)', content)
            price = self._extract_price(price_match.group(1)) if price_match else None
            
            # Extract any useful information from the content
            summary = content[:300] + "..." if len(content) > 300 else content
            
            listing = {
                'id': 1,
                'title': f'Rental Properties in {location}',
                'price': price or 0,
                'location': location,
                'amenities': ['Contact for details'],
                'description': f'Rental information for {location}. {summary}',
                'contact': {'name': 'Contact individual listings', 'phone': 'N/A', 'email': 'N/A'},
                'source_website': 'Perplexity Search',
                'availability_date': datetime.now().strftime('%Y-%m-%d'),
                'collected_date': datetime.now().isoformat(),
                'source': 'Perplexity API',
                'raw_response': content[:500] + '...' if len(content) > 500 else content
            }
            
            return [listing]
            
        except Exception as e:
            logger.error(f"Error creating fallback listing: {e}")
            return []

    def _is_valid_listing(self, data: Dict) -> bool:
        """Check if a data object represents a valid rental listing."""
        # Check for basic required fields
        if not isinstance(data, dict):
            return False
        
        # Must have at least a title or description
        has_title = 'title' in data and data['title']
        has_description = 'description' in data and data['description']
        
        return has_title or has_description

    def _normalize_listing(self, data: Dict, location: str) -> Dict:
        """Normalize a listing to the standard format."""
        return {
            'id': data.get('id', len(data) + 1),
            'title': data.get('title', 'No title'),
            'price': self._extract_price(str(data.get('price', 0))),
            'location': data.get('location', location),
            'bedrooms': data.get('bedrooms'),
            'bathrooms': data.get('bathrooms'),
            'amenities': data.get('amenities', ['Contact for details']),
            'description': data.get('description', f'Rental property in {location}'),
            'contact': data.get('contact', {'name': 'Contact for details', 'phone': 'N/A', 'email': 'N/A'}),
            'source_website': data.get('source_website', 'Perplexity Search'),
            'availability_date': datetime.now().strftime('%Y-%m-%d'),
            'collected_date': datetime.now().isoformat(),
            'source': 'Perplexity API'
        }

    def _extract_price(self, price_text: str) -> Optional[int]:
        """Extract numeric price from text."""
        if not price_text:
            return None
        
        import re
        # Remove all non-digit characters except decimal points
        cleaned = re.sub(r'[^\d.]', '', str(price_text))
        try:
            # Convert to float first, then to int
            price_float = float(cleaned)
            return int(price_float)
        except (ValueError, TypeError):
            return None

    def get_api_status(self) -> Dict:
        """Get the status of the Perplexity API connection."""
        if not self.api_key:
            return {
                'available': False,
                'api_key_set': False,
                'status': 'API key not set'
            }
        
        try:
            # Test API connection with a simple request
            test_payload = {
                "model": "sonar-medium-online",
                "messages": [
                    {
                        "role": "user",
                        "content": "Hello"
                    }
                ],
                "max_tokens": 10
            }
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=test_payload,
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    'available': True,
                    'api_key_set': True,
                    'status': 'Connected'
                }
            else:
                return {
                    'available': False,
                    'api_key_set': True,
                    'status': f'API Error: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'available': False,
                'api_key_set': True,
                'status': f'Connection Error: {str(e)}'
            }

# Global instance
perplexity_search = PerplexityRentalSearch()

def search_rentals_with_perplexity(location: str, min_price: Optional[int] = None,
                                 max_price: Optional[int] = None, bedrooms: Optional[int] = None) -> List[Dict]:
    """Convenience function to search rentals using Perplexity API."""
    return perplexity_search.search_rentals(location, min_price, max_price, bedrooms)

def get_perplexity_status() -> Dict:
    """Get Perplexity API status."""
    return perplexity_search.get_api_status() 