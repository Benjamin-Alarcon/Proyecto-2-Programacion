import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from PIL import Image
from datetime import datetime

# --- 1. EXPLORACIÓN Y SELECCIÓN DE ARCHIVOS ---

def buscador():
    """Busca y lista las imágenes válidas en la carpeta Objetos/"""
    imgs = []
    if not os.path.exists('Objetos'):
        print("Error: La carpeta 'Objetos' no existe.")
        return imgs
    
    for imagen in os.listdir('Objetos'):
        # Validar formatos permitidos por el enunciado
        if imagen.lower().endswith(('.png', '.jpg', '.jpeg')):
            imgs.append(imagen)
    return imgs

def buscar_fondos():
    """Busca y retorna de forma automática los dos primeros fondos de la carpeta Fondos/"""
    fondos = []
    if not os.path.exists('Fondos'):
        print("Error: La carpeta 'Fondos' no existe.")
        return fondos
    
    for archivo in os.listdir('Fondos'):
        if archivo.lower().endswith(('.png', '.jpg', '.jpeg')):
            fondos.append(archivo)
    
    # Estrategia fija: Tomar los dos primeros disponibles como lo permite la rúbrica
    if len(fondos) >= 2:
        return [fondos[0], fondos[1]]
    else:
        print("Advertencia: Se necesitan al menos 2 imágenes en la carpeta 'Fondos/'.")
        return fondos

def seleccionar_archivo(lista):
    """Solicita al usuario el número de la imagen a procesar y valida la entrada"""
    print("\nArchivos disponibles en la carpeta Objetos/: ")
    for idx, img in enumerate(lista, 1):
        print(f'{idx}. {img}')

    while True:
        try:
            opcion = int(input("\nSeleccionar el archivo a cargar (ingrese el número): "))
            if 1 <= opcion <= len(lista):
                return lista[opcion - 1]
            else:
                print(f"Por favor elija un número válido entre 1 y {len(lista)}")
        except ValueError:
            print("Por favor ingrese un número entero válido.")


# --- 2. PROCESAMIENTO MATRICIAL DE IMÁGENES (ALGORITMO DINÁMICO) ---

def segmentar_y_reemplazar(matriz_obj, matriz_fon, tolerancia=45):
    """
    Recorre de forma matricial los canales RGB píxel por píxel.
    Detecta automáticamente el color de fondo usando la esquina superior izquierda [0,0].
    """
    resultado = matriz_obj.copy()
    filas, columnas, canales = matriz_obj.shape
    pixeles_objeto = 0
    coordenadas_objeto = []
    
    # Detección automática del color de fondo usando el primer píxel [0, 0]
    color_fondo = matriz_obj[0, 0]
    bg_r = int(color_fondo[0])
    bg_g = int(color_fondo[1])
    bg_b = int(color_fondo[2])
    
    # Recorrido de matrices por filas, columnas y canales RGB
    for f in range(filas):
        for c in range(columnas):
            r = int(matriz_obj[f, c, 0])
            g = int(matriz_obj[f, c, 1])
            b = int(matriz_obj[f, c, 2])
            
            # Cálculo de distancia euclidiana de color en 3D (R, G, B)
            distancia = np.sqrt((r - bg_r)**2 + (g - bg_g)**2 + (b - bg_b)**2)
            
            # Si el píxel está cerca del color de fondo detectado, se reemplaza
            if distancia < tolerancia:
                resultado[f, c] = matriz_fon[f, c]
            else:
                # Si el píxel difiere del fondo, pertenece al objeto principal
                pixeles_objeto += 1
                coordenadas_objeto.append((f, c))
                
    return resultado, pixeles_objeto, coordenadas_objeto


# --- 3. ACCIONES PARA LOS BOTONES DE LA INTERFAZ ---

def accion_original(event):
    ax_imagen.imshow(matriz_original)
    ax_imagen.set_title("Imagen Original")
    global imagen_actual_en_pantalla
    imagen_actual_en_pantalla = matriz_original
    plt.draw()

def accion_fondo1(event):
    ax_imagen.imshow(matriz_resultado1)
    ax_imagen.set_title("Imagen con Fondo Alternativo 1")
    global imagen_actual_en_pantalla
    imagen_actual_en_pantalla = matriz_resultado1
    plt.draw()

def accion_fondo2(event):
    ax_imagen.imshow(matriz_resultado2)
    ax_imagen.set_title("Imagen con Fondo Alternativo 2")
    global imagen_actual_en_pantalla
    imagen_actual_en_pantalla = matriz_resultado2
    plt.draw()

def accion_guardar(event):
    try:
        # Formato de guardado con fecha y hora actual (YYYYMMDD_HHMMSS)
        ahora = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"resultado_{ahora}.png"
        
        # Convertir la matriz de vuelta a objeto PIL Image para guardar en disco
        img_guardar = Image.fromarray(imagen_actual_en_pantalla)
        img_guardar.save(nombre_archivo)
        print(f"¡Imagen guardada exitosamente como '{nombre_archivo}'!")
    except Exception as e:
        print(f"Error al guardar la imagen: {e}")

def accion_reporte(event):
    try:
        # Formato exigido de reporte por la rúbrica: reporte_ddmmyyyy_HHMMSS.txt
        ahora = datetime.now().strftime("%d%m%Y_%H%M%S")
        nombre_reporte = f"reporte_{ahora}.txt"
        
        with open(nombre_reporte, "w") as f:
            f.write(f"Cantidad de píxeles del objeto: {info_objeto['cantidad']}\n")
            f.write("Coordenadas:\n")
            for coord in info_objeto['coordenadas']:
                f.write(f"({coord[0]},{coord[1]})\n")
                
        print(f"¡Reporte generado con éxito: '{nombre_reporte}'!")
    except Exception as e:
        print(f"Error al generar el reporte: {e}")


# --- 4. FLUJO PRINCIPAL Y CONTROL DE ERRORES ---

lista_archivos = buscador()
fondos_disponibles = buscar_fondos()

if lista_archivos and len(fondos_disponibles) == 2:
    archivo_seleccionado = seleccionar_archivo(lista_archivos)
    
    ruta_objeto = os.path.join('Objetos', archivo_seleccionado)
    ruta_fondo1 = os.path.join('Fondos', fondos_disponibles[0])
    ruta_fondo2 = os.path.join('Fondos', fondos_disponibles[1])
    
    try:
        # Carga segura y unificación de formato de color a RGB
        img_obj_pil = Image.open(ruta_objeto).convert("RGB")
        img_f1_pil  = Image.open(ruta_fondo1).convert("RGB")
        img_f2_pil  = Image.open(ruta_fondo2).convert("RGB")
        
        # Redimensionamiento automático de los fondos al tamaño de la imagen principal
        img_f1_resized = img_f1_pil.resize(img_obj_pil.size)
        img_f2_resized = img_f2_pil.resize(img_obj_pil.size)
        
        # Conversión a matrices tridimensionales NumPy
        matriz_original = np.array(img_obj_pil)
        matriz_f1       = np.array(img_f1_resized)
        matriz_f2       = np.array(img_f2_resized)
        
        print("\nProcesando segmentación en matrices... Por favor espere un momento.")
        
        # Procesar primer escenario alternativo y extraer los datos de píxeles del objeto
        matriz_resultado1, cant_pix, coords = segmentar_y_reemplazar(matriz_original, matriz_f1)
        
        info_objeto = {
            'cantidad': cant_pix,
            'coordenadas': coords
        }
        
        # Procesar segundo escenario alternativo
        matriz_resultado2, _, _ = segmentar_y_reemplazar(matriz_original, matriz_f2)
        
        # Variable que almacena el estado visual dinámico de la pantalla
        imagen_actual_en_pantalla = matriz_original
        
        # --- Configuración de la interfaz gráfica con Matplotlib ---
        fig, ax_imagen = plt.subplots(figsize=(9, 7))
        plt.subplots_adjust(bottom=0.2) # Deja espacio abajo para que quepan los botones sin tapar la imagen
        
        ax_imagen.imshow(matriz_original)
        ax_imagen.set_title("Imagen Original")
        ax_imagen.axis('off') # Desactiva las rejillas de coordenadas numéricas para estética visual
        
        # Geometría y posicionamiento de botones [izquierda, abajo, ancho, alto]
        ax_btn_orig = plt.axes([0.08, 0.05, 0.14, 0.06])
        ax_btn_f1   = plt.axes([0.24, 0.05, 0.14, 0.06])
        ax_btn_f2   = plt.axes([0.40, 0.05, 0.14, 0.06])
        ax_btn_g    = plt.axes([0.56, 0.05, 0.14, 0.06])
        ax_btn_rep  = plt.axes([0.72, 0.05, 0.16, 0.06])
        
        btn_original = Button(ax_btn_orig, 'Original')
        btn_fondo1   = Button(ax_btn_f1, 'Fondo 1')
        btn_fondo2   = Button(ax_btn_f2, 'Fondo 2')
        btn_guardar  = Button(ax_btn_g, 'Guardar')
        btn_reporte  = Button(ax_btn_rep, 'Reporte')
        
        # Vinculación de los eventos de click a sus respectivas funciones
        btn_original.on_clicked(accion_original)
        btn_fondo1.on_clicked(accion_fondo1)
        btn_fondo2.on_clicked(accion_fondo2)
        btn_guardar.on_clicked(accion_guardar)
        btn_reporte.on_clicked(accion_reporte)
        
        # Despliega la interfaz interactiva de usuario
        plt.show()

    except Exception as e:
        print(f"Error crítico durante la lectura o procesamiento de archivos: {e}")
else:
    print("Recursos insuficientes. Verifique que existan imágenes en 'Objetos/' y mínimo 2 en 'Fondos/'.")