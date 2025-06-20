#!/usr/bin/env python3
"""
Manual Data Collection Script for House Crush
This script allows manual collection of rental listings from multiple sources.
"""

import asyncio
import sys
import os
from datetime import datetime
from data_collector import DataCollector

def print_banner():
    print("=" * 60)
    print("🏠 HOUSE CRUSH - DATA COLLECTOR")
    print("=" * 60)
    print("This script will collect rental listings from multiple sources:")
    print("• Apartments.com")
    print("• PadMapper")
    print("• RentalFast")
    print("• Zillow")
    print("and save them to houseAds.txt for AI-powered filtering.")
    print("=" * 60)

def get_user_input():
    """Get collection parameters from user"""
    print("\n📍 Enter locations to search (comma-separated):")
    print("Example: Toronto, New York, San Francisco")
    locations_input = input("Locations: ").strip()
    
    if not locations_input:
        print("Using default locations: Toronto, New York, San Francisco")
        locations = ['Toronto', 'New York', 'San Francisco']
    else:
        locations = [loc.strip() for loc in locations_input.split(',')]
    
    print(f"\n🎯 Will collect data for: {', '.join(locations)}")
    print("📊 Sources: Apartments.com, PadMapper, RentalFast, Zillow")
    
    # Ask for confirmation
    confirm = input("\nProceed with data collection? (y/N): ").strip().lower()
    return locations if confirm in ['y', 'yes'] else None

async def run_collection(locations):
    """Run the data collection process"""
    print(f"\n🚀 Starting data collection at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("This may take several minutes...")
    print("Collecting from: Apartments.com, PadMapper, RentalFast, Zillow")
    
    try:
        collector = DataCollector()
        listings = await collector.collect_all_data(locations)
        
        if listings:
            collector.save_to_file(listings)
            print(f"\n✅ Collection complete!")
            print(f"📊 Collected {len(listings)} unique listings")
            print(f"💾 Saved to: houseAds.txt")
            
            # Show sample of collected data
            print(f"\n📋 Sample listings:")
            for i, listing in enumerate(listings[:3]):
                source = listing.get('source', 'Unknown')
                print(f"  {i+1}. {listing.get('title', 'N/A')} - ${listing.get('price', 'N/A')} - {listing.get('location', 'N/A')} ({source})")
            
            if len(listings) > 3:
                print(f"  ... and {len(listings) - 3} more listings")
        else:
            print("\n⚠️  No listings were collected. This might be due to:")
            print("   - Network issues")
            print("   - Website structure changes")
            print("   - Rate limiting")
            print("   - No available listings in the specified locations")
    
    except Exception as e:
        print(f"\n❌ Error during collection: {str(e)}")
        print("Check data_collector.log for detailed error information.")

def main():
    print_banner()
    
    # Check if required dependencies are available
    try:
        import playwright
        import bs4
        import fake_useragent
    except ImportError as e:
        print(f"\n❌ Missing dependency: {e}")
        print("Please install required packages:")
        print("pip install playwright beautifulsoup4 fake-useragent")
        print("playwright install")
        return
    
    # Get user input
    locations = get_user_input()
    if not locations:
        print("\n❌ Collection cancelled by user.")
        return
    
    # Run collection
    asyncio.run(run_collection(locations))
    
    print(f"\n🎉 Data collection finished at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("You can now run the Flask app to filter and search the collected data!")

if __name__ == '__main__':
    main()
