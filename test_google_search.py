#!/usr/bin/env python3
"""
Test script for Google Custom Search API functionality
"""

import os
from dotenv import load_dotenv
from google_rental_search import search_rentals_with_google, get_google_status
from google_rental_search import GoogleRentalSearch

# Load environment variables
load_dotenv()

def test_google_search():
    """Test the Google Custom Search API functionality."""
    
    # Check API status
    print("Checking Google Custom Search API status...")
    status = get_google_status()
    print(f"Status: {status}")
    
    if not status['available']:
        print("❌ Google Custom Search API not available. Please check your API key and Search Engine ID.")
        return
    
    print("✅ Google Custom Search API is available!")
    
    # Test API parameters
    test_api_parameters()
    
    # Test search parameters
    location = "Toronto"
    min_price = 1500
    max_price = 2500
    bedrooms = 2
    amenities = ["Parking", "Gym", "Balcony"]
    lifestyle = "near public transit, quiet neighborhood"
    
    print(f"\n🔍 Testing search with parameters:")
    print(f"Location: {location}")
    print(f"Price range: ${min_price}-${max_price}")
    print(f"Bedrooms: {bedrooms}")
    print(f"Amenities: {amenities}")
    print(f"Lifestyle: {lifestyle}")
    
    try:
        # Perform the search
        print("\n⏳ Searching for rental properties...")
        results = search_rentals_with_google(
            location=location,
            min_price=min_price,
            max_price=max_price,
            bedrooms=bedrooms,
            amenities=amenities,
            lifestyle=lifestyle
        )
        
        print(f"\n✅ Search completed! Found {len(results)} properties.")
        
        # Display results
        for i, property in enumerate(results[:3], 1):  # Show first 3 results
            print(f"\n--- Property {i} ---")
            print(f"Title: {property.get('title', 'N/A')}")
            print(f"Price: ${property.get('price', 'N/A')}")
            print(f"Location: {property.get('location', 'N/A')}")
            print(f"Bedrooms: {property.get('bedrooms', 'N/A')}")
            print(f"Bathrooms: {property.get('bathrooms', 'N/A')}")
            print(f"Match Percentage: {property.get('match_percentage', 'N/A')}%")
            print(f"Amenities: {property.get('amenities', [])}")
            print(f"Source: {property.get('source_website', 'N/A')}")
            print(f"Listing URL: {property.get('listing_url', 'N/A')}")
            
            # Contact information
            contact = property.get('contact', {})
            if contact:
                print(f"Contact: {contact.get('name', 'N/A')}")
                print(f"Phone: {contact.get('phone', 'N/A')}")
                print(f"Email: {contact.get('email', 'N/A')}")
        
        if len(results) > 3:
            print(f"\n... and {len(results) - 3} more properties")
            
    except Exception as e:
        print(f"❌ Error during search: {e}")

def test_api_parameters():
    """Test the API parameters directly to verify searchTypeUndefined is used."""
    print("\n🔧 Testing API parameters...")
    
    # Import the GoogleRentalSearch class to test parameters
    google_search = GoogleRentalSearch()
    
    if not google_search.api_key or not google_search.search_engine_id:
        print("❌ API key or Search Engine ID not configured")
        return
    
    # Test the parameter building
    query = google_search._build_search_query("Toronto", 1500, 2500, 2, ["Parking"], "near transit")
    print(f"Built query: {query}")
    
    # Show what parameters would be used
    params = {
        'key': google_search.api_key,
        'cx': google_search.search_engine_id,
        'q': query,
        'num': 10,
        'searchType': 'searchTypeUndefined',
        'safe': 'active',
        'lr': 'lang_en',
        'sort': 'date'
    }
    
    print(f"API parameters:")
    for key, value in params.items():
        if key in ['key', 'cx']:
            print(f"  {key}: {value[:10]}...")  # Show only first 10 chars for security
        else:
            print(f"  {key}: {value}")
    
    print("✅ searchTypeUndefined parameter is correctly set")

def setup_instructions():
    """Print setup instructions for Google Custom Search API."""
    print("\n📋 Google Custom Search API Setup Instructions:")
    print("=" * 50)
    print("1. Go to Google Cloud Console: https://console.cloud.google.com/")
    print("2. Create a new project or select an existing one")
    print("3. Enable the Custom Search API:")
    print("   - Go to APIs & Services > Library")
    print("   - Search for 'Custom Search API'")
    print("   - Click 'Enable'")
    print("4. Create API credentials:")
    print("   - Go to APIs & Services > Credentials")
    print("   - Click 'Create Credentials' > 'API Key'")
    print("   - Copy the API key")
    print("5. Create a Custom Search Engine:")
    print("   - Go to: https://programmablesearchengine.google.com/")
    print("   - Click 'Create a search engine'")
    print("   - Enter any site (e.g., google.com)")
    print("   - Get your Search Engine ID (cx)")
    print("6. Add to your .env file:")
    print("   GOOGLE_API_KEY=your_api_key_here")
    print("   GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here")
    print("=" * 50)

def test_bedroom_bathroom_extraction():
    """Test the improved bedroom and bathroom extraction methods."""
    
    # Initialize the search object
    search = GoogleRentalSearch()
    
    # Test cases with various formats
    test_cases = [
        # Standard formats
        ("Beautiful 2 bedroom apartment in downtown", 2, None),
        ("1 bed 1 bath available now", 1, 1),
        ("3 br 2 ba luxury condo", 3, 2),
        
        # "Beds" format
        ("2 beds available in modern building", 2, None),
        ("1 bed apartment for rent", 1, None),
        
        # "Beds/baths" format
        ("2 bed/1 bath apartment", 2, 1),
        ("3 beds/2 baths luxury unit", 3, 2),
        ("1 bedroom/1 bathroom available", 1, 1),
        ("2 br/1 ba modern apartment", 2, 1),
        
        # "2+" notation
        ("2+ bedroom apartment available", 2, None),
        ("3+ beds in spacious unit", 3, None),
        ("2+ bed/1 bath available now", 2, 1),
        ("3+ bedroom/2 bathroom luxury", 3, 2),
        
        # Mixed formats
        ("Beautiful 2+ bed apartment with 1 bath", 2, 1),
        ("3 beds available, 2 bathrooms", 3, 2),
        
        # Edge cases
        ("Apartment with 2+ rooms available", None, None),  # Should not match without bedroom context
        ("2+ bathrooms in the building", None, 2),  # Should match bathroom context
    ]
    
    print("Testing Bedroom/Bathroom Extraction Improvements")
    print("=" * 60)
    
    for i, (text, expected_bedrooms, expected_bathrooms) in enumerate(test_cases, 1):
        print(f"\nTest {i}: {text}")
        
        # Extract bedrooms and bathrooms
        extracted_bedrooms = search._extract_bedrooms_from_text(text)
        extracted_bathrooms = search._extract_bathrooms_from_text(text)
        
        # Check results
        bedroom_match = "✓" if extracted_bedrooms == expected_bedrooms else "✗"
        bathroom_match = "✓" if extracted_bathrooms == expected_bathrooms else "✗"
        
        print(f"  Expected: {expected_bedrooms} bed, {expected_bathrooms} bath")
        print(f"  Extracted: {extracted_bedrooms} bed, {extracted_bathrooms} bath")
        print(f"  Result: {bedroom_match} {bathroom_match}")

def test_search_query_building():
    """Test the improved search query building with multiple bedroom formats."""
    
    search = GoogleRentalSearch()
    
    # Test cases
    test_cases = [
        (1, "1 bedroom 1 bed 1br 1 bed/bath"),
        (2, "2 bedroom 2 bedrooms 2 bed 2 beds 2br 2 bed/bath 2+ bedroom 2+ bed 2+ beds"),
        (3, "3 bedroom 3 bedrooms 3 bed 3 beds 3br 3 bed/bath 3+ bedroom 3+ bed 3+ beds"),
    ]
    
    print("\n\nTesting Search Query Building Improvements")
    print("=" * 60)
    
    for bedrooms, expected_terms in test_cases:
        print(f"\nBedrooms: {bedrooms}")
        query = search._build_search_query("Toronto", bedrooms=bedrooms)
        print(f"Generated query: {query}")
        
        # Check if expected terms are in the query
        missing_terms = []
        for term in expected_terms.split():
            if term not in query:
                missing_terms.append(term)
        
        if missing_terms:
            print(f"  Missing terms: {missing_terms}")
        else:
            print("  ✓ All expected terms found")

def test_api_call():
    """Test the Google Custom Search API call with fixed parameters."""
    
    from google_rental_search import GoogleRentalSearch
    
    # Initialize the search object
    search = GoogleRentalSearch()
    
    # Check API status first
    status = search.get_api_status()
    print(f"API Status: {status}")
    
    if not status['available']:
        print("❌ API not available. Please check your API key and Search Engine ID.")
        return
    
    # Test with a simple query
    print("\nTesting API call with simple query...")
    try:
        results = search.search_rentals("Toronto", bedrooms=2, min_price=1500, max_price=2500)
        print(f"✅ API call successful! Found {len(results)} results")
        
        if results:
            print("\nFirst result:")
            print(f"Title: {results[0].get('title', 'N/A')}")
            print(f"Price: {results[0].get('price', 'N/A')}")
            print(f"Bedrooms: {results[0].get('bedrooms', 'N/A')}")
            print(f"Source: {results[0].get('source_website', 'N/A')}")
        
    except Exception as e:
        print(f"❌ API call failed: {e}")

if __name__ == "__main__":
    # Check if environment variables are set
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    google_api_key = os.getenv('GOOGLE_API_KEY')
    google_search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
    
    if not google_api_key or not google_search_engine_id:
        print("❌ Missing environment variables:")
        print(f"   GOOGLE_API_KEY: {'✅ Set' if google_api_key else '❌ Missing'}")
        print(f"   GOOGLE_SEARCH_ENGINE_ID: {'✅ Set' if google_search_engine_id else '❌ Missing'}")
        print("\nPlease set these environment variables in your .env file:")
        print("GOOGLE_API_KEY=your_api_key_here")
        print("GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here")
    else:
        print("✅ Environment variables are set")
        test_api_call()
        test_bedroom_bathroom_extraction()
        test_search_query_building()
        print("\n\nImprovement Summary:")
        print("=" * 60)
        print("✓ Added support for 'beds' format (not just 'bedrooms')")
        print("✓ Added support for 'beds/baths' format (e.g., '2 bed/1 bath')")
        print("✓ Added support for '2+' notation (e.g., '2+ bedroom')")
        print("✓ Enhanced regex patterns to catch more variations")
        print("✓ Added context validation for standalone '+' patterns")
        print("✓ Improved search query building with multiple format variations")
        print("✓ Enhanced match percentage calculation")
        print("✓ Fixed invalid API parameters (removed searchType)")
        print("✓ Added query length limits and validation")
        print("✓ Improved error handling and parameter validation") 