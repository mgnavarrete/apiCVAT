
# Sincronización de CVAT con Plataforma Antenas de ADENTU

Este script tiene como objetivo automatizar tareas relacionadas con el servicio de anotación y almacenamiento en la nube de CVAT y AWS S3. El programa puede crear nuevas tareas en CVAT, obtener datos relacionados con esas tareas, y subir archivos y resultados a un bucket de Amazon S3. El script admite dos procesos diferentes, definidos por el argumento `proceso`: `new_task` y `get_data`.

- `new_task`: Crea una nueva tarea en el servidor CVAT con el nombre proporcionado. (Falta por implementar)
- `get_data`: Obtiene datos de la tarea existente y los sube a un bucket de Amazon S3.

## Dependencias

El script usa varias bibliotecas, como `os`, `argparse`, `tqdm`, `boto3`, y funciones auxiliares del módulo `ultis.functions`. Es importante asegurarse de que todas las dependencias estén instaladas antes de ejecutar el script para evitar errores de importación o fallas en la conexión a los servicios.

Puedes instalar todas las dependencias ejecutando:
```bash
pip install -r requirements.txt
```

## Instrucciones para Ejecutar el Script

1. **Instalar Dependencias**: Asegúrate de tener Python instalado. Instala las dependencias mencionadas anteriormente.

2. **Ejecutar el Script**:
   - Para crear una nueva tarea en CVAT, ejecuta:
     ```bash
     python3 main.py new_task [task_name]
     ```
     Donde `[task_name]` es el nombre de la tarea a crear.

   - Para obtener los labels, las imágenes con bounding box, el json del reporte de una tarea existente y subirlos a AWS S3, ejecuta:
     ```bash
     python3 main.py get_data [task_name]
     ```
     Donde `[task_name]` es el nombre de la tarea existente.

   - `[task_name]` tiene un fromato definido el cual debe ser:
   ```bash
     ID_Levantamiento-ID_Medición
     ```
   - Ejemplo de ejecucion para el levantamient 11 y la medición 15:
   ```bash
     python3 main.py new_task 11-15
     python3 main.py get_data 11-15
     ```
     
3. **Importancia de las Credenciales**:
   Asegúrate de tener credenciales válidas para CVAT y AWS S3. El script necesita información como el ID de acceso, la clave secreta y el nombre del bucket para interactuar con estos servicios.

4. **Advertencias**:

## Configuración del Archivo .env

Antes de ejecutar el script, asegúrate de tener un archivo `.env` con las siguientes variables configuradas:
```bash
# Parámetros de conexión con S3
AWS_ACCESS_KEY_ID = 'AWS_ACCESS_KEY_ID'
AWS_SECRET_ACCESS_KEY = 'AWS_SECRET_ACCESS_KEY'
AWS_DEFAULT_REGION = 'AWS_DEFAULT_REGION'
AWS_BUCKET = 'AWS_BUCKET'

# Parámetros de conexión con CVAT
CVAT_HOST = 'CVAT_HOST'
CVAT_USERNAME = 'CVAT_USERNAME'
CVAT_PASSWORD = 'CVAT_PASSWORD'
```

Asegúrate de que el archivo `.env` esté en el mismo directorio que el script y que las credenciales sean correctas antes de ejecutar el script.
   - Asegúrate de tener los permisos adecuados para crear tareas en CVAT y subir datos a AWS S3.
   - La manipulación incorrecta de datos puede resultar en la pérdida de información o problemas de seguridad.
