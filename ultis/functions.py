import os
from cvat_sdk import Client
from cvat_sdk.api_client import Configuration, ApiClient
from time import sleep
from PIL import Image, ImageDraw
from collections import defaultdict
from random import randint

def connect_to_cvat(host, username, password):
    """Conecta al servidor CVAT y retorna el objeto de cliente."""
    client = Client(host)
    client.login((username, password))
    return client


def find_task(client, task_name):
    """Busca una tarea por nombre y retorna la primera coincidencia."""
    tasks = client.tasks.list()
    for task in tasks:
        if task.name == task_name:
            print(f"Tarea encontrada: {task_name}")
            return task
        
    if not tasks:
        raise ValueError(f"No se encontró la tarea con el nombre '{task_name}'")
    return tasks[0]

def get_dataset(task, user, passw):
    """Obtiene el nombre del archivo de imagen para un marco específico."""
    configuration = Configuration(
    host = "http://3.225.205.173:8080",
    username = user,
    password = passw,
)
    with ApiClient(configuration) as api_client:
        # Export a task as a dataset
        while True:
            (_, response) = api_client.tasks_api.retrieve_dataset(
                id=task.id,
                format='YOLO 1.1',
                _parse_response=False,
            )
            if response.status == 201:
                print("Respuesta del CVAT recibida!")
                break
            
            print("Esperando a respuesta del servidor CVAT...")
            sleep(5)
            

        (_, response) = api_client.tasks_api.retrieve_dataset(
            id=task.id,
            format='YOLO 1.1',
            action="download",
            _parse_response=False,
         )
        
        # Save the resulting file
        with open(f'{task.name}.zip', 'wb') as output_file:
            print(f"Comenzando a descargar {task.name}.zip...")
            output_file.write(response.data)
            print(f"{task.name}.zip descargado!")


# Función para dibujar bounding boxes y sobrescribir la imagen original
def draw_bounding_boxes(image_path, label_path):
    # Cargar la imagen y obtener sus dimensiones originales
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    image_width, image_height = image.size  # Dimensiones originales de la imagen

    # Leer el archivo de etiquetas
    if os.path.exists(label_path):
        with open(label_path, "r") as file:
            labels = file.readlines()

        for label in labels:
            # Formato YOLO: <class_id> <x_center> <y_center> <width> <height>
            label_info = label.split()

            x_center = float(label_info[1]) * image_width  # Centro X desnormalizado
            y_center = float(label_info[2]) * image_height  # Centro Y desnormalizado
            box_width = float(label_info[3]) * image_width  # Ancho desnormalizado
            box_height = float(label_info[4]) * image_height  # Altura desnormalizada

            # Calcular las coordenadas del bounding box
            x_min = int(x_center - box_width / 2)
            x_max = int(x_center + box_width / 2)
            y_min = int(y_center - box_height / 2)
            y_max = int(y_center + box_height / 2)

            # Dibujar el bounding box
            draw.rectangle([x_min, y_min, x_max, y_max], outline="red", width=20)

    # Sobrescribir la imagen original con el bounding box
    image.save(image_path)

# Funcion para crear la base del reporte
def create_base_report():
    report_dict = defaultdict(dict)
    nClasses = 3
    for id in range(nClasses):
        if id == 0:
            type = "antenna"
            model = "A01-2"
        elif id == 1:
            type = "antenna"
            model = "RRU"
        elif id == 2:
            type = "Micro Wave"
            model = "MW"    
                    
        report_dict[id] = {
            "type": type,
            "model": model,
            "detected": 0,
            "filenames": list(),
        }

    return report_dict

      
# Funcion que saca infromacion de label y rellena el reporte 
def get_report(label_path, report_dict):
    
    if os.path.exists(label_path):
        with open(label_path, "r") as file:
            labels = file.readlines()

        for label in labels:
            # Formato YOLO: <class_id> <x_center> <y_center> <width> <height>
            label_info = label.split()
            IDclass = int(label_info[0])
            IDclass = randint(0, 2)
            report_dict[IDclass]["detected"] += 1
            if label_path.split('/')[-1].split('.')[0] not in report_dict[IDclass]["filenames"]:
                report_dict[IDclass]["filenames"].append(label_path.split('/')[-1].split('.')[0])
    return report_dict