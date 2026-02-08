# Routes package
from .stored_libraries import register_library_routes
from .loaded_libraries import register_loaded_library_routes
from .frameworks import register_framework_routes
from .controls_and_matrices import register_control_routes, register_risk_matrix_routes
from .mappings import register_mapping_routes


def register_all_routes(app):
    """Register all API routes"""
    register_library_routes(app)
    register_loaded_library_routes(app)
    register_framework_routes(app)
    register_control_routes(app)
    register_risk_matrix_routes(app)
    register_mapping_routes(app)
