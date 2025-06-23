# House Crush - AI-Powered Rental Search

House Crush is your intelligent rental assistant that finds the perfect home by searching across multiple property websites and matching listings with your specific needs. Our AI-powered system ranks properties based on your budget, location preferences, amenities, and proximity to important places like work, school, or gym.

## ✨ Features

- **Modern Landing Page**: Beautiful, responsive design with comprehensive information about the rental search process
- **Multi-Site Property Search**: Aggregates listings from Zillow, Apartments.com, PadMapper, and Kijiji
- **AI-Powered Q&A**: Get instant answers to rental-related questions using our RAG system
- **Smart Filtering**: Filter by city, price range, bedrooms, amenities, and lifestyle preferences
- **Interactive Feedback System**: Submit feedback and suggestions directly through the web interface
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Modern web browser

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd HouseCrush
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   Create a `.env` file in your project root with your API keys:
   ```
   TOGETHER_API_KEY=your_together_api_key_here
   HUGGINGFACE_HUB_TOKEN=your_huggingface_token_here
   ```

4. **Start the application:**
   ```bash
   python app.py
   ```

5. **Open your browser and navigate to:**
   [http://localhost:5000](http://localhost:5000)

### 🐳 Docker Deployment (Alternative)

For containerized deployment or Hugging Face Spaces:

1. **Build and run with Docker:**
   ```bash
   docker build -t housecrush .
   docker run -p 7860:7860 -e TOGETHER_API_KEY=your_key housecrush
   ```

2. **Or use Docker Compose:**
   ```bash
   docker-compose up --build
   ```

3. **For detailed Docker instructions, see:**
   [README_DOCKER.md](README_DOCKER.md)

## 🏠 How It Works

### Property Search
- Enter your city, budget range, number of bedrooms, and desired amenities
- Add custom amenities and lifestyle preferences
- Get AI-ranked results with match scores and proximity information
- View properties from multiple sources in a unified interface

### Q&A System
- Ask rental-related questions using the interactive Q&A section
- Use quick question buttons for common inquiries
- Get detailed answers with source citations
- Powered by Retrieval-Augmented Generation (RAG) technology

### Feedback System
- Submit feedback, suggestions, or report issues
- All feedback is logged and reviewed for continuous improvement

## 🛠️ Technical Architecture

### Frontend
- **HTML5/CSS3**: Modern, responsive design with Tailwind CSS
- **JavaScript**: Interactive elements and form handling
- **Font Awesome**: Icons and visual elements
- **Google Fonts**: Inter font family for clean typography

### Backend
- **Flask**: Web framework for handling requests and serving content
- **Together AI**: AI model integration for intelligent responses
- **Sentence Transformers**: Text embedding for RAG system
- **Playwright**: Web scraping for property listings
- **BeautifulSoup4**: HTML parsing for data extraction

### Data Sources
- **Zillow**: Residential property listings
- **Apartments.com**: Apartment and rental properties
- **PadMapper**: Interactive map-based property search
- **Kijiji**: Canadian classifieds and rental listings

## 📁 Project Structure

```
HouseCrush/
├── app.py                          # Main Flask application
├── templates/
│   └── index.html                  # Modern landing page with integrated functionality
├── data/
│   └── houseAds.txt               # Property data and knowledge base
├── scripts/
│   ├── rag_example.py             # RAG system example
│   ├── mcp_client_example.py      # MCP client example
│   └── mcp_server_example.py      # MCP server example
├── results/                       # Search results and API responses
├── requirements.txt               # Python dependencies
└── README.md                     # This file
```

## 🔧 Configuration

### Environment Variables
- `TOGETHER_API_KEY`: API key for Together AI services
- `HUGGINGFACE_HUB_TOKEN`: Token for Hugging Face model access

### Customization
- Modify `data/houseAds.txt` to update the knowledge base
- Adjust scraping parameters in the main application files
- Customize the UI by editing `templates/index.html`

## 🐛 Troubleshooting

### Common Issues
- **Missing API Keys**: Ensure all required environment variables are set in `.env`
- **Scraping Errors**: Check `scraper_errors.log` for detailed error information
- **City Not Found**: Add your city and region ID to the scraping configuration
- **Dependency Issues**: Ensure all packages are installed with `pip install -r requirements.txt`

### Logs
- `scraper_errors.log`: Web scraping error details
- `user_feedback.log`: User feedback and suggestions
- `results/`: API responses and search results

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## 📞 Support

- **Feedback**: Use the feedback form on the website
- **Issues**: Report bugs and issues through the feedback system
- **Questions**: Check the Q&A section for common rental-related questions

---

**House Crush** - Making rental search intelligent, efficient, and user-friendly. 🏡✨