"""
Configuración del evaluador de perfiles judiciales.
Contiene las palabras clave y rutas utilizadas en el análisis.
"""

# Palabras clave para experiencia judicial
experiencia_judicial = [
    # Funciones jurisdiccionales
    "juez", "magistrado", "tribunal", "juzgado", "sala", "pleno",
    "ministro", "magistrado", "juez de distrito", "juez de circuito",
    
    # Tipos de resoluciones
    "sentencia", "resolución", "acuerdo", "auto", "decreto",
    "providencia", "dictamen", "fallo", "laudo",
    
    # Procesos judiciales
    "proceso judicial", "audiencia", "vista", "juicio", "litigio",
    "controversia", "recurso", "amparo", "apelación", "revisión",
    
    # Materias jurisdiccionales
    "penal", "civil", "familiar", "mercantil", "laboral",
    "administrativo", "constitucional", "fiscal", "electoral",
    
    # Funciones específicas
    "impartición de justicia", "ejercicio de la judicatura",
    "carrera judicial", "especialización judicial",
    "actualización judicial", "desarrollo jurisprudencial",
    "técnica jurisdiccional", "razonamiento jurídico",
    "argumentación jurídica", "interpretación constitucional",
    "control de convencionalidad", "garantías procesales",
    "debido proceso", "independencia judicial",
    "autonomía judicial"
]

# Palabras clave para experiencia administrativa
experiencia_administrativa = [
    # Roles administrativos
    "director", "coordinador", "asesor", "consultor",
    "secretario", "subdirector", "jefe de departamento",
    "encargado de área", "supervisor", "gerente",
    
    # Gestión judicial
    "gestión judicial", "administración de tribunales",
    "coordinación jurisdiccional", "planeación judicial",
    "presupuesto judicial", "recursos humanos judiciales",
    "tecnologías de la información judicial",
    "estadística judicial", "transparencia judicial",
    
    # Proyectos y programas
    "proyecto", "programa", "iniciativa", "plan",
    "estrategia", "política", "protocolo", "procedimiento",
    
    # Evaluación y control
    "evaluación", "control", "seguimiento", "monitoreo",
    "auditoría", "supervisión", "verificación", "inspección"
]

# Palabras clave para experiencia docente
experiencia_docente = [
    # Roles docentes
    "profesor", "catedrático", "docente", "instructor",
    "facilitador", "tutor", "asesor académico",
    
    # Niveles de docencia
    "profesor titular", "profesor asociado", "profesor adjunto",
    "profesor invitado", "profesor emérito",
    
    # Tipos de cursos
    "asignatura", "materia", "curso", "seminario", "taller",
    "diplomado", "especialidad", "maestría", "doctorado",
    "posgrado", "pregrado", "licenciatura",
    
    # Formación judicial
    "formación judicial", "capacitación judicial",
    "actualización judicial", "especialización judicial",
    "formación continua", "desarrollo profesional",
    
    # Métodos de enseñanza
    "impartir", "enseñanza", "educación", "formación",
    "capacitación", "actualización", "especialización",
    "tutoría", "asesoría", "mentoría"
]

# Palabras clave para investigación
experiencia_investigacion = [
    # Roles de investigación
    "investigador", "investigador principal", "co-investigador",
    "colaborador de investigación", "asistente de investigación",
    
    # Tipos de publicaciones
    "publicación", "artículo", "libro", "capítulo", "revista",
    "ponencia", "congreso", "seminario", "conferencia",
    "memoria", "compilación", "antología",
    
    # Proyectos de investigación
    "proyecto", "estudio", "análisis", "investigación",
    "trabajo de investigación", "tesis", "disertación",
    
    # Calidad de publicaciones
    "revista indexada", "revista arbitrada", "revista científica",
    "publicación arbitrada", "publicación científica",
    "publicación especializada", "publicación académica",
    
    # Métodos de investigación
    "metodología", "método", "técnica", "instrumento",
    "análisis", "estudio", "investigación", "exploración"
]

# Palabras clave de riesgo
palabras_riesgo = [
    # Experiencia política y partidista
    "asesor legislativo", "asesor político", "coordinador de campaña", 
    "delegado partidista", "militante", "secretario particular", 
    "candidato a", "diputado", "senador", "presidente municipal",
    "vínculo con", "designado por", "propuesto por", 
    "nombrado por el ejecutivo", "representante de partido",
    "cargos de confianza", "cargos políticos", 
    "encargado del despacho", "encargado interino",
    "sin trayectoria judicial", "sin experiencia jurisdiccional",
    # Términos adicionales
    "partido político", "militancia", "campaña electoral",
    "gabinete", "asamblea legislativa", "congreso",
    "cargo de elección popular", "cargo público electivo",
    "función pública no jurisdiccional", "actividad política",
    "cargo de confianza política", "designación política"
]

# Palabras clave positivas
palabras_positivas = [
    # Experiencia jurisdiccional
    "impartición de justicia", "tribunal", "juez", "magistrado",
    "sentencias emitidas", "resoluciones", "jurisprudencia", 
    "capacitación judicial", "ética judicial", "imparcialidad",
    "derechos humanos", "transparencia", "igualdad de género", 
    "perspectiva de género", "acceso a la justicia", 
    "servicio público", "formación continua", "pueblos originarios",
    # Términos adicionales
    "función jurisdiccional", "actividad jurisdiccional",
    "ejercicio de la judicatura", "carrera judicial",
    "especialización judicial", "actualización judicial",
    "desarrollo jurisprudencial", "técnica jurisdiccional",
    "razonamiento jurídico", "argumentación jurídica",
    "interpretación constitucional", "control de convencionalidad",
    "garantías procesales", "debido proceso",
    "independencia judicial", "autonomía judicial",
    "formación judicial", "actualización profesional",
    "desarrollo profesional", "excelencia judicial"
]

# Configuración de rutas
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, "src")
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# Rutas de datos
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")

# Rutas de salida
PDF_DIR = os.path.join(OUTPUT_DIR, "pdfs")
RESULTS_DIR = os.path.join(OUTPUT_DIR, "resultados")
LOGS_DIR = os.path.join(OUTPUT_DIR, "logs")
LOG_DIR = LOGS_DIR  # Alias para mantener compatibilidad

# Configuración de archivos
archivos_entrada = {
    "SCJN": os.path.join(RAW_DATA_DIR, "Candidatos_MSCJN"),
    "TDJ": os.path.join(RAW_DATA_DIR, "Candidatos_MTDJ"),
    "SALA_SUPERIOR": os.path.join(RAW_DATA_DIR, "Candidatos_MSSTEPJF"),
    "SALA_REGIONAL": os.path.join(RAW_DATA_DIR, "Candidatos_MSRTEPJF"),
    "CIRCUITO": os.path.join(RAW_DATA_DIR, "Candidatos_MC"),
    "DISTRITO": os.path.join(RAW_DATA_DIR, "Candidatos_JD")
}

archivos_salida = {
    "SCJN": os.path.join(RESULTS_DIR, "resultados_ministros_scjn.csv"),
    "TDJ": os.path.join(RESULTS_DIR, "resultados_magistrados_tdj.csv"),
    "SALA_SUPERIOR": os.path.join(RESULTS_DIR, "resultados_sala_superior.csv"),
    "SALA_REGIONAL": os.path.join(RESULTS_DIR, "resultados_sala_regional.csv"),
    "CIRCUITO": os.path.join(RESULTS_DIR, "resultados_magistrados_circuito.csv"),
    "DISTRITO": os.path.join(RESULTS_DIR, "resultados_jueces_distrito.csv")
} 