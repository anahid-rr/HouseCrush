#!/usr/bin/env python3
"""
Test script for OpenAI rental search functionality
"""

import os
from dotenv import load_dotenv
from openai_rental_search import search_rentals_with_openai, get_openai_status

# Load environment variables
load_dotenv()

def test_openai_search():
    """Test the OpenAI rental search functionality."""
    
    # Check API status
    print("Checking OpenAI API status...")
    status = get_openai_status()
    print(f"Status: {status}")
    
    if not status['available']:
        print("❌ OpenAI API not available. Please check your API key.")
        return
    
    print("✅ OpenAI API is available!")
    
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
        results = search_rentals_with_openai(
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

if __name__ == "__main__":
    test_openai_search() 