# Evaluador de Perfiles Judiciales

Este proyecto es un sistema automatizado para evaluar perfiles de candidatos judiciales, analizando su experiencia, formación académica y otros criterios relevantes.

## Requisitos del Sistema

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Conexión a internet para descargar los PDFs de los candidatos

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/tu-usuario/evaluador_ine.git
cd evaluador_ine
```

2. Crear un entorno virtual (recomendado):
```bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate
```

3. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

## Estructura del Proyecto

```
evaluador_ine/
├── src/
│   ├── evaluador.py      # Lógica principal de evaluación
│   ├── config.py         # Configuración y constantes
│   ├── nlp_analyzer.py   # Análisis de texto y NLP
│   └── utils.py          # Utilidades generales
├── input/                # Archivos Excel de entrada
├── output/
│   ├── pdfs/            # PDFs descargados de los candidatos
│   ├── resultados/      # Resultados de la evaluación
│   └── logs/            # Registros de ejecución
└── requirements.txt      # Dependencias del proyecto
```

## Uso

1. Preparar los archivos de entrada:
   - Colocar los archivos Excel con los datos de los candidatos en la carpeta `input/`
   - El Excel debe tener las columnas: "Poder", "Nombre" y "URL" (del PDF)

2. Ejecutar el evaluador:
```bash
python -m src.evaluador
```

3. Los resultados se guardarán en:
   - `output/resultados/resultados.xlsx`: Archivo Excel con múltiples hojas, una por cada sección evaluada
   - `output/logs/evaluador.log`: Registro detallado de la ejecución

## Criterios de Evaluación

### Clasificación de Candidatos

1. **Apto**
   - Doctorado
   - ≥ 8 años de experiencia judicial
   - 0 palabras de riesgo

2. **Observado**
   - Maestría o Doctorado
   - ≥ 5 años de experiencia judicial
   - 0 palabras de riesgo

3. **No Apto**
   - No cumple con los criterios anteriores

### Sistema de Puntuación

El sistema asigna puntos en las siguientes categorías:

- **Experiencia Judicial** (máx. 30 puntos)
  - 3.0 puntos por cada mención relevante

- **Experiencia Docente** (máx. 20 puntos)
  - 2.0 puntos por cada mención relevante

- **Experiencia en Investigación** (máx. 15 puntos)
  - 1.5 puntos por cada mención relevante

- **Experiencia Administrativa** (máx. 10 puntos)
  - 1.0 punto por cada mención relevante

- **Años de Experiencia** (máx. 20 puntos)
  - 2.0 puntos por año (máx. 10 años)

- **Formación Académica**
  - Doctorado: 20 puntos
  - Maestría: 15 puntos
  - Licenciatura: 10 puntos
  - Especialidad: 5 puntos

- **Instituciones de Formación** (máx. 10 puntos)
  - 2 puntos por institución

- **Palabras Positivas** (máx. 15 puntos)
  - 1.5 puntos por palabra positiva

- **Palabras de Riesgo** (penalización)
  - -2.0 puntos por palabra de riesgo

- **Calidad del Texto** (máx. 20 puntos)
  - Basado en longitud, complejidad y coherencia

## Interpretación de Resultados

El archivo Excel de resultados contiene las siguientes columnas:

- **Poder**: Poder judicial al que pertenece el candidato
- **Nombre**: Nombre del candidato
- **URL**: Enlace al PDF del candidato
- **Puntaje Total**: Puntaje final (0-100)
- **Aptitud**: Clasificación final (Apto/Observado/No Apto)
- **Puntaje Judicial**: Puntos por experiencia judicial
- **Puntaje Docente**: Puntos por experiencia docente
- **Puntaje Investigación**: Puntos por experiencia en investigación
- **Puntaje Administrativa**: Puntos por experiencia administrativa
- **Puntaje Años**: Puntos por años de experiencia
- **Puntaje Formación**: Puntos por nivel de formación
- **Puntaje Instituciones**: Puntos por instituciones de formación
- **Puntaje Positivas**: Puntos por palabras positivas
- **Puntaje Riesgos**: Penalización por palabras de riesgo
- **Puntaje Calidad**: Puntos por calidad del texto
- **Conteo Palabras Riesgo**: Número de palabras de riesgo encontradas
- **Conteo Palabras Positivas**: Número de palabras positivas encontradas
- **Redes Sociales**: Indica si se detectaron redes sociales en el perfil

## Solución de Problemas

1. **Error al descargar PDFs**
   - Verificar la conexión a internet
   - Comprobar que las URLs en el Excel sean válidas
   - Revisar los permisos de escritura en la carpeta output/pdfs

2. **Error al procesar archivos Excel**
   - Asegurar que los archivos Excel tengan el formato correcto
   - Verificar que las columnas requeridas estén presentes
   - Comprobar que no haya caracteres especiales en los nombres

3. **Error al guardar resultados**
   - Verificar que el archivo Excel de resultados no esté abierto
   - Comprobar los permisos de escritura en la carpeta output/resultados

## Contribuir

Las contribuciones son bienvenidas. Por favor, sigue estos pasos:

1. Haz un fork del repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Haz commit de tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles. 