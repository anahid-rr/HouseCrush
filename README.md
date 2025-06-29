# House Crush - AI-Powered Rental Search

House Crush is your intelligent rental assistant that finds the perfect home by searching across multiple property websites and matching listings with your specific needs. Our AI-powered system ranks properties based on your budget, location preferences, amenities, and proximity to important places like work, school, or gym.

## ✨ Features

- **Modern Landing Page**: Beautiful, responsive design with comprehensive information about the rental search process
- **Streamlined Property Search**: AI-powered search across multiple rental platforms with intelligent filtering
- **AI-Powered Q&A**: Get instant answers to rental-related questions using OpenAI integration
- **Smart Filtering**: Filter by city, price range, bedrooms, amenities, and lifestyle preferences
- **Interactive Feedback System**: Submit feedback and suggestions directly through the web interface
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Multiple Page Support**: About, Blog, Contact, Help, Privacy, and Terms pages

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- Modern web browser

### Local Installation

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
   OPENAI_API_KEY=your_openai_api_key_here
   GOOGLE_API_KEY=your_google_api_key_here
   GOOGLE_SEARCH_ENGINE_ID=your_google_search_engine_id_here
   ```

4. **Start the application:**
   ```bash
   python app.py
   ```

5. **Open your browser and navigate to:**
   [http://localhost:7860](http://localhost:7860)


## 🏠 How It Works

### Property Search
- Enter your city, budget range, number of bedrooms, and desired amenities
- Add custom amenities and lifestyle preferences
- Get AI-ranked results with match scores and proximity information
- View properties from multiple sources in a unified interface
- Uses streamlined search method for optimal results

### Q&A System
- Ask rental-related questions using the interactive Q&A section
- Use quick question buttons for common inquiries
- Get detailed answers with source citations
- Powered by OpenAI GPT models (GPT-4o with fallback to GPT-3.5-turbo)

### Feedback System
- Submit feedback, suggestions, or report issues
- All feedback is logged and reviewed for continuous improvement
- Supports both simple feedback and detailed contact forms



## 📁 Project Structure

```
HouseCrush/
├── app.py                          # Main Flask application with streamlined search
├── templates/
│   ├── index.html                  # Main landing page with integrated functionality
│   ├── about.html                  # About page
│   ├── blog.html                   # Blog page
│   ├── contact.html                # Contact page with feedback form
│   ├── help.html                   # Help page
│   ├── privacy.html                # Privacy policy
│   └── terms.html                  # Terms of service
├── static/
│   └── img/
│       └── background.jpg          # Background images
├── google_search.py               # Google Custom Search integration with streamlined search
├── qanda.py                      # OpenAI-powered Q&A system
├── feedback_logger.py            # User feedback system
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Docker configuration for Hugging Face
└── README.md                     # This file
```


## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE.md](LICENSE.md) file for details.

## 📞 Support

- **Feedback**: Use the feedback form on the website
- **Issues**: Report bugs and issues through the feedback system
- **Questions**: Check the Q&A section for common rental-related questions

---

**House Crush** - Making rental search intelligent, efficient, and user-friendly. 🏡✨
