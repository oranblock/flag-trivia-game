from flask import Flask, render_template, jsonify, request
import random
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = 'debug_key'

# More comprehensive country data for testing
COUNTRIES = {
    'United States': {'code': 'US'},
    'France': {'code': 'FR'},
    'Japan': {'code': 'JP'},
    'Brazil': {'code': 'BR'},
    'South Africa': {'code': 'ZA'},
    'Australia': {'code': 'AU'},
    'Egypt': {'code': 'EG'},
    'India': {'code': 'IN'},
    'Canada': {'code': 'CA'},
    'Germany': {'code': 'DE'},
    'United Kingdom': {'code': 'GB'},
    'China': {'code': 'CN'},
    'Russia': {'code': 'RU'},
    'Mexico': {'code': 'MX'}
}

# For tracking visited countries across sessions (would use a database in production)
VISITED_COUNTRIES = set()

@app.route('/')
def debug_map():
    # Pick a random country for the test
    target_country = random.choice(list(COUNTRIES.keys()))
    target_code = COUNTRIES[target_country]['code']
    
    # Create flags directory if it doesn't exist
    os.makedirs(os.path.join('static', 'flags'), exist_ok=True)
    
    return render_template('debug_map.html', 
                          country=target_country,
                          country_code=target_code,
                          countries=json.dumps(COUNTRIES),
                          visited=json.dumps(list(VISITED_COUNTRIES)),
                          refresh=False)  # Disable auto-refresh for better interaction

@app.route('/visit_country', methods=['POST'])
def visit_country():
    country_code = request.json.get('country_code')
    if country_code:
        VISITED_COUNTRIES.add(country_code)
        return jsonify({'success': True, 'visited': list(VISITED_COUNTRIES)})
    return jsonify({'success': False})

@app.route('/reset_countries', methods=['POST'])
def reset_countries():
    VISITED_COUNTRIES.clear()
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')