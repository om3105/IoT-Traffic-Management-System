"""
ThingSpeak Integration Module
Sends traffic density data to ThingSpeak IoT platform
"""

import requests
import json
import sys
from datetime import datetime
from pathlib import Path

# Add project directory to path
sys.path.insert(0, str(Path(__file__).parent))
from config import THINGSPEAK_BASE_URL, THINGSPEAK_API_KEY, VERBOSE


class ThingSpeakClient:
    """Client to send data to ThingSpeak."""
    
    def __init__(self, api_key=THINGSPEAK_API_KEY):
        self.api_key = api_key
        self.base_url = THINGSPEAK_BASE_URL
        self.last_update = None
    
    def send_traffic_data(self, road_data):
        """
        Send traffic density data to ThingSpeak.
        
        Args:
            road_data: Dict with road detection results
                {
                    0: {"cars": 5, "ambulances": 1, "total": 6, "density": "MEDIUM"},
                    1: {"cars": 3, "ambulances": 0, "total": 3, "density": "LOW"},
                    ...
                }
        """
        try:
            # Prepare payload for ThingSpeak
            payload = {
                "api_key": self.api_key,
                "field1": road_data[0]["total"],  # Road 1 total
                "field2": road_data[1]["total"],  # Road 2 total
                "field3": road_data[2]["total"],  # Road 3 total
                "field4": road_data[3]["total"],  # Road 4 total
                "field5": sum(rd["cars"] for rd in road_data.values()),  # Total cars
                "field6": sum(rd["ambulances"] for rd in road_data.values()),  # Total ambulances
                "field7": self._encode_density(road_data),  # Encoded density status
                "field8": self._get_priority_alert(road_data),  # Priority alert
            }
            
            # Send to ThingSpeak
            response = requests.post(self.base_url, params=payload, timeout=5)
            
            if response.status_code == 200:
                if VERBOSE:
                    print(f"[THINGSPEAK] ✓ Data sent successfully at {datetime.now().strftime('%H:%M:%S')}")
                    print(f"  Road 1: {road_data[0]['total']} | Road 2: {road_data[1]['total']} | "
                          f"Road 3: {road_data[2]['total']} | Road 4: {road_data[3]['total']}")
                return True
            else:
                print(f"[THINGSPEAK] ✗ Failed to send data. Status: {response.status_code}")
                return False
        
        except requests.exceptions.Timeout:
            print("[THINGSPEAK] ✗ Request timeout")
            return False
        except Exception as e:
            print(f"[THINGSPEAK] ✗ Error: {e}")
            return False
    
    def _encode_density(self, road_data):
        """Encode overall density as numeric value for ThingSpeak."""
        densities = [rd["density"] for rd in road_data.values()]
        
        if "HIGH" in densities:
            return 3  # High
        elif "MEDIUM" in densities:
            return 2  # Medium
        else:
            return 1  # Low
    
    def _get_priority_alert(self, road_data):
        """Check if ambulance detected and return priority flag."""
        ambulance_count = sum(rd["ambulances"] for rd in road_data.values())
        return 1 if ambulance_count > 0 else 0
    
    def verify_connection(self):
        """Test ThingSpeak connection."""
        try:
            payload = {"api_key": self.api_key, "field1": 0}
            response = requests.post(self.base_url, params=payload, timeout=5)
            
            if response.status_code == 200:
                print("[THINGSPEAK] ✓ Connection verified")
                return True
            else:
                print(f"[THINGSPEAK] ✗ Connection failed. Status: {response.status_code}")
                return False
        except Exception as e:
            print(f"[THINGSPEAK] ✗ Connection error: {e}")
            return False


if __name__ == "__main__":
    # Test connection
    client = ThingSpeakClient()
    client.verify_connection()
