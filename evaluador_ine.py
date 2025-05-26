import os
import pandas as pd
import requests
from PyPDF2 import PdfReader
import io
import re
from datetime import datetime
import unicodedata
import logging
from src.utils import configurar_logging, crear_estructura_directorios
from src.evaluador import procesar_seccion # Importar solo procesar_seccion
from src.config import (
    archivos_entrada, 
    archivos_salida, 
    BASE_DIR, 
    LOG_DIR,
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    PDF_DIR,
    RESULTS_DIR,
    LOGS_DIR
) # Importar configuraciones necesarias

def slugify(value, allow_unicode=False):
    """
    Convierte una cadena a un formato amigable para URL/nombre de archivo.
    Tomado de Django.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    # Eliminar caracteres no alfanuméricos y reemplazar espacios/guiones con guiones bajos
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return re.sub(r'[-\s]+', '_', value)

def cargar_datos(ruta_carpeta):
    """
    Carga los datos de los archivos Excel en la carpeta especificada.
    
    Args:
        ruta_carpeta (str): Ruta a la carpeta que contiene los archivos Excel
        
    Returns:
        dict: Diccionario con los datos de cada tipo de candidato
    """
    datos = {}
    
    # Mapeo de prefijos a tipos de candidatos
    prefijos = {
        'Candidatos_JD': 'Jueces de Distrito',
        'Candidatos_MC': 'Magistrados de Circuito',
        'Candidatos_MSRTEPJF': 'Magistrados de Sala Regional del TEPJF',
        'Candidatos_MSSTEPJF': 'Magistrados de Sala Superior del TEPJF',
        'Candidatos_MTDJ': 'Magistrados del Tribunal de Justicia',
        'Candidatos_MSCJN': 'Magistrados de la Suprema Corte de Justicia de la Nación'
    }
    
    # Obtener lista de archivos en la carpeta
    archivos = os.listdir(ruta_carpeta)
    
    # Filtrar solo archivos Excel
    archivos_excel = [f for f in archivos if f.endswith('.xlsx')]
    
    for archivo in archivos_excel:
        # Obtener el prefijo del archivo (ignorando la fecha)
        partes_nombre = archivo.split('_')
        # Asegurarse de que hay al menos dos partes para evitar errores de índice
        if len(partes_nombre) > 1:
            prefijo = '_'.join(partes_nombre[:-1])
        else:
            # Si el nombre del archivo no tiene el formato esperado, usar el nombre completo
            prefijo = partes_nombre[0].replace('.xlsx', '')
            
        if prefijo in prefijos:
            tipo_candidato = prefijos[prefijo]
            ruta_completa = os.path.join(ruta_carpeta, archivo)
            
            try:
                df = pd.read_excel(ruta_completa)
                datos[tipo_candidato] = df
                print(f"Archivo cargado exitosamente: {archivo}")
            except Exception as e:
                print(f"Error al cargar {archivo}: {str(e)}")
        else:
            print(f"Advertencia: Archivo '{archivo}' ignorado por prefijo desconocido '{prefijo}'")
    
    return datos

def descargar_pdf(url, nombre_candidato):
    """
    Descarga un PDF desde una URL, lo guarda y extrae su texto.
    Si el PDF ya existe localmente, lo lee en lugar de descargarlo.
    
    Args:
        url (str): URL del PDF
        nombre_candidato (str): Nombre del candidato para el archivo
        
    Returns:
        str: Texto extraído del PDF, o None si falla.
    """
    # Crear carpeta para PDFs si no existe
    carpeta_pdfs = os.path.join('data', 'pdfs')
    os.makedirs(carpeta_pdfs, exist_ok=True)
    
    # Generar nombre de archivo limpio y ruta potencial
    nombre_archivo_limpio = slugify(nombre_candidato)
    if not nombre_archivo_limpio:
        # Usar un nombre genérico si el nombre del candidato está vacío después de slugify
        nombre_archivo_limpio = "pdf_descargado"
        
    ruta_pdf_base = os.path.join(carpeta_pdfs, f"{nombre_archivo_limpio}.pdf")
    ruta_pdf = ruta_pdf_base
    contador = 1

    # Verificar si el archivo ya existe (con o sin sufijo numérico de corridas anteriores)
    # Buscamos el archivo que coincida con el nombre base o base_N
    archivos_existentes = [f for f in os.listdir(carpeta_pdfs) if f.startswith(nombre_archivo_limpio) and f.endswith('.pdf')]
    
    if archivos_existentes:
        # Si encontramos algún archivo que coincida, asumimos que es el descargado previamente
        # Podríamos añadir lógica más sofisticada aquí si fuera necesario (ej. verificar URL dentro del PDF)
        # Pero por ahora, tomamos el primero que coincida como el archivo ya descargado.
        archivo_local_existente = os.path.join(carpeta_pdfs, archivos_existentes[0])
        print(f"Archivo PDF encontrado localmente para {nombre_candidato}: {archivos_existentes[0]}. Leyendo...")
        try:
            with open(archivo_local_existente, 'rb') as f:
                pdf_reader = PdfReader(f)
                texto = ""
                for pagina in pdf_reader.pages:
                    texto += pagina.extract_text() or "" # Manejar páginas vacías
            return texto
        except Exception as e:
            print(f"Error al leer el archivo PDF local {archivo_local_existente}: {str(e)}. Intentando descargar de nuevo...")
            # Si falla la lectura del archivo local, intentamos descargar
            pass # Continuar al bloque de descarga
    
    # Si el archivo no se encontró localmente o falló la lectura, descargar
    print(f"Descargando PDF para {nombre_candidato} desde {url}")
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # Determinar la ruta final del archivo manejando duplicados
            # Esta parte asegura que si hay un archivo local (quizás de una corrida anterior
            # que falló después de descargar pero antes de guardar correctamente), o si 
            # se genera un duplicado en esta misma corrida, se maneje.
            while os.path.exists(ruta_pdf):
                 ruta_pdf = os.path.join(carpeta_pdfs, f"{nombre_archivo_limpio}_{contador}.pdf")
                 contador += 1

            with open(ruta_pdf, 'wb') as f:
                f.write(response.content)
            
            print(f"PDF descargado y guardado como: {os.path.basename(ruta_pdf)}")

            # Extraer texto del PDF recién descargado
            pdf_reader = PdfReader(io.BytesIO(response.content))
            texto = ""
            for pagina in pdf_reader.pages:
                texto += pagina.extract_text() or "" # Manejar páginas vacías
            
            return texto
        else:
            print(f"Error al descargar PDF para {nombre_candidato}: Código de estado {response.status_code}")
            return None
    except Exception as e:
        print(f"Error durante la descarga o procesamiento del PDF para {nombre_candidato}: {str(e)}")
        return None

def analizar_experiencia(texto):
    """
    Analiza la experiencia del candidato en el texto del PDF.
    
    Args:
        texto (str): Texto extraído del PDF
        
    Returns:
        dict: Diccionario con los resultados del análisis
    """
    resultados = {
        'experiencia_judicial': 0,
        'experiencia_docente': 0,
        'experiencia_investigacion': 0,
        'experiencia_administrativa': 0,
        'años_experiencia': 0,
        'formacion_academica': 0,
        'instituciones_formacion': 0,
        'palabras_positivas': 0,
        'palabras_riesgo': 0
    }
    
    # Palabras clave para cada tipo de experiencia
    palabras_clave = {
        'experiencia_judicial': ['juez', 'magistrado', 'tribunal', 'sentencia', 'juicio', 'poder judicial'],
        'experiencia_docente': ['profesor', 'catedrático', 'docente', 'maestro', 'enseñanza', 'universidad', 'instituto'],
        'experiencia_investigacion': ['investigador', 'investigación', 'publicación', 'artículo', 'estudio', 'tesis'],
        'experiencia_administrativa': ['director', 'coordinador', 'administrativo', 'gestión', 'gerencia', 'secretario', 'jefe']
    }
    
    # Palabras positivas y de riesgo
    palabras_positivas = ['excelente', 'destacado', 'reconocido', 'experto', 'especialista', 'trayectoria impecable', 'amplia experiencia']
    palabras_riesgo = ['controversia', 'irregularidad', 'sanción', 'investigación penal', 'queja', 'denuncia', 'conflicto de interés']
    
    # Analizar texto
    texto = texto.lower()
    
    # Contar ocurrencias de palabras clave (usando word boundaries más robustas)
    for tipo, palabras in palabras_clave.items():
        for palabra in palabras:
            # Usar regex para encontrar la palabra completa, ignorando puntuación alrededor
            resultados[tipo] += len(re.findall(r'[^\w]' + re.escape(palabra) + r'[^\w]', texto))
    
    # Contar palabras positivas y de riesgo (usando word boundaries más robustas)
    for palabra in palabras_positivas:
        resultados['palabras_positivas'] += len(re.findall(r'[^\w]' + re.escape(palabra) + r'[^\w]', texto))
    
    for palabra in palabras_riesgo:
        resultados['palabras_riesgo'] += len(re.findall(r'[^\w]' + re.escape(palabra) + r'[^\w]', texto))

    # Calcular años de experiencia (intentar ser más flexible)
    años_encontrados = re.findall(r'(\d+)\s*(?:años|años de experiencia)', texto)
    if años_encontrados:
        resultados['años_experiencia'] = max(map(int, años_encontrados))

    # Análisis básico de formación académica (ejemplo: buscar palabras clave como 'Licenciatura', 'Maestría', 'Doctorado')
    if re.search(r'doctorado|dr\.', texto):
        resultados['formacion_academica'] = 3 # Doctorado
    elif re.search(r'maestría|mcía\.', texto):
        resultados['formacion_academica'] = 2 # Maestría
    elif re.search(r'licenciatura|lic\.', texto):
        resultados['formacion_academica'] = 1 # Licenciatura

    # Análisis básico de instituciones (ejemplo: buscar nombres de universidades conocidas, muy simplificado)
    instituciones_conocidas = ['unam', 'itez', 'itam', 'colegio de mexico']
    for inst in instituciones_conocidas:
        if inst in texto:
            resultados['instituciones_formacion'] += 1 # Contar cuántas instituciones conocidas se mencionan
    
    return resultados

def calcular_puntaje(resultados):
    """
    Calcula el puntaje total del candidato.
    
    Args:
        resultados (dict): Resultados del análisis
        
    Returns:
        dict: Puntaje total y clasificación
    """
    puntaje = 0
    
    # Ponderación de la experiencia (ajustando valores)
    puntaje += min(resultados['experiencia_judicial'] * 6, 30) # Judicial más peso
    puntaje += min(resultados['experiencia_docente'] * 3, 15)
    puntaje += min(resultados['experiencia_investigacion'] * 4, 20) # Investigación más peso
    puntaje += min(resultados['experiencia_administrativa'] * 2, 10)
    
    # Años de Experiencia (ajustando)
    puntaje += min(resultados['años_experiencia'] * 2.5, 25) # Años de experiencia con más peso
    
    # Formación Académica (ponderación por nivel)
    puntaje += resultados['formacion_academica'] * 5 # 5 puntos por nivel (Lic: 5, Maestría: 10, Doctorado: 15)
    
    # Instituciones de Formación (ponderación por conteo simple)
    puntaje += min(resultados['instituciones_formacion'] * 3, 10) # Hasta 10 puntos por instituciones

    # Palabras Positivas (ajustando)
    puntaje += min(resultados['palabras_positivas'] * 4, 15) # Más peso a palabras positivas
    
    # Penalización por Palabras de Riesgo (ajustando penalización)
    puntaje -= resultados['palabras_riesgo'] * 5 # Mayor penalización por palabras de riesgo
    
    # Asegurar que el puntaje no sea negativo
    puntaje = max(0, puntaje)

    # Clasificación (ajustando umbrales)
    if resultados['palabras_riesgo'] > 2:
        clasificacion = "No Apto" # Más de 2 palabras de riesgo lo marca como No Apto
    elif puntaje >= 80 and resultados['palabras_riesgo'] == 0:
        clasificacion = "Apto"
    elif puntaje >= 60 and resultados['palabras_riesgo'] <= 2:
        clasificacion = "Observado"
    else:
        clasificacion = "No Apto"
    
    return {
        'puntaje_total': round(puntaje, 2), # Redondear puntaje
        'clasificacion': clasificacion
    }

def analizar_candidatos(datos):
    """
    Analiza los datos de los candidatos y muestra un resumen.
    
    Args:
        datos (dict): Diccionario con los datos de cada tipo de candidato
    """
    print("\n=== ANÁLISIS DE CANDIDATOS ===\n")
    
    resultados_totales = []
    
    for tipo_candidato, df in datos.items():
        print(f"\nAnalizando {tipo_candidato}...")
        
        columnas_disponibles = df.columns.tolist()
        print(f"Columnas disponibles en {tipo_candidato}: {columnas_disponibles}")

        # Intentar identificar las columnas de Nombre y URL de forma flexible
        nombre_col = None
        url_col = None

        # Buscar columna de nombre
        for col in columnas_disponibles:
            if 'persona' in col.lower() or 'nombre' in col.lower():
                nombre_col = col
                break # Tomar la primera coincidencia

        # Buscar columna de URL
        for col in columnas_disponibles:
            # Verificar si el nombre de la columna contiene 'url' o 'curriculum' o si alguna celda en las primeras filas contiene 'http'
            if 'url' in col.lower() or 'curriculum' in col.lower() or (df[col].head().astype(str).str.startswith('http')).any():
                 url_col = col
                 break # Tomar la primera coincidencia

        if not nombre_col or not url_col:
            print(f"Error: No se pudieron identificar las columnas 'Nombre' o 'URL' en {tipo_candidato}")
            print(f"Columnas esperadas: una columna para el nombre (ej. 'Persona C') y una columna con URLs (ej. 'Curriculum' o similar)")
            continue

        print(f"Columna de Nombre identificada: '{nombre_col}'")
        print(f"Columna de URL identificada: '{url_col}'")
        
        # Mostrar primeros registros para verificar datos
        print("\nPrimeros registros para verificación:")
        try:
            print(df[[nombre_col, url_col]].head().to_string())
        except KeyError as e:
            print(f"Error al mostrar primeros registros: Columna no encontrada {e}. Columnas disponibles: {columnas_disponibles}")
            continue
        
        total_candidatos_tipo = len(df)
        candidatos_procesados_tipo = 0

        for index, row in df.iterrows():
            nombre = row.get(nombre_col, 'N/A')
            url = row.get(url_col, '')
            
            # print(f"DEBUG: Procesando fila {index} - Nombre: {nombre}, URL: {url}") # Debug print

            if not url or not isinstance(url, str) or not url.startswith('http'):
                # print(f"Advertencia: URL inválida o faltante para el candidato {nombre} (fila {index}) - {url}")
                continue
            
            # print(f"\nProcesando candidato: {nombre} de {tipo_candidato}")
            # print(f"URL: {url}")
            
            # Descargar y analizar PDF
            texto = descargar_pdf(url, nombre)
            if texto:
                # Analizar experiencia
                resultados = analizar_experiencia(texto)
                
                # Calcular puntaje
                puntaje = calcular_puntaje(resultados)
                
                # Agregar resultados
                resultados_totales.append({
                    'Tipo': tipo_candidato,
                    'Nombre': nombre,
                    'Puntaje Total': puntaje['puntaje_total'],
                    'Clasificación': puntaje['clasificacion'],
                    'Puntaje Experiencia Judicial': resultados['experiencia_judicial'] * 6, # Ajustar según la lógica de puntaje real si es diferente
                    'Puntaje Experiencia Docente': resultados['experiencia_docente'] * 3, # Ajustar
                    'Puntaje Experiencia Investigación': resultados['experiencia_investigacion'] * 4, # Ajustar
                    'Puntaje Experiencia Administrativa': resultados['experiencia_administrativa'] * 2, # Ajustar
                    'Puntaje Años de Experiencia': resultados['años_experiencia'] * 2.5, # Ajustar
                    'Puntaje Formación Académica': resultados['formacion_academica'] * 5, # Ajustar
                    'Puntaje Instituciones': resultados['instituciones_formacion'] * 3, # Ajustar
                    'Puntaje Palabras Positivas': resultados['palabras_positivas'] * 4, # Ajustar
                    'Puntaje Palabras Riesgo': resultados['palabras_riesgo'] * -5, # Ajustar
                    'Conteo Palabras Riesgo': resultados['palabras_riesgo'],
                    'Conteo Palabras Positivas': resultados['palabras_positivas'],
                    'Palabras Riesgo': resultados['palabras_riesgo'] # Mantener columna original de conteo de riesgo
                })
                
                print(f" -> {nombre}: Puntaje={puntaje['puntaje_total']}, Clasificación={puntaje['clasificacion']}")
                candidatos_procesados_tipo += 1

            else:
                # print(f"Error: No se pudo procesar el PDF para {nombre} (fila {index})")
                pass # Continuar con el siguiente candidato si falla la descarga o procesamiento del PDF

        print(f"\nTerminado análisis de {tipo_candidato}. Candidatos procesados: {candidatos_procesados_tipo}/{total_candidatos_tipo}")

    if not resultados_totales:
        print("\nNo se pudo analizar ningún candidato. Esto puede deberse a:")
        print("1. Los archivos Excel no tienen las columnas correctas para Nombre y URL.")
        print("2. Las URLs en los archivos no son válidas o no se pudo acceder a ellas.")
        print("3. No se pudo descargar o leer el contenido de los PDFs.")
        return
    
    # Crear DataFrame con resultados
    df_resultados = pd.DataFrame(resultados_totales)
    
    # Guardar resultados
    carpeta_resultados = os.path.join('data', 'resultados')
    os.makedirs(carpeta_resultados, exist_ok=True)
    
    fecha = datetime.now().strftime('%Y%m%d_%H%M%S')
    archivo_resultados = os.path.join(carpeta_resultados, f'resultados_{fecha}.xlsx')
    
    try:
        df_resultados.to_excel(archivo_resultados, index=False)
        print(f"\n Resultados guardados exitosamente en: {archivo_resultados}")
    except Exception as e:
        print(f"Error al guardar el archivo de resultados {archivo_resultados}: {str(e)}")

    
    # Mostrar resumen
    print("\n=== RESUMEN DE RESULTADOS ===")
    print(f"\nTotal de candidatos analizados con éxito: {len(resultados_totales)}")
    
    if len(resultados_totales) > 0:
        print("\nClasificación por tipo:")
        try:
            print(df_resultados.groupby(['Tipo', 'Clasificación']).size().unstack(fill_value=0))
        except KeyError as e:
            print(f"Error al generar resumen por tipo: {e}")
            print("Asegúrate de que la columna 'Tipo' y 'Clasificación' existan en los resultados.")
    else:
        print("No hay resultados para mostrar en el resumen.")

def main():
    """Función principal para ejecutar el evaluador."""
    # Definir la estructura de directorios necesaria
    directorios = {
        RAW_DATA_DIR: "Datos sin procesar",
        PROCESSED_DATA_DIR: "Datos procesados",
        PDF_DIR: "Archivos PDF descargados",
        RESULTS_DIR: "Resultados del análisis",
        LOGS_DIR: "Archivos de registro"
    }
    
    crear_estructura_directorios(directorios) # Asegurar que los directorios existan
    log_file = os.path.join(LOG_DIR, "evaluador.log")
    configurar_logging(log_file) # Configurar logging

    # Iterar sobre las secciones y procesar cada una
    for seccion, archivo_entrada in archivos_entrada.items():
        archivo_salida = archivos_salida.get(seccion)
        if not archivo_salida:
            print(f"Advertencia: No se encontró archivo de salida para la sección {seccion}")
            continue

        # Llamar a la función procesar_seccion para cada sección
        procesar_seccion(seccion, os.path.join(BASE_DIR, archivo_entrada), os.path.join(BASE_DIR, archivo_salida), log_file)

if __name__ == "__main__":
    main() 