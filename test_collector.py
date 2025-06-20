#!/usr/bin/env python3
"""
Test script for the data collector
This script tests the data collection functionality and shows results.
"""

import asyncio
import json
from data_collector import DataCollector

async def test_collector():
    print("🧪 Testing Data Collector")
    print("=" * 50)
    
    # Test with a single location first
    test_locations = ['Toronto']
    
    collector = DataCollector()
    
    print(f"Testing with location: {test_locations[0]}")
    print("This may take a few minutes...")
    
    try:
        listings = await collector.collect_all_data(test_locations)
        
        if listings:
            print(f"\n✅ Success! Collected {len(listings)} listings")
            print("\n📋 Sample listings:")
            
            for i, listing in enumerate(listings[:5]):  # Show first 5
                print(f"\n{i+1}. {listing.get('title', 'N/A')}")
                print(f"   Price: ${listing.get('price', 'N/A')}")
                print(f"   Location: {listing.get('location', 'N/A')}")
                print(f"   Source: {listing.get('source', 'N/A')}")
                print(f"   Website: {listing.get('source_website', 'N/A')}")
            
            if len(listings) > 5:
                print(f"\n... and {len(listings) - 5} more listings")
            
            # Save to test file
            test_filename = 'test_listings.txt'
            collector.save_to_file(listings, test_filename)
            print(f"\n💾 Test data saved to: {test_filename}")
            
        else:
            print("\n❌ No listings collected")
            print("This could be due to:")
            print("- Website structure changes")
            print("- Network issues")
            print("- Rate limiting")
            print("- No available listings")
    
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        print("Check the logs for more details")

def show_help():
    print("\n🔧 Troubleshooting Tips:")
    print("1. Make sure you have installed all dependencies:")
    print("   pip install -r requirements.txt")
    print("   playwright install")
    print("\n2. Check your internet connection")
    print("\n3. Some websites may block automated access")
    print("\n4. Try running with different locations")

if __name__ == '__main__':
    asyncio.run(test_collector())
    show_help() 