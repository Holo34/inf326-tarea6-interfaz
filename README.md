# Tarea Unidad 7: Control de Calidad y Pruebas Automatizadas

Suite de pruebas automatizadas para el microservicio **profiles**

Esta entrega implementa pruebas de servicio (casos exitosos y de error), aislamiento de base de datos en memoria, verificación de contrato con el servicio `users` y pruebas de integración orquestadas con Docker Compose.

```
  ┌─────────────────────────────────────────────────────────────────────┐
  │                       Suite de Pruebas (pytest)                     │
  ├───────────────────────────────┬─────────────────────────────────────┤
  │  Pruebas de Servicio          │  Pruebas de Contrato                │
  │  (profiles/tests/             │  (profiles/tests/                   │
  │   test_profiles.py)           │   test_contract.py)                 │
  │                               │                                     │
  │  • TestClient (FastAPI)       │  • Valida contrato HTTP de users    │
  │  • BD aislada con mongomock   │    (/api/v1/users/{id})             │
  └───────────────────────────────┴─────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────┐
  │                 Prueba de Integración (Docker Compose)              │
  │                      (docker-compose.test.yml)                      │
  ├─────────────┬─────────────┬─────────────┬─────────────┬─────────────┤
  │    users    │  channels   │  messages   │  profiles   │  MongoDBs   │
  │   (base)    │   (base)    │   (base)    │  (nuestro)  │  (aisladas) │
  └─────────────┴─────────────┴─────────────┴─────────────┴─────────────┘
```

## Cómo ejecutar las pruebas

### 1. Pruebas de servicio y contrato (aisladas)

Desde la carpeta `profiles/`, activar el entorno virtual e instalar las dependencias:

```bash
cd profiles
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Ejecutar la suite completa con `pytest`:

```bash
pytest -v
```

### 2. Prueba de integración con Docker Compose

Desde la raíz del proyecto, levantar los servicios base junto con `profiles` y sus bases de datos de prueba:

```bash
docker compose -f docker-compose.test.yml up --build
```

| Servicio | Puerto local | Descripción |
| --- | --- | --- |
| **users** | http://localhost:8001 | Servicio base de usuarios |
| **channels** | http://localhost:8002 | Servicio base de canales |
| **messages** | http://localhost:8003 | Servicio base de mensajes |
| **profiles** | http://localhost:8006 | Microservicio de perfiles bajo prueba |

Todos los contenedores quedan aislados en la red **`microsvcs-test`**.

Para detener y limpiar los contenedores de prueba: `docker compose -f docker-compose.test.yml down -v`.

## Estructura de pruebas en el repositorio

| Archivo / Carpeta | Contenido | Propósito en la rúbrica |
| --- | --- | --- |
| `profiles/tests/conftest.py` | Fixtures de `pytest` y cliente HTTP (`TestClient`) | Aislamiento de la base de datos mediante `mongomock` |
| `profiles/tests/test_profiles.py` | Pruebas de endpoints (`GET`, `PATCH`, `POST`, `DELETE`) | Dos pruebas por endpoint (caso exitoso y caso de error) |
| `profiles/tests/test_contract.py` | Verificación de esquema de respuesta de `users` | Prueba de contrato con el chat base sin levantar el sistema |
| `docker-compose.test.yml` | Orquestación de `users`, `channels`, `messages` y `profiles` | Prueba de integración de extremo a extremo del flujo |

## Cobertura de pruebas implementadas

### Pruebas de servicio (`test_profiles.py`)

Cada endpoint de la API REST de `profiles` cuenta con al menos dos casos de prueba (éxito y error):

| Endpoint | Caso exitoso | Caso de error |
| --- | --- | --- |
| `GET /api/v1/profiles/{user_id}` | `200 OK`: Retorna o crea el perfil por defecto si el usuario existe en `users` | `404 Not Found`: Usuario inexistente en `users` |
| `PATCH /api/v1/profiles/{user_id}` | `200 OK`: Actualiza campos parciales (`bio`, `status`) | `422 Unprocessable Entity`: Cuerpo vacío sin campos a modificar |
| `POST /api/v1/profiles/{user_id}/avatar` | `200 OK`: Sube una imagen PNG válida y actualiza `avatar_url` | `415 Unsupported Media Type`: Archivo que no corresponde a imagen válida |
| `DELETE /api/v1/profiles/{user_id}/avatar` | `200 OK`: Elimina el avatar activo y deja `avatar_url` en `null` | `404 Not Found`: Intento de eliminar avatar cuando el perfil no tiene uno |

### Estrategia de aislamiento (`conftest.py`)

- **Base de datos en memoria:** Se intercepta `pymongo.MongoClient` con `mongomock.MongoClient` antes de inicializar la aplicación FastAPI.
- **Limpieza automática:** Una fixture con `autouse=True` ejecuta `database.profiles.drop()` antes de cada prueba, garantizando independencia entre tests y cero impacto sobre instancias reales de MongoDB.

### Prueba de contrato (`test_contract.py`)

- Verifica que el consumidor `profiles` procese correctamente la estructura JSON esperada desde el endpoint `GET /api/v1/users/{id}` del servicio proveedor `users` (validando la presencia y formato de los campos `id` y `display_name`) mediante simulación de respuesta HTTP sin requerir conexión de red ni base de datos externa.

## Decisiones principales

- **Imágenes de prueba autocontenidas:** En lugar de depender de archivos binarios externos en el repositorio, las pruebas de subida de avatar decodifican en memoria un PNG válido de 1x1 píxel en Base64.
- **Entorno de integración dedicado:** Se separó `docker-compose.test.yml` del `docker-compose.yaml` principal para levantar únicamente los servicios base (`users`, `channels`, `messages`) junto a `profiles`, sin volúmenes persistentes y con política `restart: "no"`.
