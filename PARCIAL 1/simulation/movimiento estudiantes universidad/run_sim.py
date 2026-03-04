#!/usr/bin/env python3
"""
Script para ejecutar la simulación de movimiento de estudiantes de forma sencilla.

Ejemplo:
  python run_sim.py --num 50 --pasos 100

Todas las salidas y textos están en español según las reglas del proyecto.
"""
import argparse
import sys
from pathlib import Path
import importlib.util


def main():
    parser = argparse.ArgumentParser(description='Ejecutar simulación de estudiantes')
    parser.add_argument('--num', type=int, default=50, help='Número de estudiantes')
    parser.add_argument('--pasos', type=int, default=100, help='Pasos de simulación')
    args = parser.parse_args()

    proyecto_root = Path(__file__).resolve().parent
    sim_path = proyecto_root / 'PARCIAL 1' / 'simulation' / 'movimiento estudiantes universidad' / 'simulacion_movimiento_estudiantes_universidad.py'

    if not sim_path.exists():
        print(f"ERROR: no se encontró el archivo de simulación en: {sim_path}")
        sys.exit(1)

    spec = importlib.util.spec_from_file_location('sim_module', str(sim_path))
    sim_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sim_module)

    # Llama a la función pública que ejecuta la simulación
    sim_module.ejecutar_simulacion(num_estudiantes=args.num, pasos=args.pasos)


if __name__ == '__main__':
    main()
