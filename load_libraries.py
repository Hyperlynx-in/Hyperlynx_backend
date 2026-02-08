"""Command to load YAML libraries from libraries/ folder into database"""
import os
import yaml
import json
from pathlib import Path
from datetime import datetime, date
from application import db, create_app
from app.models import StoredLibrary


class DateEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime objects"""
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)


def sanitize_content(obj):
    """Convert date objects to strings in nested structures"""
    if isinstance(obj, dict):
        return {k: sanitize_content(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_content(item) for item in obj]
    elif isinstance(obj, (date, datetime)):
        return obj.isoformat()
    return obj


def load_libraries_from_folder():
    """Load all YAML files from libraries folder into database"""
    app = create_app()
    
    with app.app_context():
        # Get the correct path to libraries folder
        libraries_path = Path(__file__).parent / 'libraries'
        
        if not libraries_path.exists():
            print(f"Libraries folder not found: {libraries_path}")
            return
        
        loaded_count = 0
        skipped_count = 0
        error_count = 0
        
        for yaml_file in libraries_path.glob('*.yaml'):
            try:
                print(f"Processing: {yaml_file.name}")
                
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    content = yaml.safe_load(f)
                
                urn = content.get('urn', f'urn:intuitem:risk:library:{yaml_file.stem}')
                
                # Check if already exists
                existing = StoredLibrary.query.filter_by(urn=urn).first()
                if existing:
                    print(f"  → Already exists, updating...")
                    library = existing
                else:
                    library = StoredLibrary(id=urn, urn=urn)
                
                # Determine object type
                object_type = 'mixed'
                if 'objects' in content:
                    objects = content['objects']
                    if 'framework' in objects:
                        object_type = 'framework'
                    elif 'reference_controls' in objects:
                        object_type = 'reference_controls'
                    elif 'risk_matrix' in objects:
                        object_type = 'risk_matrix'
                    elif 'requirement_mapping_sets' in objects:
                        object_type = 'mapping'
                
                # Update fields
                library.ref_id = content.get('ref_id', yaml_file.stem)
                library.locale = content.get('locale', 'en')
                library.name = content.get('name', yaml_file.stem)
                library.description = content.get('description', '')
                library.copyright = content.get('copyright', '')
                library.version = str(content.get('version', '1'))
                library.provider = content.get('provider', '')
                library.packager = content.get('packager', 'intuitem')
                library.object_type = object_type
                library.content = sanitize_content(content)  # Sanitize dates
                library.translations = content.get('translations', {})
                
                # Parse publication date
                if pub_date := content.get('publication_date'):
                    try:
                        library.publication_date = datetime.strptime(str(pub_date), '%Y-%m-%d').date()
                    except:
                        pass
                
                db.session.add(library)
                loaded_count += 1
                print(f"  [OK] Loaded: {library.name}")
                
            except Exception as e:
                error_count += 1
                print(f"  [ERROR] {str(e)}")
        
        db.session.commit()
        
        print(f"\n=== Summary ===")
        print(f"Loaded: {loaded_count}")
        print(f"Errors: {error_count}")
        print(f"Total libraries in DB: {StoredLibrary.query.count()}")


if __name__ == '__main__':
    load_libraries_from_folder()
