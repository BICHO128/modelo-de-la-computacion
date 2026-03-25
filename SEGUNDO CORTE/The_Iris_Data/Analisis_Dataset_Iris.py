from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Análisis del dataset de Iris - Página de la Dataset:
# <script src="https://gist.github.com/curran/a08a1080b88344b0c8a7.js"></script>

base = Path(__file__).resolve().parent
csv_path = base / 'iris.csv'

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


def calcular_especie_mas_pequena(df):
	"""Calcula e imprime la especie más pequeña según medias de medidas.

	Se muestran las especies con la media más baja por cada columna
	(sepal_length, sepal_width, petal_length, petal_width) y una
	medida agregada `mean_all` que es el promedio de las cuatro medidas.
	"""
	cols = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']
	# Agrupar por especie y calcular la media de las columnas numéricas relevantes
	medias = df.groupby('species')[cols].mean()
	# Media agregada (promedio de las cuatro medidas)
	medias['mean_all'] = medias.mean(axis=1)

	print("\nMedias por especie:")
	print(medias)

	# Mostrar qué especie es la más pequeña por cada medida
	for col in medias.columns:
		especie_min = medias[col].idxmin()
		valor_min = medias[col].min()
		if col == 'mean_all':
			print(f"Especie con menor tamaño promedio general: {especie_min} ({valor_min:.3f})")
		else:
			print(f"Especie con menor {col}: {especie_min} ({valor_min:.3f})")

	# Generar gráfica comparativa y guardarla
	def plot_comparativa(medias_df, save_path=None, show=False):
		# Usar solo las cuatro medidas principales
		cols_plot = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']
		# Establecer estilo
		sns.set(style='whitegrid')
		ax = medias_df[cols_plot].plot(kind='bar', figsize=(9,6))
		ax.set_ylabel('Media (cm)')
		ax.set_xlabel('Especie')
		ax.set_title('Comparativa de medias por especie (sepal/petal)')
		plt.xticks(rotation=0)
		plt.legend(title='Medida')
		plt.tight_layout()
		if save_path:
			plt.savefig(save_path)
			print(f"Gráfica guardada en: {save_path}")
		if show:
			plt.show()
		plt.close()

	# Guardar la gráfica en el mismo directorio del script
	output_img = Path(__file__).resolve().parent / 'comparativa_medias.png'
	plot_comparativa(medias, save_path=output_img, show=True)


# Ejecutar el cálculo adicional
calcular_especie_mas_pequena(csv)
