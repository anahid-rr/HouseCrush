# Data Collection Scripts for House Crush

This directory contains scripts for collecting rental listings data from various sources using both direct site access and Bing search.

## Data Sources

The data collector now supports multiple rental listing websites:

- **Apartments.com** - https://www.apartments.com
- **PadMapper** - https://www.padmapper.com
- **RentalFast** - https://www.rentalfast.ca
- **Zillow** - https://www.zillow.com

## Collection Methods

### 1. Direct Site Access
- Directly visits rental websites
- Uses multiple URL patterns for each site
- Robust error handling for each source

### 2. Bing Search Integration
- Uses Bing search to find rental listings
- Searches for specific rental queries on each platform
- Follows search results to actual listing pages
- More likely to find current and relevant listings

## Files Overview

### 1. `data_collector.py`
The core data collection class that handles web scraping using Playwright.

**Features:**
- Asynchronous web scraping with Playwright
- Rotating user agents to avoid detection
- Random delays between requests
- Duplicate removal
- JSON data export
- Multi-source data collection
- Bing search integration
- Robust parsing with fallback selectors

**Usage:**
```python
from data_collector import DataCollector

collector = DataCollector()
listings = await collector.collect_all_data(['Toronto', 'New York'])
collector.save_to_file(listings)
```

### 2. `collect_data.py`
Interactive script for manual data collection.

**Features:**
- User-friendly command-line interface
- Configurable locations
- Progress tracking
- Sample data preview
- Error handling
- Multi-source collection

**Usage:**
```bash
python collect_data.py
```

### 3. `scheduled_collector.py`
Automated script for scheduled data collection.

**Features:**
- Configurable collection intervals
- Automatic backup creation
- Logging to file and console
- Background operation
- Graceful shutdown
- Multi-source data collection

**Usage:**
```bash
python scheduled_collector.py
```

### 4. `test_collector.py`
Test script to verify data collection functionality.

**Usage:**
```bash
python test_collector.py
```

## Setup Requirements

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   playwright install
   ```

2. **Required Packages:**
   - `playwright` - Web automation
   - `beautifulsoup4` - HTML parsing
   - `fake-useragent` - User agent rotation
   - `schedule` - Task scheduling (for scheduled collector)

## Data Format

All collected data is saved to `houseAds.txt` in JSON Lines format:

```json
{"id": 1, "title": "Downtown Apartment", "price": 2500, "location": "Toronto", "source": "Apartments.com", ...}
{"id": 2, "title": "Modern Studio", "price": 1800, "location": "Vancouver", "source": "PadMapper", ...}
{"id": 3, "title": "Family Home", "price": 3200, "location": "Toronto", "source": "Zillow", ...}
```

## Collection Strategy

### Bing Search Queries
The collector uses these search patterns:
- `"{location} rental apartments" site:apartments.com`
- `"{location} rental properties" site:zillow.com`
- `"{location} apartments for rent" site:rentalfast.ca`
- `"{location} rental listings" site:padmapper.com`

### Robust Parsing
Each parser tries multiple CSS selectors:
- `.property-card`, `.listing-card`, `.apartment-card`
- `.property-title`, `.listing-title`, `.title`
- `.property-price`, `.listing-price`, `.price`
- Generic selectors with wildcards: `[class*="property"]`

## Website URLs and Structure

### Apartments.com
- **URL Pattern:** `https://www.apartments.com/{location}`
- **Selectors:** `.placardContainer`, `.property-title`, `.property-rent`

### PadMapper
- **URL Pattern:** `https://www.padmapper.com/apartments/{location}`
- **Selectors:** `.listing-card`, `.listing-title`, `.listing-price`

### RentalFast
- **URL Pattern:** `https://www.rentalfast.ca/search?location={location}`
- **Selectors:** `.property-card`, `.property-title`, `.property-price`

### Zillow
- **URL Pattern:** `https://www.zillow.com/{location}-rentals/`
- **Selectors:** `.property-card`, `.property-title`, `.property-price`

## Logging

- **Manual Collection:** Output to console
- **Scheduled Collection:** Logs to `scheduled_collector.log`
- **Data Collector:** Logs to `data_collector.log`

## Backup System

The scheduled collector automatically creates backups:
- Backup files: `houseAds_backup_YYYYMMDD_HHMMSS.txt`
- Keeps last 5 backups
- Automatic cleanup of old backups

## Error Handling

All scripts include comprehensive error handling:
- Network timeouts
- Website structure changes
- Rate limiting
- Missing dependencies
- File I/O errors
- Individual source failures (continues with other sources)
- Fallback parsing methods

## Testing

Use the test script to verify functionality:
```bash
python test_collector.py
```

This will:
- Test with a single location (Toronto)
- Show sample collected data
- Save results to `test_listings.txt`
- Provide troubleshooting tips

## Integration with Flask App

The collected data in `houseAds.txt` is automatically used by the Flask app (`app.py`) for AI-powered filtering and search.

## Troubleshooting

1. **No listings collected:**
   - Run `python test_collector.py` to diagnose issues
   - Check internet connection
   - Verify website accessibility
   - Check log files for errors
   - Some sources may be temporarily unavailable

2. **Playwright errors:**
   - Run `playwright install` to install browsers
   - Update Playwright: `pip install --upgrade playwright`

3. **Permission errors:**
   - Ensure write permissions in the directory
   - Check if files are locked by other processes

4. **Website structure changes:**
   - Check log files for parsing errors
   - The collector uses multiple fallback selectors
   - Update selectors in `data_collector.py` if needed

5. **Bing search issues:**
   - Bing may rate limit requests
   - Try different locations
   - Check if search results are being blocked

## Security Notes

- Scripts use rotating user agents to avoid detection
- Random delays between requests
- No personal data is collected or stored
- All data is publicly available rental listings
- Respects robots.txt and rate limiting
- Uses legitimate search queries 