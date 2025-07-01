#!/usr/bin/env python3
"""
Google Custom Search API Integration for Rental Listings
Clean Modular Design with Four Main Methods

This module provides a clean, modular approach to Google search with:
1. simple_google_search() - Basic search and save JSON
2. simple_filtered() - Parse and apply existing filters
3. intelligent_filtered() - AI-powered filtering
4. streamlined_search() - High-level orchestration
"""

import requests
import json
import logging
import os
import re
import glob
from datetime import datetime
from typing import List, Optional, Dict
from dotenv import load_dotenv
from config import config

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
        
        if not self.api_key or not self.search_engine_id:
            raise ValueError("Google API key and Search Engine ID must be set in environment variables")
    def _build_search_query(self, location: str, min_price: Optional[int] = None,
                           max_price: Optional[int] = None, bedrooms: Optional[int] = None,
                           amenities: Optional[List[str]] = None, lifestyle: Optional[str] = None) -> str:
        """Build a search query for rental listings."""
        # Define the sites to search
        target_sites = [
            
            "zillow.com",
            "apartments.com",
            "padmapper.com"        # 
            # "kijiji.ca"
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
           
    def search_rentals(self, location: str, min_price: Optional[int] = None, 
                      max_price: Optional[int] = None, bedrooms: Optional[int] = None,
                      amenities: Optional[List[str]] = None, lifestyle: Optional[str] = None) -> Dict:
        """
        Perform Google Custom Search for rental listings.
        
        Args:
            location: City/location to search
            min_price: Minimum price filter
            max_price: Maximum price filter
            bedrooms: Number of bedrooms
            amenities: List of amenities
            lifestyle: Lifestyle preferences
            
        Returns:
            Dictionary containing search results
        """
        google_search = GoogleRentalSearch()
        # Build search query
        query = self._build_search_query(location, min_price, max_price, bedrooms, amenities, lifestyle)
        
        # Prepare API request
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': self.api_key,
            'cx': self.search_engine_id,
            'q': query,
            'num': 10  # Number of results
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Google API request failed: {e}")
            return {"error": str(e)}

def simple_google_search(location: str, min_price: Optional[int] = None, 
                        max_price: Optional[int] = None, bedrooms: Optional[int] = None,
                        amenities: Optional[List[str]] = None, lifestyle: Optional[str] = None) -> Dict:
    """
    Performs a basic Google Search using the Google Search API and saves the raw JSON file.
    
    Args:
        location: City/location to search
        min_price: Minimum price filter
        max_price: Maximum price filter
        bedrooms: Number of bedrooms
        amenities: List of amenities
        lifestyle: Lifestyle preferences
        
    Returns:
        Dictionary containing:
        - success: Boolean indicating success
        - message: Status message
        - file_path: Path to saved JSON file (if successful)
        - error: Error message (if failed)
    """
    try:
        # Initialize Google search client
        google_search = GoogleRentalSearch()
        
        # Perform search
        search_results = google_search.search_rentals(
            location=location,
            min_price=min_price,
            max_price=max_price,
            bedrooms=bedrooms,
            amenities=amenities,
            lifestyle=lifestyle
        )
        
        if "error" in search_results:
            return {
                "success": False,
                "error": search_results["error"],
                "message": "Google search failed"
            }
        
        # Create results directory if it doesn't exist
        results_dir = "results"
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)
        
        # Save raw JSON response
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"google_search_{timestamp}.json"
        file_path = os.path.join(results_dir, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(search_results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Google search results saved to: {file_path}")
        
        return {
            "success": True,
            "message": f"Search completed successfully. Found {len(search_results.get('items', []))} results.",
            "file_path": file_path,
            "json_data": search_results,
            "results_count": len(search_results.get('items', []))
        }
        
    except Exception as e:
        logger.error(f"Error in simple_google_search: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Search failed"
        }

def _extract_price(text):
    if not text:
        return None
    price_patterns = [
        r'\$([0-9,]+)',
        r'([0-9,]+)\s*USD',
        r'([0-9,]+)\s*CAD',
        r'([0-9,]+)\s*/\s*month',
        r'([0-9,]+)\s*per\s*month',
        r'([0-9,]+)\s*monthly',
    ]
    for pattern in price_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                return int(match.group(1).replace(',', ''))
            except Exception:
                continue
    return None

def _extract_bedrooms(text):
    if not text:
        return None
    match = re.search(r'(\d+)\s*(?:bedroom|bed|br)', text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None

def _extract_bathrooms(text):
    if not text:
        return None
    match = re.search(r'(\d+(?:\.\d+)?)\s*(?:bathroom|bath|ba)', text, re.IGNORECASE)
    if match:
        try:
            return float(match.group(1))
        except Exception:
            return None
    return None

def _extract_canonical_url(item):
    link = item.get('link', '')
    pagemap = item.get('pagemap', {})
    # metatags > og:url
    if 'metatags' in pagemap and pagemap['metatags']:
        metatags = pagemap['metatags'][0]
        if 'og:url' in metatags:
            return metatags['og:url']
    # event > url
    if 'event' in pagemap and pagemap['event']:
        event = pagemap['event'][0]
        if 'url' in event:
            return event['url']
    return link

def _extract_image_url(item):
    pagemap = item.get('pagemap', {})
    if 'cse_image' in pagemap and pagemap['cse_image']:
        return pagemap['cse_image'][0].get('src', '')
    return ''

def extract_urls_and_images(raw_response):
    extracted_results = []
    seen_combinations = set()  # To track duplicates

    items = raw_response.get("items", [])
    for item in items:
        display_link = item.get("displayLink", "")
        pagemap = item.get("pagemap", {})

        if display_link == "www.apartments.com":
            # For apartments.com, extract from BOTH metatags AND Event paths
            extracted_results_apartments = []
            apartments_urls_seen = set()  # Track URLs specifically for apartments
            
            # First, try metatags path (like Zillow)
            metatags = pagemap.get("metatags", [])
            if metatags:
                tag = metatags[0]  # Usually a single dict in a list
                url = tag.get("og:url")
                image = tag.get("og:image")
                # Check if both URL and image exist and are not empty
                if url and image and url.strip() and image.strip():
                    clean_url = url.strip()
                    # Check for duplicate URLs specifically for apartments
                    if clean_url not in apartments_urls_seen:
                        apartments_urls_seen.add(clean_url)
                        # Create a unique key for global duplicate checking
                        combination = f"apartments_{clean_url}_{image.strip()}"
                        if combination not in seen_combinations:
                            seen_combinations.add(combination)
                            extracted_results_apartments.append({
                                "source": display_link,
                                "url": clean_url,
                                "image": image.strip(),
                                "extraction_method": "metatags"
                            })
            
            # Second, try Event path (apartments.com specific)
            events = pagemap.get("Event", [])
            if events:
                # Iterate through all events in the array
                for event in events:
                    url = event.get("url")
                    image = event.get("image")
                    # Check if both URL and image exist and are not empty
                    if url and image and url.strip() and image.strip():
                        clean_url = url.strip()
                        # Check for duplicate URLs specifically for apartments
                        if clean_url not in apartments_urls_seen:
                            apartments_urls_seen.add(clean_url)
                            # Create a unique key for global duplicate checking
                            combination = f"apartments_{clean_url}_{image.strip()}"
                            if combination not in seen_combinations:
                                seen_combinations.add(combination)
                                extracted_results_apartments.append({
                                    "source": display_link,
                                    "url": clean_url,
                                    "image": image.strip(),
                                    "extraction_method": "event"
                                })
            
            # Add all apartments.com results to the main results
            extracted_results.extend(extracted_results_apartments)

        else:
            # For other sites (like Zillow), extract only from metatags
            metatags = pagemap.get("metatags", [])
            if metatags:
                tag = metatags[0]  # Usually a single dict in a list
                url = tag.get("og:url")
                image = tag.get("og:image")
                # Check if both URL and image exist and are not empty
                if url and image and url.strip() and image.strip():
                    # Create a unique key for duplicate checking
                    combination = f"other_{url}_{image}"
                    if combination not in seen_combinations:
                        seen_combinations.add(combination)
                        extracted_results.append({
                            "source": display_link,
                            "url": url.strip(),
                            "image": image.strip()
                        })

    # Return in JSON-like dictionary format
    return {
        "items": extracted_results,
        "total_results": len(extracted_results),
        "extracted_data": True,
        "format": "extracted_urls_and_images"
    }

def _parse_google_response(json_data):
    """
    Parse Google Custom Search API response and extract property fields using helper methods.
    Returns a list of property dicts.
    """
    items = json_data.get('items', [])
    properties = []
    for item in items:
        title = item.get('title', '')
        snippet = item.get('snippet', '')
        canonical_url = _extract_canonical_url(item)
        image_url = _extract_image_url(item)
        price = _extract_price(title) or _extract_price(snippet)
        bedrooms = _extract_bedrooms(title) or _extract_bedrooms(snippet)
        bathrooms = _extract_bathrooms(title) or _extract_bathrooms(snippet)
        property_obj = {
            'title': title,
            'description': snippet,
            'url': canonical_url,
            'image_url': image_url,
            'price': price,
            'bedrooms': bedrooms,
            'bathrooms': bathrooms,
            'source': 'Google Search',
        }
        properties.append(property_obj)
    return properties

def simple_filtered(json_file_path: str) -> Dict:
    """
    Takes the saved JSON file, parses the results, applies filtering and extraction logic.
    Preserves all existing filtering patterns (off-market listings, etc.).
    
    Args:
        json_file_path: Path to the saved JSON file
        
    Returns:
        Dictionary containing:
        - success: Boolean indicating success
        - properties: List of filtered and extracted properties
        - message: Status message
        - error: Error message (if failed)
    """
    try:
        # Load JSON file
        with open(json_file_path, 'r', encoding='utf-8') as f:
            search_data = json.load(f)
        
        if "error" in search_data:
            return {
                "success": False,
                "error": search_data["error"],
                "message": "Invalid search data"
            }
        
        # Use the new parser
        all_properties = _parse_google_response(search_data)
        filtered_properties = []
        skip_keywords = ['off-market', 'sold', 'pending', 'average', 'under', 'apartments']
        for property_obj in all_properties:
            title = property_obj['title']
            description = property_obj['description']
            if any(keyword.lower() in title.lower() or keyword.lower() in description.lower() for keyword in skip_keywords):
                continue
            # Add rank and tags
            property_obj['rank'] = len(filtered_properties) + 1
            tags = []
            if property_obj.get('bedrooms'):
                tags.append(f"{property_obj['bedrooms']} BR")
            if property_obj.get('bathrooms'):
                tags.append(f"{property_obj['bathrooms']} Bath")
            property_obj['tags'] = tags
            filtered_properties.append(property_obj)
        
        logger.info(f"Simple filtering completed. {len(filtered_properties)} properties filtered from {len(all_properties)} results.")
        
        return {
            "success": True,
            "properties": filtered_properties,
            "message": f"Filtered {len(filtered_properties)} properties from {len(all_properties)} results",
            "total_original": len(all_properties),
            "total_filtered": len(filtered_properties)
        }
        
    except Exception as e:
        logger.error(f"Error in simple_filtered: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Filtering failed"
        }

def intelligent_filtered(json_file_path: str, user_preferences: Dict) -> Dict:
    """
    Uses the same JSON file and sends the prompt to OpenAI for more intelligent filtering 
    or ranking based on user preferences (like lifestyle, amenities, etc.).
    
    Args:
        json_file_path: Path to the saved JSON file
        user_preferences: Dictionary containing user preferences (location, price, bedrooms, amenities, lifestyle)
        
    Returns:
        Dictionary containing:
        - success: Boolean indicating success
        - properties: List of AI-filtered properties
        - message: Status message
        - error: Error message (if failed)
    """
    try:
        # Check if OpenAI is available
        try:
            import openai
            if not openai.api_key:
                openai.api_key = os.getenv('OPENAI_API_KEY')
            
            if not openai.api_key:
                return {
                    "success": False,
                    "error": "OpenAI API key not configured",
                    "message": "OpenAI not available for intelligent filtering"
                }
        except ImportError:
            return {
                "success": False,
                "error": "OpenAI integration not available",
                "message": "Intelligent filtering requires OpenAI integration"
            }
        
        # Load JSON file
        with open(json_file_path, 'r', encoding='utf-8') as f:
            google_search_data = json.load(f)
        
        if "error" in google_search_data:
            return {
                "success": False,
                "error": google_search_data["error"],
                "message": "Invalid search data"
            }
        
        logger.info("Starting intelligent filtering with OpenAI...")
        
        # Create the prompt for OpenAI (same as in app.py)
        prompt = f"""
You are analyzing Google search results for rental properties. 

Your task is to:
1. Extract URLs from raw_response > items > pagemap > Event > url and pagemap > metatags > og:url in the JSON data that are individual rental property listings
2. Filter for URLs that contain:
   - Zip codes
   - Street names
   - Unit numbers  
   - 3D tours
3. Return only the relevant rental listings

For each relevant listing, extract:
- title: The property title
- desc: Property description
- image: extract from image_url or og:image
- url: The property URL
- price: The property price you can find in the snippet or description if you can't find it, search on website.
- features: The property features you can find in the snippet or description as a list of strings(e.g. dishwasher, dryer, In-unit laundry, etc.)
- source: Extract the domain/host (e.g., kijiji.ca, zillow.com) from the property URL
- tags: find the tags of the property URL as a list of strings(e.g. 2 BR, 2 Bath,  dishwasher, dryer, In-unit laundry, etc.)

After that, Rank and calculate the match percentage of the extracted properties based on the user preferences(for example, if the user prefers a 2 bedroom apartment, and the property has 2 bedrooms, the match percentage should be 100%)

Return a JSON array with this structure:
[
  {{
    "title": "Property Title",
    "desc": "Property Description", 
    "image": "Image URL if available",
    "url": "Property URL",
    "price": "Property Price",
    "features": "Property Features",
    "source": "Property Source",
    "rank": "Property Rank",
    "tags": "Property Tags",
    "match": "Property Match Percentage"
  }}
]

Here is the Google search results JSON to analyze:
{json.dumps(google_search_data, indent=2)}
Here is the user preferences:
{json.dumps(user_preferences, indent=2)}

Return only valid JSON without any additional text.
"""

        # Save the prompt to a file for debugging
        save_openai_debug_data("prompt", {
            "timestamp": datetime.now().isoformat(),
            "user_preferences": user_preferences,
            "google_search_file": json_file_path,
            "prompt": prompt
        })
       
        # Call OpenAI API
        logger.info("Calling OpenAI API with Google search data...")
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini-search-preview",
            messages=[
                {"role": "system", "content": "You are a rental property analysis expert. Extract and filter and rank rental listings from Google search results. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000,
            temperature=0.1
        )
        
        # Parse the response
        response_text = response.choices[0].message.content.strip()
        logger.info(f"OpenAI response received, length: {len(response_text)}")
        
        # Save the raw OpenAI response
        save_openai_debug_data("response", {
            "timestamp": datetime.now().isoformat(),
            "user_preferences": user_preferences,
            "google_search_file": json_file_path,
            "raw_response": response_text,
            "response_length": len(response_text),
            "model_used": "gpt-3.5-turbo",
            "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else None
        })
        
        # Extract JSON from response (in case there's extra text)
        json_start = response_text.find('[')
        json_end = response_text.rfind(']') + 1
        if json_start != -1 and json_end != -1:
            response_text = response_text[json_start:json_end]
        
        filtered_results = json.loads(response_text)
        logger.info(f"Successfully parsed {len(filtered_results)} filtered listings")
        
        # Save the final filtered results
        save_openai_debug_data("final_results", {
            "timestamp": datetime.now().isoformat(),
            "user_preferences": user_preferences,
            "google_search_file": json_file_path,
            "filtered_results": filtered_results,
            "total_filtered": len(filtered_results)
        })
        
        # Format results to match expected structure
        ai_filtered_properties = []
        for i, property_data in enumerate(filtered_results):
            property_obj = {
                'title': property_data.get('title', ''),
                'description': property_data.get('desc', ''),
                'url': property_data.get('url', ''),
                'image_url': property_data.get('image', ''),
                'price': property_data.get('price', ''),
                'source': property_data.get('source', ''),
                'rank': property_data.get('rank', ''),
                'features': property_data.get('features', ''),
                'tags': property_data.get('tags', ''),
                'match': property_data.get('match', '')
            }
            ai_filtered_properties.append(property_obj)
        
        logger.info(f"Intelligent filtering completed. {len(ai_filtered_properties)} properties AI-filtered.")
        
        return {
            "success": True,
            "properties": ai_filtered_properties,
            "message": f"AI filtered {len(ai_filtered_properties)} properties",
            "total_original": len(google_search_data.get('items', [])),
            "total_ai_filtered": len(ai_filtered_properties)
        }
        
    except Exception as e:
        logger.error(f"Error in intelligent_filtered: {e}")
        
        # Save error information
        save_openai_debug_data("error", {
            "timestamp": datetime.now().isoformat(),
            "user_preferences": user_preferences,
            "error": str(e),
            "error_type": type(e).__name__
        })
        
        return {
            "success": False,
            "error": str(e),
            "message": "Intelligent filtering failed"
        }

def save_openai_debug_data(data_type: str, data: Dict):
    """
    Save OpenAI debug data to files for analysis and debugging (only in development).
    
    Args:
        data_type: Type of data ('prompt', 'response', 'parsed_results', 'final_results', 'error')
        data: Data to save
    """
    if not config.should_save_debug_files():
        return
    
    try:
        # Create debug directory if it doesn't exist
        debug_dir = 'debug'
        if not os.path.exists(debug_dir):
            os.makedirs(debug_dir)
            if config.should_log_debug():
                logger.info(f"Created debug directory: {debug_dir}")
        
        # Create OpenAI debug subdirectory
        openai_debug_dir = os.path.join(debug_dir, 'openai')
        if not os.path.exists(openai_debug_dir):
            os.makedirs(openai_debug_dir)
            if config.should_log_debug():
                logger.info(f"Created OpenAI debug directory: {openai_debug_dir}")
        
        # Generate timestamp for filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create filename based on data type
        filename = f"openai_{data_type}_{timestamp}.json"
        filepath = os.path.join(openai_debug_dir, filename)
        
        # Save data to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        if config.should_log_debug():
            logger.info(f"✅ Saved {data_type} data to: {filepath}")
        
    except Exception as e:
        logger.error(f"❌ Error saving debug data: {e}")
        # Try to save to current directory as fallback
        if config.should_save_debug_files():
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"openai_{data_type}_{timestamp}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                if config.should_log_debug():
                    logger.info(f"✅ Saved {data_type} data to current directory: {filename}")
            except Exception as fallback_error:
                logger.error(f"❌ Failed to save debug data even to current directory: {fallback_error}")

def intelligent_filtered_json(google_search_data: Dict, user_preferences: Dict) -> Dict:
    """
    Uses JSON content directly and sends the prompt to OpenAI for more intelligent filtering 
    or ranking based on user preferences (like lifestyle, amenities, etc.).
    
    Args:
        google_search_data: Dictionary containing Google search results
        user_preferences: Dictionary containing user preferences (location, price, bedrooms, amenities, lifestyle)
        
    Returns:
        Dictionary containing:
        - success: Boolean indicating success
        - properties: List of AI-filtered properties
        - message: Status message
        - error: Error message (if failed)
    """
    try:
        # Check if OpenAI is available
        try:
            import openai
            if not openai.api_key:
                openai.api_key = os.getenv('OPENAI_API_KEY')
            
            if not openai.api_key:
                return {
                    "success": False,
                    "error": "OpenAI API key not configured",
                    "message": "OpenAI not available for intelligent filtering"
                }
        except ImportError:
            return {
                "success": False,
                "error": "OpenAI integration not available",
                "message": "Intelligent filtering requires OpenAI integration"
            }
        
        if "error" in google_search_data:
            return {
                "success": False,
                "error": google_search_data["error"],
                "message": "Invalid search data"
            }
        
        logger.info("Starting intelligent filtering with OpenAI using JSON content...")
        
        # Create the prompt for OpenAI (same as in intelligent_filtered)
        prompt = f"""
In the json data I give you,
Filter URLs that contain:
   - Zip codes
   - Street names
   - Unit numbers  
   - threedTours
   - apartments name

For each extracted url, search the website and complete the following fields:
- title: Property title
- desc: Property description
- price: Find the property price in the snippet or description or search it in other website and findout the price only and only set the price in the price field.
- features: Find the features in the snippet or description as a list of strings(e.g. dishwasher, dryer, In-unit laundry, etc.)
- source: use displayLink
- tags: find the property tags as a list of strings(e.g. 2 BR, 2 Bath,  dishwasher, dryer, In-unit laundry, etc.)
Exclude all listings where the minimum price is higher than the user's maximum desired price. For instance, if the user wants $2300–$3200, include listings priced $2300–$4500, but exclude listings with a minimum price above $3200.  
For the extracted properties, calculate how many user preferences are satisfied, treating each as an equal part of the whole.
Then, return both the match percentage and a ranking of the properties from highest to lowest match.
Return result in a JSON array with this structure:
[
  {{
    "title": "Property Title",
    "desc": "Property Description", 
    "image": "Image URL if available",
    "url": "Property URL",
    "price": "Property Price",
    "features": "Property Features",
    "source": "Property Source",
    "rank": "Property Rank",
    "tags": "Property Tags",
    "match": "Property Match Percentage"
  }}
]

Here is the Google search results JSON to analyze:
{json.dumps(google_search_data, indent=2)}
Here is the user preferences:
{json.dumps(user_preferences, indent=2)}

Return only valid JSON without any additional text.
"""

        # Save the prompt to a file for debugging
        save_openai_debug_data("prompt", {
            "timestamp": datetime.now().isoformat(),
            "user_preferences": user_preferences,
            "google_search_data_source": "direct_json",
            "prompt": prompt
        })
       
        # Call OpenAI API
        logger.info("Calling OpenAI API with Google search data...")
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini-search-preview",
            messages=[
                {"role": "system", "content": "You are a rental property analysis expert. Extract and filter and rank rental listings from Google search results. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000,
            # temperature=0.1
        )
        
        # Parse the response
        response_text = response.choices[0].message.content.strip()
        logger.info(f"OpenAI response received, length: {len(response_text)}")
        
        # Save the raw OpenAI response
        save_openai_debug_data("response", {
            "timestamp": datetime.now().isoformat(),
            "user_preferences": user_preferences,
            "google_search_data_source": "direct_json",
            "raw_response": response_text,
            "response_length": len(response_text),
            "model_used": "gpt-4o-mini-search-preview",
            "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else None
        })
        
        # Extract JSON from response (in case there's extra text)
        json_start = response_text.find('[')
        json_end = response_text.rfind(']') + 1
        if json_start != -1 and json_end != -1:
            response_text = response_text[json_start:json_end]
        
        filtered_results = json.loads(response_text)
        logger.info(f"Successfully parsed {len(filtered_results)} filtered listings")
        
        # Save the final filtered results
        save_openai_debug_data("final_results", {
            "timestamp": datetime.now().isoformat(),
            "user_preferences": user_preferences,
            "google_search_data_source": "direct_json",
            "filtered_results": filtered_results,
            "total_filtered": len(filtered_results)
        })
        
        # Format results to match expected structure
        ai_filtered_properties = []
        for i, property_data in enumerate(filtered_results):
            property_obj = {
                'title': property_data.get('title', ''),
                'description': property_data.get('desc', ''),
                'url': property_data.get('url', ''),
                'image_url': property_data.get('image', ''),
                'price': property_data.get('price', ''),
                'source': property_data.get('source', ''),
                'rank': property_data.get('rank', ''),
                'features': property_data.get('features', ''),
                'tags': property_data.get('tags', ''),
                'match': property_data.get('match', '')
            }
            ai_filtered_properties.append(property_obj)
        
        logger.info(f"Intelligent filtering completed. {len(ai_filtered_properties)} properties AI-filtered.")
        
        return {
            "success": True,
            "properties": ai_filtered_properties,
            "message": f"AI filtered {len(ai_filtered_properties)} properties",
            "total_original": len(google_search_data.get('items', [])),
            "total_ai_filtered": len(ai_filtered_properties)
        }
        
    except Exception as e:
        logger.error(f"Error in intelligent_filtered_json: {e}")
        
        # Save error information
        save_openai_debug_data("error", {
            "timestamp": datetime.now().isoformat(),
            "user_preferences": user_preferences,
            "google_search_data_source": "direct_json",
            "error": str(e),
            "error_type": type(e).__name__
        })
        
        return {
            "success": False,
            "error": str(e),
            "message": "Intelligent filtering failed"
        }

def streamlined_search(location: str, min_price: Optional[int] = None, 
                      max_price: Optional[int] = None, bedrooms: Optional[int] = None,
                      amenities: Optional[List[str]] = None, lifestyle: Optional[str] = None) -> Dict:
    """
    High-level function that calls simple_google_search(), then calls intelligent_filtered(), 
    and finally returns the final formatted result.
    
    Args:
        location: City/location to search
        min_price: Minimum price filter
        max_price: Maximum price filter
        bedrooms: Number of bedrooms
        amenities: List of amenities
        lifestyle: Lifestyle preferences
        
    Returns:
        Dictionary containing:
        - success: Boolean indicating success
        - properties: List of final properties
        - summary: Summary message
        - error: Error message (if failed)
    """
    try:
        # Step 1: Perform simple Google search
        logger.info("Step 1: Performing simple Google search...")
        search_result = simple_google_search(
            location=location,
            min_price=min_price,
            max_price=max_price,
            bedrooms=bedrooms,
            amenities=amenities,
            lifestyle=lifestyle
        )
        
        if not search_result.get('success', False):
            return {
                "success": False,
                "error": search_result.get('error', 'Search failed'),
                "message": "Google search failed"
            }
        
        json_file_path = search_result['file_path']
        logger.info(f"Search completed. Results saved to: {json_file_path}")
        
        # step 1.1: extract urls and images
        logger.info("Step 1.1: Extracting URLs and images...")
        urls_and_images = extract_urls_and_images(search_result['json_data'])
        logger.info(f"Extracted {len(urls_and_images['items'])} URLs and images")

        # Step 2: Apply intelligent filtering
        logger.info("Step 2: Applying intelligent filtering...")
        user_preferences = {
            'location': location,
            'min_price': min_price,
            'max_price': max_price,
            'bedrooms': bedrooms,
            'amenities': amenities or [],
            'lifestyle': lifestyle or []
        }
        
        # ai_result = intelligent_filtered(json_file_path, user_preferences)
        ai_result = intelligent_filtered_json(urls_and_images, user_preferences)
        
        if not ai_result.get('success', False):
            # Fallback to simple filtering if AI fails
            logger.warning("AI filtering failed, falling back to simple filtering...")
            simple_result = simple_filtered(json_file_path)
            
            if simple_result.get('success', False):
                return {
                    "success": True,
                    "properties": simple_result['properties'],
                    "summary": f"Found {len(simple_result['properties'])} properties using simple filtering (AI unavailable)",
                    "method_used": "simple_filtered"
                }
            else:
                return {
                    "success": False,
                    "error": "Both AI and simple filtering failed",
                    "message": "No filtering method available"
                }
        
        # Step 3: Return final results
        final_properties = ai_result['properties']
        
        summary = f"Found {len(final_properties)} properties using AI-powered filtering"
        if lifestyle:
            summary += f" matching your {lifestyle} lifestyle preferences"
        
        logger.info(f"Streamlined search completed successfully. {len(final_properties)} properties found.")
        
        return {
            "success": True,
            "properties": final_properties,
            "summary": summary,
            "method_used": "intelligent_filtered",
            "total_original": ai_result.get('total_original', 0),
            "total_filtered": len(final_properties)
        }
        
    except Exception as e:
        logger.error(f"Error in streamlined_search: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Streamlined search failed"
        }

def get_latest_google_search_file() -> Optional[str]:
    """
    Get the path to the most recent Google search JSON file.
    
    Returns:
        Path to the latest JSON file or None if no files found
    """
    try:
        results_dir = "results"
        if not os.path.exists(results_dir):
            return None
        
        # Find all Google search JSON files
        pattern = os.path.join(results_dir, "google_search_*.json")
        files = glob.glob(pattern)
        
        if not files:
            return None
        
        # Return the most recent file
        latest_file = max(files, key=os.path.getctime)
        return latest_file
        
    except Exception as e:
        logger.error(f"Error getting latest Google search file: {e}")
        return None

# Convenience functions for backward compatibility
def search_rentals_with_google(location: str, min_price: Optional[int] = None, 
                              max_price: Optional[int] = None, bedrooms: Optional[int] = None,
                              amenities: Optional[List[str]] = None, lifestyle: Optional[str] = None) -> Dict:
    """Backward compatibility function - calls streamlined_search"""
    return streamlined_search(location, min_price, max_price, bedrooms, amenities, lifestyle)

def get_google_status() -> Dict:
    """Get Google API status"""
    try:
        api_key = os.getenv('GOOGLE_API_KEY')
        search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
        
        if not api_key or not search_engine_id:
            return {
                "available": False,
                "status": "Configuration missing",
                "message": "Google API key or Search Engine ID not configured"
            }
        
        return {
            "available": True,
            "status": "Ready",
            "message": "Google Custom Search API is configured and ready"
        }
    except Exception as e:
        return {
            "available": False,
            "status": "Error",
            "message": f"Error checking Google API status: {str(e)}"
        }

    