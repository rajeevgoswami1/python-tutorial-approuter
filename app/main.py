"""
SAP BTP Hello World Python Application with XSUAA Authentication
"""
import os
from flask import Flask, jsonify, request
from cfenv import AppEnv
from sap import xssec

app = Flask(__name__)

# Get Cloud Foundry environment
env = AppEnv()

# Get XSUAA service credentials
xsuaa_service = env.get_service(label='xsuaa')
xsuaa_credentials = xsuaa_service.credentials if xsuaa_service else None


def get_token_from_request():
    """Extract JWT token from Authorization header (forwarded by AppRouter)."""
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        return auth_header[7:]
    return None


def get_security_context():
    """Get security context from JWT token."""
    token = get_token_from_request()
    if not token or not xsuaa_credentials:
        return None
    
    try:
        return xssec.create_security_context(token, xsuaa_credentials)
    except Exception:
        return None


@app.route('/')
def home():
    """Home page - shows user info if authenticated."""
    security_context = get_security_context()
    
    if security_context:
        user_info = {
            "email": security_context.get_email() if hasattr(security_context, 'get_email') else "N/A",
            "user_name": security_context.get_logon_name() if hasattr(security_context, 'get_logon_name') else "N/A",
            "given_name": security_context.get_given_name() if hasattr(security_context, 'get_given_name') else "N/A",
            "family_name": security_context.get_family_name() if hasattr(security_context, 'get_family_name') else "N/A"
        }
        return jsonify({
            "message": "Welcome to SAP BTP Python Hello World!",
            "authenticated": True,
            "user": user_info
        })
    
    return jsonify({
        "message": "Welcome to SAP BTP Python Hello World!",
        "authenticated": False,
        "info": "Access via AppRouter for automatic authentication"
    })


@app.route('/hello')
def hello():
    """Protected endpoint - requires authentication via AppRouter."""
    security_context = get_security_context()
    
    if not security_context:
        return jsonify({
            "error": "Not authenticated",
            "hint": "Access this endpoint via the AppRouter URL"
        }), 401
    
    user_info = {
        "email": security_context.get_email() if hasattr(security_context, 'get_email') else "N/A",
        "user_name": security_context.get_logon_name() if hasattr(security_context, 'get_logon_name') else "N/A",
        "given_name": security_context.get_given_name() if hasattr(security_context, 'get_given_name') else "N/A",
        "family_name": security_context.get_family_name() if hasattr(security_context, 'get_family_name') else "N/A"
    }
    
    return jsonify({
        "message": "Hello from SAP BTP!",
        "authenticated": True,
        "user": user_info
    })


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "xsuaa_bound": xsuaa_credentials is not None
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
