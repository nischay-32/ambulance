import sys
import os
from dotenv import load_dotenv

# Ensure backend directory is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

load_dotenv(os.path.join(current_dir, '.env'))
from routing_engine import RoutingEngine
re = RoutingEngine()
hosp = re.get_nearest_hospital({'lat': 12.9716, 'lng': 77.5946})
print('FIND HOSP:', hosp)
if 'lat' in hosp:
    route = re.get_route({'lat': 12.9716, 'lng': 77.5946}, {'lat': hosp['lat'], 'lng': hosp['lng']})
    if isinstance(route, dict) and 'error' in route:
        print('ROUTE ERROR:', route['error'])
        if 'details' in route: print('DETAILS:', route['details'])
    else:
        print('ROUTE SUCCESS')

