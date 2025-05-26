"""
Utilidades para el evaluador de perfiles judiciales.
Contiene funciones auxiliares utilizadas en el análisis.
"""

import re
from datetime import datetime
import os
import logging

from .config import LOGS_DIR

def extraer_años_experiencia(texto):
    """Extrae los años de experiencia mencionados en el texto."""
    patrones = [
        r'(\d+)\s*años?\s*de\s*experiencia',
        r'experiencia\s*de\s*(\d+)\s*años?',
        r'(\d+)\s*años?\s*en\s*el\s*cargo',
        r'(\d+)\s*años?\s*como\s*juez',
        r'(\d+)\s*años?\s*como\s*magistrado',
        r'desde\s*el\s*año\s*(\d{4})',
        r'desde\s*(\d{4})\s*a\s*la\s*fecha'
    ]
    
    años = []
    for patron in patrones:
        matches = re.finditer(patron, texto.lower())
        for match in matches:
            if len(match.group(1)) == 4:  # Si es un año
                años.append(2024 - int(match.group(1)))  # Calcular años hasta 2024
            else:
                años.append(int(match.group(1)))
    
    return max(años) if años else 0

def analizar_formacion(texto):
    """Analiza la formación académica mencionada en el texto."""
    texto = texto.lower()
    
    # Detectar grados académicos
    grados = {
        "doctorado": len(re.findall(r'doctorado|doctora|doctor', texto)),
        "maestría": len(re.findall(r'maestría|maestro|maestra', texto)),
        "licenciatura": len(re.findall(r'licenciatura|licenciado|licenciada', texto)),
        "especialidad": len(re.findall(r'especialidad|especialista', texto))
    }
    
    # Detectar instituciones de prestigio
    instituciones = len(re.findall(r'universidad|instituto|centro|escuela', texto))
    
    return {
        "grados_academicos": grados,
        "instituciones": instituciones,
        "nivel_maximo": max(grados.items(), key=lambda x: x[1])[0] if any(grados.values()) else "ninguno"
    }

def configurar_logging(log_file=None):
    """Configura el sistema de logging."""
    log_dir = LOGS_DIR
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Si no se proporciona un archivo de log, usar uno con timestamp
    if log_file is None:
        log_filename = datetime.now().strftime('evaluacion_%Y%m%d_%H%M%S.log')
        log_filepath = os.path.join(log_dir, log_filename)
    else:
        log_filepath = log_file
    
    logging.basicConfig(
        level=logging.DEBUG, # Establecer nivel de logging a DEBUG
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename=log_filepath,
        filemode='w'
    )
    
    # También configurar un handler para la consola para ver logs en tiempo real
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

def mostrar_banner():
    """Muestra un banner informativo al inicio del programa."""
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║             EVALUADOR DE PERFILES JUDICIALES               ║
    ║                                                            ║
    ║  Analizador de candidatos al Poder Judicial de México      ║
    ║  Versión 1.0                                              ║
    ╚════════════════════════════════════════════════════════════╝
    """)

def crear_estructura_directorios(directorios):
    """Crea la estructura de directorios necesaria."""
    for dir_path, desc in directorios.items():
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"✓ Creado directorio: {dir_path} ({desc})")

def mover_archivos_existentes(directorios):
    """Mueve los archivos existentes a la nueva estructura."""
    import shutil
    
    # Mover PDFs existentes
    if os.path.exists("pdfs"):
        for file in os.listdir("pdfs"):
            if file.endswith(".pdf"):
                shutil.move(os.path.join("pdfs", file), os.path.join(directorios["PDF_DIR"], file))
        os.rmdir("pdfs")
    
    # Mover archivos CSV existentes
    for file in os.listdir():
        if file.endswith(".csv"):
            shutil.move(file, os.path.join(directorios["RESULTS_DIR"], file))
    
    # Mover archivos Excel existentes
    for file in os.listdir():
        if file.endswith(".xlsx"):
            shutil.move(file, os.path.join(directorios["RAW_DATA_DIR"], file)) 