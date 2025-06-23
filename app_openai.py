#!/usr/bin/env python3
"""
House Crush - OpenAI Version (GPT-4o-mini)
A rental property assistant that uses OpenAI API for intelligent property search and recommendations.
"""

from flask import Flask, render_template, request
import json
import os
from datetime import datetime
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

# Import feedback logger
try:
    from feedback_logger import log_user_feedback
    FEEDBACK_AVAILABLE = True
except ImportError as e:
    FEEDBACK_AVAILABLE = False
    print(f"Warning: Feedback logging not available: {e}")

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

def search_rentals_openai(location: str, min_price: Optional[int] = None, 
                         max_price: Optional[int] = None, bedrooms: Optional[int] = None,
                         amenities: Optional[List[str]] = None, lifestyle: Optional[str] = None) -> List[Dict]:
    """Search for rentals using OpenAI API with GPT-4o-mini."""
    if not OPENAI_AVAILABLE:
        print("OpenAI API not available")
        return []
    
    try:
        # Convert string values to integers
        min_price_int = int(min_price) if min_price and str(min_price).isdigit() else None
        max_price_int = int(max_price) if max_price and str(max_price).isdigit() else None
        bedrooms_int = int(bedrooms) if bedrooms and str(bedrooms).isdigit() else None
        
        print(f"🔍 Searching OpenAI (GPT-4o-mini) for: {location}")
        print(f"💰 Price range: ${min_price_int}-${max_price_int}")
        print(f"🛏️ Bedrooms: {bedrooms_int}")
        print(f"🏠 Amenities: {amenities}")
        print(f"🌍 Lifestyle: {lifestyle}")
        
        # Call OpenAI API with GPT-4o-mini
        listings = search_rentals_with_openai(location, min_price_int, max_price_int, bedrooms_int, amenities, lifestyle)
        
        print(f"✅ Found {len(listings)} listings from OpenAI GPT-4o-mini")
        
        # Process listings to ensure they have the required fields
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
        print(f"❌ Error searching with OpenAI: {e}")
        return []

def simple_qa_system(question: str) -> str:
    """Simple Q&A system using the data dictionary."""
    question_lower = question.lower()
    
    # Simple keyword matching
    if any(word in question_lower for word in ['requirement', 'need', 'document']):
        return data_dict.get('rental_requirements', 'Contact individual properties for specific requirements.')
    
    elif any(word in question_lower for word in ['amenity', 'amenities', 'feature']):
        return data_dict.get('nearby_amenities', 'Consider proximity to essential services and lifestyle amenities.')
    
    elif any(word in question_lower for word in ['downtown', 'suburban', 'city', 'urban']):
        return f"{data_dict.get('downtown_apartments', '')} {data_dict.get('suburban_homes', '')}"
    
    elif any(word in question_lower for word in ['trend', 'market', 'current']):
        return data_dict.get('rental_trends', 'Market conditions vary by location and time.')
    
    elif any(word in question_lower for word in ['type', 'property', 'apartment', 'house']):
        return data_dict.get('property_types', 'Various property types are available depending on your needs.')
    
    elif any(word in question_lower for word in ['location', 'area', 'neighborhood']):
        return data_dict.get('location_factors', 'Location factors vary by individual preferences and needs.')
    
    else:
        return "I can help you with rental requirements, amenities, property types, location factors, and market trends. Please ask a specific question about rental properties."

def handle_feedback_submission(feedback: str, request) -> str:
    """Handle user feedback submission."""
    try:
        if FEEDBACK_AVAILABLE:
            log_user_feedback(feedback, request)
            return "Thank you for your feedback! It has been logged successfully."
        else:
            # Fallback to simple file logging
            with open('user_feedback.log', 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {feedback.strip()}\n")
            return "Thank you for your feedback!"
            
    except Exception as e:
        print(f"Error handling feedback: {e}")
        return "Thank you for your feedback! (Note: Could not save to log)"

def format_property_for_display(house: Dict, index: int) -> Dict:
    """
    Format a property for display with enhanced features for GPT-4o-mini results.
    
    Args:
        house: The property data
        index: Index in the results list
        
    Returns:
        Dict: Formatted property for display
    """
    # Handle price formatting
    price = house.get('price')
    if price is None or price == 0 or price == 'N/A':
        display_price = 'Contact for details'
    else:
        try:
            # Ensure price is a number and format it
            price_num = int(float(price))
            display_price = f"${price_num:,}/month"
        except (ValueError, TypeError):
            display_price = 'Contact for details'
    
    # Handle URL formatting - use listing_url if available
    url = house.get('listing_url') or house.get('source_website')
    if not url or url == '#' or url == 'N/A':
        display_url = None
    else:
        # Ensure URL has proper protocol
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        display_url = url
    
    # Build tags
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
    
    return {
        'title': house.get('title', 'No title'),
        'price': display_price,
        'price_raw': price,  # Keep raw price for sorting
        'tags': tags,
        'top_match': index == 0,
        'match_score': house.get('match_score', 50),
        'match_percentage': house.get('match_percentage', 85),
        'url': display_url,
        'source': house.get('source_website', 'OpenAI Search'),
        'match_reason': house.get('match_reason', 'AI analysis'),
        'location': house.get('location', ''),
        'bedrooms': house.get('bedrooms'),
        'bathrooms': house.get('bathrooms'),
        'amenities': house.get('amenities', []),
        'description': house.get('description', ''),
        'source_website': house.get('source_website', ''),
        'listing_url': house.get('listing_url'),
        'contact': house.get('contact', {}),
        'availability_date': house.get('availability_date'),
        'features': house.get('features', []),
        'images': house.get('images', [])
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    answer = None
    sources = None
    filters = []
    properties = []
    summary = None
    feedback_msg = None

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
            answer = simple_qa_system(question)
            sources = ['House Crush Knowledge Base']

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

        # Search for properties using OpenAI GPT-4o-mini
        try:
            if OPENAI_AVAILABLE and filter_values['location']:
                print("🚀 Starting OpenAI GPT-4o-mini search...")
                houses = search_rentals_openai(
                    filter_values['location'],
                    filter_values['min_price'],
                    filter_values['max_price'],
                    filter_values['num_bedrooms'],
                    filter_values['amenities'],
                    filter_values['lifestyle']
                )
                
                if houses:
                    # Format properties for display (top 10)
                    for i, house in enumerate(houses[:10]):
                        formatted_property = format_property_for_display(house, i)
                        properties.append(formatted_property)
                    
                    # Create summary with match information
                    top_match = houses[0] if houses else None
                    match_percentage = top_match.get('match_percentage', 85) if top_match else 0
                    summary = f"I found {len(houses)} properties matching your criteria using OpenAI GPT-4o-mini. Top match has {match_percentage}% compatibility!"
                else:
                    summary = "No properties found using OpenAI GPT-4o-mini. Try adjusting your search criteria or check your API key."
            else:
                if not filter_values['location']:
                    summary = "Please enter a location to search for properties."
                elif not OPENAI_AVAILABLE:
                    summary = "OpenAI API is not available. Please check your API key configuration."
                
        except Exception as e:
            summary = f"Error processing search: {str(e)}"
            print(f"❌ Error in search processing: {e}")

        # Handle feedback submission
        if 'feedback' in request.form:
            feedback = request.form.get('feedback')
            if feedback:
                feedback_msg = handle_feedback_submission(feedback, request)

    # Get OpenAI API status for the template
    openai_status = get_openai_status() if OPENAI_AVAILABLE else {'available': False, 'status': 'Not installed'}

    return render_template('index.html', 
                         answer=answer, 
                         sources=sources, 
                         filters=filters, 
                         properties=properties, 
                         summary=summary, 
                         filter_values=filter_values, 
                         feedback_msg=feedback_msg,
                         openai_available=OPENAI_AVAILABLE,
                         openai_status=openai_status)

if __name__ == '__main__':
    # Check OpenAI API status
    if OPENAI_AVAILABLE:
        status = get_openai_status()
        if status['available']:
            print("✅ OpenAI API is available and ready to use")
            print(f"🤖 Model: GPT-4o-mini")
            print(f"⚡ Status: {status['status']}")
        else:
            print("⚠️  OpenAI API key not set. Set OPENAI_API_KEY environment variable to enable real-time search.")
    else:
        print("⚠️  OpenAI integration not available. Check dependencies and API key setup.")
    
    # Check feedback logging
    if FEEDBACK_AVAILABLE:
        print("✅ Feedback logging is available")
    else:
        print("⚠️  Feedback logging not available - using fallback method")
    
    print("\n🚀 Starting House Crush OpenAI Edition (GPT-4o-mini)...")
    print("📱 Open your browser to: http://127.0.0.1:5000")
    print("🤖 Using OpenAI GPT-4o-mini for ultra-fast rental search")
    print("💰 Cost-effective and high-performance search")
    print("📝 Feedback logging enabled")
    
    app.run(debug=True) 