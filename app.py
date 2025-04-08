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
    character_image_url = "https://api.together.ai/imgproxy/ap7-cwvokiI54cBvfJz5uLaKFNZ8CJW9ACwCfuD6hkI/format:jpeg/aHR0cHM6Ly90b2dldGhlci1haS1iZmwtaW1hZ2VzLXByb2QuczMudXMtd2VzdC0yLmFtYXpvbmF3cy5jb20vaW1hZ2VzLzEwNzQzZDBlMGNmM2M3YTY0OGE3MTM1NDdmYTVhZTc1ZWU5OGY0ZTMyNjJmN2ZjYzlmYmJjN2U5YTI3ODEwODY_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ29udGVudC1TaGEyNTY9VU5TSUdORUQtUEFZTE9BRCZYLUFtei1DcmVkZW50aWFsPUFTSUFZV1pXNEhWQ1AyQ0MzUUdCJTJGMjAyNTA0MDglMkZ1cy13ZXN0LTIlMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjUwNDA4VDE0MjczNlomWC1BbXotRXhwaXJlcz0zNjAwJlgtQW16LVNlY3VyaXR5LVRva2VuPUlRb0piM0pwWjJsdVgyVmpFUCUyRiUyRiUyRiUyRiUyRiUyRiUyRiUyRiUyRiUyRiUyRndFYUNYVnpMWGRsYzNRdE1pSklNRVlDSVFDNnQ1NUt2eWU2JTJGJTJGZ0hBNGFqV1VxTTlic21PSlhidkkwbjBXd0Z4QlFoT1FJaEFKYnJNJTJCN2V3UGg2NzdKJTJCemdoTFFrdnBvZWRvOSUyQkRzMnNPTE5EenF4aXVZS3BBRkNIZ1FBQm9NTlRrNE56STJNVFl6Tnpnd0lnd3B5UkwwMDJCc2s1clNpSWNxN1FUUDRVYkhnMWlNZFFVT1MlMkJkU2tKT215MHJwMzZ6aUh3NXptMlJGUzFnSGhMcnRPMUc3WThGdnJOUnpzNEElMkZXS0h6aWtUbHNUd0k5R2tDSkhKM2d0YTMwUkZnViUyQnZtc011eG8xZllsUVZGRWdwZEN2REpEcGRndDE4NWxWa3c4V1dmeFJYbzRRb0x5ejB4WERPTTElMkJUc3ZjOTJ1MkFySE1FaTlyclFXRDVBN0Y1VDF5OHhLV09IeGMyVnFTUE1zMXJJN2UyMyUyQmJ5YW9QeUsybnU3RkFTczBpMXZHSWxIYVlVSVdHbndWdXVMbWxWUEJJdzJzRnRjQ09QSG55dU1pWFdiSGpZWHBFQlJEWFNNJTJGd0tycHo0VmhuaFo2TUg0YnRDQmpmYjdCYlZ6WCUyRlNQTDlJcSUyRnFrVCUyRm9ENk1BTU5KblR3TnFCMXVJSUREWWJGc2Y3dyUyRkFORTMySVdFaWh1YmQ0dElGbUhpQWNtbDc3NWsyemhyQTNZU01VNDY0NExsVldOT3QyTFdUYzRlciUyQkhucHZlaHY3ZGtWMmhsdlhsZm15UlZpVUFmbkNJR3V0TkwyckNCWGpERlczOGhQMjJqU2hRWWp3cnN0NldjanBIWVllNkV6MGp2dlRBdWRYODZ0MjF1M3loc0JKZDRFTVNyVyUyRjdQVkNFUjF1dG9KODUlMkJYQ2hkaTAlMkZQUGEyamRGYkhIVHNSR0tQWFVzRHlDTzE4cDRYTExJSzhHRjQlMkJCeFBlMjRnWnk1U2hldE5IMHBwd2FRUzRQYXo1ejVPRU0lMkY2MlhRTWFUdHVzJTJCZGdqakJFN2dta1Z4SjUzUm5JekhrZGpwSGpRWEkzdDBnWkMwTkI1MDhlWSUyRmpoT0olMkJuMU56eERMNzBYY1NHT0lYM2lYWmNwV0dTbzJtQWNQNzYxQzV1YmlvSGhMaUVMMmV2YlZCcyUyQmdxWHV6WlVWYWkySTJoUTlLVG5uQ0RZVFg4WHhlYWxPZHlKSERvMjBwV0gxQUVENTZXYXdUMFhPdlNFeHdHajBqckhpbmpyRjlQJTJCZTExVVRoRGRUMDdkTUs4azN5ZTNjb3p5VzlDNmluNGpxNVJUVXV1S2kwJTJCM3BiMXpOTjB3Mk9UVXZ3WTZtZ0V5QTBvVkpLbGdXZWJneldxWSUyQjg2am53ZjFjOG9ENzloaFNaR0M0a3ZqUkd3ekZVdzFQclQlMkI5T0xXUmJDQnNuT2klMkJZVjg2SlJUOWlpcVZIYU81RUdENTVIeWpvc09Pa2psNFA2cUdhTzBHOUF3YXJrbENzQmRMNzdnS0ZUTHpxOTZYMXo0YjZNTFlYZkdLNk1zSkNtSzk3ekElMkJIQUVXWWhtenp0UkslMkZzUlUxNk9VV2pwdng2WDF0MTZYVERUaENCZ3dPRVQ2aVhTcUJ6dCZYLUFtei1TaWduYXR1cmU9ZDIxMzY3ODY4YjUwZmU4NWNjZWIzNDcxZDkxZTliMzI3ZjhjNTAzMDVhZWQ2YTM0NDgyOTJlM2JkYmFlNDBjNCZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QmeC1pZD1HZXRPYmplY3Q"
    
    # Create character dictionary
    character = {
        'system': "Generic Fantasy RPG",
        'class': char_class,
        'background': background,
        'species': species_choice,
        'alignment': alignment,
        'details': details,
        'description': description,
        'image_url': character_image_url  # Add the image URL from env variable
    }
    
    return render_template('result.html', character=character)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5123, debug=True)