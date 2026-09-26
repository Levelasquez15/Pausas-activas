"""
Catálogo con instrucciones paso a paso, área anatómica y postura recomendada
para cada pausa activa ergonómica.
"""

EXERCISE_DETAILS = {
    "ESTIRAMIENTO_MUNECA": {
        "title": "Estiramiento de Muñecas",
        "target": "Prevención del Síndrome del Túnel Carpiano",
        "recommended_posture": "🪑 Sentado o 🧍 De pie",
        "steps": [
            "1. Extiende el brazo al frente a la altura del hombro.",
            "2. Con la otra mano, jala suavemente los dedos hacia atrás.",
            "3. Siente el alivio en la muñeca durante 10 segundos y luego alterna."
        ]
    },
    "APERTURA_PECHO": {
        "title": "Apertura de Pecho y Retracción",
        "target": "Corrección Postural Anti-Joroba de Oficina",
        "recommended_posture": "🪑 Sentado erguido o 🧍 De pie",
        "steps": [
            "1. Flexiona los codos a 90° a la altura del pecho.",
            "2. Lleva los codos hacia atrás juntando las escápulas.",
            "3. Abre el tórax, inhala profundo y mantén 6 segundos."
        ]
    },
    "INCLINACION_CUELLO": {
        "title": "Inclinación Lateral de Cuello",
        "target": "Descompresión Cervical y Alivio de Trapecios",
        "recommended_posture": "🪑 Sentado con espalda erguida",
        "steps": [
            "1. Ancla ambos hombros abajo, completamente relajados.",
            "2. Inclina suavemente la cabeza hacia el hombro.",
            "3. No eleves el hombro contrario; sostén 5 segundos."
        ]
    },
    "TORSION_TRONCO": {
        "title": "Torsión de Tronco y Columna",
        "target": "Descarga de Tensión Lumbar y Espalda Baja",
        "recommended_posture": "🪑 Sentado con pies firmes o 🧍 De pie",
        "steps": [
            "1. Mantén la cadera fija apuntando hacia el frente.",
            "2. Rota suavemente los hombros y el pecho hacia un lado.",
            "3. Siente la descompresión lumbar durante 6 segundos."
        ]
    },
    "BOMBEO_PANTORRILLAS": {
        "title": "Bombeo de Pantorrillas",
        "target": "Activación Venosa y Circulación en Piernas",
        "recommended_posture": "🧍 De pie",
        "steps": [
            "1. Ponte de pie erguido con los pies al ancho de hombros.",
            "2. Elévate sobre la punta de los pies despegando talones.",
            "3. Desciende con control. Realiza 10 repeticiones completas."
        ]
    },
    "CUELLO_IZQ": {
        "title": "Cuello a la Izquierda",
        "target": "Estiramiento del Trapecio Derecho",
        "recommended_posture": "🪑 Sentado o 🧍 De pie",
        "steps": [
            "1. Mantén los hombros nivelados y relajados abajo.",
            "2. Inclina la cabeza hacia el lado izquierdo de la pantalla.",
            "3. Sostén la posición hasta completar los 3.5 segundos."
        ]
    },
    "CUELLO_DER": {
        "title": "Cuello a la Derecha",
        "target": "Estiramiento del Trapecio Izquierdo",
        "recommended_posture": "🪑 Sentado o 🧍 De pie",
        "steps": [
            "1. Mantén los hombros nivelados y anclados.",
            "2. Inclina la cabeza hacia el lado derecho de la pantalla.",
            "3. Sostén la posición hasta completar los 3.5 segundos."
        ]
    },
    "BRAZOS_ARRIBA": {
        "title": "Brazos al Cielo",
        "target": "Alineación y Descompresión de Columna",
        "recommended_posture": "🪑 Sentado o 🧍 De pie",
        "steps": [
            "1. Extiende ambos brazos directamente hacia arriba.",
            "2. Estira la columna vertebral alargando el torso.",
            "3. Inhala profundo y mantén los brazos elevados."
        ]
    },
    "SENTADILLA": {
        "title": "Sentadillas con IA",
        "target": "Activación de Tren Inferior y Quema de Glucosa",
        "recommended_posture": "🧍 De pie frente a la cámara",
        "steps": [
            "1. Separa los pies al ancho de los hombros.",
            "2. Desciende flexionando rodillas a 90° con cadera atrás.",
            "3. Extiende brazos al frente como contrapeso (meta: 10 reps)."
        ]
    },
    "RESPIRA_TRIANGULO": {
        "title": "Respiración Triangular",
        "target": "Anti-Estrés Rápido y Control de Cortisol",
        "recommended_posture": "🪑 Sentado relajado",
        "steps": [
            "1. Sigue la esfera que recorre el triángulo en pantalla.",
            "2. Inhala por 3.5s ➔ Retén por 3.5s ➔ Exhala por 3.5s.",
            "3. Completa 3 ciclos profundos de calma."
        ]
    },
    "RESPIRA_478": {
        "title": "Técnica 4-7-8 (Calma Profunda)",
        "target": "Despejar la Mente y Restaurar el Sistema Nervioso",
        "recommended_posture": "🪑 Sentado con espalda apoyada",
        "steps": [
            "1. Inhala suave por la nariz durante 4 segundos.",
            "2. Retén el aire en los pulmones durante 7 segundos.",
            "3. Exhala completamente por la boca durante 8 segundos."
        ]
    },
    "SALUDO_INICIO": {
        "title": "Saludo de Inicio 👋",
        "target": "Activación Touchless sin tocar el ratón",
        "recommended_posture": "🪑 Sentado o 🧍 De pie",
        "steps": [
            "1. Levanta tu mano frente a la cámara web.",
            "2. Saluda suavemente de lado a lado.",
            "3. ¡La pausa ergonómica comenzará automáticamente!"
        ]
    },
    "HOMBROS_CIRCULOS": {
        "title": "Rotación de Hombros",
        "target": "Liberación de Tensión en Trapecios y Escápulas",
        "recommended_posture": "🪑 Sentado erguido o 🧍 De pie",
        "steps": [
            "1. Deja los brazos descansando suavemente a los costados.",
            "2. Eleva los hombros hacia las orejas y rótalos hacia atrás.",
            "3. Realiza círculos amplios y continuos respirando con calma."
        ]
    },
    "ESTIRAMIENTO_TRICEPS": {
        "title": "Estiramiento de Tríceps",
        "target": "Descompresión de Dorsales, Brazos y Hombros",
        "recommended_posture": "🪑 Sentado o 🧍 De pie",
        "steps": [
            "1. Eleva un brazo flexionando el codo detrás de la cabeza.",
            "2. Con la otra mano, toma el codo y empújalo suavemente hacia atrás.",
            "3. Siente el estiramiento en la parte posterior del brazo y dorsal."
        ]
    },
    "EXTENSION_LUMBAR": {
        "title": "Extensión Lumbar",
        "target": "Descompresión Espinal y Alivio de Espalda Baja",
        "recommended_posture": "🧍 De pie o 🪑 Sentado al borde",
        "steps": [
            "1. Apoya ambas manos en la espalda baja o cintura.",
            "2. Lleva los codos hacia atrás y arquea suavemente el torso.",
            "3. Inhala profundo abriendo el tórax y siente el alivio lumbar."
        ]
    },
    "FINALIZACION_GESTO": {
        "title": "Gesto de Desactivación 👍",
        "target": "Cierre de pausa y retorno al trabajo",
        "recommended_posture": "🪑 Sentado o 🧍 De pie",
        "steps": [
            "1. ¡Rutina completada con técnica excelente!",
            "2. Levanta el pulgar 👍 o ambas manos 🙌.",
            "3. La pausa se cerrará volviendo al modo trabajo."
        ]
    },
    "COMPLETED": {
        "title": "¡Rutina Completada!",
        "target": "Salud Laboral y Articulaciones Protegidas",
        "recommended_posture": "🎉 Descanso activo",
        "steps": [
            "1. ¡Excelente trabajo! Has protegido tus articulaciones.",
            "2. Haz el gesto de pulgar 👍 para reiniciar o volver.",
            "3. Presiona 'Reiniciar Rutina' para repetir la sesión."
        ]
    }
}


def get_exercise_detail(key: str) -> dict:
    key_upper = (key or "").upper()
    for k, data in EXERCISE_DETAILS.items():
        if k in key_upper or key_upper in k:
            return data
    # Fallback genérico
    return {
        "title": key.replace("_", " ").title(),
        "target": "Pausa Activa Ergonómica",
        "recommended_posture": "🪑 Sentado o 🧍 De pie",
        "steps": [
            "1. Mantén una postura alineada y natural.",
            "2. Sigue la guía del Coach virtual en pantalla.",
            "3. Respira con calma y mantén el movimiento."
        ]
    }
