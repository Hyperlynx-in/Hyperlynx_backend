import os
import yaml

def inspect_yaml_structure(file_name):
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../libraries', file_name))
    
    if not os.path.exists(file_path):
        print(f"Could not find {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        docs = list(yaml.safe_load_all(f))
        if not docs or not docs[0]:
            print("Empty file")
            return
            
        data = docs[0]
        
        print(f"\n--- Inspecting {file_name} ---")
        print(f"Top-level keys: {list(data.keys())}")
        
        for key in ['requirements', 'nodes', 'controls', 'items', 'content', 'tree']:
            if key in data:
                items = data[key]
                if isinstance(items, list):
                    print(f"Found '{key}' list with {len(items)} items.")
                    if len(items) > 0:
                        print(f"Sample of first item in '{key}': {list(items[0].keys())}")
                elif isinstance(items, dict):
                    print(f"Found '{key}' dict with {len(items)} keys.")

if __name__ == "__main__":
    inspect_yaml_structure('dora.yaml')
    inspect_yaml_structure('iso27001-2022.yaml')
    inspect_yaml_structure('nist-csf-2.0.yaml')