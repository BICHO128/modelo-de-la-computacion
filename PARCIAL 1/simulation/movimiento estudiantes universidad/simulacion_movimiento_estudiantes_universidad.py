"""
SIMULACIÓN DEL MOVIMIENTO DE ESTUDIANTES EN LA UNIVERSIDAD
=========================================================
Este programa simula cómo los estudiantes se mueven entre diferentes espacios
del campus (aula, biblioteca, cafetería) según la disponibilidad de cada lugar.

Autor: Simulación basada en agentes
Propósito: Entender dinámicas de ocupación en espacios universitarios
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import random
from enum import Enum

# =============================================================================
# ENUMERACIÓN DE UBICACIONES
# =============================================================================

class UbicacionCampus(Enum):
    """
    Define los diferentes espacios disponibles en el campus.
    
    ¿Por qué usar Enum?
    - Evita errores de escritura (no podemos escribir "Aula" mal por accidente)
    - Hace el código más legible y profesional
    - Facilita agregar nuevos espacios en el futuro
    """
    AULA = "Aula"
    BIBLIOTECA = "Biblioteca"
    CAFETERIA = "Cafetería"


# =============================================================================
# CLASE AGENTE (ESTUDIANTE)
# =============================================================================

class Estudiante:
    """
    Representa a un estudiante individual que se mueve por el campus.
    
    Cada estudiante tiene:
    - Una ubicación actual
    - Una posición visual (x, y) para graficar
    - Capacidad de decidir a dónde moverse según disponibilidad
    """
    
    # Contador estático para asignar IDs únicos a cada estudiante
    # ¿Por qué? Para poder identificar y rastrear estudiantes individuales
    contador_id = 0
    
    def __init__(self, ubicacion_inicial, posicion_x, posicion_y):
        """
        Inicializa un nuevo estudiante.
        
        Parámetros:
        - ubicacion_inicial: Dónde comienza el estudiante (enum UbicacionCampus)
        - posicion_x: Coordenada X en el gráfico (0-100)
        - posicion_y: Coordenada Y en el gráfico (0-100)
        
        ¿Por qué guardar posiciones separadas de ubicación?
        - La ubicación (aula, biblioteca) es conceptual
        - La posición (x,y) es para visualizar en el gráfico
        """
        Estudiante.contador_id += 1
        self.id = Estudiante.contador_id
        self.ubicacion_actual = ubicacion_inicial
        self.posicion_x = posicion_x
        self.posicion_y = posicion_y
        # Tiempo que lleva en su ubicación actual (para simular permanencia)
        self.tiempo_en_ubicacion = 0
        # Tiempo mínimo antes de considerar moverse (entre 3 y 8 pasos)
        self.tiempo_minimo_permanencia = random.randint(3, 8)
    
    def decidir_siguiente_ubicacion(self, entorno):
        """
        El estudiante analiza qué espacio del campus le conviene más.
        
        Lógica de decisión:
        1. Si apenas llegó a un lugar, se queda un tiempo mínimo
        2. Si el lugar actual está muy lleno, busca alternativas
        3. Elige el espacio con más capacidad disponible
        
        ¿Por qué esta lógica?
        - Simula comportamiento realista (nadie se mueve cada segundo)
        - Considera la comodidad (evita lugares llenos)
        - Tiene algo de aleatoriedad (como decisiones humanas reales)
        """
        self.tiempo_en_ubicacion += 1
        
        # Si no ha cumplido el tiempo mínimo, se queda donde está
        if self.tiempo_en_ubicacion < self.tiempo_minimo_permanencia:
            return self.ubicacion_actual
        
        # Calcula qué tan lleno está el lugar actual (0 a 1)
        nivel_ocupacion_actual = entorno.obtener_nivel_ocupacion(self.ubicacion_actual)
        
        # Si el lugar está cómodo (menos del 70% lleno), tiene 70% probabilidad de quedarse
        if nivel_ocupacion_actual < 0.7 and random.random() < 0.7:
            return self.ubicacion_actual
        
        # Si llegó aquí, está considerando moverse
        # Busca el lugar con más espacio disponible
        mejor_ubicacion = None
        menor_ocupacion = 1.0  # Empieza con el peor caso (100% lleno)
        
        for ubicacion in UbicacionCampus:
            ocupacion = entorno.obtener_nivel_ocupacion(ubicacion)
            # Si este lugar está menos lleno que los anteriores
            if ocupacion < menor_ocupacion:
                menor_ocupacion = ocupacion
                mejor_ubicacion = ubicacion
        
        return mejor_ubicacion
    
    def moverse_a(self, nueva_ubicacion, entorno):
        """
        Mueve al estudiante a una nueva ubicación del campus.
        
        ¿Qué hace este método?
        1. Actualiza la ubicación conceptual del estudiante
        2. Calcula nueva posición visual en el gráfico
        3. Reinicia el contador de tiempo en ese lugar
        4. Define nuevo tiempo mínimo de permanencia
        
        ¿Por qué reiniciar contadores?
        - Para que el estudiante "se establezca" en el nuevo lugar
        - Evita que esté saltando constantemente entre ubicaciones
        """
        if nueva_ubicacion != self.ubicacion_actual:
            self.ubicacion_actual = nueva_ubicacion
            self.tiempo_en_ubicacion = 0
            self.tiempo_minimo_permanencia = random.randint(3, 8)
            
            # Obtiene las coordenadas visuales del nuevo espacio
            zona = entorno.obtener_zona_ubicacion(nueva_ubicacion)
            # Agrega algo de aleatoriedad para que no todos estén en el mismo pixel
            self.posicion_x = zona['x'] + random.uniform(-zona['ancho']/2, zona['ancho']/2)
            self.posicion_y = zona['y'] + random.uniform(-zona['alto']/2, zona['alto']/2)


# =============================================================================
# CLASE ENTORNO (CAMPUS UNIVERSITARIO)
# =============================================================================

class CampusUniversitario:
    """
    Representa el campus completo con todos sus espacios y estudiantes.
    
    Responsabilidades:
    - Mantiene registro de capacidades máximas de cada espacio
    - Cuenta cuántos estudiantes hay en cada lugar
    - Coordina el movimiento de todos los estudiantes
    - Proporciona datos para visualización
    """
    
    def __init__(self, num_estudiantes=50):
        """
        Crea el campus y coloca estudiantes inicialmente.
        
        ¿Por qué 50 estudiantes por defecto?
        - Es suficiente para ver patrones interesantes
        - No sobrecarga la visualización
        - Se puede ajustar fácilmente
        """
        # Capacidades máximas de cada espacio
        # ¿Por qué estos números? Simula un aula típica, biblioteca mediana y cafetería
        self.capacidades = {
            UbicacionCampus.AULA: 30,
            UbicacionCampus.BIBLIOTECA: 25,
            UbicacionCampus.CAFETERIA: 20
        }
        
        # Define las zonas visuales en el gráfico (coordenadas y tamaños)
        # Divide el espacio 100x100 en tres áreas claramente separadas
        self.zonas = {
            UbicacionCampus.AULA: {'x': 25, 'y': 75, 'ancho': 40, 'alto': 40},
            UbicacionCampus.BIBLIOTECA: {'x': 75, 'y': 75, 'ancho': 40, 'alto': 40},
            UbicacionCampus.CAFETERIA: {'x': 50, 'y': 25, 'ancho': 40, 'alto': 40}
        }
        
        # Colores para visualización (facilita identificar cada espacio)
        self.colores_zonas = {
            UbicacionCampus.AULA: '#FFE5E5',          # Rosa claro
            UbicacionCampus.BIBLIOTECA: '#E5F2FF',    # Azul claro
            UbicacionCampus.CAFETERIA: '#E5FFE5'      # Verde claro
        }
        
        # Lista que contendrá todos los objetos Estudiante
        self.estudiantes = []
        
        # Crea los estudiantes y los distribuye inicialmente
        self._crear_estudiantes(num_estudiantes)
        
        # Historial de ocupación para análisis posterior
        # ¿Por qué guardar historial? Para ver tendencias y patrones a lo largo del tiempo
        self.historial_ocupacion = {
            UbicacionCampus.AULA: [],
            UbicacionCampus.BIBLIOTECA: [],
            UbicacionCampus.CAFETERIA: []
        }
    
    def _crear_estudiantes(self, num_estudiantes):
        """
        Crea y distribuye estudiantes en el campus.
        
        Estrategia de distribución inicial:
        - 60% empiezan en el aula (la mayoría viene de clase)
        - 20% en biblioteca
        - 20% en cafetería
        
        ¿Por qué esta distribución?
        - Simula un escenario realista después de clases
        - Crea una situación interesante: el aula estará llena al inicio
        - Fuerza a algunos estudiantes a moverse, generando dinámica
        """
        ubicaciones_iniciales = (
            [UbicacionCampus.AULA] * int(num_estudiantes * 0.6) +
            [UbicacionCampus.BIBLIOTECA] * int(num_estudiantes * 0.2) +
            [UbicacionCampus.CAFETERIA] * int(num_estudiantes * 0.2)
        )
        
        # Asegura que tengamos exactamente el número pedido
        while len(ubicaciones_iniciales) < num_estudiantes:
            ubicaciones_iniciales.append(random.choice(list(UbicacionCampus)))
        
        # Mezcla aleatoriamente para que no todos los de "aula" se creen primero
        random.shuffle(ubicaciones_iniciales)
        
        # Crea cada estudiante
        for ubicacion in ubicaciones_iniciales:
            zona = self.zonas[ubicacion]
            # Posición aleatoria dentro de su zona inicial
            x = zona['x'] + random.uniform(-zona['ancho']/2, zona['ancho']/2)
            y = zona['y'] + random.uniform(-zona['alto']/2, zona['alto']/2)
            
            estudiante = Estudiante(ubicacion, x, y)
            self.estudiantes.append(estudiante)
    
    def contar_estudiantes_en(self, ubicacion):
        """
        Cuenta cuántos estudiantes hay actualmente en una ubicación.
        
        ¿Por qué un método separado?
        - Centraliza esta lógica en un solo lugar
        - Fácil de modificar si cambia la forma de contar
        - Hace el código más legible
        """
        return sum(1 for est in self.estudiantes if est.ubicacion_actual == ubicacion)
    
    def obtener_nivel_ocupacion(self, ubicacion):
        """
        Calcula qué tan lleno está un espacio (valor entre 0 y 1).
        
        Retorna:
        - 0.0 = completamente vacío
        - 0.5 = medio lleno
        - 1.0 = al máximo de capacidad
        
        ¿Por qué normalizar a 0-1?
        - Facilita comparaciones entre espacios de diferentes tamaños
        - Permite usar porcentajes fácilmente (multiplicar por 100)
        - Estándar en simulaciones y machine learning
        """
        cantidad_actual = self.contar_estudiantes_en(ubicacion)
        capacidad_maxima = self.capacidades[ubicacion]
        return cantidad_actual / capacidad_maxima
    
    def obtener_zona_ubicacion(self, ubicacion):
        """
        Retorna las coordenadas visuales de una ubicación.
        
        ¿Por qué? Para que los estudiantes sepan dónde dibujarse en el gráfico.
        """
        return self.zonas[ubicacion]
    
    def actualizar_simulacion(self):
        """
        Ejecuta un paso de tiempo en la simulación.
        
        En cada paso:
        1. Cada estudiante evalúa si quiere moverse
        2. Se ejecutan los movimientos
        3. Se registra el estado actual para el historial
        
        ¿Por qué este orden?
        - Primero todos DECIDEN (para que las decisiones sean justas)
        - Luego todos se MUEVEN (evita que los primeros influyan en los últimos)
        - Finalmente se REGISTRA el resultado
        """
        # Fase 1: Todos los estudiantes deciden su próximo movimiento
        decisiones = []
        for estudiante in self.estudiantes:
            siguiente_ubicacion = estudiante.decidir_siguiente_ubicacion(self)
            decisiones.append((estudiante, siguiente_ubicacion))
        
        # Fase 2: Se ejecutan todos los movimientos
        for estudiante, nueva_ubicacion in decisiones:
            estudiante.moverse_a(nueva_ubicacion, self)
        
        # Fase 3: Registra el estado actual en el historial
        for ubicacion in UbicacionCampus:
            cantidad = self.contar_estudiantes_en(ubicacion)
            self.historial_ocupacion[ubicacion].append(cantidad)
    
    def obtener_estadisticas(self):
        """
        Genera un reporte de ocupación actual.
        
        Útil para:
        - Mostrar en pantalla durante la simulación
        - Debugging
        - Análisis post-simulación
        """
        estadisticas = {}
        for ubicacion in UbicacionCampus:
            cantidad = self.contar_estudiantes_en(ubicacion)
            capacidad = self.capacidades[ubicacion]
            porcentaje = (cantidad / capacidad) * 100
            estadisticas[ubicacion.value] = {
                'cantidad': cantidad,
                'capacidad': capacidad,
                'porcentaje': porcentaje
            }
        return estadisticas


# =============================================================================
# VISUALIZACIÓN Y ANIMACIÓN
# =============================================================================

class VisualizadorSimulacion:
    """
    Maneja toda la parte gráfica de la simulación.
    
    Responsabilidades:
    - Crear la ventana y los gráficos
    - Dibujar el campus y los estudiantes
    - Animar el movimiento
    - Mostrar estadísticas en tiempo real
    """
    
    def __init__(self, campus, pasos_simulacion=100):
        """
        Prepara la visualización.
        
        Parámetros:
        - campus: El objeto CampusUniversitario a visualizar
        - pasos_simulacion: Cuántos pasos de tiempo simular
        """
        self.campus = campus
        self.pasos_simulacion = pasos_simulacion
        self.paso_actual = 0
        
        # Configura la figura con dos subgráficos lado a lado
        # ¿Por qué dos gráficos?
        # - Izquierda: Vista espacial del campus (dónde están los estudiantes)
        # - Derecha: Gráfico de ocupación en el tiempo (análisis cuantitativo)
        self.fig, (self.ax_campus, self.ax_estadisticas) = plt.subplots(1, 2, figsize=(16, 7))
        self.fig.suptitle('Simulación de Movimiento de Estudiantes en el Campus', 
                          fontsize=16, fontweight='bold')
    
    def _dibujar_zonas_campus(self):
        """
        Dibuja los rectángulos de fondo que representan cada espacio.
        
        ¿Por qué?
        - Ayuda a identificar visualmente cada área
        - Proporciona contexto espacial
        - Hace la simulación más intuitiva
        """
        for ubicacion, zona in self.campus.zonas.items():
            rectangulo = plt.Rectangle(
                (zona['x'] - zona['ancho']/2, zona['y'] - zona['alto']/2),
                zona['ancho'],
                zona['alto'],
                facecolor=self.campus.colores_zonas[ubicacion],
                edgecolor='black',
                linewidth=2,
                alpha=0.3  # Transparencia para que se vean los estudiantes encima
            )
            self.ax_campus.add_patch(rectangulo)
            
            # Añade etiqueta con el nombre del espacio
            self.ax_campus.text(
                zona['x'], zona['y'],
                ubicacion.value,
                ha='center', va='center',
                fontsize=12, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8)
            )
    
    def _actualizar_animacion(self, frame):
        """
        Función llamada en cada frame de la animación.
        
        ¿Qué hace?
        1. Ejecuta un paso de simulación (estudiantes se mueven)
        2. Actualiza el gráfico del campus
        3. Actualiza el gráfico de estadísticas
        
        Parámetro 'frame':
        - Proporcionado automáticamente por matplotlib.animation
        - Indica qué frame estamos dibujando (0, 1, 2, ...)
        """
        # Ejecuta la lógica de simulación
        self.campus.actualizar_simulacion()
        self.paso_actual += 1
        
        # Limpia los gráficos anteriores
        self.ax_campus.clear()
        self.ax_estadisticas.clear()
        
        # Redibuja el campus
        self._dibujar_zonas_campus()
        
        # Dibuja cada estudiante como un punto
        for estudiante in self.campus.estudiantes:
            # Color según ubicación actual
            if estudiante.ubicacion_actual == UbicacionCampus.AULA:
                color = 'red'
            elif estudiante.ubicacion_actual == UbicacionCampus.BIBLIOTECA:
                color = 'blue'
            else:
                color = 'green'
            
            self.ax_campus.scatter(
                estudiante.posicion_x,
                estudiante.posicion_y,
                c=color,
                s=50,  # Tamaño del punto
                alpha=0.6,
                edgecolors='black',
                linewidth=0.5
            )
        
        # Configura el gráfico del campus
        self.ax_campus.set_xlim(0, 100)
        self.ax_campus.set_ylim(0, 100)
        self.ax_campus.set_aspect('equal')
        self.ax_campus.set_title(f'Vista del Campus - Paso {self.paso_actual}/{self.pasos_simulacion}',
                                  fontsize=14, fontweight='bold')
        self.ax_campus.set_xlabel('Coordenada X')
        self.ax_campus.set_ylabel('Coordenada Y')
        self.ax_campus.grid(True, alpha=0.3)
        
        # Dibuja el gráfico de ocupación en el tiempo
        if self.paso_actual > 1:  # Necesita al menos 2 puntos para graficar
            pasos = range(1, self.paso_actual + 1)
            
            for ubicacion in UbicacionCampus:
                datos = self.campus.historial_ocupacion[ubicacion][:self.paso_actual]
                
                if ubicacion == UbicacionCampus.AULA:
                    color = 'red'
                elif ubicacion == UbicacionCampus.BIBLIOTECA:
                    color = 'blue'
                else:
                    color = 'green'
                
                self.ax_estadisticas.plot(
                    pasos,
                    datos,
                    label=ubicacion.value,
                    color=color,
                    linewidth=2,
                    marker='o',
                    markersize=3
                )
                
                # Dibuja línea de capacidad máxima
                capacidad = self.campus.capacidades[ubicacion]
                self.ax_estadisticas.axhline(
                    y=capacidad,
                    color=color,
                    linestyle='--',
                    alpha=0.5,
                    linewidth=1
                )
        
        # Configura el gráfico de estadísticas
        self.ax_estadisticas.set_title('Ocupación de Espacios en el Tiempo',
                                       fontsize=14, fontweight='bold')
        self.ax_estadisticas.set_xlabel('Paso de Tiempo')
        self.ax_estadisticas.set_ylabel('Número de Estudiantes')
        self.ax_estadisticas.legend(loc='upper right')
        self.ax_estadisticas.grid(True, alpha=0.3)
        self.ax_estadisticas.set_xlim(0, self.pasos_simulacion)
        
        # Calcula el máximo para el eje Y (un poco más que la capacidad mayor)
        max_capacidad = max(self.campus.capacidades.values())
        self.ax_estadisticas.set_ylim(0, max_capacidad * 1.2)
        
        # Añade texto con estadísticas actuales
        stats = self.campus.obtener_estadisticas()
        texto_stats = "Ocupación Actual:\n"
        for ubicacion, datos in stats.items():
            texto_stats += f"{ubicacion}: {datos['cantidad']}/{datos['capacidad']} ({datos['porcentaje']:.1f}%)\n"
        
        self.ax_estadisticas.text(
            0.02, 0.98,
            texto_stats,
            transform=self.ax_estadisticas.transAxes,
            fontsize=10,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        )
    
    def ejecutar(self):
        """
        Inicia la animación de la simulación.
        
        ¿Cómo funciona?
        - matplotlib.animation.FuncAnimation llama a _actualizar_animacion repetidamente
        - interval=500 significa 500ms entre frames (2 frames por segundo)
        - repeat=False hace que la animación se detenga al terminar
        """
        anim = animation.FuncAnimation(
            self.fig,
            self._actualizar_animacion,
            frames=self.pasos_simulacion,
            interval=500,  # Milisegundos entre frames
            repeat=False,
            blit=False
        )
        
        plt.tight_layout()
        plt.show()
        
        return anim


# =============================================================================
# FUNCIÓN PRINCIPAL
# =============================================================================

def ejecutar_simulacion(num_estudiantes=50, pasos=100):
    """
    Función principal que orquesta toda la simulación.
    
    Parámetros personalizables:
    - num_estudiantes: Cuántos estudiantes simular (default: 50)
    - pasos: Cuántos pasos de tiempo ejecutar (default: 100)
    
    ¿Cómo usarlo en Colab?
    Simplemente ejecuta: ejecutar_simulacion()
    
    O personaliza: ejecutar_simulacion(num_estudiantes=80, pasos=150)
    """
    print("="*70)
    print("INICIANDO SIMULACIÓN DE MOVIMIENTO DE ESTUDIANTES")
    print("="*70)
    print(f"\nParámetros de simulación:")
    print(f"  - Número de estudiantes: {num_estudiantes}")
    print(f"  - Pasos de simulación: {pasos}")
    print(f"\nCreando campus universitario...")
    
    # Crea el entorno (campus) con los estudiantes
    campus = CampusUniversitario(num_estudiantes=num_estudiantes)
    
    print(f"Campus creado exitosamente!")
    print(f"\nCapacidades de cada espacio:")
    for ubicacion, capacidad in campus.capacidades.items():
        print(f"  - {ubicacion.value}: {capacidad} estudiantes")
    
    print(f"\nDistribución inicial:")
    stats_iniciales = campus.obtener_estadisticas()
    for ubicacion, datos in stats_iniciales.items():
        print(f"  - {ubicacion}: {datos['cantidad']} estudiantes ({datos['porcentaje']:.1f}%)")
    
    print(f"\n¡Iniciando visualización animada!")
    print(f"Observa cómo los estudiantes se redistribuyen buscando espacios disponibles...\n")
    
    # Crea el visualizador y ejecuta la animación
    visualizador = VisualizadorSimulacion(campus, pasos_simulacion=pasos)
    anim = visualizador.ejecutar()
    
    # Muestra estadísticas finales
    print("\n" + "="*70)
    print("SIMULACIÓN COMPLETADA")
    print("="*70)
    print(f"\nDistribución final:")
    stats_finales = campus.obtener_estadisticas()
    for ubicacion, datos in stats_finales.items():
        print(f"  - {ubicacion}: {datos['cantidad']} estudiantes ({datos['porcentaje']:.1f}%)")
    
    return campus, visualizador, anim


# =============================================================================
# PUNTO DE ENTRADA
# =============================================================================

if __name__ == "__main__":
    """
    Bloque que se ejecuta cuando corres el archivo directamente.
    
    ¿Por qué usar if __name__ == "__main__"?
    - Permite importar este archivo sin ejecutar la simulación automáticamente
    - Es una práctica estándar en Python profesional
    - Facilita reutilizar el código en otros proyectos
    """
    # Configuración de estilo para gráficos más bonitos
    plt.style.use('seaborn-v0_8-darkgrid')
    
    # Ejecuta la simulación con valores por defecto
    # Puedes modificar estos números para experimentar
    campus, visualizador, animacion = ejecutar_simulacion(
        num_estudiantes=50,
        pasos=100
    )
