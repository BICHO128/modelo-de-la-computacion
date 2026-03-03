#!/usr/bin/env python3
"""
Script para ejecutar la simulación de tráfico de forma sencilla.

Ejemplo:
  python run_traffic.py --ancho 20 --alto 20 --pasos 200
"""
import argparse
import sys
from pathlib import Path
import importlib.util


def main():
    parser = argparse.ArgumentParser(description='Ejecutar simulación de tráfico')
    parser.add_argument('--ancho', type=int, default=20, help='Ancho de la ciudad (celdas)')
    parser.add_argument('--alto', type=int, default=20, help='Alto de la ciudad (celdas)')
    parser.add_argument('--pasos', type=int, default=200, help='Pasos de simulación')
    args = parser.parse_args()

    proyecto_root = Path(__file__).resolve().parent
    sim_path = proyecto_root / 'simulacion_trafico_ciudad.py'

    if not sim_path.exists():
        print(f"ERROR: no se encontró el archivo de simulación en: {sim_path}")
        sys.exit(1)

    spec = importlib.util.spec_from_file_location('sim_trafico', str(sim_path))
    sim_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sim_module)

    # Llama a la función pública que ejecuta la simulación
    sim_module.ejecutar_simulacion(ancho_ciudad=args.ancho, alto_ciudad=args.alto, pasos=args.pasos)


if __name__ == '__main__':
    main()
