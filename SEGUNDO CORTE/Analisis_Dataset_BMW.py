from pathlib import Path
import pandas as pd

# Análisis del dataset de BMW - Página de la Dataset:
# https://www.kaggle.com/datasets/guriya79/bmw-cars

base = Path(__file__).resolve().parent
csv_path = base / 'bmw.csv'

try:
	csv = pd.read_csv(csv_path)
except FileNotFoundError:
	raise FileNotFoundError(f"No se encontró el archivo CSV en: {csv_path}")

# Mostrar las primeras filas del DataFrame
print("Primeras filas del DataFrame:")
print(csv.head())
# Descripción estadística de las columnas numéricas
print("\nDescripción estadística de las columnas numéricas:")
print(csv.describe())
# Información sobre el DataFrame, incluyendo tipos de datos y valores nulos
print("\nInformación del DataFrame:")
print(csv.info())

print("\nAnálisis de datos completado.")
