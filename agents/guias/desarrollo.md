# Guía de Desarrollo

Cómo correr el proyecto, configurar el entorno y seguir las convenciones.

## Requisitos

- **Backend:** Python 3.10+ (`fastapi`, `uvicorn`, `numpy`, `opencv-python`,
  `pydantic`, `tflite-runtime`, `python-dotenv`).
- **Frontend:** Node.js + Expo (React Native).
- **EDA:** Python con `pandas`, `numpy`, `opencv-python`, `matplotlib`,
  `seaborn`, `scipy`, `scikit-image`.

## Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

- Docs de API: `http://localhost:8000/docs`
- Prueba rápida (demo): `GET /api/health` debe devolver `"mode": "demo"`.

## Frontend

```bash
cd frontend
npm install
npm start                     # o: npx expo start
```

Flujo de la app: **menú → ubicación → cámara → reporte**. Usa `expo-camera` y
`expo-sensors` (giróscopo + acelerómetro). Los sensores no están disponibles en
web; para probarlos usa un dispositivo físico con Expo Go.

## Configuración (`.env` único en la raíz)

Toda la configuración vive en un **único `.env` en la raíz del repositorio**.
Backend y frontend lo leen desde ahí (no hay `.env` en subcarpetas). Se crea una
copia local a partir de `.env.example`:

```bash
cp .env.example .env   # ajusta los valores a tu entorno
```

| Variable | Default | Descripción |
|----------|---------|-------------|
| `APP_MODE` | `demo` | `demo` → reporte sintético; `prod` → pipeline real (sin mock). |
| `API_HOST` | `0.0.0.0` | Interfaz de escucha del backend. |
| `API_PORT` | `8000` | Puerto del backend. |
| `LOG_LEVEL` | `info` | Nivel de logging. |
| `EXPO_PUBLIC_API_URL` | — | URL base de la API (la lee el frontend). |

- **Backend** lo lee en `core/config.py` (carga `REPO_ROOT/.env`).
- **Frontend** lo lee vía `frontend/metro.config.js` (inyecta
  `EXPO_PUBLIC_API_URL` al build de Metro).

> El `.env` **no se versiona**; se crea a partir de `.env.example`.
> El frontend consume únicamente `POST /api/analyze` (ver
> [`api_contrato.md`](../tecnico/api_contrato.md)).

## EDA (cuadernos)

```bash
cd EDA
# opcional: definir ruta de datos
export EDA_DATA_DIR=/ruta/a/data
jupyter notebook notebooks/
```

Los cuadernos cargan el dataset real desde `EDA/data/` si existe; si no, entran
en **modo simulación** claramente etiquetado. Estructura esperada:

- `EDA/data/metu/Positive|Negative/*.jpg`  o  `EDA/data/sdnet2018/{C,D,M}/{train,test}/{crack,uncracked}/*.png`
- `EDA/data/crack500/{images,masks}/*`  o  `EDA/data/cfd/*`

## Convenciones

- **Código y docs en español.**
- **API:** los contratos viven en `backend/core/schemas.py`; el frontend solo
  consume esos modelos. Cambiar un schema implica actualizar
  `frontend/src/types/inspection.ts` y la documentación en `agents/tecnico/api_contrato.md`.
- **Sin mocks silenciosos:** si falta un modelo, reporta `SIN_MODELO`, no inventes datos.
- **Modelos/datos:** los binarios `*.tflite` y datasets grandes van en
  `.gitignore`; no los versiones.
- **Antes de editar código,** consulta el índice graphify
  (ver [`graphify.md`](graphify.md)) para ubicar símbolos sin grepear a ciegas.

## Verificación rápida tras cambios

- Backend: levantar `uvicorn` y probar `/api/health` y `/api/analyze` (demo).
- Frontend: `npx tsc --noEmit` para chequeo de tipos.
- EDA: re-ejecutar los cuadernos con `jupyter nbconvert --execute`.