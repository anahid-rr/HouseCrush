# House Crush - AI-Powered Rental Assistant

## 🆕 New Approach: AI-Powered Filtering & Ranking

House Crush now uses an intelligent AI-powered approach inspired by `minimal.py` to filter and rank house listings instead of web scraping. This provides more accurate, personalized results with better performance.

## 🚀 Key Features

### **AI-Powered House Ranking**
- Uses Together AI to intelligently rank houses based on user preferences
- Analyzes price compatibility, location, bedrooms, bathrooms, and amenities
- Provides match scores (0-100%) and detailed reasoning for each match
- Adapts to different user preferences and requirements

### **Smart Filtering**
- Filters houses from a local database (`houseAds.txt`)
- Supports location, budget range, and bedroom requirements
- No dependency on external websites or scraping
- Faster and more reliable than web scraping

### **Interactive Q&A System**
- Ask questions about rental properties and requirements
- Get intelligent answers based on comprehensive rental knowledge
- Covers topics like rental requirements, amenities, market trends, and more

## 📁 File Structure

```
HouseCrush/
├── app.py                 # Main Flask application (NEW APPROACH)
├── app_backup.py          # Backup of original scraping approach
├── house_scraper.py       # Web scraping functionality (still available)
├── minimal.py             # Original AI ranking approach
├── houseAds.txt           # House listings database
├── setup_env.py           # Environment setup script
├── requirements.txt       # Python dependencies
└── templates/
    └── index.html         # Web interface
```

## 🛠️ Setup Instructions

### 1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 2. **Set Up Together AI API Key**
```bash
python setup_env.py
```
Or manually create a `.env` file:
```
TOGETHER_API_KEY=your_api_key_here
```

### 3. **Prepare House Listings**
The app reads from `houseAds.txt` which should contain JSON-formatted house listings:
```json
{"id": 1, "title": "Modern Downtown Apartment", "price": 2500, "bedrooms": 2, "bathrooms": 2, "location": "Downtown", "amenities": ["gym", "parking", "pool"], "description": "Beautiful modern apartment...", "contact": {"name": "John Smith", "phone": "555-0123", "email": "john.smith@realty.com"}, "source_website": "https://realty.com/listings/123", "availability_date": "2024-04-01"}
```

### 4. **Run the Application**
```bash
python app.py
```

## 🎯 How It Works

### **1. User Input Processing**
- Users enter location, budget, and bedroom requirements
- System builds a comprehensive preferences string
- Filters are displayed for user confirmation

### **2. AI-Powered Ranking**
- Loads house listings from `houseAds.txt`
- Sends user preferences and house data to Together AI
- AI analyzes each house against user requirements
- Returns ranked results with match scores and reasoning

### **3. Results Display**
- Shows top 8 matches with compatibility scores
- Displays key information: price, location, bedrooms, amenities
- Provides match reasoning for transparency
- Links to original listings when available

## 🔧 Configuration

### **Environment Variables**
- `TOGETHER_API_KEY`: Your Together AI API key (required for AI ranking)

### **House Listings Format**
Each line in `houseAds.txt` should be a valid JSON object with:
- `title`: Property title
- `price`: Monthly rent
- `bedrooms`: Number of bedrooms
- `bathrooms`: Number of bathrooms
- `location`: Property location
- `amenities`: Array of available amenities
- `description`: Property description
- `contact`: Contact information object
- `source_website`: Original listing URL
- `availability_date`: When the property is available

## 🆚 Comparison: New vs Old Approach

| Feature | New Approach (AI) | Old Approach (Scraping) |
|---------|------------------|------------------------|
| **Speed** | ⚡ Fast (local data) | 🐌 Slow (web requests) |
| **Reliability** | ✅ High (no external dependencies) | ❌ Low (website changes) |
| **Accuracy** | 🎯 High (AI analysis) | 📊 Medium (basic filtering) |
| **Personalization** | 🧠 Intelligent ranking | 🔍 Simple matching |
| **Maintenance** | 🔧 Low (no scraping updates) | 🔧 High (constant updates) |
| **Cost** | 💰 API calls | 💰 Free but unreliable |

## 🚀 Benefits

1. **Better Performance**: No web scraping delays
2. **More Accurate**: AI-powered intelligent ranking
3. **Personalized**: Considers multiple factors for ranking
4. **Reliable**: Works consistently without website changes
5. **Scalable**: Easy to add more house listings
6. **Transparent**: Shows reasoning for each match

## 🔄 Migration from Scraping

If you want to switch back to the scraping approach:
1. Use `app_backup.py` instead of `app.py`
2. Install Playwright browsers: `python setup_playwright.py`
3. The scraping approach is still available in `house_scraper.py`

## 📝 Notes

- The AI ranking requires a Together AI API key
- House listings must be in the correct JSON format
- The system gracefully handles missing API keys with fallback scoring
- All original functionality (Q&A, feedback) is preserved

## 🆘 Troubleshooting

### **No API Key Set**
- Run `python setup_env.py` to configure your API key
- Or set the `TOGETHER_API_KEY` environment variable

### **No House Listings**
- Check that `houseAds.txt` exists and contains valid JSON
- Each line should be a complete JSON object

### **AI Ranking Not Working**
- Verify your Together AI API key is valid
- Check your internet connection
- Review the console for error messages

---

**House Crush** - Making rental searches intelligent and personalized! 🏠✨ 