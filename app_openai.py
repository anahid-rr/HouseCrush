#!/usr/bin/env python3
"""
House Crush - OpenAI Version
A rental property assistant that uses OpenAI API for intelligent property search and recommendations.
"""

from flask import Flask, render_template, request, flash, redirect, url_for
from scripts.rag_example import run_rag
from house_scraper import log_user_feedback
import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
import together
from typing import List, Dict, Optional
import warnings
from dotenv import load_dotenv

# Import OpenAI integration
try:
    from openai_rental_search import search_rentals_with_openai, get_openai_status
    OPENAI_AVAILABLE = True
except ImportError as e:
    OPENAI_AVAILABLE = False
    print(f"Warning: OpenAI integration not available: {e}")

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
                         max_price: Optional[int] = None, bedrooms: Optional[int] = None) -> List[Dict]:
    """Search for rentals using OpenAI API."""
    if not OPENAI_AVAILABLE:
        print("OpenAI API not available")
        return []
    
    try:
        # Convert string values to integers
        min_price_int = int(min_price) if min_price and min_price.isdigit() else None
        max_price_int = int(max_price) if max_price and max_price.isdigit() else None
        bedrooms_int = int(bedrooms) if bedrooms and bedrooms.isdigit() else None
        
        print(f"Searching OpenAI for: {location}, price: ${min_price_int}-${max_price_int}, bedrooms: {bedrooms_int}")
        
        listings = search_rentals_with_openai(location, min_price_int, max_price_int, bedrooms_int)
        
        # Add match scores for consistency with local data
        for listing in listings:
            listing['match_score'] = 85  # Default high score for real-time data
            listing['match_reason'] = 'Real-time search result from OpenAI API'
        
        return listings
        
    except Exception as e:
        print(f"Error searching with OpenAI: {e}")
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
    
    return " | ".join(preferences) if preferences else "No specific preferences"

@app.route('/', methods=['GET', 'POST'])
def index():
    answer = None
    sources = None
    filters = []
    properties = []
    summary = None
    feedback_msg = None
    search_method = "local"  # Default to local search

    # Default filter values
    filter_values = {
        'location': '',
        'min_price': '',
        'max_price': '',
        'num_bedrooms': ''
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

        # Search for properties based on selected method
        try:
            if search_method == 'openai' and OPENAI_AVAILABLE and filter_values['location']:
                # Use OpenAI API for real-time search
                print("Using OpenAI API for real-time search...")
                houses = search_rentals_openai(
                    filter_values['location'],
                    filter_values['min_price'],
                    filter_values['max_price'],
                    filter_values['num_bedrooms']
                )
                search_source = "OpenAI API (Real-time)"
            else:
                # Use local file-based search
                print("Using local database for search...")
                houses = load_house_ads()
                search_source = "Local Database"
                
                if houses and filter_values['location']:
                    # Build user preferences string
                    user_preferences = build_user_preferences(filter_values)
                    
                    # Rank houses using AI
                    houses = rank_houses(houses, user_preferences)
            
            if houses:
                # Format properties for display (top 8)
                for i, house in enumerate(houses[:8]):
                    tags = []
                    if house.get('bedrooms'):
                        tags.append(f"{house['bedrooms']} BR")
                    if house.get('bathrooms'):
                        tags.append(f"{house['bathrooms']} Bath")
                    if house.get('location'):
                        tags.append(house['location'])
                    if house.get('amenities'):
                        # Take first few amenities for display
                        amenity_tags = house['amenities'][:3] if isinstance(house['amenities'], list) else []
                        tags.extend(amenity_tags)
                    
                    properties.append({
                        'title': house.get('title', 'No title'),
                        'price': house.get('price', 'N/A'),
                        'tags': tags,
                        'top_match': i == 0,
                        'match_score': house.get('match_score', 50),
                        'url': house.get('url', '#'),
                        'source': house.get('source_website', search_source),
                        'match_reason': house.get('match_reason', 'AI analysis')
                    })
                
                summary = f"I found {len(houses)} properties matching your criteria using {search_source}. The top match has a {houses[0].get('match_score', 50)}% compatibility score!" if houses else "No properties found for your criteria."
            else:
                if search_method == 'openai':
                    summary = "No properties found using OpenAI API. Try adjusting your search criteria or use local database."
                else:
                    summary = "No house listings available in the database. Please check the houseAds.txt file or try OpenAI API search."
                
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

    return render_template('index_openai.html', 
                         answer=answer, 
                         sources=sources, 
                         filters=filters, 
                         properties=properties, 
                         summary=summary, 
                         filter_values=filter_values, 
                         feedback_msg=feedback_msg,
                         search_method=search_method,
                         openai_available=OPENAI_AVAILABLE,
                         openai_status=openai_status)

if __name__ == '__main__':
    # Set up Together AI (you'll need to set this as an environment variable)
    together.api_key = os.getenv('TOGETHER_API_KEY')
    if not together.api_key:
        print("Warning: TOGETHER_API_KEY environment variable not set. AI ranking will not work.")
    
    # Check OpenAI API status
    if OPENAI_AVAILABLE:
        status = get_openai_status()
        if status['available']:
            print("✅ OpenAI API is available and ready to use")
        else:
            print("⚠️  OpenAI API key not set. Set OPENAI_API_KEY environment variable to enable real-time search.")
    else:
        print("⚠️  OpenAI integration not available. Check dependencies and API key setup.")
    
    app.run(debug=True) 