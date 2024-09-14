#   Universidad de las Fuerzas Armadas ESPE - Sede Santo Domingo
#             Ingeniería en Tecnologías de la Información
#                  Software Prototipo de Escáner 3D
#                           Autor: José Ruiz



#Librerías
import os
import subprocess
import imghdr
from tkinter import filedialog
import open3d as o3d
import threading
from PIL import Image
import customtkinter

# Ruta completa del ejecutable de COLMAP
COLMAP_PATH = "C:/Users/José Ruiz/Documents/ESPE/TRABAJO UIC 202450/DESARROLLO DEL PROTOTIPO DE ESCANER 3D/5. SOFTWARE DEL PROTOTIPO/SOFTWARE PROTOTIPO DE ESCANER 3D/Protipo_escaner_3D/colmap-x64-windows-nocuda/bin/colmap.exe"

# Directorios de trabajo
BASE_DIR = os.getcwd()
IMAGE_DIR = os.path.join(BASE_DIR, 'images')
DATABASE_PATH = os.path.join(BASE_DIR, 'database.db')
SPARSE_DIR = os.path.join(BASE_DIR, 'sparse')
DENSE_DIR = os.path.join(BASE_DIR, 'dense')
MODEL_DIR = os.path.join(BASE_DIR, 'model.ply')
MESH_DIR = os.path.join(BASE_DIR, 'mesh.ply')

# Función para asegurar que los directorios existen
def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# Asegurarse de que los directorios de salida existen
ensure_directory_exists(SPARSE_DIR)
ensure_directory_exists(DENSE_DIR)

# Funciones para ejecutar COLMAP desde Python

def run_colmap_feature_extraction():
    """
    Ejecuta el extractor de características de COLMAP.

    Esta función ejecuta el comando `feature_extractor` de COLMAP utilizando
    los parámetros especificados para la base de datos y la ruta de las imágenes.

    Parámetros:
    Ninguno

    Excepciones:
    subprocess.CalledProcessError: Si el comando `feature_extractor` falla, se captura
    la excepción y se muestra un mensaje de error.
    """
    try:
        subprocess.run([
            COLMAP_PATH, 'feature_extractor',
            '--database_path', DATABASE_PATH,
            '--image_path', IMAGE_DIR
        ], check=True)
    except subprocess.CalledProcessError as e:
        show_message(f"Error en feature_extractor: {e}")

def run_colmap_exhaustive_matcher():
    """
    Ejecuta el emparejador exhaustivo de COLMAP.

    Esta función ejecuta el comando `exhaustive_matcher` de COLMAP utilizando
    los parámetros especificados para la base de datos.

    Parámetros:
    Ninguno

    Excepciones:
    subprocess.CalledProcessError: Si el comando `exhaustive_matcher` falla, se captura
    la excepción y se muestra un mensaje de error.
    """
    try:
        subprocess.run([
            COLMAP_PATH, 'exhaustive_matcher',
            '--database_path', DATABASE_PATH
        ], check=True)
    except subprocess.CalledProcessError as e:
        show_message(f"Error en exhaustive_matcher: {e}")

def run_colmap_mapper():
    """
    Ejecuta el mapeador de COLMAP.

    Esta función ejecuta el comando `mapper` de COLMAP utilizando
    los parámetros especificados para la base de datos, la ruta de las imágenes
    y la ruta de salida.

    Parámetros:
    Ninguno

    Excepciones:
    subprocess.CalledProcessError: Si el comando `mapper` falla, se captura
    la excepción y se muestra un mensaje de error.
    """
    try:
        subprocess.run([
            COLMAP_PATH, 'mapper',
            '--database_path', DATABASE_PATH,
            '--image_path', IMAGE_DIR,
            '--output_path', SPARSE_DIR
        ], check=True)
    except subprocess.CalledProcessError as e:
        show_message(f"Error en mapper: {e}")

def run_colmap_image_undistorter():
    """
    Ejecuta el desdistorsionador de imágenes de COLMAP.

    Esta función ejecuta el comando `image_undistorter` de COLMAP utilizando
    los parámetros especificados para la ruta de las imágenes, la ruta de entrada
    y la ruta de salida.

    Parámetros:
    Ninguno

    Excepciones:
    subprocess.CalledProcessError: Si el comando `image_undistorter` falla, se captura
    la excepción y se muestra un mensaje de error.
    """
    try:
        subprocess.run([
            COLMAP_PATH, 'image_undistorter',
            '--image_path', IMAGE_DIR,
            '--input_path', os.path.join(SPARSE_DIR, '0'),
            '--output_path', DENSE_DIR,
            '--output_type', 'COLMAP'
        ], check=True)
    except subprocess.CalledProcessError as e:
        show_message(f"Error en image_undistorter: {e}")

def run_colmap_patch_match_stereo():
    """
    Ejecuta el algoritmo PatchMatch Stereo de COLMAP.

    Esta función ejecuta el comando `patch_match_stereo` de COLMAP utilizando
    los parámetros especificados para la ruta del espacio de trabajo y el formato
    del espacio de trabajo.

    Parámetros:
    Ninguno

    Excepciones:
    subprocess.CalledProcessError: Si el comando `patch_match_stereo` falla, se captura
    la excepción y se muestra un mensaje de error.
    """
    try:
        subprocess.run([
            COLMAP_PATH, 'patch_match_stereo',
            '--workspace_path', DENSE_DIR,
            '--workspace_format', 'COLMAP',
            '--PatchMatchStereo.geom_consistency', 'true'
        ], check=True)
    except subprocess.CalledProcessError as e:
        show_message(f"Error en patch_match_stereo: {e}")

def run_colmap_stereo_fusion():
    """
    Ejecuta el algoritmo Stereo Fusion de COLMAP.

    Esta función ejecuta el comando `stereo_fusion` de COLMAP utilizando
    los parámetros especificados para la ruta del espacio de trabajo, el formato
    del espacio de trabajo, el tipo de entrada y la ruta de salida.

    Parámetros:
    Ninguno

    Excepciones:
    subprocess.CalledProcessError: Si el comando `stereo_fusion` falla, se captura
    la excepción y se muestra un mensaje de error.
    """
    try:
        subprocess.run([
            COLMAP_PATH, 'stereo_fusion',
            '--workspace_path', DENSE_DIR,
            '--workspace_format', 'COLMAP',
            '--input_type', 'geometric',
            '--output_path', MODEL_DIR
        ], check=True)
    except subprocess.CalledProcessError as e:
        show_message(f"Error en stereo_fusion: {e}")

# Integración con Tkinter
def load_images():
    """
    Carga las imágenes desde una carpeta seleccionada por el usuario.

    Esta función abre un cuadro de diálogo para que el usuario seleccione una carpeta
    que contenga las imágenes. Verifica que la carpeta exista, que no esté vacía y que
    todos los archivos en la carpeta sean imágenes válidas.

    Parámetros:
    Ninguno

    Retorna:
    bool: True si las imágenes se cargaron exitosamente, False en caso contrario.
    """
    global IMAGE_DIR
    show_message("Selecciona la carpeta de imágenes")
    IMAGE_DIR = filedialog.askdirectory()
    if not os.path.exists(IMAGE_DIR):
        show_message("Error: la carpeta de imágenes no existe.")
        return False
    if not os.listdir(IMAGE_DIR):
        show_message("Error: la carpeta de imágenes está vacía.")
        return False
    for f in os.listdir(IMAGE_DIR):
        if not imghdr.what(os.path.join(IMAGE_DIR, f)):
            show_message("La carpeta solo debe contener solo imágenes.")
            return False
    show_message("Imágenes cargadas exitosamente.")
    return True

def run_colmap():
    """
    Ejecuta la secuencia completa de COLMAP para la reconstrucción 3D.

    Esta función ejecuta una serie de comandos de COLMAP en secuencia para realizar
    la extracción de características, coincidencias exhaustivas, mapeo, undistorsión
    de imágenes, cálculo de stereo denso y fusión de resultados.

    Parámetros:
    Ninguno

    Excepciones:
    subprocess.CalledProcessError: Si algún comando de COLMAP falla, se captura
    la excepción y se muestra un mensaje de error.
    """
    if not os.path.exists(IMAGE_DIR):
        show_message("Error: la carpeta de imágenes no existe.")
        return
    progress_var.set(0)
    show_message("Extrayendo características...")
    run_colmap_feature_extraction()
    progress_var.set(16.6)
    show_message("Realizando coincidencias exhaustivas...")
    run_colmap_exhaustive_matcher()
    progress_var.set(33.2)
    show_message("Construyendo mapa...")
    run_colmap_mapper()
    progress_var.set(49.8)
    show_message("Undistorsionando imágenes...")
    run_colmap_image_undistorter()
    progress_var.set(66.4)
    show_message("Calculando stereo denso...")
    run_colmap_patch_match_stereo()
    progress_var.set(83.0)
    show_message("Fusionando resultados...")
    run_colmap_stereo_fusion()
    progress_var.set(100)
    show_message("Reconstrucción completada.")
    show_model()

def show_model():
    """
    Muestra el modelo 3D utilizando Open3D.

    Esta función carga el modelo 3D desde la ruta especificada y lo muestra en una
    ventana de visualización utilizando la biblioteca Open3D.

    Parámetros:
    Ninguno

    Excepciones:
    FileNotFoundError: Si el archivo del modelo 3D no existe, se muestra un mensaje de error.
    """
    if not os.path.exists(MODEL_DIR):
        show_message("Error: el archivo del modelo 3D no existe.")
        return
    show_message("Mostrando modelo 3D")
    vis = o3d.visualization.Visualizer()
    vis.create_window()
    model = o3d.io.read_point_cloud(MODEL_DIR)
    vis.add_geometry(model)
    vis.run()
    vis.destroy_window()

def generate_polygons():
    """
    Genera una malla de polígonos a partir de un modelo 3D.

    Esta función lee un archivo de nube de puntos 3D, genera una malla de polígonos
    utilizando el algoritmo Poisson y guarda la malla en un archivo.

    Parámetros:
    Ninguno

    Excepciones:
    FileNotFoundError: Si el archivo del modelo 3D no existe, se muestra un mensaje de error.
    """
    if not os.path.exists(MODEL_DIR):
        show_message("Error: el archivo del modelo 3D no existe.")
        return
    show_message("Generando polígonos...")
    pcd = o3d.io.read_point_cloud(MODEL_DIR)
    mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd, depth=9)
    o3d.io.write_triangle_mesh(MESH_DIR, mesh)
    show_message("Polígonos generados y guardados como mesh.ply")
    show_mesh()

def show_mesh():
    """
    Muestra la malla 3D generada.

    Esta función carga la malla 3D desde un archivo y la muestra en una ventana
    de visualización utilizando la biblioteca Open3D.

    Parámetros:
    Ninguno

    Excepciones:
    FileNotFoundError: Si el archivo de la malla 3D no existe, se muestra un mensaje de error.
    """
    if not os.path.exists(MESH_DIR):
        show_message("Error: el archivo de la malla 3D no existe.")
        return
    show_message("Mostrando malla 3D")
    vis = o3d.visualization.Visualizer()
    vis.create_window()
    mesh = o3d.io.read_triangle_mesh(MESH_DIR)
    vis.add_geometry(mesh)
    vis.run()
    vis.destroy_window()

def load_and_show_model():
    """
    Carga y muestra un modelo 3D seleccionado por el usuario.

    Esta función abre un cuadro de diálogo para que el usuario seleccione un archivo
    de modelo 3D, lo carga y lo muestra en una ventana de visualización.

    Parámetros:
    Ninguno

    Excepciones:
    FileNotFoundError: Si el archivo del modelo 3D no existe, se muestra un mensaje de error.
    """
    global MODEL_DIR
    show_message("Selecciona el archivo del modelo 3D")
    MODEL_DIR = filedialog.askopenfilename(filetypes=[("3D Model Files", "*.ply")])
    if not os.path.exists(MODEL_DIR):
        show_message("Error: el archivo del modelo 3D no existe.")
        return
    show_message("Mostrando modelo 3D")
    show_model()

def run_in_thread(func):
    """
    Ejecuta una función en un hilo separado y espera a que termine.

    Esta función crea un nuevo hilo para ejecutar la función proporcionada y
    espera a que el hilo termine antes de continuar.

    Parámetros:
    func (callable): La función que se ejecutará en un hilo separado.
    """
    thread = threading.Thread(target=func)
    thread.start()
    thread.join()  # Espera a que el hilo termine

def show_message(message):
    """
    Muestra un mensaje en la interfaz de usuario.

    Esta función actualiza el texto de un label en la interfaz de usuario con el
    mensaje proporcionado.

    Parámetros:
    message (str): El mensaje que se mostrará en la interfaz de usuario.
    """
    message_label.configure(text=message)
    root.update_idletasks()

# Función principal para la ejecución automática
def auto_run():
    """
    Ejecuta automáticamente una serie de funciones para la reconstrucción 3D.

    Esta función carga imágenes, ejecuta COLMAP, carga y muestra el modelo 3D,
    y genera polígonos en secuencia, cada una en un hilo separado.

    Parámetros:
    Ninguno
    """
    if load_images():
        run_in_thread(run_colmap)
        run_in_thread(load_and_show_model)
        run_in_thread(generate_polygons)

def on_option_select(choice):
    """
    Ejecuta una acción basada en la opción seleccionada por el usuario.

    Esta función ejecuta diferentes funciones basadas en la opción seleccionada
    por el usuario en la interfaz de usuario.

    Parámetros:
    choice (str): La opción seleccionada por el usuario.
    """
    if choice == "Cargar Imágenes":
        load_images()
    elif choice == "Ejecutar COLMAP":
        run_in_thread(run_colmap)
    elif choice == "Cargar y Mostrar Modelo 3D":
        run_in_thread(load_and_show_model)
    elif choice == "Generar Polígonos":
        run_in_thread(generate_polygons)

options_select = ["Cargar Imágenes", "Ejecutar COLMAP", "Cargar y Mostrar Modelo 3D", "Generar Polígonos"]

# Crear la interfaz gráfica
root = customtkinter.CTk()
root.title("Prototipo de Escáner 3D con COLMAP")
root.geometry("550x350")

# Crear un marco para el título
frameTitle = customtkinter.CTkFrame(master=root, width=400, height=100)
frameTitle.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="wesn")

# Título principal alineado a la derecha con margen
title_label = customtkinter.CTkLabel(frameTitle, text="Prototipo de Escáner 3D", font=("Helvetica", 30, "bold"))
title_label.grid(row=0, column=0, pady=[10, 0], padx=20)

# Subtítulo alineado a la derecha con margen
subtitle_label = customtkinter.CTkLabel(frameTitle, justify="right", text="ESPE Sede Santo Domingo", font=("Helvetica", 15, "bold"))
subtitle_label.grid(row=1, column=0, pady=[0, 40], padx=20)

frameImage = customtkinter.CTkFrame(master=root, width=100, height=100)
frameImage.grid(row=0, column=1, padx=10, pady=(10, 0), sticky="e")

# Cargar y redimensionar la imagen
image = Image.open('./Espe-Angular-Logo.png')
image = image.convert("RGBA")  # Asegurarse de que la imagen tenga un canal alfa
image = image.resize((90, 100))  # Ajusta el tamaño según sea necesario

# Crear un fondo transparente
background = Image.new("RGBA", image.size, (0, 0, 0, 0))
image = Image.alpha_composite(background, image)

# Convertir la imagen a CTkImage
img = customtkinter.CTkImage(light_image=image, dark_image=image, size=(90, 100))

image_label = customtkinter.CTkLabel(frameImage, image=img, text="")
image_label.grid(row=0, column=4, sticky="e", padx=10, pady=10)  # Ajusta la posición según sea necesario

# Crear un marco para los botones
frameButtons = customtkinter.CTkFrame(master=root, width=600, height=30)
frameButtons.grid(row=1, column=0, padx=10, pady=10, sticky="we", columnspan=2)

load_button = customtkinter.CTkButton(frameButtons, text="Inicio rápido", command=auto_run, fg_color="#e47200", hover_color="#ff8c1a")
load_button.grid(row=0, column=0, padx=[80,10], pady=10)

or_label = customtkinter.CTkLabel(frameButtons, text="O", font=("Helvetica", 15, "bold"))
or_label.grid(row=0, column=1, padx=20, pady=10)

# Crear el CTkOptionMenu con una opción predeterminada y asignar la función de comando
optionmenu = customtkinter.CTkOptionMenu(frameButtons, values=options_select, command=on_option_select)
optionmenu.set("Acciones")  # Establecer la opción predeterminada
optionmenu.grid(row=0, column=2, padx=[10,80], pady=10)

# Etiqueta para mostrar mensajes
message_label = customtkinter.CTkLabel(root, text="")
message_label.grid(row=2, column=0)

# Barra de progreso
progress_var = customtkinter.DoubleVar()
progress_bar = customtkinter.CTkProgressBar(root, variable=progress_var)
progress_bar.grid(row=3, column=0, columnspan=2, padx=20, pady=10,sticky="we", )

# Crear el marco para el pie de página
frameFooter = customtkinter.CTkFrame(master=root, width=600, height=30)
frameFooter.grid(row=5, column=0, padx=10, pady=10, sticky="we", columnspan=2)

# Footer
footer_label = customtkinter.CTkLabel(frameFooter, text="Copyright © José Ruiz 2024\nESPE", font=("Helvetica", 12, "bold"))
footer_label.grid(row=0, column=0, padx=20, pady=10, sticky="we")

# Ajustar las columnas del frameFooter para centrar el texto
frameFooter.grid_columnconfigure(0, weight=1)

# Iniciar el bucle principal de la interfaz
root.mainloop()