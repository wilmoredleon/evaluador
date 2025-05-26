"""
Evaluador de perfiles judiciales.
Contiene la lógica principal de análisis de candidatos.
"""

import os
import pandas as pd
import requests
from PyPDF2 import PdfReader
import re
from urllib.parse import urlparse
import logging
from datetime import datetime

from .config import *
from .utils import (
    extraer_años_experiencia,
    analizar_formacion,
    configurar_logging,
    mostrar_banner,
    crear_estructura_directorios,
    mover_archivos_existentes
)
from .nlp_analyzer import NLPAnalyzer

def analizar_experiencia(texto):
    """Analiza la experiencia mencionada en el texto."""
    # Inicializar analizador NLP
    nlp_analyzer = NLPAnalyzer()
    
    # Realizar análisis NLP
    resultados_nlp = nlp_analyzer.analizar_texto(texto)
    
    # Análisis tradicional
    texto = texto.lower()
    exp_judicial = sum(texto.count(p) for p in experiencia_judicial)
    exp_administrativa = sum(texto.count(p) for p in experiencia_administrativa)
    exp_docente = sum(texto.count(p) for p in experiencia_docente)
    exp_investigacion = sum(texto.count(p) for p in experiencia_investigacion)
    
    # Extraer años de experiencia
    años_experiencia = min(
        max(
            extraer_años_experiencia(texto),
            resultados_nlp['experiencia']['años']
        ),
        10  # Limitar a máximo 10 años
    )
    
    # Analizar formación
    formacion = analizar_formacion(texto)
    
    # Evaluar la calidad de la experiencia
    calidad_experiencia = "Alta" if (exp_judicial >= 5 or exp_docente >= 5) and años_experiencia >= 5 else \
                         "Media" if (exp_judicial >= 3 or exp_docente >= 3) or años_experiencia >= 3 else \
                         "Baja"
    
    # Calcular puntaje de calidad del texto
    calidad_texto = resultados_nlp['calidad_texto']
    puntaje_calidad = 0
    if calidad_texto['longitud'] == 'adecuada':
        puntaje_calidad += 5
    if calidad_texto['complejidad'] == 'alta':
        puntaje_calidad += 10
    elif calidad_texto['complejidad'] == 'media':
        puntaje_calidad += 5
    if calidad_texto['coherencia'] == 'alta':
        puntaje_calidad += 5
    
    return {
        "experiencia_judicial": exp_judicial,
        "experiencia_administrativa": exp_administrativa,
        "experiencia_docente": exp_docente,
        "experiencia_investigacion": exp_investigacion,
        "años_experiencia": años_experiencia,
        "calidad_experiencia": calidad_experiencia,
        "formacion": formacion,
        "calidad_texto": puntaje_calidad,
        "entidades": resultados_nlp['entidades'],
        "competencias": resultados_nlp['competencias'],
        "sentimiento": resultados_nlp['sentimiento']['general']
    }

def calcular_puntaje(exp, conteo_positivas, conteo_riesgos):
    """Calcula el puntaje total del candidato."""
    # Pesos para cada categoría
    pesos = {
        "experiencia_judicial": 3.0,      # Experiencia judicial es lo más importante
        "experiencia_docente": 2.0,       # Experiencia docente es muy relevante
        "experiencia_investigacion": 1.5,  # Investigación es importante
        "experiencia_administrativa": 1.0, # Experiencia administrativa es básica
        "años_experiencia": 2.0,          # Años de experiencia son muy importantes
        "formacion": 2.0,                 # Formación académica es muy importante
        "palabras_positivas": 1.5,        # Palabras positivas son importantes
        "palabras_riesgo": -2.0,          # Palabras de riesgo penalizan
        "calidad_texto": 1.0              # Calidad del texto es importante
    }
    
    # Calcular puntaje base
    puntaje = 0
    
    # Puntaje por experiencia judicial (máximo 30 puntos)
    puntaje += min(exp["experiencia_judicial"] * pesos["experiencia_judicial"], 30)
    
    # Puntaje por experiencia docente (máximo 20 puntos)
    puntaje += min(exp["experiencia_docente"] * pesos["experiencia_docente"], 20)
    
    # Puntaje por experiencia en investigación (máximo 15 puntos)
    puntaje += min(exp["experiencia_investigacion"] * pesos["experiencia_investigacion"], 15)
    
    # Puntaje por experiencia administrativa (máximo 10 puntos)
    puntaje += min(exp["experiencia_administrativa"] * pesos["experiencia_administrativa"], 10)
    
    # Puntaje por años de experiencia (máximo 20 puntos)
    # Limitar años de experiencia a un máximo de 10 años para el cálculo
    años_limite = min(exp["años_experiencia"], 10)
    años_puntaje = min(años_limite * pesos["años_experiencia"], 20)
    puntaje += años_puntaje
    
    # Puntaje por formación académica
    formacion_pesos = {
        "doctorado": 20,
        "maestría": 15,
        "licenciatura": 10,
        "especialidad": 5,
        "ninguno": 0
    }
    puntaje += formacion_pesos.get(exp["formacion"]["nivel_maximo"], 0)
    
    # Puntaje por instituciones de formación (máximo 10 puntos)
    puntaje += min(exp["formacion"]["instituciones"] * 2, 10)
    
    # Puntaje por palabras positivas (máximo 15 puntos)
    puntaje += min(conteo_positivas * pesos["palabras_positivas"], 15)
    
    # Penalización por palabras de riesgo
    puntaje += conteo_riesgos * pesos["palabras_riesgo"]
    
    # Puntaje por calidad del texto (máximo 20 puntos)
    puntaje += min(exp["calidad_texto"] * pesos["calidad_texto"], 20)
    
    # Asegurar que el puntaje no sea negativo y no exceda 100
    return max(0, min(puntaje, 100))

def evaluar_aptitud(exp, conteo_riesgos):
    """Evalúa la aptitud del candidato basado en formación y experiencia judicial, usando conteos pre-calculados."""
    # --- Lógica de Evaluación de Aptitud (Formación y Experiencia Judicial) ---
    nivel_formacion = exp["formacion"]["nivel_maximo"]
    exp_judicial = exp["experiencia_judicial"]

    logging.debug(f"Evaluando aptitud: Nivel Formación={nivel_formacion}, Exp Judicial Conteo={exp_judicial}, Riesgo Conteo={conteo_riesgos}")

    aptitud = "No Apto"

    # Criterio para Apto - Más estricto
    # Nivel Doctorado, >= 8 judicial, 0 riesgos
    if nivel_formacion == "doctorado" and exp_judicial >= 8 and conteo_riesgos == 0:
        aptitud = "Apto"
    # Criterio para Observado - Más estricto
    # Nivel Maestría o superior, >= 5 judicial, 0 riesgos
    elif nivel_formacion in ["maestría", "doctorado"] and exp_judicial >= 5 and conteo_riesgos == 0:
        aptitud = "Observado"

    logging.debug(f"Resultado Aptitud: {aptitud}")
    return aptitud

def procesar_seccion(seccion, archivo_entrada, archivo_salida, log_file):
    """Procesa una sección específica de candidatos."""
    logging.info(f"Procesando sección: {seccion}")
    
    # Asegurar que el archivo de salida tenga extensión .xlsx
    archivo_salida = os.path.splitext(archivo_salida)[0] + '.xlsx'
    
    # Obtener el directorio y el prefijo del archivo
    directorio = os.path.dirname(archivo_entrada)
    prefijo = os.path.basename(archivo_entrada).replace('.xlsx', '')
    
    # Buscar archivos que coincidan con el prefijo
    archivos_coincidentes = []
    if os.path.exists(directorio):
        for archivo in os.listdir(directorio):
            if archivo.startswith(prefijo) and archivo.endswith('.xlsx'):
                archivos_coincidentes.append(os.path.join(directorio, archivo))
    
    if not archivos_coincidentes:
        logging.error(f"No se encontraron archivos con prefijo {prefijo} en {directorio}")
        return
    
    # Usar el archivo más reciente si hay múltiples coincidencias
    archivo_entrada = max(archivos_coincidentes, key=os.path.getctime)
    logging.info(f"Usando archivo: {archivo_entrada}")
    
    # Cargar Excel
    try:
        df = pd.read_excel(archivo_entrada)
        df.columns = [col.strip() for col in df.columns]
        df = df.rename(columns={df.columns[0]: "Poder", df.columns[1]: "Nombre", df.columns[2]: "URL"})
    except Exception as e:
        logging.error(f"Error al cargar {archivo_entrada}: {e}")
        return
    
    # Resultados
    resultados = []
    total_candidatos = len(df)
    
    logging.info(f"Total de candidatos a procesar: {total_candidatos}")
    
    for idx, row in df.iterrows():
        nombre = row["Nombre"]
        url_pdf = row["URL"]
        poder = row["Poder"]
        
        logging.info(f"Procesando candidato {idx + 1}/{total_candidatos}: {nombre}")
        
        if not isinstance(url_pdf, str) or not url_pdf.lower().endswith(".pdf"):
            logging.warning(f"URL inválida para {nombre}")
            continue
        
        archivo_pdf = os.path.join(PDF_DIR, os.path.basename(urlparse(url_pdf).path))
        
        # Descargar PDF si no existe
        if not os.path.exists(archivo_pdf):
            logging.info(f"Descargando PDF de {nombre}...")
            try:
                r = requests.get(url_pdf)
                with open(archivo_pdf, "wb") as f:
                    f.write(r.content)
            except Exception as e:
                logging.error(f"Error al descargar {url_pdf}: {e}")
                continue
        else:
            logging.info(f"PDF ya existe: {archivo_pdf}")
        
        # Leer texto del PDF
        try:
            reader = PdfReader(archivo_pdf)
            texto = "".join(page.extract_text() or "" for page in reader.pages).lower()
        except Exception as e:
            logging.error(f"Error al leer {archivo_pdf}: {e}")
            texto = ""
        
        # Detectar redes sociales
        redes_detectadas = bool(re.search(r"(facebook|instagram|tiktok|x\.com|twitter|youtube|linkedin)", texto))
        
        # Evaluar palabras clave
        conteo_positivas = sum(texto.count(p) for p in palabras_positivas)
        conteo_riesgos = sum(texto.count(p) for p in palabras_riesgo)
        
        # Penalización si no hay redes
        if not redes_detectadas:
            conteo_riesgos += 1 # Penalización
        
        # Análisis de experiencia
        exp = analizar_experiencia(texto)
        
        # Calcular puntajes individuales
        puntaje_judicial = min(exp["experiencia_judicial"] * 3.0, 30)
        puntaje_docente = min(exp["experiencia_docente"] * 2.0, 20)
        puntaje_investigacion = min(exp["experiencia_investigacion"] * 1.5, 15)
        puntaje_administrativa = min(exp["experiencia_administrativa"] * 1.0, 10)
        puntaje_años = min(exp["años_experiencia"] * 2.0, 20)
        
        # Puntaje por formación académica
        formacion_pesos = {
            "doctorado": 20,
            "maestría": 15,
            "licenciatura": 10,
            "especialidad": 5,
            "ninguno": 0
        }
        puntaje_formacion = formacion_pesos.get(exp["formacion"]["nivel_maximo"], 0)
        
        # Puntaje por instituciones de formación
        puntaje_instituciones = min(exp["formacion"]["instituciones"] * 2, 10)
        
        # Puntaje por palabras positivas
        puntaje_positivas = min(conteo_positivas * 1.5, 15)
        
        # Penalización por palabras de riesgo
        puntaje_riesgos = conteo_riesgos * -2.0
        
        # Puntaje por calidad del texto
        puntaje_calidad = min(exp["calidad_texto"] * 1.0, 20)
        
        # Calcular puntaje total
        puntaje_total = (
            puntaje_judicial +
            puntaje_docente +
            puntaje_investigacion +
            puntaje_administrativa +
            puntaje_años +
            puntaje_formacion +
            puntaje_instituciones +
            puntaje_positivas +
            puntaje_riesgos +
            puntaje_calidad
        )
        
        # Asegurar que el puntaje no sea negativo y no exceda 100
        puntaje_total = max(0, min(puntaje_total, 100))
        
        # Evaluar aptitud
        aptitud = evaluar_aptitud(exp, conteo_riesgos)
        
        # Agregar resultados
        resultados.append({
            "Poder": poder,
            "Nombre": nombre,
            "URL": url_pdf,
            "Puntaje Total": puntaje_total,
            "Aptitud": aptitud,
            "Puntaje Judicial": puntaje_judicial,
            "Puntaje Docente": puntaje_docente,
            "Puntaje Investigación": puntaje_investigacion,
            "Puntaje Administrativa": puntaje_administrativa,
            "Puntaje Años": puntaje_años,
            "Puntaje Formación": puntaje_formacion,
            "Puntaje Instituciones": puntaje_instituciones,
            "Puntaje Positivas": puntaje_positivas,
            "Puntaje Riesgos": puntaje_riesgos,
            "Puntaje Calidad": puntaje_calidad,
            "Conteo Palabras Riesgo": conteo_riesgos,
            "Conteo Palabras Positivas": conteo_positivas,
            "Redes Sociales": "Sí" if redes_detectadas else "No"
        })
    
    # Crear DataFrame con resultados
    df_resultados = pd.DataFrame(resultados)
    
    # Guardar resultados en Excel
    try:
        # Si el archivo ya existe, cargarlo y agregar nueva hoja
        if os.path.exists(archivo_salida):
            with pd.ExcelWriter(archivo_salida, engine='openpyxl', mode='a') as writer:
                df_resultados.to_excel(writer, sheet_name=seccion, index=False)
        else:
            # Si no existe, crear nuevo archivo
            df_resultados.to_excel(archivo_salida, sheet_name=seccion, index=False)
        logging.info(f"Resultados guardados en hoja '{seccion}' de {archivo_salida}")
    except Exception as e:
        logging.error(f"Error al guardar resultados en {archivo_salida}: {e}") 