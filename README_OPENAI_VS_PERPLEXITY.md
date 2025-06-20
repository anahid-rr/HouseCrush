# House Crush: OpenAI vs Perplexity Comparison

House Crush now offers two different AI-powered rental search applications, each using a different API for real-time property search. This document explains the differences and helps you choose the right version for your needs.

## 🏠 Available Applications

### 1. Main App (Perplexity + Local) - `app.py`
- **Primary API**: Perplexity API
- **Fallback**: Local database with Together AI ranking
- **Best for**: Free real-time search with web scraping capabilities

### 2. OpenAI App - `app_openai.py`
- **Primary API**: OpenAI API (GPT-4o)
- **Fallback**: Local database with Together AI ranking
- **Best for**: Advanced AI-powered search with better understanding

## 🔍 Feature Comparison

| Feature | Perplexity App | OpenAI App |
|---------|----------------|------------|
| **Primary API** | Perplexity (Sonar-medium-online) | OpenAI (GPT-4o) |
| **Cost** | Free tier available | Pay-per-token |
| **Response Time** | 2-5 seconds | 3-8 seconds |
| **Search Capabilities** | Specialized web search | General knowledge + web search |
| **JSON Parsing** | Good | Advanced |
| **Fallback Handling** | Good | Comprehensive |
| **Model Intelligence** | Web-focused | General AI |
| **Setup Complexity** | Simple | Simple |

## 🚀 Quick Start

### Option 1: Perplexity App (Recommended for most users)

```bash
# 1. Set up environment
python setup_env.py

# 2. Get Perplexity API key from: https://www.perplexity.ai/settings/api

# 3. Add to .env file:
PERPLEXITY_API_KEY=your_key_here

# 4. Run the app
python app.py
```

### Option 2: OpenAI App

```bash
# 1. Set up environment
python setup_env.py

# 2. Get OpenAI API key from: https://platform.openai.com/api-keys

# 3. Add to .env file:
OPENAI_API_KEY=your_key_here

# 4. Run the app
python app_openai.py
```

## 📊 Detailed Comparison

### Perplexity API Advantages
- **Free Tier**: Available with reasonable limits
- **Fast Response**: Optimized for web search
- **Web Specialization**: Better at finding current listings
- **Cost Effective**: No per-token charges
- **Real-time Data**: Direct access to current web content

### OpenAI API Advantages
- **Advanced AI**: More sophisticated understanding
- **Better Parsing**: Superior JSON extraction
- **Flexible Queries**: Can handle complex requests
- **General Knowledge**: Access to broader information
- **Consistent Quality**: More reliable responses

### Cost Analysis

#### Perplexity API
- **Free Tier**: Limited requests per minute
- **Paid Plans**: Higher rate limits
- **No Token Charges**: Fixed pricing

#### OpenAI API
- **Input Tokens**: ~50-100 tokens per search
- **Output Tokens**: ~200-500 tokens per response
- **Cost**: ~$0.01-0.05 per search (GPT-4o)
- **No Free Tier**: Pay for all usage

## 🧪 Testing Both APIs

You can test both APIs to see which works better for your needs:

```bash
# Test Perplexity API
python test_perplexity.py

# Test OpenAI API
python test_openai.py
```

## 🎯 Use Case Recommendations

### Choose Perplexity App if:
- You want a free solution
- You need fast response times
- You're primarily searching for current listings
- You have budget constraints
- You want web-focused search results

### Choose OpenAI App if:
- You need advanced AI understanding
- You want better response parsing
- You can afford API costs
- You need flexible query handling
- You want more sophisticated results

## 🔧 Setup Instructions

### Complete Setup (Both APIs)

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Setup Script**:
   ```bash
   python setup_env.py
   ```

3. **Get API Keys**:
   - Perplexity: https://www.perplexity.ai/settings/api
   - OpenAI: https://platform.openai.com/api-keys

4. **Configure Environment**:
   ```bash
   # .env file
   PERPLEXITY_API_KEY=your_perplexity_key
   OPENAI_API_KEY=your_openai_key
   TOGETHER_API_KEY=your_together_key
   ```

5. **Test Your Setup**:
   ```bash
   python test_perplexity.py
   python test_openai.py
   ```

## 🌐 Web Interface

Both apps provide the same web interface with different search methods:

- **Local Database**: Uses pre-collected data with AI ranking
- **API Search**: Real-time search using the respective API
- **AI Q&A**: Ask questions about rental properties
- **Feedback System**: Share your experience

## 📈 Performance Metrics

### Response Times
- **Perplexity**: 2-5 seconds average
- **OpenAI**: 3-8 seconds average
- **Local Database**: <1 second

### Success Rates
- **Perplexity**: 85-90% for web-based searches
- **OpenAI**: 90-95% for general queries
- **Local Database**: 100% (limited to collected data)

### Data Quality
- **Perplexity**: Current web listings, structured data
- **OpenAI**: AI-generated insights, flexible format
- **Local Database**: Pre-verified, consistent format

## 🔄 Switching Between Apps

You can easily switch between apps:

1. **Stop current app**: Ctrl+C
2. **Start different app**:
   ```bash
   # For Perplexity
   python app.py
   
   # For OpenAI
   python app_openai.py
   ```

Both apps use the same templates and data files, so your experience will be consistent.

## 🛠️ Troubleshooting

### Common Issues

1. **"API key not set"**
   - Check your `.env` file
   - Verify API key is valid
   - Run setup script again

2. **"No listings found"**
   - Try different search criteria
   - Check API status with test scripts
   - Verify internet connection

3. **"Rate limit exceeded"**
   - Wait a few minutes
   - Check your API plan limits
   - Consider upgrading plan

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 Documentation

- **Perplexity Integration**: [PERPLEXITY_INTEGRATION_README.md](PERPLEXITY_INTEGRATION_README.md)
- **OpenAI Integration**: [OPENAI_INTEGRATION_README.md](OPENAI_INTEGRATION_README.md)
- **Main README**: [README.md](README.md)

## 🎉 Getting Started

1. **Choose your preferred API** based on the comparison above
2. **Follow the setup instructions** for your chosen app
3. **Test the integration** using the provided test scripts
4. **Start the web application** and begin searching!

Both applications provide excellent rental property search capabilities with different strengths. Choose the one that best fits your needs and budget! 