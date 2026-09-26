# 🧘‍♂️ Pausas Activas & Bienestar Laboral con IA 🏋️‍♀️

Sistema inteligente de escritorio para monitoreo de **pausas activas ergonómicas**, estimación de poses en tiempo real con visión artificial, gamificación interactiva con Coach Virtual y módulos de respiración anti-estrés para desarrolladores y trabajadores de oficina.

---

## ⚡ Guía Rápida de Descarga e Instalación

Diseñado para que cualquier persona pueda descargarlo en `.zip`, descomprimirlo y empezar a usarlo en **menos de 2 minutos**.

### 📥 Paso 1: Descargar el Proyecto
1. Ve al botón verde **`<> Code`** en la parte superior de este repositorio en GitHub.
2. Haz clic en **`Download ZIP`** (o [descarga directa aquí](https://github.com/Levelasquez15/Pausas-activas/archive/refs/heads/main.zip)).
3. Haz clic derecho sobre el archivo `.zip` descargado y selecciona **"Extraer todo..."** en una carpeta de tu preferencia.

---

### 💻 Paso 2: Instalación (En Windows con 1 solo Clic)

> **Requisito previo:** Tener instalado **Python 3.10 o superior** (descárgalo gratis en [python.org](https://www.python.org/downloads/)).  
> ⚠️ *Importante:* Al instalar Python, asegúrate de marcar la casilla **"Add python.exe to PATH"**.

#### 🖱️ Opción A: Con accesos directos (Recomendada)
1. Entra a la carpeta descomprimida.
2. Haz doble clic en **`instalar.bat`** (solo la primera vez). Esto instalará automáticamente todas las librerías necesarias.
3. Haz doble clic en **`ejecutar.bat`** para abrir la aplicación. ¡Listo!

#### ⌨️ Opción B: Por Consola / Terminal
Abre PowerShell o CMD dentro de la carpeta y ejecuta:
```bash
# 1. Instalar librerías
py -m pip install -r requirements.txt

# 2. Iniciar la aplicación
py run.py
```

---

## 🎯 Características Principales

### 1. 🕺 Modo TuxDance: Rutina Ergonómica con Coach Virtual
- **Avatar Biomecánico Articulado**: Un stickman dinámico que te muestra en tiempo real cómo realizar cada estiramiento.
- **Detección Bilateral Calibrada**: Para ejercicios de ambos lados (tríceps, torsión de tronco, cuello, muñecas), el sistema detecta cada lado de forma independiente y te guía con **flechas direccionales animadas** de izquierda a derecha.
- **Catálogo de 8 Pausas Ergonómicas**:
  1. *Estiramiento de Muñecas*: Prevención del síndrome del túnel carpiano.
  2. *Círculos de Hombros*: Descarga de trapecios y cuello.
  3. *Apertura de Pecho ('W')*: Corrección de joroba y hombros caídos.
  4. *Inclinación de Cuello*: Alivio de tensión cervical bilateral.
  5. *Estiramiento de Tríceps*: Descarga dorsal y escapular tras la cabeza.
  6. *Torsión de Tronco*: Movilidad de columna y descompresión lumbar.
  7. *Brazos al Cielo*: Elongación axial de columna vertebral.
  8. *Bombeo de Pantorrillas*: Reactivación venosa y circulación en piernas.

### 2. 🔒 Modo Bloqueo de Pantalla (Enfoque Ergonómico)
- Opción configurable para bloquear la pantalla o mantener la pausa activa al frente durante el descanso, evitando distracciones y asegurando que realmente te tomes el descanso.

### 3. 🏋️ Sentadillas con Diagnóstico Biomecánico
- Conteo inteligente de repeticiones analizando los ángulos articulares Cadera-Rodilla-Tobillo (160° a 90°).
- Diagnóstico físico en tiempo real con recomendaciones de fortalecimiento muscular.

### 4. 🧘 Módulos de Respiración y Relajación
- **Respiración Triangular**: Pacer visual rítmico (*Inhala 3.5s ➔ Mantén 3.5s ➔ Exhala 3.5s*).
- **Técnica 4-7-8**: Reducción de pulsaciones y estrés (*4s Inhala ➔ 7s Retén ➔ 8s Exhala*).
- **Evaluación Postural Zen**: Supervisión de hombros relajados y espalda alineada.

### 5. 📊 Editor de Pausas e Historial Local
- **Editor de Ejercicios**: Permite crear, modificar o personalizar la duración de los ejercicios desde la interfaz.
- **Base de Datos SQLite**: Registro histórico de pausas completadas, combo máximo y calorías estimadas (`pausas_activas.db`).

---

## 🏛️ Arquitectura y Patrones de Diseño

El sistema está construido siguiendo buenas prácticas de ingeniería de software:
- **Strategy Pattern (`src/patterns/strategy.py`)**: Intercambio dinámico de estrategias de ejercicio (`DanceGameStrategy`, `SquatStrategy`, `BreathingStrategy`, `StretchStrategy`) sin alterar el hilo de captura de video.
- **Observer Pattern (`src/patterns/observer.py`)**: Desacopla la lógica de visión de la interfaz gráfica y los sonidos mediante un `EventBus` de eventos reactivos (`REP_COMPLETED`, `BREATH_PHASE_CHANGE`, etc.).
- **State Pattern (`src/patterns/state.py`)**: Máquina de estados para gestionar el ciclo de trabajo y descanso (`WORKING`, `BREAK_ALERT`, `EXERCISING`, `SUMMARY`).
- **Factory Method (`src/vision/pose_detector.py`)**: Centraliza la instanciación y configuración de modelos de MediaPipe Pose.

---

## 🧪 Pruebas Unitarias

Para validar el catálogo, la cinemática de ángulos y la progresión bilateral:
```bash
py tests/test_ergonomics.py
py tests/test_pipeline.py
```

---

## 👥 Tecnologías Utilizadas
- **Lenguaje**: Python 3.10+
- **Visión Artificial**: Google MediaPipe Pose, OpenCV, NumPy
- **Interfaz Gráfica**: CustomTkinter, Pillow (PIL)
- **Audio y Efectos**: Pygame
- **Persistencia**: SQLite3
