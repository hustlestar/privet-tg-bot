#!/usr/bin/env python3
"""Extract OpenAPI spec from running FastAPI server."""

import json
import sys
from pathlib import Path
import requests


def extract_spec(base_url="http://localhost:8000", output_file="openapi.json"):
    """Extract OpenAPI spec from a running FastAPI server."""
    try:
        # Try to get the spec
        response = requests.get(f"{base_url}/openapi.json")
        response.raise_for_status()
        
        spec = response.json()
        
        # Save to file
        with open(output_file, "w") as f:
            json.dump(spec, f, indent=2)
        
        print(f"✅ OpenAPI spec saved to {output_file}")
        print(f"   Title: {spec.get('info', {}).get('title', 'Unknown')}")
        print(f"   Version: {spec.get('info', {}).get('version', 'Unknown')}")
        print(f"   Paths: {len(spec.get('paths', {}))}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to {base_url}")
        print("   Make sure the FastAPI server is running:")
        print("   python -m privet_api.main")
        return False
    except Exception as e:
        print(f"❌ Error extracting spec: {e}")
        return False


if __name__ == "__main__":
    # Parse command line arguments
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "openapi.json"
    
    if extract_spec(base_url, output_file):
        sys.exit(0)
    else:
        sys.exit(1)