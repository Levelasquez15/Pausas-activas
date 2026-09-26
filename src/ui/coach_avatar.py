"""
Módulo de Animación del Coach Virtual: Figura de Palito Articulada (Stickman Coach).
Animaciones biomecánicas ultra-claras, realistas y fluidas para cada ejercicio:
- Estiramiento de muñecas (antebrazo extendido + mano opuesta traccionando dedos).
- Apertura de pecho y retracción escapular (codos atrás, expansión torácica).
- Inclinación lateral de cuello (cabeza inclinada con hombros nivelados).
- Torsión de tronco (giro de hombros con cadera fija).
- Bombeo de pantorrillas (elevación rítmica en puntillas).
- Sentadillas (flexión de cadera y rodillas a 90° con brazos de contrapeso).
"""
import math
import numpy as np
import cv2

class CoachAvatar:
    """Renderizador vectorial del Coach Estilo Stickman Articulado con cinemática realista."""

    @classmethod
    def render_pose(cls, pose_name: str, tick: int, size: tuple = (190, 190)) -> np.ndarray:
        w, h = size
        canvas = np.zeros((h, w, 3), dtype=np.uint8)
        canvas[:] = (38, 23, 17) # Fondo Slate Refero (#111726 en BGR)

        # Marco sutil de 1px
        cv2.rectangle(canvas, (1, 1), (w - 2, h - 2), (56, 38, 28), 1)

        # Centro base del stickman
        cx = w // 2
        floor_y = h - 24
        cy = h // 2 + 3

        # Línea de piso minimalista
        cv2.line(canvas, (cx - 48, floor_y), (cx + 48, floor_y), (56, 38, 28), 1)

        # Colores del Stickman (Alta fidelidad estética)
        color_body = (248, 250, 252)   # Blanco puro nítido
        color_accent = (248, 189, 56)  # Azul celeste cielo (#38BDF8 en BGR)
        color_assist = (129, 185, 16)  # Verde esmeralda (#10B981 en BGR)
        color_joints = (246, 130, 59)  # Azul eléctrico (#3B82F6 en BGR)


        pose_upper = pose_name.upper()

        # Ciclos armónicos suaves
        t = tick * 0.12
        cycle_slow = math.sin(t * 0.8)
        cycle_med = math.sin(t * 1.5)

        # Parámetros por defecto (Postura erguida de pie)
        head_radius = 12
        torso_len = 34
        head_tilt_angle = 0.0
        elevate_y = 0

        hip_center = (cx, cy + 12)
        neck_center = (cx, cy - torso_len // 2)

        # Por defecto: piernas de pie
        l_knee = (cx - 10, cy + 32)
        r_knee = (cx + 10, cy + 32)
        l_foot = (cx - 14, floor_y)
        r_foot = (cx + 14, floor_y)

        # Por defecto: brazos relajados a los costados
        l_elbow = (cx - 18, cy - 4)
        r_elbow = (cx + 18, cy - 4)
        l_hand = (cx - 20, cy + 18)
        r_hand = (cx + 20, cy + 18)

        action_label = "COACH GUIA"

        # =========================================================================
        # 0. SALUDO DE INICIO TOUCHLESS (WAVE)
        # =========================================================================
        if "SALUDO" in pose_upper or "WAVE" in pose_upper or "HOLA" in pose_upper or "INICIO" in pose_upper:
            action_label = "SALUDA A LA CAMARA"
            wave_x = int(math.sin(t * 3.5) * 12)
            r_elbow = (cx + 22, cy - 16)
            r_hand = (cx + 24 + wave_x, cy - 42)
            # Dibujar líneas de saludo en la mano
            cv2.line(canvas, (r_hand[0] - 6, r_hand[1] - 8), (r_hand[0] - 10, r_hand[1] - 14), color_accent, 2)
            cv2.line(canvas, (r_hand[0] + 6, r_hand[1] - 8), (r_hand[0] + 10, r_hand[1] - 14), color_accent, 2)

        # =========================================================================
        # 0.1 GESTO DE FINALIZACION / DESACTIVACION (PULGAR ARRIBA)
        # =========================================================================
        elif "GESTO" in pose_upper or "PULGAR" in pose_upper or "THUMB" in pose_upper or "DESACTIVA" in pose_upper:
            action_label = "PULGAR ARRIBA PARA SALIR"
            r_elbow = (cx + 20, cy - 10)
            r_hand = (cx + 22, cy - 28)
            # Pulgar hacia arriba
            cv2.line(canvas, r_hand, (r_hand[0], r_hand[1] - 10), color_assist, 3)

        # =========================================================================
        # 1. ESTIRAMIENTO DE MUÑECAS (TÚNEL CARPIANO)
        # Brazo derecho estirado al frente, mano izquierda sujeta y tira dedos atrás
        # =========================================================================
        elif "MUNECA" in pose_upper or "CARPIANO" in pose_upper or "WRIST" in pose_upper:
            action_label = "ESTIRA MUNECA"

            # Brazo derecho totalmente extendido al frente
            r_elbow = (cx + 24, cy - 12)
            r_wrist = (cx + 48, cy - 12)
            # Palma extendida hacia arriba
            pull = int(cycle_slow * 4)
            r_hand = (r_wrist[0] + pull, r_wrist[1] - 14)

            # Brazo izquierdo cruza el pecho y sujeta los dedos derechos
            l_elbow = (cx - 2, cy)
            l_hand = (r_wrist[0] + pull + 3, r_wrist[1] - 8)

            # Dibujar flechitas de tracción suave sobre la muñeca
            cv2.arrowedLine(canvas, (r_hand[0] + 10, r_hand[1]), (r_hand[0] - 2, r_hand[1]), color_accent, 2, tipLength=0.4)

        # =========================================================================
        # 2. APERTURA DE PECHO Y RETRACCIÓN ESCAPULAR (ANTI-JOROBA)
        # Codos flexionados a 90° tirando hacia atrás, tórax expandido
        # =========================================================================
        elif "PECHO" in pose_upper or "ESCAPUL" in pose_upper or "CHEST" in pose_upper:
            action_label = "ABRE PECHO"
            expand = int((cycle_slow + 1.0) * 8)
            # Codos tirados hacia atrás a la altura de las costillas
            l_elbow = (cx - 28 - expand, cy - 4)
            r_elbow = (cx + 28 + expand, cy - 4)
            # Manos orientadas hacia arriba / afuera
            l_hand = (cx - 30 - expand, cy - 24)
            r_hand = (cx + 30 + expand, cy - 24)

            # Aura expansiva de pecho en el centro
            cv2.circle(canvas, (cx, cy - 6), 14 + expand, (34, 197, 94), 1)

        # =========================================================================
        # 3. INCLINACIÓN LATERAL DE CUELLO (LIBERACIÓN CERVICAL)
        # Cabeza inclinada a la izquierda o derecha suavemente, hombros quietos
        # =========================================================================
        elif "CUELLO" in pose_upper or "NECK" in pose_upper or "CERVICAL" in pose_upper:
            # Si especifica derecha o izquierda, o oscilación suave guiada
            if "DER" in pose_upper or "RIGHT" in pose_upper:
                action_label = "CUELLO A LA DER"
                head_tilt_angle = 24.0
            elif "IZQ" in pose_upper or "LEFT" in pose_upper:
                action_label = "CUELLO A LA IZQ"
                head_tilt_angle = -24.0
            else:
                action_label = "INCLINA CUELLO"
                head_tilt_angle = cycle_slow * 22.0

            # Hombros completamente relajados hacia abajo
            l_elbow = (cx - 16, cy + 2)
            r_elbow = (cx + 16, cy + 2)
            l_hand = (cx - 18, cy + 22)
            r_hand = (cx + 18, cy + 22)

            # Línea guía de hombros nivelados
            cv2.line(canvas, (cx - 30, cy - 14), (cx + 30, cy - 14), (100, 116, 139), 1)

        # =========================================================================
        # 4. TORSIÓN DE TRONCO (DESCARGA LUMBAR)
        # Hombros y brazos rotan a los lados mientras la cadera queda fija
        # =========================================================================
        elif "TORSION" in pose_upper or "TRONCO" in pose_upper or "TWIST" in pose_upper:
            action_label = "GIRA TRONCO"
            twist_x = int(cycle_slow * 20)
            neck_center = (cx + int(twist_x * 0.4), cy - torso_len // 2)

            # Hombros rotados en perspectiva
            l_elbow = (cx - 18 + twist_x, cy - 2)
            r_elbow = (cx + 18 + twist_x, cy - 2)
            l_hand = (cx - 26 + twist_x, cy + 12)
            r_hand = (cx + 26 + twist_x, cy + 12)

        # =========================================================================
        # 5. BOMBEO DE PANTORRILLAS (ACTIVACIÓN CIRCULATORIA)
        # Todo el cuerpo se eleva en puntillas rítmicamente despegando talones
        # =========================================================================
        elif "PANTORRILLA" in pose_upper or "CALF" in pose_upper or "PUNTILLAS" in pose_upper:
            action_label = "EN PUNTILLAS"
            # Elevación en puntillas
            lift = max(0, int((math.sin(t * 1.8) + 0.3) * 12))
            elevate_y = -lift

            hip_center = (cx, cy + 12 + elevate_y)
            neck_center = (cx, cy - torso_len // 2 + elevate_y)

            l_knee = (cx - 10, cy + 32 + elevate_y)
            r_knee = (cx + 10, cy + 32 + elevate_y)

            # Pies apoyados en la punta con talones alzados
            l_foot = (cx - 14, floor_y - int(lift * 0.4))
            r_foot = (cx + 14, floor_y - int(lift * 0.4))

            # Brazos oscilan rítmicamente
            l_elbow = (cx - 18, cy - 4 + elevate_y)
            r_elbow = (cx + 18, cy - 4 + elevate_y)
            l_hand = (cx - 20, cy + 16 + elevate_y)
            r_hand = (cx + 20, cy + 16 + elevate_y)

            # Flechas indicadoras de elevación bajo los talones
            if lift > 4:
                cv2.arrowedLine(canvas, (cx - 14, floor_y + 4), (cx - 14, floor_y - 8), color_accent, 2, tipLength=0.4)
                cv2.arrowedLine(canvas, (cx + 14, floor_y + 4), (cx + 14, floor_y - 8), color_accent, 2, tipLength=0.4)

        # =========================================================================
        # 5.1 ROTACIÓN Y CÍRCULOS DE HOMBROS (DESCARGA DE TRAPECIOS)
        # Hombros suben y giran en órbita suave hacia atrás
        # =========================================================================
        elif "HOMBRO" in pose_upper or "SHOULDER" in pose_upper:
            action_label = "CIRCULOS HOMBROS"
            sh_lift = int(math.sin(t * 2.2) * 7)
            sh_orbit = int(math.cos(t * 2.2) * 5)
            neck_center = (cx, cy - torso_len // 2 - max(0, sh_lift))

            l_elbow = (cx - 18 - sh_orbit, cy - 4 - sh_lift)
            r_elbow = (cx + 18 + sh_orbit, cy - 4 - sh_lift)
            l_hand = (cx - 18 - sh_orbit, cy + 18)
            r_hand = (cx + 18 + sh_orbit, cy + 18)

            # Flechitas orbitales en hombros
            cv2.ellipse(canvas, (cx - 18, cy - 14), (8, 6), 0, 0, 270, color_accent, 1, cv2.LINE_AA)
            cv2.ellipse(canvas, (cx + 18, cy - 14), (8, 6), 0, 0, 270, color_accent, 1, cv2.LINE_AA)

        # =========================================================================
        # 5.2 ESTIRAMIENTO DE TRÍCEPS Y DORSALES (BRAZO SOBRE LA CABEZA)
        # Codo flexionado sobre la cabeza con la otra mano traccionando suave
        # =========================================================================
        elif "TRICEP" in pose_upper or "CODO" in pose_upper:
            action_label = "ESTIRA TRICEPS"
            # Codo derecho alto sobre la cabeza
            r_elbow = (cx + 14, cy - 44)
            r_hand = (cx - 2, cy - 22) # Mano tras el cuello

            # Brazo izquierdo toma el codo derecho
            l_elbow = (cx - 16, cy - 20)
            l_hand = (cx + 14, cy - 44)

            # Flecha de tracción suave
            cv2.arrowedLine(canvas, (cx + 26, cy - 44), (cx + 14, cy - 44), color_accent, 2, tipLength=0.4)

        # =========================================================================
        # 5.3 EXTENSIÓN LUMBAR Y DESCOMPRESIÓN ESPINAL (MANOS A LA ESPALDA)
        # Manos en la cintura/espalda baja con suave arco hacia atrás
        # =========================================================================
        elif "LUMBAR" in pose_upper or "ESPALDA_BAJA" in pose_upper or "EXTENS" in pose_upper:
            action_label = "EXTI Gallón LUMBAR" if False else "EXTENSION LUMBAR"
            arch = int((cycle_slow + 1.0) * 4)
            neck_center = (cx - arch, cy - torso_len // 2)

            # Manos ancladas a la espalda baja / cintura
            l_hand = (cx - 10, cy + 8)
            r_hand = (cx + 10, cy + 8)
            # Codos empujando hacia atrás
            l_elbow = (cx - 24, cy + 2)
            r_elbow = (cx + 24, cy + 2)

            # Aura de alivio en la zona lumbar
            cv2.circle(canvas, (cx, cy + 10), 12 + arch, color_assist, 1)

        # =========================================================================
        # 6. BRAZOS AL CIELO / DESCOMPRESIÓN ESPALDA
        # =========================================================================
        elif "ARRIBA" in pose_upper or "BRAZOS" in pose_upper or "CIELO" in pose_upper:
            action_label = "BRAZOS AL CIELO"
            stretch_pulse = int(cycle_slow * 3)
            neck_center = (cx, cy - torso_len // 2 - 4)
            # Brazos totalmente estirados hacia arriba
            l_elbow = (cx - 14, cy - 28)
            r_elbow = (cx + 14, cy - 28)
            l_hand = (cx - 12, cy - 52 + stretch_pulse)
            r_hand = (cx + 12, cy - 52 + stretch_pulse)
            # Flechitas indicando elevación hacia arriba
            cv2.arrowedLine(canvas, (cx - 24, cy - 32), (cx - 24, cy - 50), color_accent, 2, tipLength=0.35)
            cv2.arrowedLine(canvas, (cx + 24, cy - 32), (cx + 24, cy - 50), color_accent, 2, tipLength=0.35)

        # =========================================================================
        # 7. CELEBRACIÓN / RUTINA COMPLETADA
        # =========================================================================
        elif "COMPLETED" in pose_upper or "CELEBRAT" in pose_upper or "EXITO" in pose_upper or "FIN" in pose_upper:
            action_label = "¡RUTINA COMPLETADA!"
            jump = int(abs(math.sin(t * 2.0)) * 14)
            elevate_y = -jump

            hip_center = (cx, cy + 12 + elevate_y)
            neck_center = (cx, cy - torso_len // 2 + elevate_y)

            # Brazos en "V" de victoria levantados con alegría
            l_elbow = (cx - 26, cy - 22 + elevate_y)
            r_elbow = (cx + 26, cy - 22 + elevate_y)
            l_hand = (cx - 38, cy - 42 + elevate_y)
            r_hand = (cx + 38, cy - 42 + elevate_y)

            # Piernas en salto
            l_knee = (cx - 14, cy + 30 + elevate_y)
            r_knee = (cx + 14, cy + 30 + elevate_y)
            l_foot = (cx - 18, floor_y - jump)
            r_foot = (cx + 18, floor_y - jump)

            # Chispas festivas orbitando
            for angle_deg in [20, 65, 110, 155, 200, 245, 290, 335]:
                rad_c = math.radians(angle_deg + tick * 5)
                sx = int(cx + math.cos(rad_c) * (50 + jump))
                sy = int((cy - 12) + math.sin(rad_c) * (42 + jump))
                cv2.circle(canvas, (sx, sy), 2, (250, 204, 21), -1)

        # =========================================================================
        # 8. SENTADILLAS (Acondicionamiento Físico)
        # Flexión de caderas y rodillas a 90° con brazos al frente
        # =========================================================================
        elif "SENTADILLA" in pose_upper or "SQUAT" in pose_upper:
            action_label = "SENTADILLA 90"
            depth = int((math.sin(t * 1.2) + 1.0) * 11) # 0 a 22 px de descenso
            elevate_y = depth

            hip_center = (cx - 8, cy + 12 + elevate_y)
            neck_center = (cx, cy - torso_len // 2 + elevate_y)

            # Rodillas flexionadas hacia adelante
            l_knee = (cx - 24, cy + 30 + int(elevate_y * 0.7))
            r_knee = (cx + 6, cy + 30 + int(elevate_y * 0.7))
            l_foot = (cx - 14, floor_y)
            r_foot = (cx + 16, floor_y)

            # Brazos estirados al frente para contrapeso
            l_elbow = (cx + 18, cy - 8 + elevate_y)
            r_elbow = (cx + 22, cy - 8 + elevate_y)
            l_hand = (cx + 38, cy - 10 + elevate_y)
            r_hand = (cx + 42, cy - 10 + elevate_y)

        # =========================================================================
        # 9. RESPIRACIÓN GUIADA (TRIANGULAR / 4-7-8)
        # =========================================================================
        elif "RESPIRA" in pose_upper or "ZEN" in pose_upper:
            action_label = "RESPIRA EN CALMA"
            breath_r = int((cycle_slow + 1.0) * 7)
            # Manos al centro del pecho
            l_elbow = (cx - 16, cy + 4)
            r_elbow = (cx + 16, cy + 4)
            l_hand = (cx - 4, cy - 2)
            r_hand = (cx + 4, cy - 2)
            # Pulso respiratorio relajante
            cv2.circle(canvas, (cx, cy - 6), 12 + breath_r, (6, 182, 212), 1)

        # ================= DIBUJAR EL STICKMAN ARTICULADO =================
        # 1. Piernas (Muslos y Pantorrillas)
        cv2.line(canvas, hip_center, l_knee, color_body, 3, cv2.LINE_AA)
        cv2.line(canvas, l_knee, l_foot, color_body, 3, cv2.LINE_AA)
        cv2.line(canvas, hip_center, r_knee, color_body, 3, cv2.LINE_AA)
        cv2.line(canvas, r_knee, r_foot, color_body, 3, cv2.LINE_AA)

        # Pies
        cv2.line(canvas, l_foot, (l_foot[0] - 6, l_foot[1]), color_body, 3, cv2.LINE_AA)
        cv2.line(canvas, r_foot, (r_foot[0] + 6, r_foot[1]), color_body, 3, cv2.LINE_AA)

        # Articulaciones de rodilla
        cv2.circle(canvas, l_knee, 3, color_joints, -1, cv2.LINE_AA)
        cv2.circle(canvas, r_knee, 3, color_joints, -1, cv2.LINE_AA)

        # 2. Torso (Columna vertebral)
        cv2.line(canvas, hip_center, neck_center, color_body, 4, cv2.LINE_AA)

        # 3. Cabeza esférica con inclinación cinemática
        rad = math.radians(head_tilt_angle)
        neck_len = 16
        head_cx = int(neck_center[0] + math.sin(rad) * neck_len)
        head_cy = int(neck_center[1] - math.cos(rad) * neck_len)

        # Cuello
        cv2.line(canvas, neck_center, (head_cx, head_cy), color_body, 3, cv2.LINE_AA)
        # Cabeza (círculo limpio con visor)
        cv2.circle(canvas, (head_cx, head_cy), head_radius, color_accent, 2, cv2.LINE_AA)
        cv2.circle(canvas, (head_cx, head_cy), head_radius - 2, (30, 41, 59), -1, cv2.LINE_AA)
        # Visor / Dirección de mirada
        eye_x = int(head_cx + math.cos(rad) * 4)
        eye_y = int(head_cy + math.sin(rad) * 2)
        cv2.circle(canvas, (eye_x, eye_y), 2, (255, 255, 255), -1, cv2.LINE_AA)

        # 4. Brazos articulados (Hombro -> Codo -> Mano)
        # Brazo izquierdo
        cv2.line(canvas, neck_center, l_elbow, color_body, 3, cv2.LINE_AA)
        cv2.line(canvas, l_elbow, l_hand, color_assist if "MUNECA" in pose_upper else color_body, 3, cv2.LINE_AA)
        cv2.circle(canvas, l_elbow, 3, color_joints, -1, cv2.LINE_AA)
        cv2.circle(canvas, l_hand, 4, color_assist if "MUNECA" in pose_upper else color_accent, -1, cv2.LINE_AA)

        # Brazo derecho
        cv2.line(canvas, neck_center, r_elbow, color_body, 3, cv2.LINE_AA)
        cv2.line(canvas, r_elbow, r_hand, color_body, 3, cv2.LINE_AA)
        cv2.circle(canvas, r_elbow, 3, color_joints, -1, cv2.LINE_AA)
        cv2.circle(canvas, r_hand, 4, color_accent, -1, cv2.LINE_AA)

        # 5. Etiqueta inferior de acción
        cv2.rectangle(canvas, (0, h - 22), (w, h), (38, 23, 17), -1)
        (tw, _), _ = cv2.getTextSize(action_label, cv2.FONT_HERSHEY_SIMPLEX, 0.36, 1)
        cv2.putText(canvas, action_label, ((w - tw) // 2, h - 7),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.36, color_accent, 1, cv2.LINE_AA)


        return canvas
