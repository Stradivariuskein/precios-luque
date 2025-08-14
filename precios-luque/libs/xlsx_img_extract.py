
import zipfile
import os

DELETE_IMG =  "media/artics_imgs/luque.png"

def comparar_imagenes_por_bytes(imagen1, imagen2):
    with open(imagen1, 'rb') as img1, open(imagen2, 'rb') as img2:
        return img1.read() == img2.read()

def extraer_imagenes_excel(archivo_excel, carpeta_salida):
    # Asegúrate de que la carpeta de salida existe
    carpeta_salida += "/" + os.path.basename(archivo_excel).replace(".xlsx", "")
    os.makedirs(carpeta_salida, exist_ok=True)

    # Abre el archivo Excel como un archivo ZIP
    with zipfile.ZipFile(archivo_excel, 'r') as archivo_zip:

        # Itera sobre los archivos en el archivo ZIP
        for nombre_archivo in archivo_zip.namelist():
            # Busca imágenes dentro del directorio "xl/media/"
            if nombre_archivo.startswith("xl/media/") and nombre_archivo.endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
                # Extrae la imagen
                
                archivo_zip.extract(nombre_archivo, carpeta_salida)
                new_img_rute = carpeta_salida + "/" + nombre_archivo
                print(f"Imagen extraída: {nombre_archivo}")

                if comparar_imagenes_por_bytes(new_img_rute, DELETE_IMG):
                    os.remove(new_img_rute)
                    print("son iguales")


    print(f"Imágenes guardadas en: {carpeta_salida}")
    return carpeta_salida



# Uso de la función
# archivo_excel = "Y:\Lista de Precio\LISTA MAYORISTA\REGATON DE GOMA DISMAY.xlsx"
# carpeta_salida = "./playground/imgs"
# extraer_imagenes_excel(archivo_excel, carpeta_salida)