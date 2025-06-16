from flask import Flask, render_template, request, flash, redirect, url_for
from scripts.rag_example import run_rag
from house_scraper import RentalScraperManager, log_user_feedback

app = Flask(__name__)

# Initialize the data dictionary with rental property information
data_dict = {
    "downtown_apartments": "Downtown apartments are typically within walking distance to major business districts, restaurants, and entertainment venues. Average rent ranges from $1,800 to $3,500 for 1-2 bedroom units. Most buildings offer amenities like gyms, rooftop terraces, and 24/7 security.",
    "suburban_homes": "Suburban homes offer more space and privacy compared to city apartments. Typical features include 2-4 bedrooms, private yards, and garage parking. Rent ranges from $2,500 to $4,000. These areas are known for good schools and family-friendly environments.",
    "nearby_amenities": "Important amenities to consider: grocery stores (within 1 mile), public transportation (bus/train stops), schools (elementary, middle, high), parks and recreation areas, medical facilities, and shopping centers. These can significantly impact daily convenience and quality of life.",
    "rental_requirements": "Standard rental requirements include: proof of income (3x monthly rent), credit score check (minimum 650), security deposit (1-2 months rent), rental history, and references. Some properties may require additional fees for pets or parking.",
    "property_types": "Common rental property types: studio apartments (400-600 sq ft), 1-bedroom apartments (600-800 sq ft), 2-bedroom apartments (800-1200 sq ft), townhouses (1200-2000 sq ft), and single-family homes (1500-3000 sq ft). Each type offers different space and privacy levels.",
    "location_factors": "Key location factors to consider: commute time to work (ideal: under 30 minutes), distance to public transportation (ideal: under 0.5 miles), neighborhood safety ratings, walkability score, and proximity to essential services like hospitals and schools.",
    "rental_trends": "Current rental market trends show increasing demand for properties with home office spaces, outdoor areas, and energy-efficient features. Properties with smart home technology and high-speed internet infrastructure are particularly sought after."
}

@app.route('/', methods=['GET', 'POST'])
def index():
    answer = None
    sources = None
    filters = []
    properties = []
    summary = None
    feedback_msg = None

    # Default filter values
    filter_values = {
        'location': '',
        'min_price': '',
        'max_price': '',
        'num_bedrooms': '',
        'amenities': '',
        'lifestyle': ''
    }

    if request.method == 'POST':
        # Q&A section
        question = request.form.get('question')
        if question:
            answer = run_rag(data_dict, question)
            if "Source Used:" in answer:
                answer_text, sources_text = answer.split("Source Used:")
                answer = answer_text.strip()
                sources = [s.strip() for s in sources_text.split(",")]

        # Property search section
        filter_values['location'] = request.form.get('location', '')
        filter_values['min_price'] = request.form.get('min_price', '')
        filter_values['max_price'] = request.form.get('max_price', '')
        filter_values['num_bedrooms'] = request.form.get('num_bedrooms', '')
        filter_values['amenities'] = request.form.get('amenities', '')
        filter_values['lifestyle'] = request.form.get('lifestyle', '')

        # Build filters for display
        if filter_values['min_price'] and filter_values['max_price']:
            filters.append(f"Budget: ${filter_values['min_price']}-${filter_values['max_price']}")
        if filter_values['num_bedrooms']:
            filters.append(f"{filter_values['num_bedrooms']}+ Bedrooms")
        if filter_values['amenities']:
            filters.append(f"Amenities: {filter_values['amenities']}")
        if filter_values['lifestyle']:
            filters.append(f"Lifestyle: {filter_values['lifestyle']}")
        if filter_values['location']:
            filters.append(f"Near {filter_values['location']}")

        # Scrape properties
        scraper = RentalScraperManager()
        try:
            listings = scraper.search_all_sites(
                location=filter_values['location'],
                min_price=int(filter_values['min_price']) if filter_values['min_price'] else None,
                max_price=int(filter_values['max_price']) if filter_values['max_price'] else None,
                num_bedrooms=int(filter_values['num_bedrooms']) if filter_values['num_bedrooms'] else None,
                amenities=[a.strip() for a in filter_values['amenities'].split(',')] if filter_values['amenities'] else None,
                lifestyle=filter_values['lifestyle'] if filter_values['lifestyle'] else None
            )
        except Exception as e:
            listings = []
            summary = f"Error fetching listings: {e}"

        # Format properties for display
        for i, prop in enumerate(listings[:8]):
            tags = []
            if prop.get('bedrooms'):
                tags.append(f"{prop['bedrooms']} BR")
            if prop.get('location'):
                tags.append(prop['location'])
            if prop.get('amenities'):
                tags.extend([a for a in prop['amenities'] if a])
            properties.append({
                'title': prop.get('title', 'No title'),
                'price': prop.get('price', 'N/A'),
                'tags': tags,
                'top_match': i == 0,
                'match_score': 98 - i if i < 2 else None  # Example match score
            })
        if not summary:
            summary = f"I found {len(listings)} properties matching your criteria. The top match is only 5 minutes from your gym!" if listings else "No properties found for your criteria."

        if 'feedback' in request.form:
            feedback = request.form.get('feedback')
            if feedback:
                log_user_feedback(feedback)
                feedback_msg = "Thank you for your feedback!"

    return render_template('index.html', answer=answer, sources=sources, filters=filters, properties=properties, summary=summary, filter_values=filter_values, feedback_msg=feedback_msg)

if __name__ == '__main__':
    app.run(debug=True)
