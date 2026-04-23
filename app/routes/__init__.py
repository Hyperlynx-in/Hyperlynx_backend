# app/routes/__init__.py

from .auth import auth_bp
from .company_profile import profile_api
from .regulatory_updates import updates_bp
from .applicability_api import applicability_api
from .frameworks_api import frameworks_api

# --- NEW IMPORTS FOR PHASE 4 ---
from .risk_api import risk_api
from .metrics_api import metrics_api
from .context_report_api import context_report_api

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
    
    app.register_blueprint(updates_bp, url_prefix='/api/updates')
    
    app.register_blueprint(profile_api)
    app.register_blueprint(applicability_api)
    app.register_blueprint(frameworks_api)
    
    app.register_blueprint(risk_api)
    app.register_blueprint(metrics_api)
    app.register_blueprint(context_report_api)

    
    
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')