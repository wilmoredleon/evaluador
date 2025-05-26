# Evaluador de Candidatos al Poder Judicial

Este programa analiza los perfiles de los candidatos al Poder Judicial en México, evaluando su experiencia, trayectoria y posibles riesgos.

## Instrucciones de Preparación

### 1. Obtención de Datos
1. Visitar la página "Conóceles" del INE:
   - Abrir el navegador web
   - Ir a: https://candidaturaspoderjudicial.ine.mx/16/1011

### 2. Identificación de Entidad y Sección Electoral
1. Consultar tu entidad y sección electoral:
   - Visitar la página del INE: https://www.ine.mx/
   - Buscar la sección "Consulta tu credencial"
   - Ingresar los datos solicitados para obtener tu entidad y sección electoral

### 3. Descarga de Archivos
1. En la página "Conóceles":
   - Seleccionar tu entidad federativa
   - Seleccionar tu sección electoral
   - Ir a la sección de resultados
   - Descargar los archivos de candidaturas disponibles

### 4. Preparación de Archivos
1. Crear una carpeta llamada `data` en el directorio del programa
2. Dentro de `data`, crear una subcarpeta llamada `raw`
3. Colocar todos los archivos descargados en la carpeta `data/raw`
   - Los archivos deben tener formato Excel (.xlsx)
   - No modificar los nombres de los archivos

## Instrucciones de Ejecución

### Requisitos Previos
1. Tener instalado Python 3.8 o superior
2. Tener instalado pip (gestor de paquetes de Python)

### Instalación de Dependencias
1. Abrir una terminal o línea de comandos
2. Navegar hasta el directorio del programa
3. Ejecutar el siguiente comando:
   ```
   pip install -r requirements.txt
   ```

### Ejecución del Programa
1. Abrir una terminal o línea de comandos
2. Navegar hasta el directorio del programa
3. Ejecutar el siguiente comando:
   ```
   python evaluador_ine.py
   ```

## Estructura de Carpetas
```
evaluador_ine/
│
├── data/
│   └── raw/           # Carpeta para los archivos Excel descargados
│
├── evaluador_ine.py   # Programa principal
├── requirements.txt   # Dependencias del programa
└── README.md         # Este archivo
```

## Notas Importantes
- No modificar los nombres de los archivos descargados
- Asegurarse de que todos los archivos estén en formato Excel (.xlsx)
- Si se presenta algún error, verificar que:
  - Los archivos estén en la carpeta correcta
  - Los nombres de los archivos no hayan sido modificados
  - Se tengan todos los permisos necesarios en la carpeta

## Soporte
Si encuentras algún problema o tienes dudas, por favor:
1. Revisar que hayas seguido todos los pasos correctamente
2. Verificar que los archivos estén en el formato correcto
3. Asegurarte de tener todas las dependencias instaladas 