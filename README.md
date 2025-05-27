# Evaluador de Perfiles Judiciales

**Sistema de evaluación automatizada de candidatos judiciales.**

Este proyecto permite analizar perfiles de candidatos a cargos en el Poder Judicial mediante un sistema automatizado que evalúa criterios como experiencia, formación académica y desempeño profesional, clasificando a los candidatos como **Apto**, **Observado** o **No Apto**.

---

## 🧠 ¿Qué hace esta herramienta?

El **Evaluador de Perfiles Judiciales** permite:

- Analizar automáticamente perfiles de candidatos.
- Evaluar con base en múltiples criterios como experiencia judicial, formación docente, investigación, calidad de redacción, etc.
- Generar informes detallados y exportables.
- Clasificar a los candidatos con criterios objetivos y transparentes.

---

## 🛠 Instrucciones de uso

### Paso 1: Obtener los datos
1. Visita [candidaturaspoderjudicial.ine.mx](https://candidaturaspoderjudicial.ine.mx/)
2. Navega a la sección de candidatos judiciales.
3. Descarga las listas perfiles en xlsx.
4. Asegúrate de que el archivo Excel contiene los campos requeridos.

Tu archivo debe contener al menos las siguientes columnas:

- `Poder` (Ej. Judicial, Electoral)
- `Nombre del candidato`
- `URL del PDF del perfil`

### Paso 2: Procesar los datos
1. Coloca el archivo Excel y los PDFs descargados en la carpeta `data/raw/`.
2. Ejecuta el siguiente comando desde la raíz del proyecto:

   ```bash
   python evaluador_ine.py
   ```

3. Los resultados se generarán automáticamente en la carpeta `output/resultados/`.

---

## ⚙️ Instalación técnica

### Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Configuración del entorno

1. Clona el repositorio:

   ```bash
   git clone https://github.com/tu_usuario/evaluador-perfiles-judiciales.git
   cd evaluador-perfiles-judiciales
   ```

2. (Opcional pero recomendado) Crea un entorno virtual:

   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

---

## ⚠️ Advertencias importantes

> Esta herramienta es un prototipo de uso personal, creada con fines informativos y educativos.
> **NO** debe ser usada como única fuente de evaluación para decisiones institucionales o legales.

- Los resultados son generados automáticamente mediante **criterios programados por el desarrollador**.
- No garantiza exactitud ni exhaustividad en los datos o puntuaciones presentadas.
- El análisis realizado **no es oficial** ni tiene validez jurídica.
- Se recomienda encarecidamente realizar una **evaluación personal**, crítica y complementaria de los perfiles.
- **El uso de esta herramienta es bajo tu propia responsabilidad.**

> Al utilizar este sistema, aceptas que los resultados presentados son únicamente de carácter informativo y no constituyen una evaluación definitiva ni autorizada.

---

## 📦 Tecnologías utilizadas

- **Python**

---

## 📄 Licencia

Este proyecto es de código abierto y se ofrece bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.

---

## 🤝 Contribuciones

Si deseas colaborar, mejorar el sistema o sugerir mejoras en los criterios de evaluación, ¡son bienvenidas las contribuciones!

---