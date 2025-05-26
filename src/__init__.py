"""
Paquete src para el evaluador de perfiles judiciales.
"""

from .evaluador import (
    analizar_experiencia,
    calcular_puntaje,
    evaluar_aptitud,
    procesar_seccion
)

from .utils import (
    extraer_años_experiencia,
    analizar_formacion,
    configurar_logging,
    mostrar_banner,
    crear_estructura_directorios,
    mover_archivos_existentes
)

from .config import (
    experiencia_judicial,
    experiencia_administrativa,
    experiencia_docente,
    experiencia_investigacion,
    palabras_riesgo,
    palabras_positivas,
    archivos_entrada,
    archivos_salida,
    BASE_DIR,
    LOG_DIR
) 