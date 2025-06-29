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

## 🌐 Hugging Face Spaces Deployment

### Step 1: Create a Hugging Face Space
1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Choose a name for your space (e.g., `your-username/house-crush`)
4. Select **Docker** as the SDK
5. Choose **Public** or **Private** visibility
6. Click "Create Space"

### Step 2: Upload Your Code
1. **Option A: Connect to GitHub (Recommended)**
   - Link your GitHub repository
   - Hugging Face will automatically sync changes
   - Go to Settings > Repository and connect your repo

2. **Option B: Upload Files Manually**
   - Upload the following files to your Space:
     - `app.py`
     - `requirements.txt`
     - `Dockerfile`
     - `templates/` folder
     - `static/` folder
     - `google_search.py`
     - `qanda.py`
     - `feedback_logger.py`
     - `data/` folder

### Step 3: Configure Environment Variables
In your Hugging Face Space settings:

1. Go to **Settings** tab in your Space
2. Scroll down to **Repository secrets**
3. Add the following environment variables:

```
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_google_search_engine_id_here
FLASK_ENV=production
PORT=7860
HOST=0.0.0.0
```

### Step 4: Deploy
1. After uploading files and setting environment variables, your Space will automatically build
2. Monitor the build process in the **Logs** tab
3. Once built successfully, your app will be available at: `https://huggingface.co/spaces/your-username/house-crush`

### Step 5: Verify Deployment
1. Check that your app loads correctly
2. Test the search functionality
3. Verify the Q&A system works
4. Test the feedback form

## 🐳 Docker Deployment (Alternative)

For local Docker deployment:

1. **Build and run with Docker:**
   ```bash
   docker build -t housecrush .
   docker run -p 7860:7860 -e OPENAI_API_KEY=your_key housecrush
   ```

2. **Or use Docker Compose:**
   ```bash
   docker compose up --build
   ```

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

## 🛠️ Technical Architecture

### Frontend
- **HTML5/CSS3**: Modern, responsive design with Tailwind CSS
- **JavaScript**: Interactive elements and form handling
- **Font Awesome**: Icons and visual elements
- **Google Fonts**: Inter font family for clean typography

### Backend
- **Flask**: Web framework for handling requests and serving content
- **OpenAI API**: AI model integration for Q&A responses
- **Google Custom Search API**: Property search across multiple websites
- **Gunicorn**: Production WSGI server for Hugging Face deployment

### Data Sources
- **Zillow**: Residential property listings (prioritized)
- **Apartments.com**: Apartment and rental properties
- **PadMapper**: Rental property aggregator
- **Kijiji**: Canadian classifieds and rental listings

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

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY`: API key for OpenAI services (required for Q&A system)
- `GOOGLE_API_KEY`: Google Custom Search API key (required for property search)
- `GOOGLE_SEARCH_ENGINE_ID`: Google Custom Search Engine ID (required for property search)

### API Setup Instructions

#### OpenAI
1. Sign up at [OpenAI](https://platform.openai.com/)
2. Get your API key from the dashboard
3. Add to environment variables: `OPENAI_API_KEY=your_key`

#### Google Custom Search
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Custom Search API
3. Create API credentials
4. Go to [Google Programmable Search Engine](https://programmablesearchengine.google.com/)
5. Create a new search engine for rental websites
6. Add to environment variables:
   ```
   GOOGLE_API_KEY=your_api_key
   GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id
   ```

## 🐛 Troubleshooting

### Common Issues

#### Local Development
- **Missing API Keys**: Ensure all required environment variables are set
- **Port Issues**: The app runs on port 7860 for Hugging Face compatibility
- **Dependency Issues**: Ensure all packages are installed with `pip install -r requirements.txt`

#### Hugging Face Spaces Issues
- **Build Failures**: Check the build logs in your Space settings
- **Environment Variables**: Ensure all API keys are set in Space settings
- **Port Configuration**: The app automatically uses port 7860

### Build Troubleshooting

#### Docker Build Issues
1. **Memory Error**: Increase Docker memory allocation
2. **Network Error**: Check internet connection for package downloads
3. **Permission Error**: Ensure proper file permissions

#### Hugging Face Spaces Build Issues
1. **Timeout**: The build may take 5-10 minutes for the first time
2. **Environment Variables**: Double-check all required variables are set

### Runtime Issues

#### Application Not Starting
1. Check logs in Hugging Face Spaces
2. Verify all environment variables are set
3. Ensure port 7860 is not blocked

#### Search Not Working
1. Verify Google API keys are correct
2. Check Google Custom Search Engine configuration
3. Ensure search engine includes rental websites

#### Q&A System Not Working
1. Verify OpenAI API key is valid
2. Check API usage limits and credits
3. Ensure proper model access

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