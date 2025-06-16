# House Crush

House Crush is your smart rental assistant that finds the perfect home for you. 
It searches across multiple property websites and matches listings with your specific needs like budget, location (city), amenities, and lifestyle preferences. 
The AI-powered system then ranks each property based on how close it is to your important places like work, school, or gym.

## Quick Start
* Install Python 3.8 or higher
* Run `pip install -r requirements.txt`

## Running the Flask Web App (index)

1. **Set up your environment variables:**
   - Create a `.env` file in your project root with your API keys:
     ```
     TOGETHER_API_KEY=your_together_api_key_here
     HUGGINGFACE_HUB_TOKEN=your_huggingface_token_here
     ```
2. **Start the Flask app:**
   ```bash
   python app.py
   ```
3. **Open your browser and go to:**
   [http://localhost:5000](http://localhost:5000)

You can now:
- Ask rental-related questions in the Q&A section (powered by RAG)
- Search for properties by city, price, bedrooms, amenities, and lifestyle
- Submit feedback and see results from multiple property sites

## Using the RAG System (scripts/rag_example.py)

The Retrieval-Augmented Generation (RAG) system answers rental-related questions using a knowledge base.

To run the RAG example directly:
```bash
python scripts/rag_example.py
```
- Edit the `data_dict` and `question` in `scripts/rag_example.py` to customize the knowledge base and question.

## Multi-Channel Property (MCP) Search

The web app and backend use `house_scraper.py` to search multiple property sites (Zillow, Apartments.com, PadMapper, Kijiji) based on your filters.
- Filters supported: city, min/max price, bedrooms, amenities, lifestyle preferences
- Errors and feedback are logged to `scraper_errors.log` and `user_feedback.log` respectively.

## Troubleshooting
- If you see errors about missing region IDs for cities, add your city and its region ID to the `_get_region_id` method in `house_scraper.py`.
- For scraping issues, check `scraper_errors.log` for details.

## Feedback
- Use the feedback form at the bottom of the web app to send suggestions or report issues. Feedback is saved in `user_feedback.log`.

For detailed setup instructions and configuration options, please refer to the requirements.txt file.