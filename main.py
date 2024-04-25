import os
from ultis.functions import *
from time import sleep
from tqdm import tqdm
import boto3
from botocore.exceptions import NoCredentialsError
import argparse
import json
from dotenv import load_dotenv

# Crea un objeto ArgumentParser para definir argumentos y opciones para tu script
parser = argparse.ArgumentParser(description='Ejecutar script con un argumento de línea de comandos')

# Agrega un argumento posicional para el task_name
parser.add_argument('proceso', type=str, help='Nombre del proceso, opciones: new_task o get_labels')
parser.add_argument('task_name', type=str, help='Nombre de la tarea, formato: levID-medID')

# Parsea los argumentos proporcionados por la línea de comandos
args = parser.parse_args()

# Usa el argumento task_name en tu programa
proceso = args.proceso
task_name = args.task_name

# Carga las variables del archivo .env
load_dotenv()
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION')
AWS_BUCKET = os.getenv('AWS_BUCKET')

# Parámetros de conexión
CVAT_HOST = os.getenv('CVAT_HOST')
CVAT_USERNAME = os.getenv('CVAT_USERNAME')
CVAT_PASSWORD = os.getenv('CVAT_PASSWORD')

# Conectar a CVAT
client = connect_to_cvat(CVAT_HOST, CVAT_USERNAME, CVAT_PASSWORD)

if proceso == 'new_task':
    print("Proceso por implementar")
    print("Crear en el servidor de cvat el task con el nombre:",task_name)
    print("Selecciona cloud storage y la carpeta correspondiente a la medición")
    print("Corre la anotación automática y corrige las anotaciones erroneas")
    print("Vuelve a correr este programa pero con el siguiente comando:")
    print("")
    print(f"python3 main.py get_data {task_name}")
    print("")
    print("Para más consultas hablar con el administrador del sistema.")
if proceso == 'get_data':
    # Buscar la tarea
    task = find_task(client, task_name)

    # Obtener el dataset con lables e imagenes
    get_dataset(task, CVAT_HOST, CVAT_USERNAME, CVAT_PASSWORD)

    # Correr unzip para descomprimir el archivo y que no haga print de lo que hace
    print(f"Descomprimiendo el archivo {task_name}.zip...")
    os.system(f'unzip {task_name}.zip -d {task_name} > /dev/null')
    print("Archivo descomprimido!")

    levID = task_name.split('-')[0]
    medID = task_name.split('-')[1]
    rootPath = f'{task_name}/obj_train_data/imagenes/{levID}/{medID}/images'
    s3_labels = f"imagenes/{levID}/{medID}/labels"
    s3_detections = f"imagenes/{levID}/{medID}/detections"
    s3_reporte = f'imagenes/{levID}/{medID}'
    filenames = os.listdir(rootPath)   
    report_dict = create_base_report() 
            
    for filename in tqdm(filenames, desc="Procesando Detecciones"):
        if not filename.endswith('.txt'):
            image_path = os.path.join(rootPath, filename)
            label_path = image_path.split('.')[0] + '.txt'
            report_dict = get_report(label_path, report_dict)
            draw_bounding_boxes(image_path, label_path)

    # Guardar el reporte en un archivo json
    with open(f'{task_name}/reporte.json', 'w') as f:
        json.dump(report_dict, f)

    s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_DEFAULT_REGION
    )     
        
    # Recorrer todos los archivos en la carpeta local
    for root, dirs, files in os.walk(rootPath):
        for file in tqdm(files, desc="Subiendo archivos a S3"):
            if file.endswith('.txt'):
                # Ruta completa al archivo
                local_path = os.path.join(root, file)

                # Generar la clave para el S3
                s3_key = os.path.relpath(local_path, rootPath)  # Obtener la ruta relativa desde la carpeta local
                s3_full_key = os.path.join(s3_labels, s3_key)

                # Subir el archivo al bucket S3
                try:
                    s3.upload_file(local_path, AWS_BUCKET, s3_full_key)
                    
                except NoCredentialsError:
                    print("No se encontraron las credenciales para AWS.")
                except Exception as e:
                    print(f"Error al subir el archivo {file}: {str(e)}")
                
            else:
                # Ruta completa al archivo
                local_path = os.path.join(root, file)

                # Generar la clave para el S3
                s3_key = os.path.relpath(local_path, rootPath)  # Obtener la ruta relativa desde la carpeta local
                s3_full_key = os.path.join(s3_detections, s3_key)

                # Subir el archivo al bucket S3
                try:
                    s3.upload_file(local_path, AWS_BUCKET, s3_full_key)
                    
                except NoCredentialsError:
                    print("No se encontraron las credenciales para AWS.")
                except Exception as e:
                    print(f"Error al subir el archivo {file}: {str(e)}")

    # Subir el reporte al bucket S3
    try:
        s3.upload_file(f'{task_name}/reporte.json', AWS_BUCKET, f'{s3_reporte}/reporte.json')
    except NoCredentialsError:
        print("No se encontraron las credenciales para AWS.")
    except Exception as e:
        print(f"Error al subir el reporte: {str(e)}")
        
    print("Archivos subidos a S3!")   

    # Eliminar el archivo zip y la carpeta descomprimida
    os.system(f'rm -r {task_name}')
    os.system(f'rm {task_name}.zip')
    print("Archivos locales eliminados!")
    print("Proceso finalizado!")          
                

    
