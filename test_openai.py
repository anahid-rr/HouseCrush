#!/usr/bin/env python3
"""
Test script for OpenAI API integration
This script tests the OpenAI rental search functionality using the official API.
"""

import os
from dotenv import load_dotenv
from openai_rental_search import search_rentals_with_openai, get_openai_status

# Load environment variables
load_dotenv()

def test_openai_integration():
    print("🧪 Testing OpenAI API Integration")
    print("=" * 50)
    
    # Check API status
    status = get_openai_status()
    print(f"API Status: {status['status']}")
    print(f"API Key Set: {status['api_key_set']}")
    print(f"Available: {status['available']}")
    
    if not status['available']:
        print("\n❌ OpenAI API not available")
        if not status['api_key_set']:
            print("Please set OPENAI_API_KEY environment variable")
        else:
            print(f"API Error: {status['status']}")
        return
    
    # Test search
    print(f"\n🔍 Testing rental search...")
    test_location = "Toronto"
    test_min_price = 1500
    test_max_price = 2500
    test_bedrooms = 2
    
    print(f"Searching for: {test_location}")
    print(f"Price range: ${test_min_price}-${test_max_price}")
    print(f"Bedrooms: {test_bedrooms}")
    
    try:
        listings = search_rentals_with_openai(
            test_location, 
            test_min_price, 
            test_max_price, 
            test_bedrooms
        )
        
        if listings:
            print(f"\n✅ Success! Found {len(listings)} listings")
            print("\n📋 Sample listings:")
            
            for i, listing in enumerate(listings[:3]):
                print(f"\n{i+1}. {listing.get('title', 'N/A')}")
                print(f"   Price: ${listing.get('price', 'N/A')}")
                print(f"   Location: {listing.get('location', 'N/A')}")
                print(f"   Source: {listing.get('source', 'N/A')}")
                print(f"   Website: {listing.get('source_website', 'N/A')}")
                if listing.get('description'):
                    print(f"   Description: {listing.get('description', 'N/A')[:100]}...")
            
            if len(listings) > 3:
                print(f"\n... and {len(listings) - 3} more listings")
        else:
            print("\n⚠️  No listings found")
            print("This might be due to:")
            print("- No available listings in the specified criteria")
            print("- API rate limiting")
            print("- Network issues")
            print("- Location not found")
    
    except Exception as e:
        print(f"\n❌ Error during search: {str(e)}")
        print("Check your API key and internet connection")

def show_setup_instructions():
    print("\n🔧 Setup Instructions:")
    print("1. Get an OpenAI API key from: https://platform.openai.com/api-keys")
    print("2. Add to your .env file:")
    print("   OPENAI_API_KEY=your_api_key_here")
    print("3. Install required dependencies:")
    print("   pip install requests python-dotenv")
    print("4. Run this test again")
    print("\n📖 API Documentation:")
    print("   https://platform.openai.com/docs/api-reference/chat")

def test_api_endpoint():
    """Test the API endpoint directly"""
    print("\n🔧 Testing API Endpoint Directly")
    print("=" * 30)
    
    import requests
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ No API key found")
        return
    
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": "Hello, can you help me find rental apartments in Toronto?"
            }
        ],
        "max_tokens": 100
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API endpoint is working correctly")
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                print(f"Response: {content[:100]}...")
        else:
            print(f"❌ API Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")

def compare_with_perplexity():
    """Compare OpenAI with Perplexity if available"""
    print("\n🔄 Comparing with Perplexity API")
    print("=" * 30)
    
    try:
        from perplexity_rental_search import search_rentals_with_perplexity, get_perplexity_status
        
        perplexity_status = get_perplexity_status()
        openai_status = get_openai_status()
        
        print(f"OpenAI Status: {openai_status['status']}")
        print(f"Perplexity Status: {perplexity_status['status']}")
        
        if openai_status['available'] and perplexity_status['available']:
            print("\nBoth APIs are available for comparison!")
            print("You can test both in the web application.")
        else:
            print("\nNot all APIs are available for comparison.")
            
    except ImportError:
        print("Perplexity integration not available for comparison")

if __name__ == '__main__':
    test_openai_integration()
    test_api_endpoint()
    compare_with_perplexity()
    show_setup_instructions() 