from flask import Flask, render_template, request, flash, redirect, url_for
from scripts.rag_example import run_rag

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
import together
from typing import List, Dict, Optional
import warnings
from dotenv import load_dotenv


# Import feedback logger
try:
    from feedback_logger import log_user_feedback
    FEEDBACK_AVAILABLE = True
except ImportError as e:
    FEEDBACK_AVAILABLE = False
    print(f"Warning: Feedback logging not available: {e}")
# Import OpenAI rental search integration
try:
    from openai_rental_search import search_rentals_with_openai, get_openai_status
    OPENAI_AVAILABLE = True
except ImportError as e:
    OPENAI_AVAILABLE = False
    print(f"Warning: OpenAI integration not available: {e}")

# Import Google Custom Search integration
try:
    from google_rental_search import search_rentals_with_google, get_google_status
    GOOGLE_AVAILABLE = True
except ImportError as e:
    GOOGLE_AVAILABLE = False
    print(f"Warning: Google Custom Search integration not available: {e}")

# Load environment variables from .env file
load_dotenv()

# Suppress warnings
warnings.filterwarnings("ignore")

app = Flask(__name__)

# Initialize the data dictionary with rental property information
data_dict = {
    "downtown_apartments": "Downtown apartments are typically within walking distance to major business districts, restaurants, and entertainment venues. Average rent ranges from $1,800 to $3,500 for 1-2 bedroom units. Most buildings offer amenities like gyms, rooftop terraces, and 24/7 security.",
    "suburban_homes": "Suburban homes offer more space and privacy compared to city apartments. Typical features include 2-4 bedrooms, private yards, and garage parking. Rent ranges from $2,500 to $4,000. These areas are known for good schools and family-friendly environments.",
    "nearby_amenities": "Important amenities to consider: grocery stores (within 1 mile), public transportation (bus/train stops), schools (elementary, middle, high), parks and recreation areas, medical facilities, and shopping centers. These can significantly impact daily convenience and quality of life.",
    "rental_requirements": "Standard rental requirements include: proof of income (3x monthly rent), credit score check (minimum 650), security deposit (1-2 months rent), rental history, and references. Some properties may require additional fees for pets or parking.",
    "property_types": "Common rental property types: studio apartments (400-600 sq ft), 1-bedroom apartments (600-800 sq ft), 2-bedroom apartments (800-1200 sq ft), townhouses (1200-2000 sq ft), and single-family homes (1500-3000 sq ft). Each type offers different space and privacy levels.",
    "location_factors": "Key location factors to consider: commute time to work (ideal: under 30 minutes), distance to public transportation (ideal: under 0.5 miles), neighborhood safety ratings, walkability score, and proximity to essential services like hospitals and schools.",
    "rental_trends": "Current rental market trends show increasing demand for properties with home office spaces, outdoor areas, and energy-efficient features. Properties with smart home technology and high-speed internet infrastructure are particularly sought after."
}

def load_house_ads(file_path: str = 'houseAds.txt') -> List[Dict]:
    """Load house advertisements from a text file."""
    try:
        if not os.path.exists(file_path):
            return []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            houses = []
            for line in f:
                if line.strip():
                    try:
                        house = json.loads(line.strip())
                        houses.append(house)
                    except json.JSONDecodeError:
                        continue
            return houses
    except Exception as e:
        print(f"Error loading house ads: {e}")
        return []

def search_rentals_openai(location: str, min_price: Optional[int] = None, 
                         max_price: Optional[int] = None, bedrooms: Optional[int] = None,
                         amenities: Optional[List[str]] = None, lifestyle: Optional[str] = None) -> List[Dict]:
    """Search for rentals using OpenAI API with conversational approach."""
    if not OPENAI_AVAILABLE:
        print("OpenAI API not available")
        return []
    
    try:
        # Convert string values to integers
        min_price_int = int(min_price) if min_price and min_price.isdigit() else None
        max_price_int = int(max_price) if max_price and max_price.isdigit() else None
        bedrooms_int = int(bedrooms) if bedrooms and bedrooms.isdigit() else None
        
        print(f"Searching OpenAI for: {location}, price: ${min_price_int}-${max_price_int}, bedrooms: {bedrooms_int}")
        print(f"Amenities: {amenities}, Lifestyle: {lifestyle}")
        
        listings = search_rentals_with_openai(location, min_price_int, max_price_int, bedrooms_int, amenities, lifestyle)
        
        # Process the listings to ensure they have the required fields
        processed_listings = []
        for listing in listings:
            processed_listing = {
                'id': listing.get('id', len(processed_listings) + 1),
                'title': listing.get('title', 'No title'),
                'price': listing.get('price', 0),
                'location': listing.get('location', location),
                'bedrooms': listing.get('bedrooms'),
                'bathrooms': listing.get('bathrooms'),
                'amenities': listing.get('amenities', []),
                'description': listing.get('description', ''),
                'match_percentage': listing.get('match_percentage', 85),
                'contact': listing.get('contact', {'name': 'Contact for details', 'phone': 'N/A', 'email': 'N/A'}),
                'source_website': listing.get('source_website', 'OpenAI Search'),
                'listing_url': listing.get('listing_url'),
                'availability_date': listing.get('availability_date', datetime.now().strftime('%Y-%m-%d')),
                'features': listing.get('features', []),
                'images': listing.get('images', [])
            }
            processed_listings.append(processed_listing)
        
        return processed_listings
        
    except Exception as e:
        print(f"Error searching with OpenAI: {e}")
        return []

def search_rentals_google(location: str, min_price: Optional[int] = None, 
                         max_price: Optional[int] = None, bedrooms: Optional[int] = None,
                         amenities: Optional[List[str]] = None, lifestyle: Optional[str] = None) -> List[Dict]:
    """Search for rentals using Google Custom Search API."""
    if not GOOGLE_AVAILABLE:
        print("Google Custom Search API not available")
        return []
    
    try:
        # Convert string values to integers
        min_price_int = int(min_price) if min_price and min_price.isdigit() else None
        max_price_int = int(max_price) if max_price and max_price.isdigit() else None
        bedrooms_int = int(bedrooms) if bedrooms and bedrooms.isdigit() else None
        
        print(f"Searching Google Custom Search for: {location}, price: ${min_price_int}-${max_price_int}, bedrooms: {bedrooms_int}")
        print(f"Amenities: {amenities}, Lifestyle: {lifestyle}")
        
        listings = search_rentals_with_google(location, min_price_int, max_price_int, bedrooms_int, amenities, lifestyle)
        
        # Process the listings to ensure they have the required fields
        processed_listings = []
        for listing in listings:
            processed_listing = {
                'id': listing.get('id', len(processed_listings) + 1),
                'title': listing.get('title', 'No title'),
                'price': listing.get('price', 0),
                'location': listing.get('location', location),
                'bedrooms': listing.get('bedrooms'),
                'bathrooms': listing.get('bathrooms'),
                'amenities': listing.get('amenities', []),
                'description': listing.get('description', ''),
                'match_percentage': listing.get('match_percentage', 75),
                'contact': listing.get('contact', {'name': 'Contact for details', 'phone': 'N/A', 'email': 'N/A'}),
                'source_website': listing.get('source_website', 'Google Search'),
                'listing_url': listing.get('listing_url'),
                'availability_date': listing.get('availability_date', datetime.now().strftime('%Y-%m-%d')),
                'features': listing.get('features', []),
                'images': listing.get('images', [])
            }
            processed_listings.append(processed_listing)
        
        return processed_listings
        
    except Exception as e:
        print(f"Error searching with Google: {e}")
        return []

def rank_houses(houses: List[Dict], user_preferences: str) -> List[Dict]:
    """Rank houses based on user preferences using Together AI."""
    if not houses:
        return []
    
    # Build a comprehensive prompt for ranking
    prompt = f"""Given these house listings and user preferences, rank them from best to worst match.
User Preferences: {user_preferences}

House Listings:
{json.dumps(houses, indent=2)}

Please analyze each house and rank them based on how well they match the user's preferences.
Return a JSON array of the same houses, but with an added 'match_score' field (0-100) and 'match_reason' field explaining why it's a good or bad match.

Focus on:
- Price compatibility with budget
- Location preferences
- Bedroom/bathroom requirements
- Amenity matches
- Overall suitability

Return only valid JSON without any additional text.
"""

    try:
        response = together.Complete.create(
            prompt=prompt,
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            max_tokens=2000,
            temperature=0.7,
            top_p=0.7,
            top_k=50,
            repetition_penalty=1.1,
            stop=['</s>', 'Human:', 'Assistant:']
        )

        # Extract the response text
        response_text = response['output']['choices'][0]['text']
        
        # Clean the response to extract JSON
        response_text = response_text.strip()
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        
        ranked_houses = json.loads(response_text.strip())
        return sorted(ranked_houses, key=lambda x: x.get('match_score', 0), reverse=True)
        
    except Exception as e:
        print(f"Error processing AI response: {e}")
        # Fallback: return houses with default scores
        for house in houses:
            house['match_score'] = 50
            house['match_reason'] = 'Default score - AI processing failed'
        return houses

def build_user_preferences(filter_values: Dict) -> str:
    """Build user preferences string from filter values."""
    preferences = []
    
    if filter_values.get('location'):
        preferences.append(f"Location: {filter_values['location']}")
    
    if filter_values.get('min_price') and filter_values.get('max_price'):
        preferences.append(f"Budget: ${filter_values['min_price']}-${filter_values['max_price']}")
    elif filter_values.get('min_price'):
        preferences.append(f"Minimum budget: ${filter_values['min_price']}")
    elif filter_values.get('max_price'):
        preferences.append(f"Maximum budget: ${filter_values['max_price']}")
    
    if filter_values.get('num_bedrooms'):
        preferences.append(f"Bedrooms: {filter_values['num_bedrooms']}+")
    
    if filter_values.get('amenities'):
        preferences.append(f"Amenities: {', '.join(filter_values['amenities'])}")
    
    if filter_values.get('lifestyle'):
        preferences.append(f"Lifestyle: {filter_values['lifestyle']}")
    
    return " | ".join(preferences) if preferences else "No specific preferences"

@app.route('/', methods=['GET', 'POST'])
def index():
    answer = None
    sources = None
    filters = []
    properties = []
    summary = None
    feedback_msg = None
    search_method = "google" if GOOGLE_AVAILABLE else "local"  # Default to Google search if available

    # Default filter values
    filter_values = {
        'location': '',
        'min_price': '',
        'max_price': '',
        'num_bedrooms': '',
        'amenities': [],
        'lifestyle': ''
    }

    if request.method == 'POST':
        # Q&A section
        question = request.form.get('question')
        if question:
            answer = run_rag(data_dict, question)
            if "Source Used:" in answer:
                answer_text, sources_text = answer.split("Source Used:")
                answer = answer_text.strip()
                sources = [s.strip() for s in sources_text.split(",")]

        # Property search section
        filter_values['location'] = request.form.get('location', '')
        filter_values['min_price'] = request.form.get('min_price', '')
        filter_values['max_price'] = request.form.get('max_price', '')
        filter_values['num_bedrooms'] = request.form.get('num_bedrooms', '')
        
        # Handle amenities - both checkboxes and custom input fields
        checkbox_amenities = request.form.getlist('amenities')
        custom_amenities = request.form.getlist('custom_amenities[]')
        # Filter out empty custom amenities
        custom_amenities = [amenity.strip() for amenity in custom_amenities if amenity.strip()]
        # Combine both types of amenities
        filter_values['amenities'] = checkbox_amenities + custom_amenities
        
        filter_values['lifestyle'] = request.form.get('lifestyle', '')
        search_method = request.form.get('search_method', 'local')

        # Build filters for display
        if filter_values['min_price'] and filter_values['max_price']:
            filters.append(f"Budget: ${filter_values['min_price']}-${filter_values['max_price']}")
        elif filter_values['min_price']:
            filters.append(f"Min Budget: ${filter_values['min_price']}")
        elif filter_values['max_price']:
            filters.append(f"Max Budget: ${filter_values['max_price']}")
        if filter_values['num_bedrooms']:
            filters.append(f"{filter_values['num_bedrooms']}+ Bedrooms")
        if filter_values['location']:
            filters.append(f"Near {filter_values['location']}")
        if filter_values['amenities']:
            filters.append(f"Amenities: {', '.join(filter_values['amenities'])}")
        if filter_values['lifestyle']:
            filters.append(f"Lifestyle: {filter_values['lifestyle']}")

        # Search for properties using Google Custom Search
        try:
            if filter_values['location']:
                # Use Google Custom Search API
                print("Using Google Custom Search API...")
                houses = search_rentals_google(
                    filter_values['location'],
                    filter_values['min_price'],
                    filter_values['max_price'],
                    filter_values['num_bedrooms'],
                    filter_values['amenities'],
                    filter_values['lifestyle']
                )
                search_source = "Google Custom Search API"

                # --- Start: New Post-Search Filtering ---
                
                filtered_houses = []
                min_price_filter = int(filter_values['min_price']) if filter_values['min_price'] else None
                max_price_filter = int(filter_values['max_price']) if filter_values['max_price'] else None
                bedrooms_filter = int(filter_values['num_bedrooms']) if filter_values['num_bedrooms'] else None

                for house in houses:
                    price = house.get('price')
                    bedrooms = house.get('bedrooms')
                    
                    # Price check
                    if price and min_price_filter and price < min_price_filter:
                        continue
                    if price and max_price_filter and price > max_price_filter:
                        continue
                        
                    # Bedroom check
                    if bedrooms and bedrooms_filter and bedrooms < bedrooms_filter:
                        continue
                        
                    filtered_houses.append(house)
                
                houses = filtered_houses

                # --- Start: Prioritize Zillow results ---
                houses.sort(key=lambda house: house.get('source_website') != 'Zillow')
                # --- End: Prioritize Zillow results ---

                # --- End: New Post-Search Filtering ---

            else:
                houses = []
                search_source = "Local Database"
            
            if houses:
                # Format properties for display
                for i, house in enumerate(houses):
                    # Skip properties with no price
                    price = house.get('price')
                    if not price or price == 'N/A' or price == 0:
                        continue

                    tags = []
                    if house.get('bedrooms'):
                        tags.append(f"{house['bedrooms']} BR")
                    if house.get('bathrooms'):
                        tags.append(f"{house['bathrooms']} Bath")
                    if house.get('location'):
                        tags.append(f"{house['location']}")
                    if house.get('amenities'):
                        # Take first few amenities for display
                        amenity_tags = house['amenities'][:3] if isinstance(house['amenities'], list) else []
                        tags.extend(amenity_tags)
                    
                    properties.append({
                        'title': house.get('title', 'No title'),
                        'price': price,
                        'tags': tags,
                        'top_match': i == 0,
                        'match_score': house.get('match_score', 50),
                        'url': house.get('listing_url', '#'),
                        'source': house.get('source_website', search_source),
                        'match_reason': house.get('match_reason', 'AI analysis')
                    })
                
                summary = f"I found {len(properties)} properties matching your criteria using {search_source}."
                if len(properties) > 0:
                    summary += f" The top match has a {properties[0].get('match_score', 50)}% compatibility score!"
                else:
                    summary = "No properties found with a valid price. Try adjusting your search criteria."

            else:
                summary = "No properties found using Google Custom Search API. Try adjusting your search criteria."
                
        except Exception as e:
            summary = f"Error processing house listings: {str(e)}"
            print(f"Error in house processing: {e}")

        if 'feedback' in request.form:
            feedback = request.form.get('feedback')
            if feedback:
                log_user_feedback(feedback)
                feedback_msg = "Thank you for your feedback!"

    # Get OpenAI API status for the template
    openai_status = get_openai_status() if OPENAI_AVAILABLE else {'available': False, 'status': 'Not installed'}
    
    # Get Google Custom Search API status for the template
    google_status = get_google_status() if GOOGLE_AVAILABLE else {'available': False, 'status': 'Not installed'}

    return render_template('index.html', 
                         answer=answer, 
                         sources=sources, 
                         filters=filters, 
                         properties=properties, 
                         summary=summary, 
                         filter_values=filter_values, 
                         feedback_msg=feedback_msg,
                         openai_available=OPENAI_AVAILABLE,
                         openai_status=openai_status,
                         google_available=GOOGLE_AVAILABLE,
                         google_status=google_status)

if __name__ == '__main__':
    # Set up Together AI (you'll need to set this as an environment variable)
    together.api_key = os.getenv('TOGETHER_API_KEY')
    if not together.api_key:
        print("Warning: TOGETHER_API_KEY environment variable not set. AI ranking will not work.")
    
    # Check Google Custom Search API status
    if GOOGLE_AVAILABLE:
        status = get_google_status()
        if status['available']:
            print("✅ Google Custom Search API is available and ready to use")
        else:
            print("⚠️  Google Custom Search API not configured. Set GOOGLE_API_KEY and GOOGLE_SEARCH_ENGINE_ID environment variables.")
    else:
        print("⚠️  Google Custom Search integration not available. Check dependencies and API key setup.")
    
    # Check OpenAI API status
    if OPENAI_AVAILABLE:
        status = get_openai_status()
        if status['available']:
            print("✅ OpenAI API is available and ready to use")
        else:
            print("⚠️  OpenAI API key not set. Set OPENAI_API_KEY environment variable to enable real-time search.")
    else:
        print("⚠️  OpenAI integration not available. Check dependencies and API key setup.")
    
    # Get configuration from environment variables (Hugging Face Spaces compatible)
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 7860))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    print(f"🚀 Starting House Crush on {host}:{port}")
    print(f"🌐 Access your app at: http://localhost:{port}")
    app.run(host=host, port=port, debug=debug)
