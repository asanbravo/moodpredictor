# MoodPredictor AI

Proyecto para predecir el estado de ánimo global de un usuario basado en las características musicales de una lista de sus canciones, utilizando gRPC y un modelo de Machine Learning (Random Forest).

## Visión del Producto

"MoodPredictor AI analiza características musicales de canciones, identifica el mood predominante de forma individual y agregada, y lo expone mediante una API gRPC simple, rápida y escalable, facilitando la integración desde cualquier aplicación cliente."

## Estructura del Proyecto

-   \`app/\`: Contiene el código fuente de la aplicación (lógica de dominio, aplicación, infraestructura).
    -   \`application/\`: Servicios de aplicación y casos de uso.
    -   \`domain/\`: Entidades, Value Objects, interfaces de repositorios.
    -   \`infrastructure/\`: Implementaciones concretas (servidor gRPC, modelo ML, repositorios).
-   \`proto/\`: Contiene los archivos de definición de Protocol Buffers (`.proto`).
-   \`tests/\`: Contiene las pruebas.
    -   \`unit/\`: Pruebas unitarias (usando `unittest`).
    -   \`acceptance/\`: Pruebas de aceptación (usando `behave`).
-   \`songs_dataset.csv\`: Dataset de ejemplo para entrenar el modelo.
-   \`mood_model.joblib\`: Modelo de Machine Learning entrenado.

## Stack Tecnológico

-   Python 3.8+
-   gRPC, Protobuf
-   Scikit-learn, Pandas, NumPy (para el modelo ML)
-   Behave (para pruebas de aceptación ATDD)
-   Unittest (para pruebas unitarias)
-   Black (para formateo de código)

## Cómo Empezar

### 1. Requisitos Previos

-   Python 3.8 o superior.
-   `pip` y `virtualenv` (recomendado).

### 2. Configuración del Entorno

```bash
# Clona el repositorio (si aplica)
# git clone <url_del_repositorio>
# cd mood-predictor-ai

# Crea y activa un entorno virtual (recomendado)
python -m venv venv
# En Windows:
# venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate

# Instala las dependencias de producción
pip install -r requirements.txt

# Instala las dependencias de desarrollo (para ejecutar pruebas, formatear, etc.)
pip install -r requirements-dev.txt
```

### 3. Generar Stubs gRPC (si modificas el .proto)

Si realizas cambios en `proto/mood_predictor.proto`, necesitarás regenerar los stubs de Python. Actualmente, los stubs se generan directamente en la carpeta `app/` para facilitar los imports `from app import ...`.

```bash
python -m grpc_tools.protoc \
    -I./proto \
    --python_out=./app \
    --pyi_out=./app \
    --grpc_python_out=./app \
    ./proto/mood_predictor.proto
```
Esto creará/actualizará `app/mood_predictor_pb2.py`, `app/mood_predictor_pb2.pyi`, `app/mood_predictor_pb2_grpc.py`, y `app/mood_predictor_pb2_grpc.pyi`.

### 4. Modelo de Machine Learning

El sistema está diseñado para cargar un modelo pre-entrenado (`mood_model.joblib`) al inicio. Si este archivo no existe, intentará entrenar uno nuevo usando `songs_dataset.csv`.
-   Ambos archivos se esperan en la raíz del proyecto.
-   Puedes generar un nuevo `songs_dataset.csv` o modificar el existente para entrenar el modelo con tus propios datos.

## Ejecución

### Iniciar el Servidor gRPC

```bash
python app/main.py
```
El servidor se iniciará en `localhost:50051`. Si el modelo `mood_model.joblib` no se encuentra, intentará entrenarlo usando `songs_dataset.csv`.

### Ejecutar Pruebas Unitarias

Asegúrate de haber instalado las dependencias de desarrollo (`requirements-dev.txt`).

```bash
python -m unittest discover -s app/tests/unit -p "test_*.py"
```
o para un archivo específico:
```bash
python -m unittest app.tests.unit.test_mood_prediction_service
```

### Ejecutar Pruebas de Aceptación (Behave)

Asegúrate de haber instalado las dependencias de desarrollo. **El servidor gRPC debe estar en ejecución en `localhost:50051` antes de ejecutar estas pruebas.**

```bash
# Configura PYTHONPATH para incluir el directorio raíz del proyecto si es necesario
export PYTHONPATH=.
# (o set PYTHONPATH=. en Windows cmd)

behave app/tests/acceptance/predict_mood.feature
```

## Ejemplo de Solicitud gRPC (Conceptual)

Para interactuar con el servidor, necesitarás un cliente gRPC.

**Solicitud:** `PredictUserMoodRequest`
Contiene una lista (repeated) de `SongFeatures`:
```protobuf
message SongFeatures {
  string song_id = 1; // Opcional
  double tempo = 2;
  double energy = 3;
  double valence = 4;
  double danceability = 5;
}

message PredictUserMoodRequest {
  repeated SongFeatures song_features = 1;
}
```
Ejemplo:
```json
// Representación conceptual de la solicitud
{
  "song_features": [
    { "song_id": "happy_song", "tempo": 120.0, "energy": 0.8, "valence": 0.9, "danceability": 0.75 },
    { "song_id": "sad_song", "tempo": 80.0, "energy": 0.3, "valence": 0.2, "danceability": 0.4 }
  ]
}
```

**Respuesta:** `PredictUserMoodResponse`
Contiene el `global_mood` predicho:
```protobuf
message PredictUserMoodResponse {
  string global_mood = 1; // Ej: "Happy", "Sad", "Energetic", "Relaxed"
}
```
Ejemplo de respuesta si la moda es "Happy":
```json
// Representación conceptual de la respuesta
{
  "global_mood": "Happy"
}
```
