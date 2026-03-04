import os
import textwrap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# Ruta del archivo fuente (ajústala si mueves archivos)
SRC_PATH = os.path.join(
    'd:', 'UNIVERSIDAD', 'SEMESTRE 7', 'MODELO DE LA COMPUTACION',
    'PARCIAL 1', 'simulation', 'movimiento estudiantes universidad',
    'simulacion_movimiento_estudiantes_universidad.py'
)

# Ruta de salida del PDF
OUT_PDF = os.path.join(
    'd:', 'UNIVERSIDAD', 'SEMESTRE 7', 'MODELO DE LA COMPUTACION',
    'PARCIAL 1', 'simulation', 'movimiento estudiantes universidad',
    'DOCUMENTACION_simulacion_movimiento_estudiantes_universidad.pdf'
)

TITLE = 'Documentación: simulacion_movimiento_estudiantes_universidad.py'
SUBTITLE = 'Explicación formal con referencias a líneas de código'

def read_source(path):
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return lines


def chunk_lines(lines, n):
    for i in range(0, len(lines), n):
        yield i+1, lines[i:i+n]


def make_title_page(pdf):
    fig = plt.figure(figsize=(11.69,8.27))  # A4 horizontal
    fig.patch.set_facecolor('white')
    plt.axis('off')
    plt.text(0.5, 0.65, TITLE, ha='center', va='center', fontsize=20, fontweight='bold')
    plt.text(0.5, 0.55, SUBTITLE, ha='center', va='center', fontsize=12)
    plt.text(0.5, 0.40, 'Autor: Generado automáticamente', ha='center', va='center', fontsize=10)
    plt.text(0.5, 0.30, 'Contenido: explicación por secciones, seguido de extractos de código con números de línea.', ha='center', va='center', fontsize=9)
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


def make_overview_page(pdf):
    fig = plt.figure(figsize=(11.69,8.27))
    plt.axis('off')
    text = (
        'Resumen ejecutivo:\n\n'
        'Este documento explica la lógica de la simulación "simulacion_movimiento_estudiantes_universidad.py".\n'
        'Se incluye: estructura general, clases principales (UbicacionCampus, Estudiante, CampusUniversitario, VisualizadorSimulacion),\n'
        'flujo de ejecución y descripción de porqués en decisiones de diseño.\n\n'
        'Instrucciones: revisa las páginas siguientes con extractos de código y referencia de líneas.'
    )
    plt.text(0.03, 0.97, text, ha='left', va='top', fontsize=11, wrap=True)
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


def make_section_page(pdf, title, paragraphs):
    fig = plt.figure(figsize=(11.69,8.27))
    plt.axis('off')
    y = 0.95
    plt.text(0.03, y, title, ha='left', va='top', fontsize=14, fontweight='bold')
    y -= 0.05
    for p in paragraphs:
        plt.text(0.03, y, p, ha='left', va='top', fontsize=10, wrap=True)
        y -= 0.06 * (1 + p.count('\n'))
        if y < 0.15:
            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)
            fig = plt.figure(figsize=(11.69,8.27))
            plt.axis('off')
            y = 0.95
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


def make_code_page(pdf, line_start, code_lines):
    fig = plt.figure(figsize=(11.69,8.27))
    plt.axis('off')
    # Prepare a monospaced block with line numbers
    formatted = ''
    for idx, line in enumerate(code_lines, start=line_start):
        # Escape percent signs for matplotlib text
        safe = line.rstrip('\n').replace('%', '%%')
        formatted += f"{idx:4d}: {safe}\n"

    wrapped = textwrap.fill(formatted, width=160)
    plt.text(0.01, 0.99, wrapped, ha='left', va='top', fontsize=8, family='monospace')
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


def generate_pdf(src_path, out_pdf):
    lines = read_source(src_path)

    with PdfPages(out_pdf) as pdf:
        make_title_page(pdf)
        make_overview_page(pdf)

        # Sections with explanations (brief) — these mirror el archivo
        sections = [
            ('Enumeración de ubicaciones (UbicacionCampus)', [
                'Definición: enum con AULA, BIBLIOTECA, CAFETERIA.',
                'Por qué: evita strings dispersos, facilita iteración y uso en diccionarios.'
            ]),
            ('Clase Estudiante', [
                'Campos clave: id, ubicacion_actual, posicion_x/y, tiempo_en_ubicacion, tiempo_minimo_permanencia.',
                'Métodos: decidir_siguiente_ubicacion(entorno) y moverse_a(nueva_ubicacion, entorno).',
                'Decisión: espera tiempo mínimo, comprueba ocupación (umbral 0.7) y con probabilidad 0.7 se queda; si no, elige la ubicación con menor ocupación.'
            ]),
            ('Clase CampusUniversitario', [
                'Mantiene capacidades, zonas visuales, colores, lista de estudiantes e historial de ocupación.',
                'Métodos importantes: _crear_estudiantes, contar_estudiantes_en, obtener_nivel_ocupacion, actualizar_simulacion, obtener_estadisticas.'
            ]),
            ('VisualizadorSimulacion', [
                'Monta figura con dos subplots: vista espacial y gráfico temporal.',
                'En cada frame llama campus.actualizar_simulacion(), redibuja estudiantes y actualiza el gráfico de historial.'
            ])
        ]

        for title, paras in sections:
            make_section_page(pdf, title, paras)

        # Add code extracts chunked by 45 lines per page
        CHUNK = 45
        for start, block in chunk_lines(lines, CHUNK):
            make_code_page(pdf, start, block)

    print(f'PDF generado en: {out_pdf}')


if __name__ == '__main__':
    if not os.path.exists(SRC_PATH):
        print('ERROR: No se encontró el archivo fuente en:')
        print(SRC_PATH)
    else:
        generate_pdf(SRC_PATH, OUT_PDF)
