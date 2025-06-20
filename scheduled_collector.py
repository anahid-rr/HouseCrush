#!/usr/bin/env python3
"""
Scheduled Data Collection Script for House Crush
This script runs automated data collection at regular intervals.
"""

import asyncio
import schedule
import time
import logging
import os
import sys
from datetime import datetime
from data_collector import DataCollector

# Set up logging for scheduled collection
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduled_collector.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class ScheduledCollector:
    def __init__(self, locations=None, collection_interval_hours=24):
        self.locations = locations or ['Toronto', 'New York', 'San Francisco']
        self.collection_interval_hours = collection_interval_hours
        self.collector = DataCollector()
        self.is_running = False
        
    async def run_collection(self):
        """Run a single collection cycle"""
        try:
            logging.info(f"Starting scheduled collection for locations: {self.locations}")
            logging.info("Sources: Apartments.com, PadMapper, RentalFast, Zillow")
            start_time = datetime.now()
            
            listings = await self.collector.collect_all_data(self.locations)
            
            if listings:
                # Create backup of existing data
                if os.path.exists('houseAds.txt'):
                    backup_name = f"houseAds_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                    os.rename('houseAds.txt', backup_name)
                    logging.info(f"Created backup: {backup_name}")
                
                # Save new data
                self.collector.save_to_file(listings)
                
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                logging.info(f"Collection completed successfully!")
                logging.info(f"Collected {len(listings)} listings in {duration:.2f} seconds")
                logging.info(f"Data saved to houseAds.txt")
                
                # Keep only the last 5 backups
                self._cleanup_old_backups()
                
            else:
                logging.warning("No listings collected in this cycle")
                
        except Exception as e:
            logging.error(f"Error during scheduled collection: {str(e)}")
    
    def _cleanup_old_backups(self):
        """Keep only the last 5 backup files"""
        try:
            backup_files = [f for f in os.listdir('.') if f.startswith('houseAds_backup_')]
            backup_files.sort(reverse=True)
            
            if len(backup_files) > 5:
                for old_backup in backup_files[5:]:
                    os.remove(old_backup)
                    logging.info(f"Removed old backup: {old_backup}")
        except Exception as e:
            logging.error(f"Error cleaning up backups: {str(e)}")
    
    def schedule_collection(self):
        """Schedule the collection to run at regular intervals"""
        # Schedule collection every X hours
        schedule.every(self.collection_interval_hours).hours.do(
            lambda: asyncio.run(self.run_collection())
        )
        
        logging.info(f"Scheduled collection every {self.collection_interval_hours} hours")
        logging.info(f"Target locations: {self.locations}")
        logging.info("Data sources: Apartments.com, PadMapper, RentalFast, Zillow")
    
    def run_scheduler(self):
        """Run the scheduler loop"""
        self.is_running = True
        logging.info("Starting scheduled collector...")
        logging.info("Press Ctrl+C to stop")
        
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logging.info("Scheduled collector stopped by user")
            self.is_running = False
        except Exception as e:
            logging.error(f"Scheduler error: {str(e)}")
            self.is_running = False

def print_banner():
    print("=" * 60)
    print("🏠 HOUSE CRUSH - SCHEDULED DATA COLLECTOR")
    print("=" * 60)
    print("This script will automatically collect rental listings")
    print("from multiple sources at regular intervals:")
    print("• Apartments.com")
    print("• PadMapper")
    print("• RentalFast")
    print("• Zillow")
    print("and keep your data fresh.")
    print("=" * 60)

def get_configuration():
    """Get configuration from user or use defaults"""
    print("\n⚙️  Configuration:")
    
    # Get locations
    print("Enter locations to monitor (comma-separated, or press Enter for defaults):")
    locations_input = input("Locations: ").strip()
    if locations_input:
        locations = [loc.strip() for loc in locations_input.split(',')]
    else:
        locations = ['Toronto', 'New York', 'San Francisco']
    
    # Get collection interval
    print("\nEnter collection interval in hours (or press Enter for 24 hours):")
    interval_input = input("Interval (hours): ").strip()
    try:
        interval = int(interval_input) if interval_input else 24
    except ValueError:
        interval = 24
    
    print(f"\n📋 Configuration:")
    print(f"   Locations: {', '.join(locations)}")
    print(f"   Collection interval: {interval} hours")
    print(f"   Data sources: Apartments.com, PadMapper, RentalFast, Zillow")
    
    confirm = input("\nStart scheduled collection? (y/N): ").strip().lower()
    return (locations, interval) if confirm in ['y', 'yes'] else (None, None)

def main():
    print_banner()
    
    # Check dependencies
    try:
        import schedule
        import playwright
        import bs4
        import fake_useragent
    except ImportError as e:
        print(f"\n❌ Missing dependency: {e}")
        print("Please install required packages:")
        print("pip install schedule playwright beautifulsoup4 fake-useragent")
        print("playwright install")
        return
    
    # Get configuration
    locations, interval = get_configuration()
    if not locations:
        print("\n❌ Scheduled collection cancelled by user.")
        return
    
    # Create and run scheduled collector
    collector = ScheduledCollector(locations, interval)
    
    # Run initial collection
    print(f"\n🚀 Running initial collection...")
    asyncio.run(collector.run_collection())
    
    # Schedule future collections
    collector.schedule_collection()
    
    # Start scheduler
    collector.run_scheduler()

if __name__ == '__main__':
    main()
