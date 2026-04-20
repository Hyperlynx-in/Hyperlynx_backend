import os
import sys
import yaml
import uuid
import glob
from datetime import date, datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from application import create_app, db
from app.models import StoredLibrary, LoadedLibrary, Framework, RequirementNode

app = create_app()

def sanitize_for_json(obj):
    """Recursively converts datetime objects to strings for JSON serialization."""
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(v) for v in obj]
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return obj

def extract_nodes_universally(data, parent_urn=None, level=0):
    """
    Universally crawls ANY JSON/YAML structure to find nested controls/requirements,
    completely bypassing schema versioning issues.
    """
    nodes = []
    
    EXCLUDED_URNS = ['library', 'framework', 'matrix', 'mapping', 'questionnaire', 'preset', 'timeline']
    
    if isinstance(data, dict):
        urn = data.get('urn', '')
        urn_lower = str(urn).lower()
        
        is_node = False
        
        if urn and not any(ex in urn_lower for ex in EXCLUDED_URNS):
            if data.get('name') or data.get('ref_id') or data.get('description'):
                is_node = True

        if is_node:
            nodes.append({
                'urn': urn,
                'ref_id': str(data.get('ref_id', '')),
                'name': str(data.get('name', '')),
                'description': str(data.get('description', '')),
                'parent_urn': parent_urn,
                'level': level,
                'order_id': data.get('order_id') or data.get('order') or 0
            })
            next_parent = urn
            next_level = level + 1
        else:
            next_parent = parent_urn
            next_level = level
            
        for key, value in data.items():
            if key in ['translations', 'scores', 'scores_definition', 'levels', 'matrix_json']:
                continue
            if isinstance(value, (dict, list)):
                nodes.extend(extract_nodes_universally(value, next_parent, next_level))

    elif isinstance(data, list):
        for idx, item in enumerate(data):
            if isinstance(item, dict) and 'order_id' not in item and 'order' not in item:
                item['order_id'] = idx # Auto-assign order based on list position
            nodes.extend(extract_nodes_universally(item, parent_urn, level))
            
    return nodes

def parse_and_insert_yaml(file_path):
    if not os.path.exists(file_path):
        return

    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            documents = list(yaml.safe_load_all(file))
            if not documents or not documents[0]:
                return
            data = documents[0]
        except yaml.YAMLError:
            return

    with app.app_context():
        db.create_all()
        
        library_urn = data.get('urn', f"urn:library:custom:{uuid.uuid4().hex[:8]}")
        
        stored_lib = StoredLibrary.query.filter_by(urn=library_urn).first()
        if not stored_lib:
            stored_lib = StoredLibrary(
                id=str(uuid.uuid4()),
                urn=library_urn,
                ref_id=data.get('ref_id', 'custom-lib'),
                name=data.get('name', 'Imported Library'),
                description=data.get('description', ''),
                provider=data.get('provider', 'Ciso Assistant Community'),
                version=str(data.get('version', '1.0')),
                content=sanitize_for_json(data)
            )
            db.session.add(stored_lib)
            db.session.flush()

        loaded_lib = LoadedLibrary.query.filter_by(urn=library_urn).first()
        if not loaded_lib:
            loaded_lib = LoadedLibrary(
                id=str(uuid.uuid4()),
                urn=library_urn,
                stored_library_id=stored_lib.id,
                ref_id=stored_lib.ref_id,
                name=stored_lib.name,
                version=stored_lib.version,
                provider=stored_lib.provider,
                loaded_by="system_import"
            )
            db.session.add(loaded_lib)
            db.session.flush()

        framework_urn = data.get('urn', '').replace('library', 'framework')
        if not framework_urn or 'framework' not in framework_urn:
            framework_urn = f"urn:intuitem:risk:framework:{uuid.uuid4().hex[:8]}"

        framework = Framework.query.filter_by(urn=framework_urn).first()
        
        if framework:
            existing_nodes = RequirementNode.query.filter_by(framework_id=framework.id).count()
            if existing_nodes > 0:
                print(f"Framework '{framework.name}' already has {existing_nodes} nodes. Skipping.")
                return
            else:
                db.session.delete(framework)
                db.session.flush()

        framework = Framework(
            id=str(uuid.uuid4()),
            urn=framework_urn,
            ref_id=data.get('ref_id', 'FWK'),
            name=data.get('name', os.path.basename(file_path)),
            description=data.get('description', ''),
            library_urn=loaded_lib.urn
        )
        db.session.add(framework)
        db.session.flush() 

        extracted_nodes = extract_nodes_universally(data)
        
        nodes_to_insert = []
        for node_data in extracted_nodes:
            nodes_to_insert.append(RequirementNode(
                id=str(uuid.uuid4()),
                urn=node_data['urn'],
                ref_id=node_data['ref_id'][:100], 
                name=node_data['name'][:500], 
                description=node_data['description'],
                framework_id=framework.id,
                parent_urn=node_data['parent_urn'],
                order_id=node_data['order_id'],
                level=node_data['level']
            ))
            
        if nodes_to_insert:
            db.session.bulk_save_objects(nodes_to_insert)

        print(f"Extracted {len(nodes_to_insert)} controls/articles for {framework.name}...")

        try:
            db.session.commit()
            print(f"Successfully imported '{framework.name}'!")
        except Exception as e:
            db.session.rollback()
            print(f"Database error: {str(e)}")

if __name__ == "__main__":
    libraries_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../libraries'))
    yaml_files = glob.glob(os.path.join(libraries_dir, '*.yaml')) + glob.glob(os.path.join(libraries_dir, '*.yml'))
    
    if yaml_files:
        print(f"Found {len(yaml_files)} framework files. Starting universal batch import...\n")
        for file_path in yaml_files:
            print(f"--- Processing {os.path.basename(file_path)} ---")
            parse_and_insert_yaml(file_path)
            print("-" * 40)
        print("\nBatch import complete!")