import os
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from config import config

app = Flask(__name__)

# --- Environment-aware Debug Logger ---
def log_debug(data_type: str, data: dict):
    """Save debug data to a file for troubleshooting (only in development)."""
    if not config.should_save_debug_files():
        return
    
    try:
        debug_dir = 'debug'
        if not os.path.exists(debug_dir):
            os.makedirs(debug_dir)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"debug_{data_type}_{timestamp}.json"
        filepath = os.path.join(debug_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        if config.should_log_debug():
            print(f"✅ Debug data saved: {filepath}")
    except Exception as e:
        if config.should_log_debug():
            print(f"❌ Error saving debug data: {e}")

# --- Streamlined Search Method ---
def do_streamlined_search(filter_values: dict) -> dict:
    """
    Perform a streamlined rental search using streamlined_search from google_search.py.
    Returns a dict with properties, summary, and error_message.
    """
    try:
        from google_search import streamlined_search as google_streamlined_search
    except ImportError as e:
        return {
            'properties': [],
            'summary': "Search module not available.",
            'error_message': f"Import error: {str(e)}"
        }
    location = filter_values.get('location', '')
    min_price = int(filter_values['min_price']) if filter_values.get('min_price', '').isdigit() else None
    max_price = int(filter_values['max_price']) if filter_values.get('max_price', '').isdigit() else None
    bedrooms = int(filter_values['num_bedrooms']) if filter_values.get('num_bedrooms', '').isdigit() else None
    amenities = filter_values.get('amenities', [])
    lifestyle = filter_values.get('lifestyle', '')
    search_result = google_streamlined_search(
        location=location,
        min_price=min_price,
        max_price=max_price,
        bedrooms=bedrooms,
        amenities=amenities,
        lifestyle=lifestyle
    )
    
    # Log debug data only in development
    if config.should_save_debug_files():
        log_debug('search_result', search_result)
    
    if not search_result.get('success', False):
        return {
            'properties': [],
            'summary': "Search failed. Please try again.",
            'error_message': search_result.get('error', 'Unknown error')
        }
    # Format for display
    raw_properties = search_result.get('properties', [])
    final_properties = []
    for property_data in raw_properties:
        title = property_data.get('title', 'No title')
        description = property_data.get('description', '')
        url = property_data.get('url', '#')
        image_url = property_data.get('image_url', '')
        source = property_data.get('source', 'Search Results')
        rank = property_data.get('rank', 0)
        ai_score = property_data.get('ai_score', 75)
        price = property_data.get('price', 'Contact for price')
        tags = property_data.get('tags', [])
      
        if price and price != 'Contact for price':
            if isinstance(price, (int, float)) and price > 0:
                # Format numeric prices with commas and dollar sign
                display_price = f"${price:,}/month"
            elif isinstance(price, str):
                # Handle string prices (e.g., "$1,500", "1500", "Contact for pricing")
                price_str = str(price).strip()
                if price_str.startswith('$'):
                    # Already has dollar sign, just add /month if not present
                    if '/month' not in price_str.lower() and '/mo' not in price_str.lower():
                        display_price = f"{price_str}/month"
                    else:
                        display_price = price_str
                elif price_str.replace(',', '').replace('.', '').isdigit():
                    # Numeric string, format it
                    try:
                        numeric_price = int(price_str.replace(',', ''))
                        display_price = f"${numeric_price:,}/month"
                    except ValueError:
                        display_price = price_str
                else:
                    # Non-numeric string, use as is
                    display_price = price_str
            else:
                display_price = str(price)
        else:
            display_price = "Contact for price"
        match_percentage = property_data.get('match', min(95, 75 + (ai_score // 10)) if ai_score else 75)
        final_properties.append({
            'title': title,
            'price': display_price,
            'tags': tags,
            'top_match': rank == 1,
            'match_score': match_percentage,
            'url': url,
            'source': source,
            'description': description,
            'image_url': image_url,
            'rank': rank,
            'ai_score': ai_score,
            'type': 'streamlined_search'
        })
    summary = search_result.get('summary', '')
    return {
        'properties': final_properties,
        'summary': summary,
        'error_message': None
    }

# --- Flask Route ---
@app.route('/', methods=['GET', 'POST'])
def index():
    properties = []
    summary = None
    error_message = None
    filters = []
    feedback_msg = None
    answer = None
    sources = None
    filter_values = {
        'location': '',
        'min_price': '',
        'max_price': '',
        'num_bedrooms': '',
        'amenities': [],
        'lifestyle': ''
    }
    if request.method == 'POST':
        form_type = request.form.get('form_type', '')
        
        if form_type == 'feedback':
            # Handle feedback submission
            feedback_text = request.form.get('feedback', '').strip()
            if feedback_text:
                from feedback_logger import log_user_feedback
                success = log_user_feedback(feedback_text)
                feedback_msg = "Thank you for your feedback!" if success else "Failed to submit feedback. Please try again."
            else:
                feedback_msg = "Please enter your feedback."
                
        elif form_type == 'qa':
            # Handle Q&A submission
            question = request.form.get('question', '').strip()
            if question:
                try:
                    from qanda import answer_user_question
                    qa_result = answer_user_question(question)
                    answer = qa_result.get('answer', '')
                    sources = qa_result.get('sources', [])
                    error_message = qa_result.get('error', '') if not qa_result.get('success', True) else None
                    
                    # Check if this is an AJAX request
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({
                            'success': qa_result.get('success', True),
                            'answer': answer,
                            'sources': sources,
                            'error': error_message
                        })
                except Exception as e:
                    error_message = f"Q&A system error: {str(e)}"
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({
                            'success': False,
                            'answer': '',
                            'sources': [],
                            'error': error_message
                        })
        
        elif form_type == 'search':
            # Handle rental search submission
            filter_values['location'] = request.form.get('location', '')
            filter_values['min_price'] = request.form.get('min_price', '')
            filter_values['max_price'] = request.form.get('max_price', '')
            filter_values['num_bedrooms'] = request.form.get('num_bedrooms', '')
            filter_values['amenities'] = request.form.getlist('amenities')
            filter_values['lifestyle'] = request.form.get('lifestyle', '')
            result = do_streamlined_search(filter_values)
            properties = result['properties']
            summary = result['summary']
            error_message = result['error_message']
            if filter_values['min_price'] or filter_values['max_price']:
                filters.append(f"Budget: ${filter_values['min_price']}–${filter_values['max_price']}")
            if filter_values['num_bedrooms']:
                filters.append(f"{filter_values['num_bedrooms']}+ Bedrooms")
            if filter_values['location']:
                filters.append(f"Near {filter_values['location']}")
            if filter_values['amenities']:
                filters.append(f"Amenities: {', '.join(filter_values['amenities'])}")
        else:
            # Fallback for forms without form_type (backward compatibility)
            if request.form.get('question'):
                # Q&A form submitted (old format)
                question = request.form.get('question', '').strip()
                if question:
                    from qanda import answer_user_question
                    qa_result = answer_user_question(question)
                    answer = qa_result.get('answer', '')
                    sources = qa_result.get('sources', [])
                    error_message = qa_result.get('error', '') if not qa_result.get('success', True) else None
            else:
                # Rental search form submitted (old format)
                filter_values['location'] = request.form.get('location', '')
                filter_values['min_price'] = request.form.get('min_price', '')
                filter_values['max_price'] = request.form.get('max_price', '')
                filter_values['num_bedrooms'] = request.form.get('num_bedrooms', '')
                filter_values['amenities'] = request.form.getlist('amenities')
                filter_values['lifestyle'] = request.form.get('lifestyle', '')
                result = do_streamlined_search(filter_values)
                properties = result['properties']
                summary = result['summary']
                error_message = result['error_message']
                if filter_values['min_price'] or filter_values['max_price']:
                    filters.append(f"Budget: ${filter_values['min_price']}–${filter_values['max_price']}")
                if filter_values['num_bedrooms']:
                    filters.append(f"{filter_values['num_bedrooms']}+ Bedrooms")
                if filter_values['location']:
                    filters.append(f"Near {filter_values['location']}")
                if filter_values['amenities']:
                    filters.append(f"Amenities: {', '.join(filter_values['amenities'])}")
    return render_template('index.html',
        filters=filters,
        properties=properties,
        filtered_properties=[],
        summary=summary,
        error_message=error_message,
        filter_values=filter_values,
        feedback_msg=feedback_msg,
        openai_available=True,
        openai_status='Ready',
        google_available=True,
        google_status='Ready',
        answer=answer,
        sources=sources)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    feedback_msg = None
    
    if request.method == 'POST':
        form_type = request.form.get('form_type', '')
        
        if form_type == 'feedback':
            # Handle feedback submission from contact page
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            subject = request.form.get('subject', '').strip()
            message = request.form.get('message', '').strip()
            
            if name and email and subject and message:
                from feedback_logger import log_user_feedback
                # Create a more detailed feedback message
                detailed_feedback = f"Name: {name}\nEmail: {email}\nSubject: {subject}\nMessage: {message}"
                success = log_user_feedback(detailed_feedback)
                feedback_msg = "Thank you for your message! We'll get back to you soon." if success else "Failed to send message. Please try again."
            else:
                feedback_msg = "Please fill in all required fields."
    
    return render_template('contact.html', feedback_msg=feedback_msg)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/blog')
def blog():
    return render_template('blog.html')


@app.route('/help')
def help():
    return render_template('help.html')


@app.route('/privacy')
def privacy():
    return render_template('privacy.html')


@app.route('/terms')
def terms():
    return render_template('terms.html')


if __name__ == "__main__":
    # Set Flask debug mode based on environment
    debug_mode = config.is_development
    
    if config.should_log_debug():
        print(f"🚀 Starting House Crush in {config.environment} mode")
        print(f"📊 Debug logging: {'Enabled' if config.enable_debug_logging else 'Disabled'}")
        print(f"📁 File logging: {'Enabled' if config.enable_file_logging else 'Disabled'}")
        print(f"🐛 Debug files: {'Enabled' if config.enable_debug_files else 'Disabled'}")
        print(f"💬 Feedback logging: {'Enabled' if config.enable_feedback_logging else 'Disabled'}")
    
    app.run(host="0.0.0.0", port=7860, debug=debug_mode)
