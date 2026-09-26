# 🧘‍♂️ Pausas Activas & Bienestar Laboral con IA 🏋️‍♀️

Sistema inteligente de escritorio para monitoreo de pausas activas ergonómicas, estimación de poses en tiempo real con visión artificial y módulo de respiración consciente/anti-estrés.

---

## 🚀 Características Principales

1. **Estimación de Poses en Tiempo Real**:
   - Detección precisa de 33 articulaciones corporales mediante **Google MediaPipe Pose** optimizado en CPU (TFLite XNNPACK).
   - Renderizado del esqueleto anatómico y cálculo de ángulos biomecánicos con **NumPy** y **OpenCV**.

2. **Sentadillas Activas con Diagnóstico Físico**:
   - Conteo automático de repeticiones basado en máquina de estados y ángulos de flexión rodilla-cadera-tobillo (160° extensión -> 90° flexión profunda).
   - **Evaluación de mejora física**: Analiza tu volumen de repeticiones y te indica cómo estás fortaleciendo tu tren inferior, previniendo dolores lumbares y reactivando la circulación venosa.

3. **Módulo de Relajación y Respiración Anti-Estrés (Estilo TikTok)**:
   - **Respiración Triangular**: Pacer visual interactivo donde una esfera recorre un triángulo en tres fases rítmicas (*Inhala 3.5s ➔ Mantén 3.5s ➔ Exhala 3.5s*).
   - **Técnica 4-7-8**: Pacer circular que guía la desaceleración del sistema nervioso (*4s Inhala por la nariz ➔ 7s Retén ➔ 8s Exhala suave por la boca*).
   - **Respiración Consciente Postural**: MediaPipe evalúa si mantienes la espalda erguida y los hombros nivelados durante la meditación/respiración.

4. **Temporizador Ergonómico para el Puesto de Trabajo**:
   - Cuenta regresiva de tiempo sedentario (por defecto 45 minutos de trabajo continuo).
   - Alarma visual y auditiva cuando es momento de levantarse a realizar la pausa.

5. **Retroalimentación Sonora & Base de Datos**:
   - Chimes ascendentes armónicos al completar cada sentadilla válida.
   - Tonos zen (528 Hz) para marcar las fases de respiración.
   - Persistencia local en SQLite (`pausas_activas.db`) con histórico de repeticiones, calorías quemadas y nivel de condición física.

---

## 🏛️ Patrones de Diseño Implementados

- **Strategy Pattern (`src/patterns/strategy.py`)**: Desacopla la lógica de cada ejercicio o técnica de relajación (`SquatStrategy`, `BreathingStrategy`, `StretchStrategy`), permitiendo alternar entre ellas en caliente sin modificar el motor de visión.
- **Observer Pattern (`src/patterns/observer.py`)**: El `EventBus` notifica eventos clave (`REP_COMPLETED`, `BREATH_PHASE_CHANGE`, `BREAK_ALERT`) a los suscriptores (interfaz visual, sintetizador de audio y base de datos) sin acoplamientos rígidos.
- **State Pattern (`src/patterns/state.py`)**: Controla las transiciones del ciclo laboral (`WORKING` ➔ `BREAK_ALERT` ➔ `EXERCISING` ➔ `BREATHING` ➔ `SUMMARY`).
- **Factory Method (`src/vision/pose_detector.py`)**: `PoseDetectorFactory` encapsula la inicialización y configuración del modelo de MediaPipe PoseLandmarker.

---

## 📋 Aclaración Técnica de Librerías y Conceptos Solicitados

- **Google MediaPipe Pose**: Librería de Google para detección de 33 puntos anatómicos 3D a más de 30 FPS en CPUs estándar, ideal para computadoras de oficina.
- **"Harmer Pi"**:
  - *Raspberry Pi*: Micro-ordenador en el que este proyecto puede desplegarse en modo edge con pantalla táctil o monitor HDMI.
  - *HaMeR*: Modelo de investigación para reconstrucción de mallas de manos/cuerpo. MediaPipe Pose resulta mucho más rápido y liviano para tiempo real.
- **"Neutron de Nvidia"**:
  - *Nvidia Jetson (Nano / Orin)*: Placas de cómputo embebido de Nvidia con aceleración CUDA.
  - *Nvidia TensorRT*: Motor de inferencia de alto rendimiento de Nvidia para maximizar FPS y minimizar latencia de modelos de IA.
  - *Netron*: Visualizador para inspeccionar arquitecturas de redes neuronales (ONNX, TFLite).

---

## 💻 Instalación y Ejecución

### 1. Requisitos Previos
- Python 3.10 o superior (compatible con Python 3.14).
- Cámara web integrada o USB.

### 2. Instalación de Dependencias
```bash
py -m pip install -r requirements.txt
```

### 3. Ejecutar la Aplicación
```bash
py run.py
```

### 4. Ejecutar las Pruebas Unitarias
```bash
py tests/test_pipeline.py
```
