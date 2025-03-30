# app.py
from flask import Flask, render_template, request, session, redirect, url_for, jsonify, send_from_directory
import random
import requests
import os
import time
import json

# Try to import dotenv, but make it optional
try:
    from dotenv import load_dotenv
    # Load environment variables from .env file if it exists
    if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')):
        load_dotenv()
except ImportError:
    print("dotenv package not found. Environment variables from .env will not be loaded.")

app = Flask(__name__)
app.secret_key = 'your_secret_key'
FLAG_API = 'https://flagpedia.net/data/flags/normal/{}.png'
FLAGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'flags')
META_JSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'data', 'meta.json')
OUTLINES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'outlines')

# Load country data from meta.json file
def load_country_data():
    try:
        with open(META_JSON_PATH, 'r', encoding='utf-8') as file:
            countries_data = json.load(file)
            
        # Transform the data into the format expected by the application
        countries_dict = {}
        
        # Define regions for each country by continent
        regions = {
            # Africa
            'DZ': 'Africa', 'AO': 'Africa', 'BJ': 'Africa', 'BW': 'Africa', 'BF': 'Africa', 
            'BI': 'Africa', 'CM': 'Africa', 'CV': 'Africa', 'CF': 'Africa', 'TD': 'Africa', 
            'KM': 'Africa', 'CD': 'Africa', 'CG': 'Africa', 'CI': 'Africa', 'DJ': 'Africa', 
            'EG': 'Africa', 'GQ': 'Africa', 'ER': 'Africa', 'SZ': 'Africa', 'ET': 'Africa', 
            'GA': 'Africa', 'GM': 'Africa', 'GH': 'Africa', 'GN': 'Africa', 'GW': 'Africa', 
            'KE': 'Africa', 'LS': 'Africa', 'LR': 'Africa', 'LY': 'Africa', 'MG': 'Africa', 
            'MW': 'Africa', 'ML': 'Africa', 'MR': 'Africa', 'MU': 'Africa', 'MA': 'Africa', 
            'MZ': 'Africa', 'NA': 'Africa', 'NE': 'Africa', 'NG': 'Africa', 'RW': 'Africa', 
            'ST': 'Africa', 'SN': 'Africa', 'SC': 'Africa', 'SL': 'Africa', 'SO': 'Africa', 
            'ZA': 'Africa', 'SS': 'Africa', 'SD': 'Africa', 'TZ': 'Africa', 'TG': 'Africa', 
            'TN': 'Africa', 'UG': 'Africa', 'ZM': 'Africa', 'ZW': 'Africa',
            
            # Asia
            'AF': 'Asia', 'AM': 'Asia', 'AZ': 'Asia', 'BH': 'Asia', 'BD': 'Asia', 'BT': 'Asia', 
            'BN': 'Asia', 'KH': 'Asia', 'CN': 'Asia', 'CY': 'Asia', 'GE': 'Asia', 'IN': 'Asia', 
            'ID': 'Asia', 'IR': 'Asia', 'IQ': 'Asia', 'IL': 'Asia', 'JP': 'Asia', 'JO': 'Asia', 
            'KZ': 'Asia', 'KW': 'Asia', 'KG': 'Asia', 'LA': 'Asia', 'LB': 'Asia', 'MY': 'Asia', 
            'MV': 'Asia', 'MN': 'Asia', 'MM': 'Asia', 'NP': 'Asia', 'KP': 'Asia', 'OM': 'Asia', 
            'PK': 'Asia', 'PS': 'Asia', 'PH': 'Asia', 'QA': 'Asia', 'SA': 'Asia', 'SG': 'Asia', 
            'KR': 'Asia', 'LK': 'Asia', 'SY': 'Asia', 'TW': 'Asia', 'TJ': 'Asia', 'TH': 'Asia', 
            'TR': 'Asia', 'TM': 'Asia', 'AE': 'Asia', 'UZ': 'Asia', 'VN': 'Asia', 'YE': 'Asia',
            
            # Europe
            'AL': 'Europe', 'AD': 'Europe', 'AT': 'Europe', 'BY': 'Europe', 'BE': 'Europe', 
            'BA': 'Europe', 'BG': 'Europe', 'HR': 'Europe', 'CZ': 'Europe', 'DK': 'Europe', 
            'EE': 'Europe', 'FI': 'Europe', 'FR': 'Europe', 'DE': 'Europe', 'GR': 'Europe', 
            'HU': 'Europe', 'IS': 'Europe', 'IE': 'Europe', 'IT': 'Europe', 'LV': 'Europe', 
            'LI': 'Europe', 'LT': 'Europe', 'LU': 'Europe', 'MK': 'Europe', 'MT': 'Europe', 
            'MD': 'Europe', 'MC': 'Europe', 'ME': 'Europe', 'NL': 'Europe', 'NO': 'Europe', 
            'PL': 'Europe', 'PT': 'Europe', 'RO': 'Europe', 'RU': 'Europe', 'SM': 'Europe', 
            'RS': 'Europe', 'SK': 'Europe', 'SI': 'Europe', 'ES': 'Europe', 'SE': 'Europe', 
            'CH': 'Europe', 'UA': 'Europe', 'GB': 'Europe', 'VA': 'Europe',
            
            # North America
            'AG': 'North America', 'BS': 'North America', 'BB': 'North America', 'BZ': 'North America', 
            'CA': 'North America', 'CR': 'North America', 'CU': 'North America', 'DM': 'North America', 
            'DO': 'North America', 'SV': 'North America', 'GD': 'North America', 'GT': 'North America', 
            'HT': 'North America', 'HN': 'North America', 'JM': 'North America', 'MX': 'North America', 
            'NI': 'North America', 'PA': 'North America', 'KN': 'North America', 'LC': 'North America', 
            'VC': 'North America', 'TT': 'North America', 'US': 'North America',
            
            # South America
            'AR': 'South America', 'BO': 'South America', 'BR': 'South America', 'CL': 'South America', 
            'CO': 'South America', 'EC': 'South America', 'GY': 'South America', 'PY': 'South America', 
            'PE': 'South America', 'SR': 'South America', 'UY': 'South America', 'VE': 'South America',
            
            # Oceania
            'AU': 'Oceania', 'FJ': 'Oceania', 'KI': 'Oceania', 'MH': 'Oceania', 'FM': 'Oceania', 
            'NR': 'Oceania', 'NZ': 'Oceania', 'PW': 'Oceania', 'PG': 'Oceania', 'WS': 'Oceania', 
            'SB': 'Oceania', 'TO': 'Oceania', 'TV': 'Oceania', 'VU': 'Oceania'
        }
        
        # Arabic translations for regions
        region_translations = {
            'Africa': 'أفريقيا',
            'Asia': 'آسيا',
            'Europe': 'أوروبا',
            'North America': 'أمريكا الشمالية',
            'South America': 'أمريكا الجنوبية',
            'Oceania': 'أوقيانوسيا',
            'Antarctica': 'القارة القطبية الجنوبية'
        }
        
        for country in countries_data:
            # Use English country name as the key
            english_name = country['countryName']['en']
            # Convert ISO code to lowercase for compatibility with the flag API
            country_code = country['countryCode'].lower()
            arabic_name = country['countryName']['ar']
            
            # Get region information
            region = regions.get(country['countryCode'], 'Unknown')
            region_arabic = region_translations.get(region, 'غير معروف')
            
            # Create entry with the same structure as the original COUNTRIES dictionary
            countries_dict[english_name] = {
                'code': country_code,
                'arabic': arabic_name,
                # Add currency information
                'currency': {
                    'code': country['currency']['code'],
                    'name': {
                        'en': country['currency']['name']['en'],
                        'ar': country['currency']['name']['ar']
                    }
                },
                # Add region information
                'region': {
                    'en': region,
                    'ar': region_arabic
                }
            }
        
        return countries_dict
    except Exception as e:
        print(f"Error loading country data from meta.json: {e}")
        # Fall back to empty dictionary if there's an error
        return {}

# Load the country data at startup
COUNTRIES = load_country_data()

# Country coordinates for the map (all 194 countries)
COUNTRY_COORDS = {
    'AF': {'lat': 33.93911, 'lng': 67.709953, 'zoom': 6},
    'AL': {'lat': 41.153332, 'lng': 20.168331, 'zoom': 7},
    'DZ': {'lat': 28.033886, 'lng': 1.659626, 'zoom': 5},
    'AD': {'lat': 42.546245, 'lng': 1.601554, 'zoom': 11},
    'AO': {'lat': -11.202692, 'lng': 17.873887, 'zoom': 6},
    'AG': {'lat': 17.060816, 'lng': -61.796428, 'zoom': 10},
    'AR': {'lat': -38.416097, 'lng': -63.616672, 'zoom': 4},
    'AM': {'lat': 40.069099, 'lng': 45.038189, 'zoom': 7},
    'AU': {'lat': -25.274398, 'lng': 133.775136, 'zoom': 4},
    'AT': {'lat': 47.516231, 'lng': 14.550072, 'zoom': 7},
    'AZ': {'lat': 40.143105, 'lng': 47.576927, 'zoom': 7},
    'BS': {'lat': 25.03428, 'lng': -77.39628, 'zoom': 7},
    'BH': {'lat': 25.930414, 'lng': 50.637772, 'zoom': 10},
    'BD': {'lat': 23.684994, 'lng': 90.356331, 'zoom': 7},
    'BB': {'lat': 13.193887, 'lng': -59.543198, 'zoom': 11},
    'BY': {'lat': 53.709807, 'lng': 27.953389, 'zoom': 6},
    'BE': {'lat': 50.503887, 'lng': 4.469936, 'zoom': 7},
    'BZ': {'lat': 17.189877, 'lng': -88.49765, 'zoom': 8},
    'BJ': {'lat': 9.30769, 'lng': 2.315834, 'zoom': 7},
    'BT': {'lat': 27.514162, 'lng': 90.433601, 'zoom': 8},
    'BO': {'lat': -16.290154, 'lng': -63.588653, 'zoom': 6},
    'BA': {'lat': 43.915886, 'lng': 17.679076, 'zoom': 7},
    'BW': {'lat': -22.328474, 'lng': 24.684866, 'zoom': 6},
    'BR': {'lat': -14.235004, 'lng': -51.92528, 'zoom': 4},
    'BN': {'lat': 4.535277, 'lng': 114.727669, 'zoom': 9},
    'BG': {'lat': 42.733883, 'lng': 25.48583, 'zoom': 7},
    'BF': {'lat': 12.238333, 'lng': -1.561593, 'zoom': 7},
    'BI': {'lat': -3.373056, 'lng': 29.918886, 'zoom': 8},
    'KH': {'lat': 12.565679, 'lng': 104.990963, 'zoom': 7},
    'CM': {'lat': 7.369722, 'lng': 12.354722, 'zoom': 6},
    'CA': {'lat': 56.130366, 'lng': -106.346771, 'zoom': 3},
    'CV': {'lat': 16.002082, 'lng': -24.013197, 'zoom': 8},
    'CF': {'lat': 6.611111, 'lng': 20.939444, 'zoom': 6},
    'TD': {'lat': 15.454166, 'lng': 18.732207, 'zoom': 5},
    'CL': {'lat': -35.675147, 'lng': -71.542969, 'zoom': 4},
    'CN': {'lat': 35.86166, 'lng': 104.195397, 'zoom': 4},
    'CO': {'lat': 4.570868, 'lng': -74.297333, 'zoom': 5},
    'KM': {'lat': -11.875001, 'lng': 43.872219, 'zoom': 9},
    'CG': {'lat': -0.228021, 'lng': 15.827659, 'zoom': 6},
    'CD': {'lat': -4.038333, 'lng': 21.758664, 'zoom': 5},
    'CR': {'lat': 9.748917, 'lng': -83.753428, 'zoom': 8},
    'CI': {'lat': 7.539989, 'lng': -5.54708, 'zoom': 7},
    'HR': {'lat': 45.1, 'lng': 15.2, 'zoom': 7},
    'CU': {'lat': 21.521757, 'lng': -77.781167, 'zoom': 7},
    'CY': {'lat': 35.126413, 'lng': 33.429859, 'zoom': 9},
    'CZ': {'lat': 49.817492, 'lng': 15.472962, 'zoom': 7},
    'DK': {'lat': 56.26392, 'lng': 9.501785, 'zoom': 6},
    'DJ': {'lat': 11.825138, 'lng': 42.590275, 'zoom': 8},
    'DM': {'lat': 15.414999, 'lng': -61.370976, 'zoom': 10},
    'DO': {'lat': 18.735693, 'lng': -70.162651, 'zoom': 8},
    'EC': {'lat': -1.831239, 'lng': -78.183406, 'zoom': 7},
    'EG': {'lat': 26.820553, 'lng': 30.802498, 'zoom': 6},
    'SV': {'lat': 13.794185, 'lng': -88.89653, 'zoom': 8},
    'GQ': {'lat': 1.650801, 'lng': 10.267895, 'zoom': 8},
    'ER': {'lat': 15.179384, 'lng': 39.782334, 'zoom': 7},
    'EE': {'lat': 58.595272, 'lng': 25.013607, 'zoom': 7},
    'SZ': {'lat': -26.522503, 'lng': 31.465866, 'zoom': 9},
    'ET': {'lat': 9.145, 'lng': 40.489673, 'zoom': 6},
    'FJ': {'lat': -16.578193, 'lng': 179.414413, 'zoom': 7},
    'FI': {'lat': 61.92411, 'lng': 25.748151, 'zoom': 5},
    'FR': {'lat': 46.227638, 'lng': 2.213749, 'zoom': 6},
    'GA': {'lat': -0.803689, 'lng': 11.609444, 'zoom': 7},
    'GM': {'lat': 13.443182, 'lng': -15.310139, 'zoom': 8},
    'GE': {'lat': 42.315407, 'lng': 43.356892, 'zoom': 7},
    'DE': {'lat': 51.165691, 'lng': 10.451526, 'zoom': 6},
    'GH': {'lat': 7.946527, 'lng': -1.023194, 'zoom': 7},
    'GR': {'lat': 39.074208, 'lng': 21.824312, 'zoom': 7},
    'GD': {'lat': 12.262776, 'lng': -61.604171, 'zoom': 11},
    'GT': {'lat': 15.783471, 'lng': -90.230759, 'zoom': 7},
    'GN': {'lat': 9.945587, 'lng': -9.696645, 'zoom': 7},
    'GW': {'lat': 11.803749, 'lng': -15.180413, 'zoom': 8},
    'GY': {'lat': 4.860416, 'lng': -58.93018, 'zoom': 7},
    'HT': {'lat': 18.971187, 'lng': -72.285215, 'zoom': 9},
    'HN': {'lat': 15.199999, 'lng': -86.241905, 'zoom': 7},
    'HU': {'lat': 47.162494, 'lng': 19.503304, 'zoom': 7},
    'IS': {'lat': 64.963051, 'lng': -19.020835, 'zoom': 6},
    'IN': {'lat': 20.593684, 'lng': 78.96288, 'zoom': 4},
    'ID': {'lat': -0.789275, 'lng': 113.921327, 'zoom': 4},
    'IR': {'lat': 32.427908, 'lng': 53.688046, 'zoom': 5},
    'IQ': {'lat': 33.223191, 'lng': 43.679291, 'zoom': 6},
    'IE': {'lat': 53.41291, 'lng': -8.24389, 'zoom': 7},
    'IL': {'lat': 31.046051, 'lng': 34.851612, 'zoom': 7},
    'IT': {'lat': 41.87194, 'lng': 12.56738, 'zoom': 5},
    'JM': {'lat': 18.109581, 'lng': -77.297508, 'zoom': 9},
    'JP': {'lat': 36.204824, 'lng': 138.252924, 'zoom': 5},
    'JO': {'lat': 30.585164, 'lng': 36.238414, 'zoom': 7},
    'KZ': {'lat': 48.019573, 'lng': 66.923684, 'zoom': 5},
    'KE': {'lat': -0.023559, 'lng': 37.906193, 'zoom': 6},
    'KI': {'lat': -3.370417, 'lng': -168.734039, 'zoom': 5},
    'KP': {'lat': 40.339852, 'lng': 127.510093, 'zoom': 7},
    'KR': {'lat': 35.907757, 'lng': 127.766922, 'zoom': 7},
    'KW': {'lat': 29.31166, 'lng': 47.481766, 'zoom': 8},
    'KG': {'lat': 41.20438, 'lng': 74.766098, 'zoom': 7},
    'LA': {'lat': 19.85627, 'lng': 102.495496, 'zoom': 6},
    'LV': {'lat': 56.879635, 'lng': 24.603189, 'zoom': 7},
    'LB': {'lat': 33.854721, 'lng': 35.862285, 'zoom': 8},
    'LS': {'lat': -29.609988, 'lng': 28.233608, 'zoom': 8},
    'LR': {'lat': 6.428055, 'lng': -9.429499, 'zoom': 7},
    'LY': {'lat': 26.3351, 'lng': 17.228331, 'zoom': 5},
    'LI': {'lat': 47.166, 'lng': 9.555373, 'zoom': 11},
    'LT': {'lat': 55.169438, 'lng': 23.881275, 'zoom': 7},
    'LU': {'lat': 49.815273, 'lng': 6.129583, 'zoom': 9},
    'MG': {'lat': -18.766947, 'lng': 46.869107, 'zoom': 6},
    'MW': {'lat': -13.254308, 'lng': 34.301525, 'zoom': 7},
    'MY': {'lat': 4.210484, 'lng': 101.975766, 'zoom': 6},
    'MV': {'lat': 3.202778, 'lng': 73.22068, 'zoom': 8},
    'ML': {'lat': 17.570692, 'lng': -3.996166, 'zoom': 6},
    'MT': {'lat': 35.937496, 'lng': 14.375416, 'zoom': 10},
    'MH': {'lat': 7.131474, 'lng': 171.184478, 'zoom': 7},
    'MR': {'lat': 21.00789, 'lng': -10.940835, 'zoom': 6},
    'MU': {'lat': -20.348404, 'lng': 57.552152, 'zoom': 10},
    'MX': {'lat': 23.634501, 'lng': -102.552784, 'zoom': 5},
    'FM': {'lat': 7.425554, 'lng': 150.550812, 'zoom': 7},
    'MD': {'lat': 47.411631, 'lng': 28.369885, 'zoom': 7},
    'MC': {'lat': 43.750298, 'lng': 7.412841, 'zoom': 13},
    'MN': {'lat': 46.862496, 'lng': 103.846656, 'zoom': 5},
    'ME': {'lat': 42.708678, 'lng': 19.37439, 'zoom': 8},
    'MA': {'lat': 31.791702, 'lng': -7.09262, 'zoom': 6},
    'MZ': {'lat': -18.665695, 'lng': 35.529562, 'zoom': 6},
    'MM': {'lat': 21.913965, 'lng': 95.956223, 'zoom': 5},
    'NA': {'lat': -22.95764, 'lng': 18.49041, 'zoom': 6},
    'NR': {'lat': -0.522778, 'lng': 166.931503, 'zoom': 12},
    'NP': {'lat': 28.394857, 'lng': 84.124008, 'zoom': 7},
    'NL': {'lat': 52.132633, 'lng': 5.291266, 'zoom': 7},
    'NZ': {'lat': -40.900557, 'lng': 174.885971, 'zoom': 5},
    'NI': {'lat': 12.865416, 'lng': -85.207229, 'zoom': 7},
    'NE': {'lat': 17.607789, 'lng': 8.081666, 'zoom': 6},
    'NG': {'lat': 9.081999, 'lng': 8.675277, 'zoom': 6},
    'MK': {'lat': 41.608635, 'lng': 21.745275, 'zoom': 8},
    'NO': {'lat': 60.472024, 'lng': 8.468946, 'zoom': 5},
    'OM': {'lat': 21.512583, 'lng': 55.923255, 'zoom': 6},
    'PK': {'lat': 30.375321, 'lng': 69.345116, 'zoom': 5},
    'PW': {'lat': 7.51498, 'lng': 134.58252, 'zoom': 9},
    'PA': {'lat': 8.537981, 'lng': -80.782127, 'zoom': 7},
    'PG': {'lat': -6.314993, 'lng': 143.95555, 'zoom': 6},
    'PY': {'lat': -23.442503, 'lng': -58.443832, 'zoom': 6},
    'PE': {'lat': -9.189967, 'lng': -75.015152, 'zoom': 5},
    'PH': {'lat': 12.879721, 'lng': 121.774017, 'zoom': 6},
    'PL': {'lat': 51.919438, 'lng': 19.145136, 'zoom': 6},
    'PT': {'lat': 39.399872, 'lng': -8.224454, 'zoom': 7},
    'QA': {'lat': 25.354826, 'lng': 51.183884, 'zoom': 9},
    'RO': {'lat': 45.943161, 'lng': 24.96676, 'zoom': 6},
    'RU': {'lat': 61.52401, 'lng': 105.318756, 'zoom': 3},
    'RW': {'lat': -1.940278, 'lng': 29.873888, 'zoom': 9},
    'KN': {'lat': 17.357822, 'lng': -62.782998, 'zoom': 11},
    'LC': {'lat': 13.909444, 'lng': -60.978893, 'zoom': 10},
    'VC': {'lat': 12.984305, 'lng': -61.287228, 'zoom': 10},
    'WS': {'lat': -13.759029, 'lng': -172.104629, 'zoom': 10},
    'SM': {'lat': 43.94236, 'lng': 12.457777, 'zoom': 11},
    'ST': {'lat': 0.18636, 'lng': 6.613081, 'zoom': 10},
    'SA': {'lat': 23.885942, 'lng': 45.079162, 'zoom': 5},
    'SN': {'lat': 14.497401, 'lng': -14.452362, 'zoom': 7},
    'RS': {'lat': 44.016521, 'lng': 21.005859, 'zoom': 7},
    'SC': {'lat': -4.679574, 'lng': 55.491977, 'zoom': 10},
    'SL': {'lat': 8.460555, 'lng': -11.779889, 'zoom': 8},
    'SG': {'lat': 1.352083, 'lng': 103.819836, 'zoom': 11},
    'SK': {'lat': 48.669026, 'lng': 19.699024, 'zoom': 7},
    'SI': {'lat': 46.151241, 'lng': 14.995463, 'zoom': 8},
    'SB': {'lat': -9.64571, 'lng': 160.156194, 'zoom': 8},
    'SO': {'lat': 5.152149, 'lng': 46.199616, 'zoom': 6},
    'ZA': {'lat': -30.559482, 'lng': 22.937506, 'zoom': 5},
    'SS': {'lat': 6.876991, 'lng': 31.306978, 'zoom': 6},
    'ES': {'lat': 40.463667, 'lng': -3.74922, 'zoom': 6},
    'LK': {'lat': 7.873054, 'lng': 80.771797, 'zoom': 7},
    'SD': {'lat': 12.862807, 'lng': 30.217636, 'zoom': 5},
    'SR': {'lat': 3.919305, 'lng': -56.027783, 'zoom': 7},
    'SE': {'lat': 60.128161, 'lng': 18.643501, 'zoom': 5},
    'CH': {'lat': 46.818188, 'lng': 8.227512, 'zoom': 7},
    'SY': {'lat': 34.802075, 'lng': 38.996815, 'zoom': 6},
    'TJ': {'lat': 38.861034, 'lng': 71.276093, 'zoom': 7},
    'TZ': {'lat': -6.369028, 'lng': 34.888822, 'zoom': 6},
    'TH': {'lat': 15.870032, 'lng': 100.992541, 'zoom': 6},
    'TL': {'lat': -8.874217, 'lng': 125.727539, 'zoom': 9},
    'TG': {'lat': 8.619543, 'lng': 0.824782, 'zoom': 7},
    'TO': {'lat': -21.178986, 'lng': -175.198242, 'zoom': 9},
    'TT': {'lat': 10.691803, 'lng': -61.222503, 'zoom': 9},
    'TN': {'lat': 33.886917, 'lng': 9.537499, 'zoom': 7},
    'TR': {'lat': 38.963745, 'lng': 35.243322, 'zoom': 6},
    'TM': {'lat': 38.969719, 'lng': 59.556278, 'zoom': 6},
    'TV': {'lat': -7.109535, 'lng': 177.64933, 'zoom': 10},
    'UG': {'lat': 1.373333, 'lng': 32.290275, 'zoom': 7},
    'UA': {'lat': 48.379433, 'lng': 31.16558, 'zoom': 6},
    'AE': {'lat': 23.424076, 'lng': 53.847818, 'zoom': 7},
    'GB': {'lat': 55.378051, 'lng': -3.435973, 'zoom': 5},
    'US': {'lat': 37.09024, 'lng': -95.712891, 'zoom': 4},
    'UY': {'lat': -32.522779, 'lng': -55.765835, 'zoom': 7},
    'UZ': {'lat': 41.377491, 'lng': 64.585262, 'zoom': 6},
    'VU': {'lat': -15.376706, 'lng': 166.959158, 'zoom': 7},
    'VA': {'lat': 41.902916, 'lng': 12.453389, 'zoom': 14},
    'VE': {'lat': 6.42375, 'lng': -66.58973, 'zoom': 6},
    'VN': {'lat': 14.058324, 'lng': 108.277199, 'zoom': 5},
    'YE': {'lat': 15.552727, 'lng': 48.516388, 'zoom': 6},
    'ZM': {'lat': -13.133897, 'lng': 27.849332, 'zoom': 6},
    'ZW': {'lat': -19.015438, 'lng': 29.154857, 'zoom': 6}
}

# For tracking visited countries on the map
VISITED_COUNTRIES = set()

def ensure_flags_directory():
    """Make sure the flags directory exists"""
    if not os.path.exists(FLAGS_DIR):
        os.makedirs(FLAGS_DIR)

def download_flag(country_code):
    """Download a flag if it doesn't already exist locally"""
    flag_path = os.path.join(FLAGS_DIR, f"{country_code}.png")
    
    # If flag already exists, just return the local path
    if os.path.exists(flag_path):
        return f"/static/flags/{country_code}.png"
    
    # If it doesn't exist, download it
    try:
        response = requests.get(FLAG_API.format(country_code))
        if response.status_code == 200:
            with open(flag_path, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded flag for {country_code}")
            return f"/static/flags/{country_code}.png"
        else:
            print(f"Failed to download flag for {country_code}: {response.status_code}")
            return FLAG_API.format(country_code)  # Fall back to API URL
    except Exception as e:
        print(f"Error downloading flag for {country_code}: {e}")
        return FLAG_API.format(country_code)  # Fall back to API URL

def download_all_flags():
    """Download all flags at once"""
    ensure_flags_directory()
    
    # Make sure COUNTRIES is loaded
    if not COUNTRIES:
        print("Country data not available. Loading now...")
        globals()['COUNTRIES'] = load_country_data()
    
    total = len(COUNTRIES)
    current = 0
    
    for country_name, country_data in COUNTRIES.items():
        country_code = country_data['code']
        current += 1
        print(f"Downloading flag {current}/{total}: {country_name} ({country_code})")
        
        download_flag(country_code)
        time.sleep(0.2)  # Small delay to avoid overloading the server

def get_flag_url(country_code):
    """Get the URL for a flag, preferring local files"""
    flag_path = os.path.join(FLAGS_DIR, f"{country_code}.png")
    if os.path.exists(flag_path):
        return f"/static/flags/{country_code}.png"
    
    # If not available locally, download it
    return download_flag(country_code)

def generate_country_outline(country_code, partial=False):
    """Generate or retrieve a country outline image
    
    Args:
        country_code: The two-letter country code
        partial: If True, generates a partial (angled) silhouette for use as a hint
    """
    # Define file paths based on whether we want a full or partial outline
    if partial:
        outline_path = os.path.join(OUTLINES_DIR, f"{country_code}_partial.png")
        outline_url = f"/static/outlines/{country_code}_partial.png"
    else:
        outline_path = os.path.join(OUTLINES_DIR, f"{country_code}.png")
        outline_url = f"/static/outlines/{country_code}.png"
    
    # If outline already exists, just use it
    if os.path.exists(outline_path):
        return outline_url
    
    # Create directory if it doesn't exist
    if not os.path.exists(OUTLINES_DIR):
        os.makedirs(OUTLINES_DIR)
    
    # Generate outline from flag
    flag_path = os.path.join(FLAGS_DIR, f"{country_code}.png")
    if os.path.exists(flag_path):
        try:
            # This part requires PIL/Pillow library
            from PIL import Image, ImageOps, ImageFilter, ImageEnhance, ImageDraw
            
            # Open flag image
            img = Image.open(flag_path)
            
            # Convert to grayscale
            img = img.convert('L')
            
            # Apply edge detection
            img = img.filter(ImageFilter.FIND_EDGES)
            
            # Invert colors
            img = ImageOps.invert(img)
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(2.0)
            
            # If partial silhouette is requested, create an angled mask
            if partial:
                # Create a blank mask the same size as the image
                mask = Image.new('L', img.size, 0)
                draw = ImageDraw.Draw(mask)
                
                # Get image dimensions
                width, height = img.size
                
                # Create an angled polygon covering roughly 60% of the image
                # Instead of a straight half, we'll do an angled reveal
                # This creates a diagonal mask from top-left to bottom-right
                polygon_points = [
                    (0, 0),  # Top-left
                    (width * 0.7, 0),  # Top-right (partial)
                    (width * 0.3, height),  # Bottom-left (partial)
                    (0, height)  # Bottom-left
                ]
                
                # Draw the polygon on the mask (255 = white = visible area)
                draw.polygon(polygon_points, fill=255)
                
                # Apply the mask to the outline image
                img = Image.composite(img, Image.new('L', img.size, 0), mask)
            
            # Save the outline
            img.save(outline_path)
            
            return outline_url
            
        except Exception as e:
            print(f"Error generating outline for {country_code}: {e}")
            # Fall back to using the flag with CSS filters
            return f"/static/flags/{country_code}.png"
    
    # If we don't have a flag either, return a placeholder
    return f"/static/flags/{country_code}.png"

def get_random_country():
    # Make sure COUNTRIES is loaded
    if not COUNTRIES:
        print("Country data not available. Loading now...")
        globals()['COUNTRIES'] = load_country_data()
        
        # If we still don't have data, return a fallback country
        if not COUNTRIES:
            print("ERROR: Could not load country data!")
            return "United States"
    
    # Exclude countries that have been already answered
    used_countries = set(session.get('used_countries', []))
    available_countries = [c for c in COUNTRIES.keys() if c not in used_countries]
    
    # If we've used up all countries, reset but don't repeat the most recent ones
    if not available_countries or len(available_countries) < 10:
        session['used_countries'] = session.get('used_countries', [])[-5:]
        available_countries = [c for c in COUNTRIES.keys() if c not in session['used_countries']]
    
    return random.choice(available_countries)

def get_random_flags(count, exclude=None):
    # Make sure COUNTRIES is loaded
    if not COUNTRIES:
        print("Country data not available. Loading now...")
        globals()['COUNTRIES'] = load_country_data()
        
    exclude = exclude or []
    all_codes = [country_data['code'] for country_data in COUNTRIES.values()]
    available_codes = [c for c in all_codes if c not in exclude]
    
    # If we need more flags than available, allow reuse but not immediate duplication
    if count > len(available_codes):
        return random.sample(all_codes, count)
    
    return random.sample(available_codes, count)

@app.route('/')
def index():
    ensure_flags_directory()
    
    if 'score' not in session:
        session['score'] = 0
        session['correct_flags'] = []
        session['used_countries'] = []
        session['current_flags'] = get_random_flags(3)
    
    target_country = get_random_country()
    target_code = COUNTRIES[target_country]['code']
    
    # Download the flag if needed
    flag_url = get_flag_url(target_code)
    
    # Generate or get both types of country outlines (full and partial)
    outline_url = generate_country_outline(target_code, partial=False)
    partial_outline_url = generate_country_outline(target_code, partial=True)
    
    # Download all the current flags
    for code in session['current_flags']:
        get_flag_url(code)
    
    # Ensure the target flag is among the choices
    if target_code not in session['current_flags']:
        # Replace a random flag with the target flag
        session['current_flags'][random.randint(0, len(session['current_flags'])-1)] = target_code
    
    session['target'] = target_country
    session['language'] = session.get('language', 'english')
    
    # Get flag count statistics
    flags_count = len(os.listdir(FLAGS_DIR)) if os.path.exists(FLAGS_DIR) else 0
    total_countries = len(COUNTRIES)
    
    # Get target country currency information
    target_currency = None
    if 'currency' in COUNTRIES[target_country]:
        target_currency = COUNTRIES[target_country]['currency']
    
    # Get region information
    target_region = None
    if 'region' in COUNTRIES[target_country]:
        target_region = COUNTRIES[target_country]['region']
    
    # Get map coordinates for this country (for showing on the map)
    target_coords = {}
    if target_code.upper() in COUNTRY_COORDS:
        target_coords = COUNTRY_COORDS[target_code.upper()]
    
    # Game mode: map-quiz - show map first, user selects flag
    return render_template('game.html', 
                          countries=COUNTRIES,
                          target=target_country,
                          target_arabic=COUNTRIES[target_country]['arabic'],
                          target_currency=target_currency,
                          target_region=target_region,
                          correct_flags=session['correct_flags'],
                          current_flags=session['current_flags'],
                          FLAG_API=FLAG_API,
                          language=session['language'],
                          flag_url=flag_url,
                          outline_url=outline_url,
                          partial_outline_url=partial_outline_url,
                          target_coords=target_coords,
                          country_coords=COUNTRY_COORDS,  # Add all country coordinates
                          flags_count=flags_count,
                          game_mode="map-quiz",
                          total_countries=total_countries)

@app.route('/check_answer', methods=['POST'])
def check_answer():
    user_choice = request.form['country']
    is_correct = request.form.get('correct', 'false') == 'true'
    target = session.get('target')
    target_code = COUNTRIES[target]['code']
    
    # Add current target to used countries to avoid repeating
    if target not in session.get('used_countries', []):
        if 'used_countries' not in session:
            session['used_countries'] = []
        session['used_countries'].append(target)
    
    if is_correct:
        session['score'] += 1
        if user_choice not in session['correct_flags']:
            session['correct_flags'].append(user_choice)
    
    # Generate new target and flags
    new_target = get_random_country()
    new_target_code = COUNTRIES[new_target]['code']
    
    # Generate both types of outlines for the new target country
    outline_url = generate_country_outline(new_target_code, partial=False)
    partial_outline_url = generate_country_outline(new_target_code, partial=True)
    
    # Calculate flag count based on progress
    flag_count = min(3 + session['score'] // 5, 8)  # Increase difficulty gradually up to 8 flags
    
    # Get new flags ensuring no repetition with correct flags
    # Only exclude answered flags, not just the current ones
    new_flags = get_random_flags(flag_count, exclude=session.get('correct_flags', []))
    
    # Download all new flags
    for code in new_flags:
        get_flag_url(code)
    
    # Ensure target flag is in the choices
    if new_target_code not in new_flags:
        if len(new_flags) > 0:
            new_flags[random.randint(0, len(new_flags)-1)] = new_target_code
        else:
            new_flags = [new_target_code]
    
    # Update session
    session['target'] = new_target
    session['current_flags'] = new_flags
    
    # Get flag URLs
    flag_urls = {code: get_flag_url(code) for code in new_flags}
    
    # Get target country currency information
    target_currency = None
    if 'currency' in COUNTRIES[new_target]:
        target_currency = COUNTRIES[new_target]['currency']
    
    # Get map coordinates for this country (for showing on the map)
    target_coords = {}
    if new_target_code.upper() in COUNTRY_COORDS:
        target_coords = COUNTRY_COORDS[new_target_code.upper()]
    
    # Return JSON for AJAX update
    response_data = {
        'target': new_target,
        'target_code': new_target_code,
        'target_arabic': COUNTRIES[new_target]['arabic'],
        'current_flags': new_flags,
        'flag_urls': flag_urls,
        'outline_url': outline_url,
        'partial_outline_url': partial_outline_url,
        'target_coords': target_coords,
        'country_coords': COUNTRY_COORDS,  # Add all country coordinates
        'score': session['score']
    }
    
    # Add currency data if available
    if target_currency:
        response_data['currency'] = target_currency
    
    return jsonify(response_data)

@app.route('/switch_language', methods=['POST'])
def switch_language():
    language = request.form.get('language', 'english')
    session['language'] = language
    return jsonify({'success': True})

@app.route('/reset_game', methods=['POST'])
def reset_game():
    # Clear all game-related session data
    session['score'] = 0
    session['correct_flags'] = []
    session['used_countries'] = []
    session['current_flags'] = get_random_flags(3)
    
    # Get a new target country
    target_country = get_random_country()
    target_code = COUNTRIES[target_country]['code']
    
    # Generate both types of outlines for the target country
    outline_url = generate_country_outline(target_code, partial=False)
    partial_outline_url = generate_country_outline(target_code, partial=True)
    
    # Ensure the target flag is among the choices
    if target_code not in session['current_flags']:
        session['current_flags'][random.randint(0, len(session['current_flags'])-1)] = target_code
    
    session['target'] = target_country
    
    # Get flag URLs
    flag_urls = {code: get_flag_url(code) for code in session['current_flags']}
    
    # Get target country currency information
    target_currency = None
    if 'currency' in COUNTRIES[target_country]:
        target_currency = COUNTRIES[target_country]['currency']
    
    # Get map coordinates for this country
    target_coords = {}
    if target_code.upper() in COUNTRY_COORDS:
        target_coords = COUNTRY_COORDS[target_code.upper()]
    
    # Return JSON for AJAX update
    response_data = {
        'target': target_country,
        'target_code': target_code,
        'target_arabic': COUNTRIES[target_country]['arabic'],
        'current_flags': session['current_flags'],
        'flag_urls': flag_urls,
        'outline_url': outline_url,
        'partial_outline_url': partial_outline_url,
        'target_coords': target_coords,
        'country_coords': COUNTRY_COORDS,  # Add all country coordinates
        'score': 0
    }
    
    # Add currency data if available
    if target_currency:
        response_data['currency'] = target_currency
    
    return jsonify(response_data)

@app.route('/download_flags', methods=['GET'])
def download_flags_route():
    download_all_flags()
    flags_count = len(os.listdir(FLAGS_DIR)) if os.path.exists(FLAGS_DIR) else 0
    return jsonify({
        'success': True, 
        'message': 'All flags downloaded',
        'count': flags_count,
        'total': len(COUNTRIES)
    })

@app.route('/flags_status', methods=['GET'])
def flags_status():
    flags_count = len(os.listdir(FLAGS_DIR)) if os.path.exists(FLAGS_DIR) else 0
    return jsonify({
        'count': flags_count,
        'total': len(COUNTRIES)
    })

# World Map Routes

@app.route('/world_map')
def world_map():
    """Display an interactive world map"""
    # Make sure all flags are available
    ensure_flags_directory()
    
    # Use session to track progress, or initialize if needed
    if 'score' not in session:
        session['score'] = 0
        session['correct_flags'] = []
        session['used_countries'] = []
    
    # Pick a random country for the initial display
    target_country = get_random_country()
    target_code = COUNTRIES[target_country]['code'].upper()
    
    # Debug info
    print(f"World Map: Target country = {target_country}, code = {target_code}")
    print(f"Number of countries in COUNTRIES: {len(COUNTRIES)}")
    print(f"Number of coordinates in COUNTRY_COORDS: {len(COUNTRY_COORDS)}")
    
    # Make copies of the data to ensure they're JSON serializable 
    countries_copy = {}
    for country_name, data in COUNTRIES.items():
        countries_copy[country_name] = {
            'code': data['code'],
            'arabic': data.get('arabic', '')
        }
        # Add region if available
        if 'region' in data:
            countries_copy[country_name]['region'] = data['region']
        # Add currency if available
        if 'currency' in data:
            countries_copy[country_name]['currency'] = data['currency']
    
    # Return the map template with normalized data
    return render_template('world_map.html',
                          country=target_country,
                          country_code=target_code,
                          countries=countries_copy,
                          country_coords=COUNTRY_COORDS,
                          visited=list(VISITED_COUNTRIES),
                          score=session['score'])

@app.route('/visit_country', methods=['POST'])
def visit_country():
    """Mark a country as visited on the map"""
    country_code = request.json.get('country_code')
    if country_code:
        # Normalize country code to uppercase for consistency
        country_code = country_code.upper()
        
        # Add to visited countries
        VISITED_COUNTRIES.add(country_code)
        
        # Add to score if not already visited
        newly_visited = False
        if country_code not in session.get('correct_flags', []):
            session['score'] = session.get('score', 0) + 1
            
            # Store the code in the session
            current_flags = session.get('correct_flags', [])
            if country_code not in current_flags:
                current_flags.append(country_code)
                session['correct_flags'] = current_flags
            
            newly_visited = True
        
        # Return success with updated information
        return jsonify({
            'success': True, 
            'visited': list(VISITED_COUNTRIES),
            'newly_visited': newly_visited,
            'score': session.get('score', 0)
        })
    
    return jsonify({'success': False, 'error': 'No country code provided'})

@app.route('/reset_map', methods=['POST'])
def reset_map():
    """Reset the world map exploration"""
    global VISITED_COUNTRIES
    VISITED_COUNTRIES = set()
    
    # Reset session data related to the map
    session['score'] = 0
    session['correct_flags'] = []
    
    return jsonify({'success': True})

if __name__ == '__main__':
    ensure_flags_directory()
    
    # Ensure the countries data is loaded
    if not COUNTRIES:
        print("Loading country data from meta.json...")
        COUNTRIES = load_country_data()
        print(f"Loaded data for {len(COUNTRIES)} countries")
    
    app.run(debug=True)