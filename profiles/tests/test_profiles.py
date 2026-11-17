import base64
import io
from unittest.mock import patch

# Mock para simular que el usuario sí existe en el servicio 'users'
mock_user_exists = patch("app.main.obtener_user", return_value={"id": "user-123", "display_name": "Test User"})

# PNG mínimo de 1x1 píxel codificado en base64
PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
)

def test_get_profile_success(client):
    """Caso exitoso: Obtener perfil de un usuario existente."""
    with mock_user_exists:
        response = client.get("/api/v1/profiles/user-123")
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "user-123"
        assert data["display_name"] == "Test User"

def test_get_profile_not_found(client):
    """Caso de error (404): El usuario no existe en el servicio 'users'."""
    with patch("app.main.obtener_user", return_value=None):
        response = client.get("/api/v1/profiles/nonexistent")
        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"


def test_update_profile_success(client):
    """Caso exitoso: Actualizar bio y estado del perfil."""
    with mock_user_exists:
        # Primero se crea/obtiene
        client.get("/api/v1/profiles/user-123")
        
        # Luego se actualiza con PATCH
        response = client.patch(
            "/api/v1/profiles/user-123",
            json={"bio": "Nueva bio de prueba", "status": "Activo"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["bio"] == "Nueva bio de prueba"
        assert data["status"] == "Activo"

def test_update_profile_empty_body(client):
    """Caso de error (422): Enviar un body vacío sin campos a modificar."""
    with mock_user_exists:
        client.get("/api/v1/profiles/user-123")
        response = client.patch("/api/v1/profiles/user-123", json={})
        assert response.status_code == 422


def test_upload_avatar_success(client):
    """Caso exitoso: Subir una imagen PNG válida como avatar."""
    with mock_user_exists:
        client.get("/api/v1/profiles/user-123")
        response = client.post(
            "/api/v1/profiles/user-123/avatar",
            files={"avatar": ("avatar.png", io.BytesIO(PNG_BYTES), "image/png")}
        )
        assert response.status_code == 200
        assert response.json()["avatar_url"] is not None

def test_upload_avatar_invalid_format(client):
    """Caso de error (415): Subir un archivo que no es imagen válida."""
    with mock_user_exists:
        client.get("/api/v1/profiles/user-123")
        response = client.post(
            "/api/v1/profiles/user-123/avatar",
            files={"avatar": ("texto.txt", io.BytesIO(b"esto no es una imagen"), "text/plain")}
        )
        assert response.status_code == 415


def test_delete_avatar_success(client):
    """Caso exitoso: Eliminar un avatar existente."""
    with mock_user_exists:
        client.get("/api/v1/profiles/user-123")
        # Sube avatar primero
        client.post(
            "/api/v1/profiles/user-123/avatar", 
            files={"avatar": ("avatar.png", io.BytesIO(PNG_BYTES), "image/png")}
        )
        
        # Lo borra
        response = client.delete("/api/v1/profiles/user-123/avatar")
        assert response.status_code == 200
        assert response.json()["avatar_url"] is None

def test_delete_avatar_not_found(client):
    """Caso de error (404): Intentar borrar un avatar cuando no tiene ninguno."""
    with mock_user_exists:
        client.get("/api/v1/profiles/user-123")
        response = client.delete("/api/v1/profiles/user-123/avatar")
        assert response.status_code == 404
        assert response.json()["detail"] == "Profile has no avatar"