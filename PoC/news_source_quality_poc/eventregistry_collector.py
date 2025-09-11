import requests
import json
from datetime import datetime
from typing import List, Dict
from config import NEWSAPI_KEY


class EventRegistryCollector:
    def __init__(self, api_key: str, output_file: str = "eventregistry_articles.json"):
        self.api_key = api_key
        # Ensure output file is in the same directory as this script
        import os

        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.output_file = os.path.join(script_dir, output_file)
        self.collected_data = self.load_existing_data()
        self.base_url = "https://eventregistry.org/api/v1"

    def load_existing_data(self) -> List[Dict]:
        """Load existing data from the output file"""
        try:
            with open(self.output_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_data(self):
        """Save all collected data to the output file"""
        with open(self.output_file, "w") as f:
            json.dump(self.collected_data, f, indent=2, default=str)

    def suggest_sources_fast(self, prefix: str) -> List[Dict]:
        """Suggest news sources based on a prefix using the suggestSourcesFast endpoint"""
        print(f"Suggesting sources for prefix: '{prefix}'...")

        try:
            # Request body as specified
            request_body = {"prefix": prefix, "apiKey": self.api_key}

            response = requests.post(f"{self.base_url}/suggestSourcesFast", json=request_body)
            response.raise_for_status()

            data = response.json()
            print(f"Raw response: {json.dumps(data, indent=2)}")

            # Store the response
            result = {
                "prefix": prefix,
                "response": data,
                "collected_at": datetime.now().isoformat(),
                "endpoint": "suggestSourcesFast",
            }

            self.collected_data.append(result)

            # Extract sources if available
            sources = data if isinstance(data, list) else data.get("sources", [])
            print(f"Found {len(sources)} suggested sources for prefix: '{prefix}'")

            return sources

        except requests.exceptions.RequestException as e:
            print(f"Error calling Event Registry API: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error: {e}")
            return []

    def run_suggest_sources(self, prefix: str):
        """Run source suggestion and save results"""
        sources = self.suggest_sources_fast(prefix)
        if sources:
            self.save_data()
            print(f"Saved suggestion results. Total data entries: {len(self.collected_data)}")

            # Display some sources if available
            print(f"\nSuggested sources for '{prefix}':")
            for i, source in enumerate(sources[:5]):  # Show first 5
                if isinstance(source, dict):
                    name = source.get("title", source.get("name", "Unknown"))
                    uri = source.get("uri", "No URI")
                    print(f"  {i+1}. {name} (URI: {uri})")
                else:
                    print(f"  {i+1}. {source}")

            if len(sources) > 5:
                print(f"  ... and {len(sources) - 5} more sources")
        else:
            print(f"No sources suggested for prefix: '{prefix}'")


# Example usage
if __name__ == "__main__":
    # Using API key from config
    API_KEY = NEWSAPI_KEY

    if not API_KEY or API_KEY == "your_eventregistry_api_key_here":
        print("Please set your Event Registry API key in the .env file")
        print("Add: EVENTREGISTRY_API_KEY=your_actual_key")
        print("Get your API key at: https://eventregistry.org/")
    else:
        collector = EventRegistryCollector(API_KEY)

        # Test with BBC as specified in your example
        print("=== Testing Event Registry suggestSourcesFast ===")
        collector.run_suggest_sources("BBC")

        # Test with other prefixes
        print("\n=== Testing with other prefixes ===")
        collector.run_suggest_sources("CNN")
        collector.run_suggest_sources("Reuters")
