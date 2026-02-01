from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
import os
import yaml
from pathlib import Path


class HealthCheckView(APIView):
    """
    Health check endpoint to verify API is running.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(
            {
                'status': 'success',
                'message': 'Hyperlynx API is running',
                'code': 200
            },
            status=status.HTTP_200_OK
        )


class FrameworkLibraryView(APIView):
    """
    Get framework library details from YAML files.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        """
        GET /api/framework-library/ - List all available frameworks
        GET /api/framework-library/?name=nist-csf-2.0 - Get specific framework by filename
        """
        framework_name = request.query_params.get('name', None)
        
        # Get the libraries directory path
        base_dir = Path(__file__).resolve().parent.parent
        libraries_dir = base_dir / 'libraries'
        
        if not libraries_dir.exists():
            return Response(
                {
                    'status': 'error',
                    'message': 'Libraries directory not found',
                    'code': 404
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        # If specific framework requested
        if framework_name:
            # Add .yaml extension if not provided
            if not framework_name.endswith('.yaml'):
                framework_name = f"{framework_name}.yaml"
            
            framework_path = libraries_dir / framework_name
            
            if not framework_path.exists():
                return Response(
                    {
                        'status': 'error',
                        'message': f'Framework "{framework_name}" not found',
                        'code': 404
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            
            try:
                with open(framework_path, 'r', encoding='utf-8') as file:
                    framework_data = yaml.safe_load(file)
                
                return Response(
                    {
                        'status': 'success',
                        'data': framework_data,
                        'code': 200
                    },
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                return Response(
                    {
                        'status': 'error',
                        'message': f'Error reading framework: {str(e)}',
                        'code': 500
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
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
            
            return Response(
                {
                    'status': 'success',
                    'count': len(frameworks),
                    'data': frameworks,
                    'code': 200
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    'status': 'error',
                    'message': f'Error listing frameworks: {str(e)}',
                    'code': 500
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

