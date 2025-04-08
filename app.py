from flask import Flask, render_template, request, jsonify
import os
from together import Together

app = Flask(__name__)

# Sample data for dropdowns
classes = ["Artificer", "Barbarian", "Bard", "Cleric", "Druid", "Fighter", "Monk", "Paladin", "Ranger", "Rogue", "Sorcerer", "Warlock", "Wizard"]
backgrounds = ["Acolyte", "Artisan", "Charlatan", "Criminal", "Entertainer", "Farmer", "Guard", "Guide", "Hermit", "Merchant", "Noble", "Sage", "Sailor", "Scribe", "Soldier", "Wayfarer"]
species = ["Dwarf", "Elf", "Halfling", "Human", "Aasimar", "Dragonborn", "Gnome", "Goliath", "Orc", "Tiefling"]
alignments = ["Lawful Good", "Neutral Good", "Chaotic Good", "Lawful Neutral", 
              "True Neutral", "Chaotic Neutral", "Lawful Evil", "Neutral Evil", "Chaotic Evil"]

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/rpg')
def rpg_creator():
    return render_template('index.html', 
                          classes=classes,
                          backgrounds=backgrounds,
                          species=species,
                          alignments=alignments)

api_key = os.environ.get("API_KEY")

def ask_llama(prompt):
    """
    Send a prompt to Llama 3 and return the response.
    
    Args:
        prompt (str): The prompt to send to Llama
        api_key (str, optional): Your Together API key. If None, looks for TOGETHER_API_KEY environment variable.
        
    Returns:
        str: Llama's response
    """
    # Set API key
    client = Together(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3-8B-Instruct-Turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def ask_image(prompt):
    client = Together(api_key=api_key)
    try:
        response = client.images.generate(
            prompt=prompt,
            model="stabilityai/stable-diffusion-xl-base-1.0",
            steps=10,
            n=4
        )
        return (response.data[0].url)
    except Exception as e:
        return f"Error: {str(e)}"


def generate_character_description(char_class, background, species_choice, alignment, details=""):
    """
    Generate a more detailed character description based on the provided parameters.
    
    Args:
        char_class (str): The character's class
        background (str): The character's background
        species_choice (str): The character's species
        alignment (str): The character's alignment
        details (str, optional): Additional details provided by user
        
    Returns:
        str: A detailed character description
    """
    # Class-specific traits
    return ask_llama("Give me a quick paragraph with possible details of a " + char_class + " with an " + background + " who is a " + species_choice +  " with alignment " + alignment + ". Details include " + details + "don't add anything else to the paragraph like 'here is a possible paragraph'")

def generate_character_image(char_class, background, species_choice, alignment, details=""):
    return ask_image("Give me a image of a D&D " + char_class + " with an " + background + " who is a " + species_choice +  " with alignment " + alignment + ". Details could include " + details)

@app.route('/generate', methods=['POST'])
def generate_character():
    # Get form data
    char_class = request.form.get('class')
    background = request.form.get('background')
    species_choice = request.form.get('species')
    alignment = request.form.get('alignment')
    details = request.form.get('details', '')
    
    # Use the new function to generate a detailed description
    description = generate_character_description(
        char_class, background, species_choice, alignment, details
    )
    
    # Get image URL from environment variable
    character_image_url = generate_character_image(
        char_class, background, species_choice, alignment, details
    )
    # Create character dictionary
    character = {
        'system': "Generic Fantasy RPG",
        'class': char_class,
        'background': background,
        'species': species_choice,
        'alignment': alignment,
        'details': details,
        'description': description,
        'image_url': character_image_url 
    }
    
    return render_template('result.html', character=character)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5123, debug=True)