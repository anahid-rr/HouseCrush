# suppress warnings
import warnings

warnings.filterwarnings("ignore")

# import libraries
import argparse
from together import Together
import textwrap
import json
import os
from datetime import datetime
from pathlib import Path
import together
from typing import List, Dict
import gradio as gr
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment variable
TOGETHER_API_KEY = os.getenv('TOGETHER_API_KEY')
if not TOGETHER_API_KEY:
    raise ValueError("Please set TOGETHER_API_KEY in your .env file")

# Set up Together AI
together.api_key = TOGETHER_API_KEY

## FUNCTION 1: This Allows Us to Prompt the AI MODEL
# -------------------------------------------------
def prompt_llm(prompt, with_linebreak=False):
    # This function allows us to prompt an LLM via the Together API

    # model
    model = "meta-llama/Meta-Llama-3-8B-Instruct-Lite"

    # Make the API call
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    output = response.choices[0].message.content

    if with_linebreak:
        # Wrap the output
        wrapped_output = textwrap.fill(output, width=50)

        return wrapped_output
    else:
        return output


def get_user_preferences() -> str:
    """Get user preferences through an interactive prompt."""
    print("\n=== House Crush - Tell us what you're looking for ===\n")
    
    preferences = []
    
    # Budget
    while True:
        try:
            budget = input("What's your maximum monthly budget? $")
            budget = float(budget)
            preferences.append(f"Maximum budget: ${budget}")
            break
        except ValueError:
            print("Please enter a valid number.")
    
    # Location
    location = input("Preferred location/neighborhood: ")
    if location:
        preferences.append(f"Location: {location}")
    
    # Bedrooms
    bedrooms = input("Number of bedrooms needed: ")
    if bedrooms:
        preferences.append(f"Bedrooms: {bedrooms}")
    
    # Bathrooms
    bathrooms = input("Number of bathrooms needed: ")
    if bathrooms:
        preferences.append(f"Bathrooms: {bathrooms}")
    
    # Must-have amenities
    print("\nEnter must-have amenities (one per line, press Enter twice to finish):")
    amenities = []
    while True:
        amenity = input("> ")
        if not amenity:
            break
        amenities.append(amenity)
    if amenities:
        preferences.append(f"Must-have amenities: {', '.join(amenities)}")
    
    # Additional preferences
    additional = input("\nAny other important preferences? (e.g., pet-friendly, parking, etc.): ")
    if additional:
        preferences.append(f"Additional preferences: {additional}")
    
    return " | ".join(preferences)

def load_house_ads(file_path: str) -> List[Dict]:
    """Load house advertisements from a text file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]

def rank_houses(houses: List[Dict], user_preferences: str) -> List[Dict]:
    """Rank houses based on user preferences using Together AI."""
    prompt = f"""Given these house listings and user preferences, rank them from best to worst match.
User Preferences: {user_preferences}

House Listings:
{json.dumps(houses, indent=2)}

Please analyze each house and rank them based on how well they match the user's preferences.
Return a JSON array of the same houses, but with an added 'match_score' field (0-100) and 'match_reason' field explaining why it's a good or bad match.
"""

    response = together.Complete.create(
        prompt=prompt,
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        max_tokens=2000,
        temperature=0.7,
        top_p=0.7,
        top_k=50,
        repetition_penalty=1.1,
        stop=['</s>', 'Human:', 'Assistant:']
    )

    try:
        ranked_houses = json.loads(response['output']['choices'][0]['text'])
        return sorted(ranked_houses, key=lambda x: x.get('match_score', 0), reverse=True)
    except Exception as e:
        print(f"Error processing AI response: {e}")
        return houses

def save_results(ranked_houses: List[Dict], output_dir: str = "results"):
    """Save ranked houses to a timestamped file."""
    # Create results directory if it doesn't exist
    Path(output_dir).mkdir(exist_ok=True)
    
    # Generate timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"{timestamp}.txt")
    
    # Save results
    with open(output_file, 'w', encoding='utf-8') as f:
        for house in ranked_houses:
            f.write(json.dumps(house, ensure_ascii=False) + '\n')
    
    print(f"\nResults saved to {output_file}")

def display_results(ranked_houses: List[Dict]):
    """Display ranked houses in a user-friendly format."""
    print("\n=== Your Personalized House Matches ===\n")
    
    for i, house in enumerate(ranked_houses, 1):
        print(f"Match #{i} (Score: {house.get('match_score', 'N/A')})")
        print(f"Title: {house['title']}")
        print(f"Price: ${house['price']}/month")
        print(f"Location: {house['location']}")
        print(f"Bedrooms: {house['bedrooms']} | Bathrooms: {house['bathrooms']}")
        print(f"Amenities: {', '.join(house['amenities'])}")
        print(f"Description: {house['description']}")
        print(f"Available from: {house.get('availability_date', 'Contact for availability')}")
        print("\nContact Information:")
        contact = house.get('contact', {})
        print(f"  Agent: {contact.get('name', 'N/A')}")
        print(f"  Phone: {contact.get('phone', 'N/A')}")
        print(f"  Email: {contact.get('email', 'N/A')}")
        print(f"Source: {house.get('source_website', 'N/A')}")
        print(f"Match Reason: {house.get('match_reason', 'No reason provided')}")
        print("-" * 80 + "\n")

def format_house_results(ranked_houses: List[Dict]) -> str:
    """Format ranked houses into a readable string."""
    output = []
    for i, house in enumerate(ranked_houses, 1):
        output.append(f"Match #{i} (Score: {house.get('match_score', 'N/A')})")
        output.append(f"Title: {house['title']}")
        output.append(f"Price: ${house['price']}/month")
        output.append(f"Location: {house['location']}")
        output.append(f"Bedrooms: {house['bedrooms']} | Bathrooms: {house['bathrooms']}")
        output.append(f"Amenities: {', '.join(house['amenities'])}")
        output.append(f"Description: {house['description']}")
        output.append(f"Available from: {house.get('availability_date', 'Contact for availability')}")
        output.append("\nContact Information:")
        contact = house.get('contact', {})
        output.append(f"  Agent: {contact.get('name', 'N/A')}")
        output.append(f"  Phone: {contact.get('phone', 'N/A')}")
        output.append(f"  Email: {contact.get('email', 'N/A')}")
        output.append(f"Source: {house.get('source_website', 'N/A')}")
        output.append(f"Match Reason: {house.get('match_reason', 'No reason provided')}")
        output.append("-" * 80 + "\n")
    
    return "\n".join(output)

def process_house_search(budget: float, location: str, bedrooms: str, bathrooms: str, 
                        amenities: str, additional_preferences: str, input_file: str) -> str:
    """Process house search with user preferences."""
    # Format user preferences
    preferences = []
    preferences.append(f"Maximum budget: ${budget}")
    if location:
        preferences.append(f"Location: {location}")
    if bedrooms:
        preferences.append(f"Bedrooms: {bedrooms}")
    if bathrooms:
        preferences.append(f"Bathrooms: {bathrooms}")
    if amenities:
        preferences.append(f"Must-have amenities: {amenities}")
    if additional_preferences:
        preferences.append(f"Additional preferences: {additional_preferences}")
    
    user_preferences = " | ".join(preferences)
    
    # Load and filter houses by budget
    houses = load_house_ads(input_file)
    filtered_houses = [h for h in houses if float(h.get('price', 0)) <= float(budget)]
    ranked_houses = rank_houses(filtered_houses, user_preferences)
    
    # Format and return results
    return format_house_results(ranked_houses)

def create_gradio_interface():
    """Create and launch the Gradio interface."""
    theme = gr.themes.Base(
        primary_hue="green",
        secondary_hue="green",
        neutral_hue="gray",
        font=["Inter", "sans-serif"],
    ).set(
        body_background_fill="#F6F8F6",
        block_background_fill="#FFFFFF",
        button_primary_background_fill="#4CAF7A",
        button_primary_background_fill_hover="#357A50",
        button_primary_text_color="#fff",
        input_background_fill="#F6F8F6"
    )
    with gr.Blocks(title="House Crush - Smart Rental Assistant", theme=theme) as interface:
        with gr.Row():
            gr.Image(
                value="https://cdn-icons-png.flaticon.com/512/69/69524.png",
                label=None,
                show_label=False,
                width=48,
                height=48
            )
            gr.Markdown("""
            # House Crush
            <span style='font-size:1.1em;'>Find your perfect rental match!</span>
            """)
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 📝 Your Preferences")
                budget = gr.Number(label="Maximum Monthly Budget ($)", minimum=0)
                location = gr.Textbox(label="Preferred Location/Neighborhood", placeholder="e.g., Downtown, Westside, etc.")
                bedrooms = gr.Dropdown(label="Number of Bedrooms", choices=["1", "2", "3", "4", "5+"], info="Select your desired number of bedrooms")
                bathrooms = gr.Dropdown(label="Number of Bathrooms", choices=["1", "1.5", "2", "2.5", "3+"], info="Select your desired number of bathrooms")
                amenities = gr.Textbox(label="Must-have Amenities", placeholder="e.g., parking, pool, gym, washer/dryer")
                additional_preferences = gr.Textbox(label="Additional Preferences", placeholder="e.g., pet-friendly, furnished, etc.")
                input_file = gr.Textbox(label="Input File Path", value="houseAds.txt", visible=False)
                search_button = gr.Button("Find My Perfect Match! 🎯", variant="primary", size="large")
            with gr.Column(scale=2):
                gr.Markdown("## �� Your Perfect Match\n---", elem_id="result-title")
                chips_md = gr.Markdown("", visible=True)
                result_grid = gr.Markdown("<div style='margin-left: 1em;'>_Results will appear here after you search._</div>", visible=True)
        footer_md = gr.Markdown("", visible=False)

        def format_chips(budget, location, bedrooms, bathrooms, amenities, additional_preferences):
            chips = []
            if budget: chips.append(f"`💰 Budget: ${budget:,.0f}`")
            if bedrooms: chips.append(f"`🛏️ {bedrooms} Bedrooms`")
            if bathrooms: chips.append(f"`🛁 {bathrooms} Bathrooms`")
            if amenities: chips.append(f"`✨ {amenities}`")
            if additional_preferences: chips.append(f"`🔖 {additional_preferences}`")
            if location: chips.append(f"`📍 {location}`")
            return ' '.join(chips)

        def format_results(ranked_houses):
            if not ranked_houses:
                return "<div style='margin-left: 1em;'>No matches found.</div>"
            cards = []
            for i, house in enumerate(ranked_houses[:4]):
                badge = "**🟩 Top Match**" if i == 0 else f"**🟩 {house.get('match_score', 'N/A')}% Match**"
                tags = []
                if 'amenities' in house:
                    tags += [f"`{a}`" for a in house['amenities']]
                if house.get('match_reason'):
                    tags.append(f"`{house['match_reason']}`")
                card = f"""
<div style='margin-left: 1em;'>
---
{badge}

### {house['title']}
**<span style='color:#357A50;'>${house['price']}/mo</span>**

{' '.join(tags)}
</div>
"""
                cards.append(card)
            return '\n'.join(cards)

        def format_footer(ranked_houses):
            if not ranked_houses:
                return ""
            return f"**House Crush AI:** I found {len(ranked_houses)} properties matching your criteria. The top match is only 5 minutes from your gym!"

        def update_ui(budget, location, bedrooms, bathrooms, amenities, additional_preferences, input_file):
            chips = format_chips(budget, location, bedrooms, bathrooms, amenities, additional_preferences)
            houses = load_house_ads(input_file)
            # Filter by budget before ranking
            filtered_houses = [h for h in houses if float(h.get('price', 0)) <= float(budget)]
            user_prefs = []
            if budget: user_prefs.append(f"Maximum budget: ${budget}")
            if location: user_prefs.append(f"Location: {location}")
            if bedrooms: user_prefs.append(f"Bedrooms: {bedrooms}")
            if bathrooms: user_prefs.append(f"Bathrooms: {bathrooms}")
            if amenities: user_prefs.append(f"Must-have amenities: {amenities}")
            if additional_preferences: user_prefs.append(f"Additional preferences: {additional_preferences}")
            user_preferences = " | ".join(user_prefs)
            ranked_houses = rank_houses(filtered_houses, user_preferences)
            results = format_results(ranked_houses)
            footer = format_footer(ranked_houses)
            return gr.update(value=chips, visible=True), gr.update(value=results, visible=True), gr.update(value=footer, visible=True)

        def show_loading(*args):
            return gr.update(value="`⏳ Searching for your perfect match...`", visible=True), gr.update(value="<div style='margin-left: 1em;'>_Searching for your perfect match..._</div>", visible=True), gr.update(value="", visible=False)

        search_button.click(
            fn=show_loading,
            inputs=[budget, location, bedrooms, bathrooms, amenities, additional_preferences, input_file],
            outputs=[chips_md, result_grid, footer_md],
            queue=False
        )
        search_button.click(
            fn=update_ui,
            inputs=[budget, location, bedrooms, bathrooms, amenities, additional_preferences, input_file],
            outputs=[chips_md, result_grid, footer_md],
            queue=True
        )
    return interface

if __name__ == "__main__":
    interface = create_gradio_interface()
    interface.launch()