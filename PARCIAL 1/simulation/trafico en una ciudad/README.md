# Simulación de Tráfico en una Ciudad

Este directorio contiene la simulación `simulacion_trafico_ciudad.py` que modela el flujo vehicular con semáforos.

Instrucciones rápidas:

1. Asegúrate de haber creado y activado el entorno virtual en la raíz del proyecto:

```powershell
python -m venv D:\UNIVERSIDAD\SEMESTRE 7\MODELO DE LA COMPUTACION\.venv
.\.venv\Scripts\Activate.ps1
```

2. Instala dependencias (en el virtualenv):

```powershell
python -m pip install -r D:\UNIVERSIDAD\SEMESTRE 7\MODELO DE LA COMPUTACION\requirements.txt
```

3. Ejecutar la simulación desde este directorio con el script de conveniencia:

```powershell
.\.venv\Scripts\python "D:\UNIVERSIDAD\SEMESTRE 7\MODELO DE LA COMPUTACION\PARCIAL 1\simulation\trafico en una ciudad\run_traffic.py" --ancho 20 --alto 20 --pasos 200
```

4. Alternativamente, usa VS Code (selecciona el intérprete `./.venv`) y ejecuta la configuración "Run Traffic Simulation" (F5) que está en la configuración del workspace.

Notas:
- El script `run_traffic.py` carga dinámicamente `simulacion_trafico_ciudad.py` y llama a `ejecutar_simulacion(...)`.
- Si la ventana de animación no aparece, verifica que no estés en un entorno headless y que `matplotlib` esté instalado en el virtualenv.

Si quieres, puedo añadir una opción para exportar la animación a vídeo (MP4) o crear tests unitarios para las funciones de la clase `Ciudad`.
