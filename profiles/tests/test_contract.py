from unittest.mock import patch
import io
from app.main import obtener_user, crear_perfil_default

def test_contract_user_response_parsing():
    """Valida el contrato esperado del servicio users (debe contener id y display_name)."""
    contract_response_json = '{"id": "usr-999", "display_name": "Contrato Test", "email": "test@test.com"}'
    
    class MockResponse:
        def read(self):
            return contract_response_json.encode("utf-8")
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    with patch("app.main.urlopen", return_value=MockResponse()):
        user = obtener_user("usr-999")
        assert user is not None
        assert "id" in user
        assert "display_name" in user
        assert user["id"] == "usr-999"