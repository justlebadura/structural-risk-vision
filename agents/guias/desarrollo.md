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
| `APP_MODE` | `demo` | `demo` → reporte sintético; `prod` → inferencia real (sin mock). |
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

## Inferencia real desde la app

1. Verifica que el modelo local cargue y prediga:

```bash
python backend/scripts/verificar_inferencia.py
```

2. En el `.env` de la raíz:

```bash
APP_MODE=prod
EXPO_PUBLIC_API_URL=http://<IP-LAN-de-tu-equipo>:8000
```

3. Levanta el backend en todas las interfaces:

```bash
cd backend
uvicorn app:app --host 0.0.0.0 --port 8000
```

4. Reinicia Metro/Expo después de cambiar el `.env` y abre la app:

```bash
cd frontend
npm start
```

5. En el menú de la app pulsa **Probar conexión**. Debe mostrar
   `inferencia real` y `Modelo: cargado`. El reporte incluye un badge de modo y
   la inclinación del elemento.

> `filter.tflite` no se versiona. Si no existe, `/api/health` reporta
> `filter_model: pending` y `/api/analyze` responde `SIN_MODELO`.

## EDA (cuadernos)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r EDA/requirements.txt
```

El cuaderno 01 ya está versionado con salidas reales de METU (muestra 2,000 por
clase). Para reproducirlo desde la raíz:

```bash
EDA_DATA_DIR=EDA/data EDA_SAMPLE_PER_CLASS=2000 \
python -m nbconvert --to notebook --execute --inplace \
  EDA/notebooks/01_clasificacion_grietas.ipynb
```

Los cuadernos cargan el dataset real desde `EDA/data/` si existe; si no, entran
en **modo simulación** claramente etiquetado. Estructura esperada:

- `EDA/data/metu/{train,validation,test}/{Positive,Negative}/*.jpg`
- `EDA/data/sdnet2018/{C,D,M}/{train,test}/{crack,uncracked}/*.png`
- `EDA/data/crack500/{images,masks}/*`  o  `EDA/data/cfd/*`

El cuaderno 02 permanece en simulación porque no hay máscaras reales de
segmentación versionadas.

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
- EDA: re-ejecutar el cuaderno con `python -m nbconvert --execute`.
- Inferencia: `python backend/scripts/verificar_inferencia.py` y
  `python backend/scripts/prediccion_ejemplo.py`.