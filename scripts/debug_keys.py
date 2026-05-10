import os
import yaml
import glob

def debug_yaml_structure():
    libraries_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../libraries'))
    yaml_files = glob.glob(os.path.join(libraries_dir, 'dora.yaml'))
    
    if not yaml_files:
        print("dora.yaml not found. Please make sure it's in the libraries folder.")
        return
        
    with open(yaml_files[0], 'r', encoding='utf-8') as file:
        data = list(yaml.safe_load_all(file))[0]
        
    objects = data.get('objects', [])
    items = objects.values() if isinstance(objects, dict) else objects
    
    print("\n--- Keys found in the first 3 objects ---")
    for i, obj in enumerate(list(items)[:3]):
        if isinstance(obj, dict):
            print(f"Object {i+1} keys: {list(obj.keys())}")
            for key in ['type', 'object_type', 'model', 'class', 'urn']:
                if key in obj:
                    print(f"   -> {key}: {obj[key]}")

if __name__ == "__main__":
    debug_yaml_structure()