"""Corporate authentication middleware for Flask applications.

Provides SSO integration, session management, and role-based access control.
"""
from .middleware import AuthMiddleware, require_auth, init_auth

__version__ = '1.2.0'
__all__ = ['AuthMiddleware', 'require_auth', 'init_auth']
