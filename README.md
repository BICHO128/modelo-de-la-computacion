**Simulación: Movimiento de Estudiantes en la Universidad**

Resumen: Este repositorio contiene una simulación basada en agentes que modela cómo estudiantes se mueven entre espacios del campus (aula, biblioteca, cafetería). El proyecto usa `matplotlib` y `numpy` y está escrito en Python.

**Requisitos**
- **Python**: versión 3.10 o superior recomendada.
- **Visual Studio Code** (opcional, para ejecución y depuración fácil).
- Sistema con capacidad gráfica para mostrar la animación (no headless), o configurar un backend apropiado.

**Archivos clave**
- `PARCIAL 1/simulation/movimiento estudiantes universidad/simulacion_movimiento_estudiantes_universidad.py`: Código principal de la simulación.
- [run_sim.py](run_sim.py): Script de conveniencia para lanzar la simulación con argumentos (`--num`, `--pasos`).
- [requirements.txt](requirements.txt): Lista de dependencias (`numpy`, `matplotlib`).
- [.vscode/settings.json](.vscode/settings.json): Configura el intérprete a `./.venv` para este workspace.
- [.vscode/launch.json](.vscode/launch.json): Configuración de ejecución (F5) para correr `run_sim.py`.

**Instalación desde cero (Windows, PowerShell)**
1. Instala Python 3.10+ desde https://python.org y asegúrate de añadirlo al PATH.
2. Abre PowerShell en la raíz del proyecto (`D:\UNIVERSIDAD\SEMESTRE 7\MODELO DE LA COMPUTACION`).
3. Crear un entorno virtual y activar:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

4. Actualizar pip e instalar dependencias:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Nota (política de ejecución PowerShell): si `Activate.ps1` falla por la política de ejecución, ejecutar antes:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
```

**Uso desde VS Code (recomendado)**
1. Abre la carpeta del proyecto en VS Code.
2. Selecciona el intérprete: abre la paleta (Ctrl+Shift+P) → `Python: Select Interpreter` → elige `./.venv/Scripts/python.exe`.
3. Para ejecutar con depuración (F5): selecciona la configuración `Run Simulation` y presiona F5. La configuración por defecto ejecuta `run_sim.py` con `--num 30 --pasos 30` (puedes modificarlo en `.vscode/launch.json`).

**Uso desde terminal**
- Activar entorno y ejecutar con argumentos personalizados:

```powershell
.\.venv\Scripts\Activate.ps1
python run_sim.py --num 50 --pasos 100
```

**Descripción rápida de `run_sim.py`**
- Facilita ejecutar la simulación sin importar la ruta del archivo. Permite `--num` (número de estudiantes) y `--pasos` (pasos de tiempo).

**Ejemplo**
- Ejecutar una prueba rápida de 20 estudiantes y 20 pasos:

```powershell
.\.venv\Scripts\Activate.ps1
python run_sim.py --num 20 --pasos 20
```

**Solución de problemas**
- Pylance muestra importaciones no resueltas: asegúrate de que VS Code usa el intérprete `./.venv` (ver sección VS Code).
- Si la animación no se muestra en entornos sin servidor X o en servidores remotos, puedes usar un backend no interactivo o guardar la animación; el script actual usa la GUI de `matplotlib`.
- Si faltan paquetes, ejecuta `python -m pip install -r requirements.txt` dentro del virtualenv.

**Cómo modificar la simulación**
- El código principal está en `PARCIAL 1/simulation/movimiento estudiantes universidad/simulacion_movimiento_estudiantes_universidad.py`.
- Para cambiar capacidades, zonas o lógica de decisión, edita las clases `CampusUniversitario` y `Estudiante` dentro de ese archivo.

**Notas finales**
- Todas las salidas y comentarios del código están en español por requisito del proyecto.
- Si quieres, puedo añadir un script para guardar la animación como vídeo/MP4 o agregar argumentos para modo headless.

Autores: Simulación basada en agentes (estructura y documentación añadida)
