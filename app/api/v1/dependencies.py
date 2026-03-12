from todo_auth import KeycloakJWTService, make_auth_dependency
from app.core.config import settings

_jwt_service = KeycloakJWTService(public_key=settings.KEYCLOAK_PUBLIC_KEY)
get_current_user = make_auth_dependency(_jwt_service)
