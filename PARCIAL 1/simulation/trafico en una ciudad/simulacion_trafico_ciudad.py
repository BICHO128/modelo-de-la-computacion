"""
╔══════════════════════════════════════════════════════════════════════════════╗
║         SIMULACIÓN DE TRÁFICO EN UNA INTERSECCIÓN URBANA                   ║
║         Modelo Basado en Agentes — Programación Orientada a Objetos        ║
╚══════════════════════════════════════════════════════════════════════════════╝

DESCRIPCIÓN DEL MODELO:
  - Una intersección de dos calles principales: una HORIZONTAL y una VERTICAL.
  - Cada calle tiene DOS sentidos de circulación (4 vías en total).
  - 4 semáforos, uno por cada flujo de entrada al cruce.
  - Los autos son agentes autónomos que:
      1. Obedecen el semáforo que tienen al frente.
      2. Evitan colisiones detectando si otro auto está justo adelante.
      3. Solo avanzan en línea recta (horizontales no cambian a vertical).

CLASES PRINCIPALES:
  - Semaforo  → Controla el estado de una vía de entrada.
  - Auto      → Agente vehículo con posición, dirección y lógica de decisión.
  - Ciudad    → Entorno que coordina semáforos y autos.
  - Visualizador → Renderiza la animación en tiempo real.

COMPATIBILIDAD: Google Colab + matplotlib
"""

# ─── IMPORTACIONES ────────────────────────────────────────────────────────────
import matplotlib.pyplot as plt                  # Motor gráfico principal
import matplotlib.animation as animacion_mod     # Módulo de animación cuadro a cuadro
import matplotlib.patches as parches             # Figuras geométricas (rectángulos, círculos)
from matplotlib.lines import Line2D              # Líneas para la leyenda personalizada
import numpy as np                               # Operaciones numéricas eficientes
import random                                    # Generación de valores aleatorios
from enum import Enum                            # Enumeraciones para estados fijos

# ─── SEMILLA ALEATORIA (reproducibilidad) ─────────────────────────────────────
# Fijar la semilla garantiza que cada ejecución produzca los mismos resultados;
# fundamental en ciencias de la computación para comparar experimentos.
random.seed(42)


# ══════════════════════════════════════════════════════════════════════════════
#  SECCIÓN 1 — CONSTANTES GLOBALES DE DISEÑO
#  Centralizar los parámetros facilita ajustar la simulación sin tocar el
#  código interno de las clases (principio Open/Closed de diseño de software).
# ══════════════════════════════════════════════════════════════════════════════

ANCHO_CUADRICULA  = 20   # Número de celdas en el eje horizontal (ancho del lienzo)
ALTO_CUADRICULA   = 20   # Número de celdas en el eje vertical (alto del lienzo)

# Posición del centro de la intersección en la cuadrícula
CENTRO_X = ANCHO_CUADRICULA // 2   # = 10 — mitad horizontal
CENTRO_Y = ALTO_CUADRICULA  // 2   # = 10 — mitad vertical

ANCHO_CALLE  = 3   # Celdas que ocupa cada calle (incluye ambos sentidos)
MITAD_CALLE  = ANCHO_CALLE // 2    # = 1 — desplazamiento de cada carril al centro

# Intervalos del ciclo de semáforo (en pasos de animación)
PASOS_VERDE    = 40   # Cuántos frames dura el estado VERDE a segundos es aproximadamente 4 segundos a 10 fps
PASOS_AMARILLO = 10   # Cuántos frames dura el estado AMARILLO a segundos es aproximadamente 1 segundo a 10 fps
PASOS_ROJO     = 50   # Cuántos frames dura el estado ROJO a segundos es aproximadamente 5 segundos a 10 fps

# Velocidad de los autos: celdas que avanzan por paso de animación
VELOCIDAD_AUTO = 0.4 # 0.4 celdas por paso es un buen equilibrio para que los autos se muevan visiblemente pero no demasiado rápido, permitiendo observar su comportamiento ante semáforos y otros autos.

# Distancia mínima entre autos para no colisionar (en celdas).
# Debe ser mayor que el lado largo del auto (1.0) + margen de separación visual.
# Con DISTANCIA_SEGURIDAD = 1.8 garantizamos al menos 0.8 celdas de espacio libre
# entre la trompa de un auto y la cola del auto de adelante.
DISTANCIA_SEGURIDAD = 1.8

# Distancia a la que el auto "ve" el semáforo y decide detenerse.
# Se amplía a 3.0 para que el auto frene con anticipación suficiente
# antes de llegar a la línea de detención, evitando colas por reacción tardía.
DISTANCIA_DETECCION_SEMAFORO = 3.0

# Tolerancia lateral: margen en el eje perpendicular para considerar que
# dos autos están en el mismo carril.  Debe ser menor que el ancho del carril
# (ANCHO_CALLE / 2 ≈ 0.75) para no confundir autos de carriles opuestos.
TOLERANCIA_LATERAL = 0.65

# ══════════════════════════════════════════════════════════════════════════════
#  SECCIÓN 2 — ENUMERACIONES (valores fijos con nombre legible)
# ══════════════════════════════════════════════════════════════════════════════

class EstadoSemaforo(Enum):
    """
    Enum que representa los tres estados posibles de un semáforo.
    Usar Enum en lugar de cadenas o enteros evita errores tipográficos
    y hace el código auto-documentado.
    """
    VERDE    = "VERDE"     # El auto puede avanzar libremente
    AMARILLO = "AMARILLO"  # El auto debe detenerse (transición)
    ROJO     = "ROJO"      # El auto está completamente detenido

class SentidoVia(Enum):
    """
    Enum que indica en qué eje y sentido circula un auto.
    Esto reemplaza comparaciones con strings propensas a error.
    """
    DERECHA   = "DERECHA"    # Circula horizontalmente de izquierda a derecha
    IZQUIERDA = "IZQUIERDA"  # Circula horizontalmente de derecha a izquierda
    ARRIBA    = "ARRIBA"     # Circula verticalmente de abajo hacia arriba
    ABAJO     = "ABAJO"      # Circula verticalmente de arriba hacia abajo


# ══════════════════════════════════════════════════════════════════════════════
#  SECCIÓN 3 — CLASE SEMÁFORO
# ══════════════════════════════════════════════════════════════════════════════

class Semaforo:
    """
    Representa un semáforo que controla UNA vía de entrada a la intersección.

    Cada semáforo:
      - Conoce su posición visual (para dibujarse en el lienzo).
      - Sigue un ciclo VERDE → AMARILLO → ROJO de forma autónoma.
      - Puede ser consultado por los autos para decidir si avanzan o se paran.

    El coordinador (Ciudad) se asegura de que solo una calle esté en verde
    a la vez, evitando que dos flujos perpendiculares circulen simultáneamente.
    """

    def __init__(self, pos_x: float, pos_y: float, sentidos_controlados: list,
                 fase_inicial: int = 0):
        """
        Constructor del semáforo.

        Parámetros:
          pos_x, pos_y       → Coordenadas visuales en la cuadrícula.
          sentidos_controlados → Lista de SentidoVia que este semáforo regula.
          fase_inicial       → Desplazamiento en pasos para sincronizar ciclos.
        """
        # Posición en el lienzo (usada solo para dibujarse)
        self.pos_x = pos_x
        self.pos_y = pos_y

        # Sentidos (flujos) que este semáforo controla
        self.sentidos_controlados = sentidos_controlados

        # Contador interno de pasos transcurridos dentro del ciclo actual
        # Iniciamos en fase_inicial para que los semáforos de la misma calle
        # estén sincronizados y los de la calle perpendicular estén desfasados.
        self.contador_ciclo = fase_inicial

        # Duración total de un ciclo completo (verde + amarillo + rojo)
        self.duracion_ciclo = PASOS_VERDE + PASOS_AMARILLO + PASOS_ROJO

        # Estado inicial calculado a partir del contador
        self.estado_actual = self._calcular_estado()

    # ── Métodos privados (lógica interna) ────────────────────────────────────

    def _calcular_estado(self) -> EstadoSemaforo:
        """
        Determina el estado del semáforo según la posición en el ciclo.

        El ciclo se divide en tres tramos consecutivos:
          [0, PASOS_VERDE)           → VERDE
          [PASOS_VERDE, +AMARILLO)   → AMARILLO
          resto hasta duracion_ciclo → ROJO
        """
        if self.contador_ciclo < PASOS_VERDE:
            return EstadoSemaforo.VERDE          # Primer tramo: luz verde
        elif self.contador_ciclo < PASOS_VERDE + PASOS_AMARILLO:
            return EstadoSemaforo.AMARILLO        # Segundo tramo: luz amarilla
        else:
            return EstadoSemaforo.ROJO            # Tercer tramo: luz roja

    # ── Métodos públicos ──────────────────────────────────────────────────────

    def actualizar(self):
        """
        Avanza el contador un paso y recalcula el estado.
        Debe llamarse una vez por frame de animación.
        El operador módulo (%) reinicia el contador al completar un ciclo completo.
        """
        self.contador_ciclo = (self.contador_ciclo + 1) % self.duracion_ciclo
        self.estado_actual = self._calcular_estado()   # Recalcula tras el avance

    def puede_pasar(self, sentido_auto: SentidoVia) -> bool:
        """
        Responde la pregunta: ¿puede este auto con este sentido avanzar ahora?

        Regla:
          - Solo el estado VERDE permite pasar.
          - AMARILLO y ROJO obligan a detenerse.
          - Si el sentido del auto no está en la lista de sentidos controlados,
            el semáforo no lo afecta (retorna True).

        Parámetro:
          sentido_auto → El SentidoVia del auto que consulta.
        """
        if sentido_auto not in self.sentidos_controlados:
            return True          # Este semáforo no controla ese flujo
        return self.estado_actual == EstadoSemaforo.VERDE   # Solo verde = paso libre

    @property
    def color_visual(self) -> str:
        """
        Retorna el color HEX del semáforo según su estado actual.
        Usado exclusivamente por el visualizador para pintar el punto.
        """
        mapa_colores = {
            EstadoSemaforo.VERDE:    "#00CC44",   # Verde saturado
            EstadoSemaforo.AMARILLO: "#FFD700",   # Amarillo dorado
            EstadoSemaforo.ROJO:     "#FF2222",   # Rojo brillante
        }
        return mapa_colores[self.estado_actual]


# ══════════════════════════════════════════════════════════════════════════════
#  SECCIÓN 4 — CLASE AUTO (AGENTE)
# ══════════════════════════════════════════════════════════════════════════════

class Auto:
    """
    Agente que representa un vehículo circulando por la intersección.

    Comportamiento autónomo de cada auto:
      1. AVANZAR en línea recta según su sentido (nunca gira).
      2. DETECTAR el semáforo al frente y obedecer su color.
      3. EVITAR COLISIONES manteniendo distancia con el auto de adelante.
      4. Desaparecer al salir de los límites de la cuadrícula.

    Analogía MBA: cada auto es como un empleado que sigue reglas claras
    (semáforo = política corporativa) y evita conflictos con sus compañeros
    (colisión = choque de recursos).
    """

    # Contador de clase para asignar IDs únicos y correlativas
    contador_global_autos = 0

    def __init__(self, pos_x: float, pos_y: float, sentido: SentidoVia):
        """
        Constructor del auto.

        Parámetros:
          pos_x, pos_y → Posición inicial en la cuadrícula.
          sentido      → Dirección de circulación (SentidoVia).
        """
        # Incrementamos el contador global y asignamos ID único
        Auto.contador_global_autos += 1
        self.id_auto = Auto.contador_global_autos   # Identificador único

        # Posición actual del auto (coordenadas flotantes para movimiento suave)
        self.pos_x = pos_x
        self.pos_y = pos_y

        # Sentido de circulación: define hacia dónde se mueve y en qué carril
        self.sentido = sentido

        # Velocidad de avance (celdas por paso de animación)
        self.auto_velocidad = VELOCIDAD_AUTO

        # Estado operativo: True = el auto está parado, False = está en movimiento
        self.esta_detenido = False

        # Color del auto según su eje de circulación (azul=horizontal, rojo=vertical)
        self.color_auto = self._asignar_color()

        # Bandera: True cuando el auto salió de la cuadrícula y debe eliminarse
        self.fuera_de_pantalla = False

    # ── Métodos privados ──────────────────────────────────────────────────────

    def _asignar_color(self) -> str:
        """
        Asigna color según el eje de circulación del auto.
        Azul para circulación horizontal, rojo para vertical.
        Esto facilita la lectura visual de la simulación.
        """
        if self.sentido in (SentidoVia.DERECHA, SentidoVia.IZQUIERDA):
            return "#1565C0"   # Azul oscuro → autos horizontales
        else:
            return "#C62828"   # Rojo oscuro → autos verticales

    def _calcular_delta(self):
        """
        Determina el desplazamiento (delta_x, delta_y) para este paso.
        Retorna la variación en X e Y según el sentido de circulación.

        Equivale a preguntar: "¿hacia dónde debo mover mis coordenadas?"
        """
        if self.sentido == SentidoVia.DERECHA:
            return (+self.auto_velocidad, 0)   # Avanza hacia la derecha
        elif self.sentido == SentidoVia.IZQUIERDA:
            return (-self.auto_velocidad, 0)   # Avanza hacia la izquierda
        elif self.sentido == SentidoVia.ARRIBA:
            return (0, +self.auto_velocidad)   # Avanza hacia arriba
        else:  # ABAJO
            return (0, -self.auto_velocidad)   # Avanza hacia abajo

    # ── Métodos públicos ──────────────────────────────────────────────────────

    def detectar_semaforo_al_frente(self, lista_semaforos: list) -> "Semaforo | None":
        """
        Busca el semáforo relevante que esté justo adelante del auto
        dentro del rango de detección definido.

        Lógica:
          1. Para cada semáforo, verificar si controla el sentido de este auto.
          2. Verificar si el semáforo está adelante (no atrás) en el eje correcto.
          3. Si está dentro de DISTANCIA_DETECCION_SEMAFORO, es el relevante.

        Retorna el semáforo relevante más cercano, o None si no hay ninguno.
        """
        semaforo_relevante = None          # Semáforo que encontremos adelante
        distancia_minima_encontrada = float('inf')   # Inicialmente infinita

        for sem in lista_semaforos:        # Recorre todos los semáforos de la ciudad
            # Verificar si este semáforo controla el sentido de nuestro auto
            if self.sentido not in sem.sentidos_controlados:
                continue                  # No es relevante para este auto, saltar

            # Calcular la distancia según el eje de circulación
            if self.sentido == SentidoVia.DERECHA:
                # Circulando a la derecha: el semáforo debe estar a la derecha (pos_x mayor)
                diferencia = sem.pos_x - self.pos_x
            elif self.sentido == SentidoVia.IZQUIERDA:
                # Circulando a la izquierda: el semáforo debe estar a la izquierda (pos_x menor)
                diferencia = self.pos_x - sem.pos_x
            elif self.sentido == SentidoVia.ARRIBA:
                # Circulando hacia arriba: el semáforo debe estar arriba (pos_y mayor)
                diferencia = sem.pos_y - self.pos_y
            else:  # ABAJO
                # Circulando hacia abajo: el semáforo debe estar abajo (pos_y menor)
                diferencia = self.pos_y - sem.pos_y

            # Solo considerar semáforos que estén ADELANTE (diferencia positiva)
            # y dentro del rango de detección definido por la constante
            if 0 < diferencia < DISTANCIA_DETECCION_SEMAFORO:
                if diferencia < distancia_minima_encontrada:
                    distancia_minima_encontrada = diferencia
                    semaforo_relevante = sem   # Este es el más cercano al frente

        return semaforo_relevante   # None si no hay semáforo adelante en rango

    def detectar_auto_al_frente(self, lista_autos: list) -> bool:
        """
        Verifica si hay otro auto justo adelante dentro de la distancia de seguridad.

        Evitar colisiones es un comportamiento emergente clave en simulaciones
        basadas en agentes: cada auto decide individualmente pero el resultado
        global es orden vial sin controlador central.

        Mejora de separación visual:
          - DISTANCIA_SEGURIDAD aumentada a 1.8 (> largo del auto 1.0 + margen 0.8)
          - TOLERANCIA_LATERAL ajustada a 0.65 para no confundir carriles opuestos
          - Se verifica tanto el centro del otro auto como su "cola" (centro - mitad largo)
            para detectar el solapamiento antes de que ocurra visualmente.

        Retorna True si hay un auto bloqueando, False si la vía está libre.
        """
        # Mitad del lado largo del auto (1.0 / 2 = 0.5) — tamaño del auto en su eje
        MITAD_LARGO_AUTO = 0.5

        for otro_auto in lista_autos:
            if otro_auto.id_auto == self.id_auto:
                continue              # No comparar el auto consigo mismo

            # Calcular diferencia de posición según el eje de circulación.
            # diferencia_eje: cuánto está adelante el otro auto en el eje de avance.
            # diferencia_lateral: separación en el eje perpendicular (¿mismo carril?).
            if self.sentido == SentidoVia.DERECHA:
                # Mi frente está en pos_x + MITAD_LARGO_AUTO
                # La cola del otro está en otro_auto.pos_x - MITAD_LARGO_AUTO
                diferencia_eje     = (otro_auto.pos_x - MITAD_LARGO_AUTO) - (self.pos_x + MITAD_LARGO_AUTO)
                diferencia_lateral = abs(otro_auto.pos_y - self.pos_y)
            elif self.sentido == SentidoVia.IZQUIERDA:
                diferencia_eje     = (self.pos_x - MITAD_LARGO_AUTO) - (otro_auto.pos_x + MITAD_LARGO_AUTO)
                diferencia_lateral = abs(otro_auto.pos_y - self.pos_y)
            elif self.sentido == SentidoVia.ARRIBA:
                diferencia_eje     = (otro_auto.pos_y - MITAD_LARGO_AUTO) - (self.pos_y + MITAD_LARGO_AUTO)
                diferencia_lateral = abs(otro_auto.pos_x - self.pos_x)
            else:  # ABAJO
                diferencia_eje     = (self.pos_y - MITAD_LARGO_AUTO) - (otro_auto.pos_y + MITAD_LARGO_AUTO)
                diferencia_lateral = abs(otro_auto.pos_x - self.pos_x)

            # Un auto bloquea si:
            #   1. Su cola está adelante del frente de este auto (diferencia_eje > -0.1)
            #      El pequeño margen -0.1 tolera imprecisiones de punto flotante.
            #   2. El espacio libre entre ambos es menor que DISTANCIA_SEGURIDAD.
            #   3. Están en el mismo carril (diferencia lateral pequeña).
            if (-0.1 < diferencia_eje < DISTANCIA_SEGURIDAD and
                    diferencia_lateral < TOLERANCIA_LATERAL):
                return True    # Hay un auto bloqueando el paso

        return False           # Vía libre adelante

    def actualizar(self, lista_semaforos: list, lista_autos: list):
        """
        Lógica de decisión y movimiento del auto para un paso de simulación.

        Jerarquía de decisiones (como en la conducción real):
          1. ¿Hay otro auto justo adelante? → Frenar (máxima prioridad).
          2. ¿El semáforo al frente está en AMARILLO o ROJO? → Frenar.
          3. Si nada lo detiene → Avanzar.

        Esta jerarquía garantiza seguridad vial en la simulación.
        """
        # ── Paso 1: Verificar colisión con auto al frente ─────────────────
        hay_auto_adelante = self.detectar_auto_al_frente(lista_autos)

        # ── Paso 2: Verificar estado del semáforo al frente ──────────────
        semaforo_frontal = self.detectar_semaforo_al_frente(lista_semaforos)
        semaforo_dice_parar = False                     # Asumimos vía libre
        if semaforo_frontal is not None:                # Si encontramos un semáforo
            # El semáforo dice parar si NO puede pasar (AMARILLO o ROJO)
            semaforo_dice_parar = not semaforo_frontal.puede_pasar(self.sentido)

        # ── Paso 3: Decidir si detenerse o avanzar ────────────────────────
        if hay_auto_adelante or semaforo_dice_parar:
            self.esta_detenido = True    # Registrar que está parado (para estadísticas)
            return                       # Salir sin mover el auto

        # ── Paso 4: Mover el auto si no hay obstrucción ───────────────────
        self.esta_detenido = False                   # El auto está en movimiento
        delta_x, delta_y = self._calcular_delta()    # Obtener desplazamiento
        self.pos_x += delta_x                        # Aplicar movimiento en X
        self.pos_y += delta_y                        # Aplicar movimiento en Y

        # ── Paso 5: Verificar si salió de los límites ─────────────────────
        fuera_x = self.pos_x < -2 or self.pos_x > ANCHO_CUADRICULA + 2
        fuera_y = self.pos_y < -2 or self.pos_y > ALTO_CUADRICULA + 2
        if fuera_x or fuera_y:
            self.fuera_de_pantalla = True   # Marcar para eliminación


# ══════════════════════════════════════════════════════════════════════════════
#  SECCIÓN 5 — CLASE CIUDAD (ENTORNO / COORDINADOR)
# ══════════════════════════════════════════════════════════════════════════════

class Ciudad:
    """
    Entorno que contiene y coordina todos los elementos de la simulación.

    Responsabilidades:
      1. Crear y mantener los 4 semáforos de la intersección.
      2. Generar autos periódicamente en los 4 puntos de entrada.
      3. Actualizar todos los agentes en cada paso de simulación.
      4. Proveer los datos necesarios al visualizador.

    Analogía MBA: la Ciudad es como una empresa; los autos son empleados
    autónomos que siguen políticas (semáforos) y el entorno les provee
    el contexto para operar.
    """

    def __init__(self):
        """
        Constructor: inicializa semáforos, lista de autos y contadores.
        """
        # Lista que contiene todos los objetos Auto activos en la simulación
        self.lista_autos = []

        # ── Crear los 4 semáforos de la intersección ──────────────────────
        #
        # La intersección está centrada en (CENTRO_X, CENTRO_Y) = (10, 10).
        # Hay 4 flujos de entrada:
        #   → DERECHA   : autos vienen desde la izquierda
        #   ← IZQUIERDA : autos vienen desde la derecha
        #   ↑ ARRIBA    : autos vienen desde abajo
        #   ↓ ABAJO     : autos vienen desde arriba
        #
        # FASE INICIAL de los semáforos:
        #   Los semáforos HORIZONTALES (→ y ←) arrancan en fase 0 (VERDE).
        #   Los semáforos VERTICALES (↑ y ↓) arrancan en fase ROJA para
        #   garantizar que nunca haya dos flujos perpendiculares en VERDE
        #   al mismo tiempo.
        #
        # Posición visual de cada semáforo: justo antes de la intersección.

        fase_inicial_rojo = PASOS_VERDE + PASOS_AMARILLO   # = 50 → arranca en ROJO

        self.lista_semaforos = [

            # Semáforo 1: controla autos que vienen de la IZQUIERDA (→ DERECHA)
            # Se ubica en el borde izquierdo de la zona de cruce
            Semaforo(
                pos_x = CENTRO_X - ANCHO_CALLE,          # Antes de la intersección
                pos_y = CENTRO_Y + MITAD_CALLE * 0.5,    # Carril inferior (→)
                sentidos_controlados = [SentidoVia.DERECHA],
                fase_inicial = 0                          # Inicia en VERDE
            ),

            # Semáforo 2: controla autos que vienen de la DERECHA (← IZQUIERDA)
            # Se ubica en el borde derecho de la zona de cruce
            Semaforo(
                pos_x = CENTRO_X + ANCHO_CALLE,          # Antes de la intersección
                pos_y = CENTRO_Y - MITAD_CALLE * 0.5,    # Carril superior (←)
                sentidos_controlados = [SentidoVia.IZQUIERDA],
                fase_inicial = 0                          # Inicia en VERDE (misma fase)
            ),

            # Semáforo 3: controla autos que vienen de ABAJO (↑ ARRIBA)
            # Se ubica en el borde inferior de la zona de cruce
            Semaforo(
                pos_x = CENTRO_X - MITAD_CALLE * 0.5,   # Carril derecho (↑)
                pos_y = CENTRO_Y - ANCHO_CALLE,          # Antes de la intersección
                sentidos_controlados = [SentidoVia.ARRIBA],
                fase_inicial = fase_inicial_rojo          # Inicia en ROJO
            ),

            # Semáforo 4: controla autos que vienen de ARRIBA (↓ ABAJO)
            # Se ubica en el borde superior de la zona de cruce
            Semaforo(
                pos_x = CENTRO_X + MITAD_CALLE * 0.5,   # Carril izquierdo (↓)
                pos_y = CENTRO_Y + ANCHO_CALLE,          # Antes de la intersección
                sentidos_controlados = [SentidoVia.ABAJO],
                fase_inicial = fase_inicial_rojo          # Inicia en ROJO
            ),
        ]

        # Contadores para controlar cada cuántos pasos se genera un nuevo auto.
        # Se aumenta a 22 pasos para dar más espacio entre autos consecutivos
        # y evitar que aparezcan pegados al inicio de la vía.
        self.pasos_desde_ultimo_auto_horizontal = 0   # Contador para autos en eje X
        self.pasos_desde_ultimo_auto_vertical   = 0   # Contador para autos en eje Y
        self.intervalo_generacion = 22                # Generar un auto cada 22 pasos

        # Contadores de estadísticas globales
        self.total_autos_creados    = 0   # Cuántos autos han existido en total
        self.total_autos_completados = 0  # Cuántos autos cruzaron completamente

        # Paso actual de simulación (equivale al frame de animación)
        self.paso_actual = 0

        # Historial de métricas para los gráficos de análisis
        self.historial_autos_activos   = []   # Autos en pantalla por paso
        self.historial_autos_detenidos = []   # Autos detenidos por paso

    # ── Métodos de generación de autos ────────────────────────────────────────

    def _zona_entrada_libre(self, pos_x: float, pos_y: float) -> bool:
        """
        Verifica que la zona de entrada esté lo suficientemente despejada
        antes de generar un nuevo auto.

        Regla: ningún auto existente debe estar a menos de (DISTANCIA_SEGURIDAD + 1.0)
        celdas del punto de entrada propuesto. El margen extra de 1.0 asegura
        que el nuevo auto no aparezca "pegado" al último en entrar.

        Retorna True si la entrada está libre y se puede generar el auto.
        """
        margen_entrada = DISTANCIA_SEGURIDAD + 1.0   # Zona de exclusión ampliada
        for auto_existente in self.lista_autos:
            distancia = ((auto_existente.pos_x - pos_x) ** 2 +
                         (auto_existente.pos_y - pos_y) ** 2) ** 0.5
            if distancia < margen_entrada:
                return False   # Hay un auto demasiado cerca: no generar
        return True            # Zona despejada: se puede generar

    def _generar_auto_horizontal(self):
        """
        Crea un auto en uno de los dos extremos horizontales (izquierda o derecha),
        pero SOLO si la zona de entrada está despejada.

        El carril de entrada horizontal está desplazado +0.5 celdas del centro
        para el sentido DERECHA, y -0.5 para el sentido IZQUIERDA.
        """
        sentido = random.choice([SentidoVia.DERECHA, SentidoVia.IZQUIERDA])

        if sentido == SentidoVia.DERECHA:
            # Entra por la izquierda, carril inferior del eje horizontal
            pos_x_inicial = 0.0                            # Extremo izquierdo
            pos_y_inicial = CENTRO_Y + MITAD_CALLE * 0.5  # Carril → (arriba del centro)
        else:
            # Entra por la derecha, carril superior del eje horizontal
            pos_x_inicial = float(ANCHO_CUADRICULA)        # Extremo derecho
            pos_y_inicial = CENTRO_Y - MITAD_CALLE * 0.5  # Carril ← (abajo del centro)

        # Solo crear el auto si la entrada está libre — evita solapamiento inicial
        if not self._zona_entrada_libre(pos_x_inicial, pos_y_inicial):
            return   # Entrada ocupada: no generar auto en este paso

        nuevo_auto = Auto(pos_x_inicial, pos_y_inicial, sentido)
        self.lista_autos.append(nuevo_auto)      # Agregar a la lista activa
        self.total_autos_creados += 1            # Incrementar contador histórico

    def _generar_auto_vertical(self):
        """
        Crea un auto en uno de los dos extremos verticales (arriba o abajo),
        pero SOLO si la zona de entrada está despejada.
        """
        sentido = random.choice([SentidoVia.ARRIBA, SentidoVia.ABAJO])

        if sentido == SentidoVia.ARRIBA:
            # Entra por abajo, carril derecho del eje vertical
            pos_x_inicial = CENTRO_X - MITAD_CALLE * 0.5   # Carril ↑ (lado derecho)
            pos_y_inicial = 0.0                             # Extremo inferior
        else:
            # Entra por arriba, carril izquierdo del eje vertical
            pos_x_inicial = CENTRO_X + MITAD_CALLE * 0.5   # Carril ↓ (lado izquierdo)
            pos_y_inicial = float(ALTO_CUADRICULA)          # Extremo superior

        # Solo crear el auto si la entrada está libre — evita solapamiento inicial
        if not self._zona_entrada_libre(pos_x_inicial, pos_y_inicial):
            return   # Entrada ocupada: no generar auto en este paso

        nuevo_auto = Auto(pos_x_inicial, pos_y_inicial, sentido)
        self.lista_autos.append(nuevo_auto)
        self.total_autos_creados += 1

    # ── Método principal de actualización ────────────────────────────────────

    def actualizar(self):
        """
        Avanza la simulación un paso de tiempo.

        Orden de ejecución (importante para consistencia):
          1. Actualizar todos los semáforos.
          2. Actualizar todos los autos (deciden y se mueven).
          3. Eliminar autos que salieron de la cuadrícula.
          4. Generar nuevos autos periódicamente.
          5. Registrar métricas del paso actual.
        """
        self.paso_actual += 1   # Incrementar el contador de tiempo

        # ── 1. Actualizar semáforos ───────────────────────────────────────
        for semaforo in self.lista_semaforos:
            semaforo.actualizar()   # Avanza el ciclo de cada semáforo

        # ── 2. Actualizar todos los autos ─────────────────────────────────
        for auto in self.lista_autos:
            # Cada auto recibe la lista completa de semáforos y autos
            # para poder tomar su propia decisión (comportamiento autónomo)
            auto.actualizar(self.lista_semaforos, self.lista_autos)

        # ── 3. Eliminar autos fuera de pantalla ───────────────────────────
        cantidad_antes = len(self.lista_autos)
        # Filtrar: conservar solo autos cuya bandera sea False
        self.lista_autos = [a for a in self.lista_autos if not a.fuera_de_pantalla]
        cantidad_despues = len(self.lista_autos)
        # Los que desaparecieron completaron su recorrido
        self.total_autos_completados += (cantidad_antes - cantidad_despues)

        # ── 4. Generar nuevos autos periódicamente ────────────────────────
        self.pasos_desde_ultimo_auto_horizontal += 1
        self.pasos_desde_ultimo_auto_vertical   += 1

        # Generar auto horizontal si pasó el intervalo
        if self.pasos_desde_ultimo_auto_horizontal >= self.intervalo_generacion:
            self._generar_auto_horizontal()
            self.pasos_desde_ultimo_auto_horizontal = 0   # Reiniciar contador

        # Generar auto vertical con un ligero desfase para más realismo
        if self.pasos_desde_ultimo_auto_vertical >= self.intervalo_generacion + 6:
            self._generar_auto_vertical()
            self.pasos_desde_ultimo_auto_vertical = 0   # Reiniciar contador

        # ── 5. Registrar métricas ─────────────────────────────────────────
        total_activos  = len(self.lista_autos)
        total_parados  = sum(1 for a in self.lista_autos if a.esta_detenido)
        self.historial_autos_activos.append(total_activos)
        self.historial_autos_detenidos.append(total_parados)


# ══════════════════════════════════════════════════════════════════════════════
#  SECCIÓN 6 — CLASE VISUALIZADOR
# ══════════════════════════════════════════════════════════════════════════════

class Visualizador:
    """
    Gestiona la representación gráfica de la simulación usando matplotlib.

    Componentes visuales:
      ┌────────────────────┬───────────────────┐
      │                    │  Gráfico Fluidez  │
      │  Vista Intersección│───────────────────│
      │                    │  Gráfico Densidad │
      └────────────────────┴───────────────────┘

    La columna izquierda muestra la intersección en tiempo real.
    La columna derecha muestra métricas históricas.
    """

    def __init__(self, ciudad: Ciudad, total_pasos: int = 300):
        """
        Constructor del visualizador.

        Parámetros:
          ciudad      → Objeto Ciudad con todos los elementos de la simulación.
          total_pasos → Número de frames que durará la animación.
        """
        self.ciudad = ciudad               # Referencia al entorno
        self.total_pasos = total_pasos     # Duración de la simulación en frames

        # ── Configurar la figura principal ────────────────────────────────
        # figsize=(16, 8) → 16 pulgadas de ancho, 8 de alto
        self.figura = plt.figure(figsize=(16, 8), facecolor='#1a1a2e')
        self.figura.suptitle(
            "Simulación de Tráfico en una Intersección — Modelo Basado en Agentes",
            fontsize=14, fontweight='bold', color='white', y=0.98
        )

        # ── Crear cuadrícula de subgráficos (GridSpec) ────────────────────
        # GridSpec permite control preciso del layout (2 filas, 2 columnas)
        disposicion = self.figura.add_gridspec(
            2, 2,
            width_ratios=[2, 1],   # Columna izquierda el doble de ancha
            hspace=0.35,           # Espacio vertical entre subgráficos
            wspace=0.3             # Espacio horizontal entre subgráficos
        )

        # Subgráfico izquierdo: ocupa AMBAS filas (vista de la intersección)
        self.eje_ciudad = self.figura.add_subplot(disposicion[:, 0])

        # Subgráfico superior derecho: fluidez del tráfico
        self.eje_fluidez = self.figura.add_subplot(disposicion[0, 1])

        # Subgráfico inferior derecho: densidad vehicular
        self.eje_densidad = self.figura.add_subplot(disposicion[1, 1])

        # Aplicar fondo oscuro a todos los ejes
        for eje in [self.eje_ciudad, self.eje_fluidez, self.eje_densidad]:
            eje.set_facecolor('#16213e')
            eje.tick_params(colors='#aaaaaa', labelsize=8)
            for spine in eje.spines.values():
                spine.set_edgecolor('#444466')

    # ── Métodos de dibujo de la infraestructura ───────────────────────────────

    def _dibujar_calles(self):
        """
        Dibuja la infraestructura estática de la intersección:
          - Bloque de asfalto de la calle horizontal
          - Bloque de asfalto de la calle vertical
          - Líneas de carril (blancas discontinuas)
          - Zona de cruce (intersección)
        """
        color_asfalto     = '#2d2d2d'   # Gris oscuro: asfalto
        color_linea_carril = '#EEEEEE'   # Blanco: marcas viales

        mitad = ANCHO_CALLE / 2   # = 1.5 → la mitad del ancho total de la calle

        # ── Calle HORIZONTAL (rectángulo horizontal que atraviesa toda la figura)
        rect_horizontal = parches.FancyBboxPatch(
            (0, CENTRO_Y - mitad),           # Esquina inferior-izquierda
            ANCHO_CUADRICULA,                # Ancho: toda la cuadrícula
            ANCHO_CALLE,                     # Alto: ancho de la calle
            boxstyle="square,pad=0",
            facecolor=color_asfalto,
            edgecolor='none',
            zorder=1                          # zorder bajo → debajo de autos y semáforos
        )
        self.eje_ciudad.add_patch(rect_horizontal)

        # ── Calle VERTICAL (rectángulo vertical que atraviesa toda la figura)
        rect_vertical = parches.FancyBboxPatch(
            (CENTRO_X - mitad, 0),           # Esquina inferior-izquierda
            ANCHO_CALLE,                     # Ancho: ancho de la calle
            ALTO_CUADRICULA,                 # Alto: toda la cuadrícula
            boxstyle="square,pad=0",
            facecolor=color_asfalto,
            edgecolor='none',
            zorder=1
        )
        self.eje_ciudad.add_patch(rect_vertical)

        # ── Línea central HORIZONTAL (divide los dos sentidos del eje horizontal)
        self.eje_ciudad.plot(
            [0, CENTRO_X - mitad],                     # Tramo izquierdo
            [CENTRO_Y, CENTRO_Y],
            color=color_linea_carril, linewidth=1,
            linestyle='--', dashes=(4, 4), alpha=0.5, zorder=2
        )
        self.eje_ciudad.plot(
            [CENTRO_X + mitad, ANCHO_CUADRICULA],      # Tramo derecho
            [CENTRO_Y, CENTRO_Y],
            color=color_linea_carril, linewidth=1,
            linestyle='--', dashes=(4, 4), alpha=0.5, zorder=2
        )

        # ── Línea central VERTICAL (divide los dos sentidos del eje vertical)
        self.eje_ciudad.plot(
            [CENTRO_X, CENTRO_X],
            [0, CENTRO_Y - mitad],                     # Tramo inferior
            color=color_linea_carril, linewidth=1,
            linestyle='--', dashes=(4, 4), alpha=0.5, zorder=2
        )
        self.eje_ciudad.plot(
            [CENTRO_X, CENTRO_X],
            [CENTRO_Y + mitad, ALTO_CUADRICULA],       # Tramo superior
            color=color_linea_carril, linewidth=1,
            linestyle='--', dashes=(4, 4), alpha=0.5, zorder=2
        )

        # ── Zona de CRUCE (cuadrado de intersección en color diferente)
        rect_cruce = parches.FancyBboxPatch(
            (CENTRO_X - mitad, CENTRO_Y - mitad),
            ANCHO_CALLE, ANCHO_CALLE,
            boxstyle="square,pad=0",
            facecolor='#3a3a3a',   # Ligeramente más claro para distinguir la zona
            edgecolor='#555566',
            linewidth=1.5,
            zorder=2
        )
        self.eje_ciudad.add_patch(rect_cruce)

        # ── Bordes blancos de las calles (efecto de borde de acera)
        for y_borde in [CENTRO_Y - mitad, CENTRO_Y + mitad]:
            self.eje_ciudad.axhline(
                y=y_borde, xmin=0, xmax=1,
                color='#888899', linewidth=0.8, alpha=0.6, zorder=2
            )
        for x_borde in [CENTRO_X - mitad, CENTRO_X + mitad]:
            self.eje_ciudad.axvline(
                x=x_borde, ymin=0, ymax=1,
                color='#888899', linewidth=0.8, alpha=0.6, zorder=2
            )

    def _dibujar_semaforos(self):
        """
        Dibuja los 4 semáforos como carcasas rectangulares negras
        con un círculo de color en su interior según el estado actual.

        Diseño visual:
          ┌─────┐
          │  ●  │  ← color según estado (verde / amarillo / rojo)
          └─────┘
        """
        for sem in self.ciudad.lista_semaforos:
            # Carcasa del semáforo (rectángulo negro)
            carcasa = parches.FancyBboxPatch(
                (sem.pos_x - 0.4, sem.pos_y - 0.4),   # Posición esquina inferior-izq
                0.8, 0.8,                               # Ancho y alto de la carcasa
                boxstyle="round,pad=0.05",
                facecolor='#111111',
                edgecolor='#888888',
                linewidth=1.2,
                zorder=6                  # Delante de calles pero detrás de autos
            )
            self.eje_ciudad.add_patch(carcasa)

            # Círculo interior con el color actual del semáforo
            luz = plt.Circle(
                (sem.pos_x, sem.pos_y),   # Centro coincide con la posición del sem.
                radius=0.28,              # Radio del punto luminoso
                color=sem.color_visual,   # Verde, amarillo o rojo según estado
                zorder=7,                 # Encima de la carcasa
                linewidth=0
            )
            self.eje_ciudad.add_patch(luz)

            # Halo de brillo alrededor del punto (efecto "luz encendida")
            halo = plt.Circle(
                (sem.pos_x, sem.pos_y),
                radius=0.42,
                color=sem.color_visual,
                alpha=0.15,               # Muy transparente → solo se percibe el brillo
                zorder=6
            )
            self.eje_ciudad.add_patch(halo)

    def _dibujar_autos(self):
        """
        Dibuja cada auto como un rectángulo orientado según su sentido.

        Autos horizontales (→ ←): rectángulo más ancho que alto
        Autos verticales (↑ ↓): rectángulo más alto que ancho

        Los autos detenidos tienen un borde blanco para destacarlos.
        """
        for auto in self.ciudad.lista_autos:
            # Determinar dimensiones según el eje de circulación
            if auto.sentido in (SentidoVia.DERECHA, SentidoVia.IZQUIERDA):
                ancho_rect = 1.0    # Autos horizontales: forma alargada horizontal
                alto_rect  = 0.55
            else:
                ancho_rect = 0.55   # Autos verticales: forma alargada vertical
                alto_rect  = 1.0

            # Calcular esquina inferior-izquierda (el parche se dibuja desde ahí)
            x_esquina = auto.pos_x - ancho_rect / 2
            y_esquina = auto.pos_y - alto_rect  / 2

            # Color de borde: blanco tenue si está detenido, sin borde si avanza
            color_borde = '#FFFFFF' if auto.esta_detenido else 'none'
            grosor_borde = 1.2 if auto.esta_detenido else 0

            rect_auto = parches.FancyBboxPatch(
                (x_esquina, y_esquina),
                ancho_rect, alto_rect,
                boxstyle="round,pad=0.1",   # Esquinas redondeadas → aspecto de auto
                facecolor=auto.color_auto,
                edgecolor=color_borde,
                linewidth=grosor_borde,
                alpha=0.88,                 # Ligera transparencia para mejor visual
                zorder=8                    # Encima de calles y semáforos
            )
            self.eje_ciudad.add_patch(rect_auto)

    def _dibujar_leyenda(self):
        """
        Agrega una leyenda personalizada con los elementos visuales clave.
        """
        elementos_leyenda = [
            Line2D([0], [0], marker='s', color='w', markerfacecolor='#1565C0',
                   markersize=10, label='Auto horizontal (→ ←)'),
            Line2D([0], [0], marker='s', color='w', markerfacecolor='#C62828',
                   markersize=10, label='Auto vertical (↑ ↓)'),
            Line2D([0], [0], marker='s', color='w', markerfacecolor='#1565C0',
                   markersize=10, markeredgecolor='white', markeredgewidth=1.5,
                   label='Auto detenido'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='#00CC44',
                   markersize=9, label='Semáforo VERDE'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='#FFD700',
                   markersize=9, label='Semáforo AMARILLO'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='#FF2222',
                   markersize=9, label='Semáforo ROJO'),
        ]
        self.eje_ciudad.legend(
            handles=elementos_leyenda,
            loc='upper right',
            fontsize=7.5,
            framealpha=0.25,
            facecolor='#1a1a2e',
            labelcolor='white',
            borderpad=0.6,
            handletextpad=0.5
        )

    def _configurar_eje_ciudad(self, paso_actual: int):
        """
        Aplica límites, etiquetas y título al eje principal de la intersección.
        """
        self.eje_ciudad.set_xlim(-0.5, ANCHO_CUADRICULA + 0.5)
        self.eje_ciudad.set_ylim(-0.5, ALTO_CUADRICULA + 0.5)
        self.eje_ciudad.set_aspect('equal')                  # Celdas cuadradas
        self.eje_ciudad.set_title(
            f"Vista de la Intersección — Paso {paso_actual}/{self.total_pasos}",
            fontsize=11, color='#ccccff', pad=8
        )
        self.eje_ciudad.set_xlabel("Eje X (Calle Horizontal)", color='#aaaacc', fontsize=9)
        self.eje_ciudad.set_ylabel("Eje Y (Calle Vertical)",   color='#aaaacc', fontsize=9)
        self.eje_ciudad.grid(False)   # Sin cuadrícula → mapa limpio

    def _dibujar_grafico_fluidez(self):
        """
        Gráfico superior derecho: porcentaje de autos en movimiento por paso.
        Mide la FLUIDEZ del tráfico (0% = todo detenido, 100% = todo fluye).
        """
        pasos = range(1, len(self.ciudad.historial_autos_activos) + 1)

        # Calcular porcentaje de autos en movimiento
        porcentaje_movimiento = []
        for activos, detenidos in zip(
            self.ciudad.historial_autos_activos,
            self.ciudad.historial_autos_detenidos
        ):
            if activos > 0:
                porcentaje = ((activos - detenidos) / activos) * 100
            else:
                porcentaje = 0.0
            porcentaje_movimiento.append(porcentaje)

        if porcentaje_movimiento:
            self.eje_fluidez.plot(
                pasos, porcentaje_movimiento,
                color='#4fc3f7', linewidth=1.5, label='Fluidez (%)'
            )
            # Línea de referencia al 50%: nivel "óptimo mínimo"
            self.eje_fluidez.axhline(
                50, color='#ffcc02', linestyle='--',
                linewidth=0.9, alpha=0.7, label='Umbral 50%'
            )
            # Área rellena bajo la curva para mejor lectura visual
            self.eje_fluidez.fill_between(
                pasos, porcentaje_movimiento, alpha=0.12, color='#4fc3f7'
            )

        self.eje_fluidez.set_title("Fluidez del Tráfico (%)", color='#ccccff', fontsize=9)
        self.eje_fluidez.set_ylabel("% En Movimiento", color='#aaaacc', fontsize=8)
        self.eje_fluidez.set_ylim(0, 105)
        self.eje_fluidez.set_xlim(0, self.total_pasos)
        self.eje_fluidez.legend(fontsize=7, labelcolor='white',
                                facecolor='#1a1a2e', framealpha=0.3)
        self.eje_fluidez.grid(True, alpha=0.2, color='#444466')
        self.eje_fluidez.tick_params(colors='#aaaaaa')

    def _dibujar_grafico_densidad(self):
        """
        Gráfico inferior derecho: número de autos activos y detenidos por paso.
        Mide la DENSIDAD y CONGESTIÓN vehicular en la intersección.
        """
        pasos = range(1, len(self.ciudad.historial_autos_activos) + 1)

        if self.ciudad.historial_autos_activos:
            self.eje_densidad.plot(
                pasos, self.ciudad.historial_autos_activos,
                color='#66BB6A', linewidth=1.5, label='Autos Activos'
            )
            self.eje_densidad.plot(
                pasos, self.ciudad.historial_autos_detenidos,
                color='#EF5350', linewidth=1.5, label='Autos Detenidos'
            )
            self.eje_densidad.fill_between(
                pasos, self.ciudad.historial_autos_detenidos,
                alpha=0.15, color='#EF5350'
            )

        # Caja de estadísticas actuales
        n_activos   = self.ciudad.historial_autos_activos[-1]   if self.ciudad.historial_autos_activos   else 0
        n_detenidos = self.ciudad.historial_autos_detenidos[-1] if self.ciudad.historial_autos_detenidos else 0
        texto_stats = (
            f"Activos:    {n_activos}\n"
            f"Detenidos:  {n_detenidos}\n"
            f"Completados:{self.ciudad.total_autos_completados}"
        )
        self.eje_densidad.text(
            0.02, 0.97, texto_stats,
            transform=self.eje_densidad.transAxes,
            fontsize=7.5, verticalalignment='top',
            color='white', family='monospace',
            bbox=dict(boxstyle='round,pad=0.4',
                      facecolor='#0d0d1a', alpha=0.7,
                      edgecolor='#444466')
        )

        self.eje_densidad.set_title("Densidad y Congestión Vehicular", color='#ccccff', fontsize=9)
        self.eje_densidad.set_xlabel("Paso de Tiempo", color='#aaaacc', fontsize=8)
        self.eje_densidad.set_ylabel("Número de Autos", color='#aaaacc', fontsize=8)
        self.eje_densidad.set_xlim(0, self.total_pasos)
        self.eje_densidad.legend(fontsize=7, labelcolor='white',
                                 facecolor='#1a1a2e', framealpha=0.3)
        self.eje_densidad.grid(True, alpha=0.2, color='#444466')
        self.eje_densidad.tick_params(colors='#aaaaaa')

    # ── Función de actualización de frame (llamada por FuncAnimation) ─────────

    def _actualizar_frame(self, numero_frame: int):
        """
        Función central de animación: se ejecuta UNA VEZ por cada frame.

        matplotlib.animation.FuncAnimation llama a esta función automáticamente
        en cada frame, pasando el número de frame como argumento.

        Flujo:
          1. Avanzar la simulación un paso.
          2. Limpiar todos los ejes.
          3. Redibujar toda la escena con el nuevo estado.
        """
        # ── 1. Avanzar la lógica de simulación ───────────────────────────
        self.ciudad.actualizar()

        # ── 2. Limpiar los ejes para redibujar ───────────────────────────
        self.eje_ciudad.cla()    # cla() = clear axis (borra contenido del eje)
        self.eje_fluidez.cla()
        self.eje_densidad.cla()

        # Reaplicar estilo de fondo (cla() lo elimina)
        for eje in [self.eje_ciudad, self.eje_fluidez, self.eje_densidad]:
            eje.set_facecolor('#16213e')
            for spine in eje.spines.values():
                spine.set_edgecolor('#444466')

        # ── 3. Dibujar todos los elementos en el nuevo estado ─────────────
        self._dibujar_calles()                            # Infraestructura estática
        self._dibujar_semaforos()                         # Luces actualizadas
        self._dibujar_autos()                             # Posiciones actualizadas
        self._dibujar_leyenda()                           # Leyenda visual
        self._configurar_eje_ciudad(self.ciudad.paso_actual)  # Títulos y ejes
        self._dibujar_grafico_fluidez()                   # Métricas históricas
        self._dibujar_grafico_densidad()

    # ── Método de inicio de animación ─────────────────────────────────────────

    def ejecutar(self):
        """
        Configura y lanza la animación usando matplotlib.animation.FuncAnimation.

        FuncAnimation:
          - fig         → Figura donde se dibuja.
          - func        → Función que se llama en cada frame.
          - frames      → Total de frames = total de pasos de simulación.
          - interval    → Milisegundos entre frames (200 ms → ~5 fps).
          - repeat      → False: la animación se detiene al terminar.
          - blit        → False: redibuja todo el frame (más compatible con Colab).

        Retorna el objeto de animación (necesario para que matplotlib no lo borre
        de memoria antes de que termine).
        """
        objeto_animacion = animacion_mod.FuncAnimation(
            fig      = self.figura,
            func     = self._actualizar_frame,
            frames   = self.total_pasos,
            interval = 120,         # 120 ms entre frames → ~8 fps
            repeat   = False,
            blit     = False
        )
        plt.tight_layout(rect=[0, 0, 1, 0.96])   # Deja espacio para el título superior
        plt.show()
        return objeto_animacion   # Guardar referencia evita que el GC lo elimine


# ══════════════════════════════════════════════════════════════════════════════
#  SECCIÓN 7 — FUNCIÓN PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

def ejecutar_simulacion(total_pasos: int = 300):
    """
    Punto de entrada de la simulación.

    Crea la Ciudad, el Visualizador y lanza la animación.
    Imprime un resumen de configuración antes de iniciar.

    Parámetro:
      total_pasos → Duración de la animación en frames.
    """
    print("=" * 65)
    print("   SIMULACIÓN DE TRÁFICO — INTERSECCIÓN URBANA")
    print("   Modelo Basado en Agentes | Python + matplotlib")
    print("=" * 65)
    print(f"\n  Configuración del entorno:")
    print(f"    Cuadrícula      : {ANCHO_CUADRICULA} x {ALTO_CUADRICULA} celdas")
    print(f"    Centro cruce    : ({CENTRO_X}, {CENTRO_Y})")
    print(f"    Ancho de calle  : {ANCHO_CALLE} celdas (2 carriles)")
    print(f"    Semáforos       : 4 (uno por vía de entrada)")
    print(f"\n  Ciclo de semáforos:")
    print(f"    Verde           : {PASOS_VERDE} pasos")
    print(f"    Amarillo        : {PASOS_AMARILLO} pasos")
    print(f"    Rojo            : {PASOS_ROJO} pasos")
    print(f"    Ciclo completo  : {PASOS_VERDE + PASOS_AMARILLO + PASOS_ROJO} pasos")
    print(f"\n  Parámetros de autos:")
    print(f"    Velocidad       : {VELOCIDAD_AUTO} celdas/paso")
    print(f"    Distancia segura: {DISTANCIA_SEGURIDAD} celdas")
    print(f"    Rango semáforo  : {DISTANCIA_DETECCION_SEMAFORO} celdas")
    print(f"\n  Duración total   : {total_pasos} pasos de animación")
    print("=" * 65)
    print("\n  Iniciando simulación...\n")

    # ── Crear los objetos principales ─────────────────────────────────────
    ciudad       = Ciudad()                             # Crear el entorno
    visualizador = Visualizador(ciudad, total_pasos)    # Crear el visualizador

    # Generar autos iniciales bien separados para que la simulación comience
    # con tráfico visible pero sin solapamientos.
    # Se usan posiciones fijas escalonadas: cada auto a >DISTANCIA_SEGURIDAD+1
    # celdas del siguiente para garantizar separación desde el primer frame.
    autos_iniciales_horizontales = [
        (2.0,  CENTRO_Y + MITAD_CALLE * 0.5, SentidoVia.DERECHA),   # Carril →
        (18.0, CENTRO_Y - MITAD_CALLE * 0.5, SentidoVia.IZQUIERDA), # Carril ←
    ]
    autos_iniciales_verticales = [
        (CENTRO_X - MITAD_CALLE * 0.5, 2.0,  SentidoVia.ARRIBA),    # Carril ↑
        (CENTRO_X + MITAD_CALLE * 0.5, 18.0, SentidoVia.ABAJO),     # Carril ↓
    ]
    for px, py, sentido in autos_iniciales_horizontales + autos_iniciales_verticales:
        auto_inicial = Auto(px, py, sentido)      # Crear auto en posición fija
        ciudad.lista_autos.append(auto_inicial)   # Insertar directamente
        ciudad.total_autos_creados += 1

    # ── Lanzar la animación ───────────────────────────────────────────────
    anim = visualizador.ejecutar()

    # ── Resumen final ─────────────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("   SIMULACIÓN COMPLETADA")
    print("=" * 65)
    print(f"    Autos generados   : {ciudad.total_autos_creados}")
    print(f"    Autos completados : {ciudad.total_autos_completados}")
    print(f"    Autos en pantalla : {len(ciudad.lista_autos)}")
    print("=" * 65)

    return ciudad, visualizador, anim


# ══════════════════════════════════════════════════════════════════════════════
#  SECCIÓN 8 — PUNTO DE ENTRADA
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    """
    Este bloque se ejecuta solo cuando el archivo se corre directamente.
    En Google Colab, basta con llamar ejecutar_simulacion() en una celda.
    """
    plt.rcParams['figure.dpi'] = 100          # Resolución de la figura
    plt.rcParams['animation.embed_limit'] = 50  # Límite MB para animación en Colab
    ciudad, visualizador, animacion = ejecutar_simulacion(total_pasos=300)
