# 🤖 Simulaciones de Modelado Basado en Agentes (MBA)
### Parcial 1 — Ingeniería de Software y Computación

> Dos simulaciones desarrolladas en Python que modelan el comportamiento de agentes en entornos dinámicos: el movimiento de estudiantes en un campus universitario y el flujo vehicular en una intersección urbana con semáforos.

---

## 📌 Descripción General

Este repositorio aplica el enfoque de **Modelado Basado en Agentes (ABM)** para replicar sistemas del mundo real de forma computacional. Cada agente posee reglas de comportamiento propias que, en conjunto, generan dinámicas emergentes comparables a las observadas en entornos reales.

Ambas simulaciones están diseñadas para ejecutarse en **Google Colab** o de forma **local mediante VS Code**, priorizando la legibilidad del código y la claridad en las visualizaciones gráficas.

---

## 🗂️ Proyectos Incluidos

### 1. 🎓 Simulación: Movimiento de Estudiantes

Modela el desplazamiento de agentes-estudiantes entre tres puntos de interés dentro de un campus universitario: el **aula**, la **biblioteca** y la **cafetería**.

- **Lógica de decisión:** Cada agente evalúa la disponibilidad de espacios en función de la capacidad de cada área. Si el destino está lleno, recalcula su ruta hacia otro punto de interés.
- **Visualización:** Gráficos de distribución de agentes en tiempo real que permiten observar patrones de movimiento y ocupación.

---

### 2. 🚦 Simulación: Tráfico en una Ciudad (Intersección 4 Vías)

Modela el flujo de vehículos en el cruce de dos calles principales con sentidos de circulación opuestos.

- **Sistema de semáforos:** 4 semáforos sincronizados con ciclos de **Verde → Amarillo → Rojo**.
- **Comportamiento de los agentes:**
  - Los vehículos se desplazan únicamente en **línea recta** (sin giros).
  - **Detección de colisiones:** Un vehículo se detiene automáticamente si detecta otro vehículo en el espacio inmediatamente frente a él.
  - **Respeto a señales:** Los vehículos frenan al detectar luz **amarilla** o **roja**.

---

## 🛠️ Requisitos Técnicos

| Componente | Detalle |
|---|---|
| Lenguaje | Python 3.10 o superior |
| Librerías principales | `numpy`, `matplotlib` |
| Entorno recomendado | Visual Studio Code / Google Colab |

---

## 📥 Instalación Local (Windows / PowerShell)

Sigue estos pasos para configurar el entorno de desarrollo en tu máquina:

**1. Clona el repositorio y accede a la carpeta raíz del proyecto:**
```powershell
cd "RUTA_DEL_PROYECTO"
```

**2. Crea y activa el entorno virtual:**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**3. Instala las dependencias del proyecto:**
```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

## 📂 Estructura del Proyecto

```
📦 Raíz del Repositorio
├── .vscode/                          # Configuraciones de ejecución (F5)
├── .venv/                            # Entorno virtual (generado tras instalación)
├── requirements.txt                  # Dependencias del proyecto
├── run_sim.py                        # Lanzador — Simulación de estudiantes
├── run_traffic.py                    # Lanzador — Simulación de tráfico
└── PARCIAL 1/
    └── simulation/
        ├── movimiento estudiantes/   # Código principal — Estudiantes
        └── trafico en una ciudad/   # Código principal — Tráfico
```

---

## 🎮 Cómo Ejecutar las Simulaciones

### Opción A: Desde Visual Studio Code *(Recomendado)*

1. Selecciona el intérprete de Python de tu entorno virtual (`./.venv`).
2. Presiona `F5` y elige la configuración deseada:
   - **`Run Simulation`** → Simulación de estudiantes
   - **`Run Traffic Simulation`** → Simulación de tráfico

### Opción B: Desde la Terminal

**Simulación de estudiantes:**
```powershell
python run_sim.py --num 50 --pasos 100
```

**Simulación de tráfico:**
```powershell
python run_traffic.py --ancho 20 --alto 20 --pasos 200
```

---

## 📜 Reglas y Convenciones del Proyecto

- **🇨🇴 Idioma:** Todo el código, comentarios, nombres de variables e interfaz de usuario están escritos **100% en español**.
- **📖 Documentación:** Cada sección del código está explicada de forma didáctica para facilitar la comprensión en el contexto académico de MBA.

---

## 👤 Autor

Desarrollado como entrega del **Parcial 1** para la asignatura de Modelado Basado en Agentes.
