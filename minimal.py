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

def main():
    parser = argparse.ArgumentParser(description='House Crush - Smart Rental Assistant')
    parser.add_argument('-k', '--api-key', required=True, help='Together AI API key')
    parser.add_argument('-i', '--input', default='houseAds.txt', help='Input file with house listings')
    args = parser.parse_args()

    # Set up Together AI
    together.api_key = args.api_key

    # Get user preferences
    user_preferences = get_user_preferences()
    print("\nAnalyzing your preferences...")

    # Load house ads
    houses = load_house_ads(args.input)
    print(f"Loaded {len(houses)} house listings")

    # Rank houses
    ranked_houses = rank_houses(houses, user_preferences)
    print(f"Ranked {len(ranked_houses)} houses")

    # Display results
    display_results(ranked_houses)

    # Save results
    save_results(ranked_houses)

if __name__ == "__main__":
    main()