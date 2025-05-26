"""
Módulo para análisis de lenguaje natural de los CVs.
Utiliza spaCy y NLTK para análisis semántico y de sentimiento.
"""

import spacy
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re
from collections import Counter
from textblob import TextBlob
import logging

# Descargar recursos necesarios de NLTK antes de cargar el modelo spaCy o inicializar la clase
try:
    # Intentar descargar 'punkt' sin el argumento language
    nltk.download('punkt', quiet=True)
except LookupError:
    # Si falla la descarga general
    print("Advertencia: No se pudo descargar el recurso 'punkt' de NLTK.")

try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

try:
    nltk.data.find('averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger', quiet=True)

try:
    nltk.data.find('wordnet')
except LookupError:
    nltk.download('wordnet', quiet=True)

# Cargar modelo de spaCy
try:
    nlp = spacy.load("es_core_news_sm")
except OSError:
    print("Descargando modelo de spaCy...")
    spacy.cli.download("es_core_news_sm")
    nlp = spacy.load("es_core_news_sm")

class NLPAnalyzer:
    def __init__(self):
        """Inicializa el analizador NLP."""
        self.sia = SentimentIntensityAnalyzer()
        self.stop_words = set(stopwords.words('spanish'))
        
        # Ya intentamos descargar los recursos al inicio del script,
        # pero aseguramos la carga del modelo de spaCy aquí también.
        try:
            self.nlp = spacy.load('es_core_news_sm')
        except OSError:
            # Si el modelo no está instalado, descargarlo
            print("Descargando modelo de spaCy en __init__...")
            spacy.cli.download('es_core_news_sm')
            self.nlp = spacy.load('es_core_news_sm')
        
    def analizar_texto(self, texto):
        """
        Realiza un análisis completo del texto usando NLP.
        
        Args:
            texto (str): Texto a analizar
            
        Returns:
            dict: Resultados del análisis
        """
        # Limpiar y preprocesar texto
        texto_limpio = self._limpiar_texto(texto)
        
        # Análisis con spaCy
        doc = self.nlp(texto_limpio)
        
        # Extraer entidades
        entidades = self._extraer_entidades(doc)
        
        # Análisis de sentimiento
        # Especificamos el idioma español para sent_tokenize
        sentimiento = self._analizar_sentimiento(texto_limpio)
        
        # Análisis de experiencia
        experiencia = self._analizar_experiencia(doc)
        
        # Análisis de formación
        formacion = self._analizar_formacion(doc)
        
        # Análisis de competencias
        competencias = self._analizar_competencias(doc)
        
        return {
            'entidades': entidades,
            'sentimiento': sentimiento,
            'experiencia': experiencia,
            'formacion': formacion,
            'competencias': competencias,
            'calidad_texto': self._evaluar_calidad_texto(doc)
        }
    
    def _limpiar_texto(self, texto):
        """Limpia y normaliza el texto."""
        # Convertir a minúsculas
        texto = texto.lower()
        
        # Eliminar caracteres especiales y números
        texto = re.sub(r'[^\w\s]', ' ', texto)
        texto = re.sub(r'\d+', '', texto)
        
        # Eliminar espacios múltiples
        texto = re.sub(r'\s+', ' ', texto).strip()
        
        return texto
    
    def _extraer_entidades(self, doc):
        """Extrae entidades nombradas del texto."""
        entidades = {
            'organizaciones': [],
            'personas': [],
            'lugares': [],
            'fechas': [],
            'otros': []
        }
        
        for ent in doc.ents:
            if ent.label_ == 'ORG':
                entidades['organizaciones'].append(ent.text)
            elif ent.label_ == 'PER':
                entidades['personas'].append(ent.text)
            elif ent.label_ == 'LOC':
                entidades['lugares'].append(ent.text)
            elif ent.label_ == 'DATE':
                entidades['fechas'].append(ent.text)
            else:
                entidades['otros'].append(ent.text)
        
        return entidades
    
    def _analizar_sentimiento(self, texto):
        """Analiza el sentimiento general del texto."""
        scores = self.sia.polarity_scores(texto)
        
        # Analizar sentimiento por oraciones
        # Especificamos el idioma 'spanish' aquí
        try:
            oraciones = nltk.sent_tokenize(texto, language='spanish')
            sentimientos_oraciones = [self.sia.polarity_scores(oracion) for oracion in oraciones]
        except LookupError as e:
            logging.error(f"LookupError al tokenizar oraciones en español: {e}")
            logging.error(f"Texto que causó el error (primeras 500 chars): {texto[:500]}...")
            oraciones = [texto] # Tratar todo el texto como una sola oración para evitar fallar
            sentimientos_oraciones = [self.sia.polarity_scores(texto)] # Analizar sentimiento del texto completo
        except Exception as e:
            logging.error(f"Error inesperado al tokenizar oraciones: {e}")
            logging.error(f"Texto que causó el error (primeras 500 chars): {texto[:500]}...")
            oraciones = [texto] # Tratar todo el texto como una sola oración
            sentimientos_oraciones = [self.sia.polarity_scores(texto)] # Analizar sentimiento del texto completo
        
        return {
            'general': scores,
            'por_oracion': sentimientos_oraciones
        }
    
    def _analizar_experiencia(self, doc):
        """Analiza la experiencia mencionada en el texto."""
        experiencia = {
            'años': 0,
            'cargos': [],
            'instituciones': [],
            'logros': []
        }
        
        # Buscar patrones de años de experiencia
        patrones_años = [
            r'(\d+)\s*años?\s*de\s*experiencia',
            r'experiencia\s*de\s*(\d+)\s*años?',
            r'(\d+)\s*años?\s*en\s*el\s*cargo'
        ]
        
        for patron in patrones_años:
            matches = re.finditer(patron, doc.text)
            for match in matches:
                experiencia['años'] = max(experiencia['años'], int(match.group(1)))
        
        # Extraer cargos e instituciones
        for ent in doc.ents:
            if ent.label_ == 'ORG':
                experiencia['instituciones'].append(ent.text)
        
        # Identificar logros
        for sent in doc.sents:
            if any(palabra in sent.text.lower() for palabra in ['logro', 'conseguí', 'alcanzado', 'obtenido']):
                experiencia['logros'].append(sent.text)
        
        return experiencia
    
    def _analizar_formacion(self, doc):
        """Analiza la formación académica mencionada en el texto."""
        formacion = {
            'grados': [],
            'instituciones': [],
            'especialidades': []
        }
        
        # Patrones de grados académicos
        patrones_grados = {
            'doctorado': r'doctorado|doctora?|ph\.d\.?',
            'maestría': r'maestría|maestro|maestra|m\.a\.?',
            'licenciatura': r'licenciatura|licenciado|licenciada|lic\.',
            'especialidad': r'especialidad|especialista'
        }
        
        for grado, patron in patrones_grados.items():
            if re.search(patron, doc.text.lower()):
                formacion['grados'].append(grado)
        
        # Extraer instituciones educativas
        for ent in doc.ents:
            if ent.label_ == 'ORG' and any(palabra in ent.text.lower() for palabra in ['universidad', 'instituto', 'escuela']):
                formacion['instituciones'].append(ent.text)
        
        return formacion
    
    def _analizar_competencias(self, doc):
        """Analiza las competencias y habilidades mencionadas en el texto."""
        competencias = {
            'técnicas': [],
            'blandas': [],
            'idiomas': []
        }
        
        # Patrones de competencias
        patrones = {
            'técnicas': r'programación|análisis|diseño|desarrollo|implementación|gestión',
            'blandas': r'liderazgo|trabajo en equipo|comunicación|resolución de problemas',
            'idiomas': r'inglés|español|francés|alemán|italiano|portugués'
        }
        
        for tipo, patron in patrones.items():
            matches = re.finditer(patron, doc.text.lower())
            for match in matches:
                competencias[tipo].append(match.group())
        
        return competencias
    
    def _evaluar_calidad_texto(self, doc):
        """Evalúa la calidad general del texto."""
        # Calcular métricas básicas
        num_palabras = len([token for token in doc if not token.is_punct])
        num_oraciones = len(list(doc.sents))
        
        # Calcular diversidad léxica
        palabras = [token.text.lower() for token in doc if not token.is_punct and not token.is_stop]
        diversidad_lexica = len(set(palabras)) / len(palabras) if palabras else 0
        
        # Evaluar estructura
        estructura = {
            'longitud': 'adecuada' if 100 <= num_palabras <= 2000 else 'inadecuada',
            'complejidad': 'alta' if diversidad_lexica > 0.6 else 'media' if diversidad_lexica > 0.4 else 'baja',
            'coherencia': 'alta' if num_oraciones > 5 else 'baja'
        }
        
        return estructura 