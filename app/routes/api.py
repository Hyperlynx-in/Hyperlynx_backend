from flask import Blueprint, jsonify, request
import os
import yaml
from pathlib import Path

api_bp = Blueprint('api', __name__)


@api_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    GET /api/health
    """
    return jsonify({
        'status': 'success',
        'message': 'Hyperlynx API is running',
        'code': 200
    }), 200


@api_bp.route('/framework-library', methods=['GET'])
def framework_library():
    """
    Get framework library details from YAML files
    GET /api/framework-library - List all frameworks
    GET /api/framework-library?name=nist-csf-2.0 - Get specific framework
    """
    framework_name = request.args.get('name', None)
    
    # Get the libraries directory path
    base_dir = Path(__file__).resolve().parent.parent.parent
    libraries_dir = base_dir / 'libraries'
    
    if not libraries_dir.exists():
        return jsonify({
            'status': 'error',
            'message': 'Libraries directory not found',
            'code': 404
        }), 404
    
    # If specific framework requested
    if framework_name:
        # Add .yaml extension if not provided
        if not framework_name.endswith('.yaml'):
            framework_name = f"{framework_name}.yaml"
        
        framework_path = libraries_dir / framework_name
        
        if not framework_path.exists():
            return jsonify({
                'status': 'error',
                'message': f'Framework "{framework_name}" not found',
                'code': 404
            }), 404
        
        try:
            with open(framework_path, 'r', encoding='utf-8') as file:
                framework_data = yaml.safe_load(file)
            
            return jsonify({
                'status': 'success',
                'data': framework_data,
                'code': 200
            }), 200
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Error reading framework: {str(e)}',
                'code': 500
            }), 500
    
    # List all available frameworks
    try:
        yaml_files = [f.name for f in libraries_dir.glob('*.yaml')]
        
        frameworks = []
        for yaml_file in sorted(yaml_files):
            try:
                with open(libraries_dir / yaml_file, 'r', encoding='utf-8') as file:
                    data = yaml.safe_load(file)
                    frameworks.append({
                        'filename': yaml_file,
                        'name': data.get('name', 'Unknown'),
                        'ref_id': data.get('ref_id', ''),
                        'description': data.get('description', ''),
                        'version': data.get('version', ''),
                        'provider': data.get('provider', ''),
                    })
            except Exception as e:
                # Skip files that can't be parsed
                continue
        
        return jsonify({
            'status': 'success',
            'count': len(frameworks),
            'data': frameworks,
            'code': 200
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error listing frameworks: {str(e)}',
            'code': 500
        }), 500
