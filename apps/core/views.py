from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.views.generic import View
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from libs.client_api import get_client_from_cuit
import os
from collections import defaultdict

from .models import ModelArtic, ModelArticOnePrice, ModelImgArtic, ModelTag
from libs.xlsx_img_extract import extraer_imagenes_excel
from libs.xlsxTools import get_artcis_from_xlsx


from concurrent.futures import ThreadPoolExecutor
import os
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib import messages


# main / index
class ViewSearchArtic(View):
    

    def get(self, request, *args, **kwargs):
        #from libs.siaacTools import reed_artics, update_artics # ESTO ES ASI PORQUE SINO HAY IMPORTACION REDUNDANTE y da un error
    
        brute_cuit = request.GET.get('cuil')


        if brute_cuit:
            cuit = brute_cuit
            client = get_client_from_cuit(cuit)

            if client:
                list_number = str(client.qlist)

            else:
                print("cuil no registrado")
                messages.error(request, 'CUIL No registrado. Por favor, utiliza el que aparece en su factura.')
                return redirect("/cuil", request)
        else:
            print(f"no hay cuit {brute_cuit}")
            messages.error(request, 'Ingrese el cuil que aparece en su factura')
            return redirect("/cuil", request)


        # siaac_artics = reed_artics()
        # update_artics(siaac_artics)
        artics = ModelArtic.objects.filter(~Q(imgs_path__isnull=True), ~Q(imgs_path=""), active=True)
        #artics = ModelArtic.objects.filter(active=True)

        artics_one_price = {}

        with open("listas-excepciones.txt", "r") as f:
            exclude_lists = f.read().split("\n") # obtenemos las listas q hay q exluir
            
            comon_folder = "media/artics_imgs/"

        with open("codes-exceptions.txt", "r") as f:
            exclude_codes = f.read().split("\n") # obtenemos los codigos q hay q exluir


        all_categoris_tags = ModelTag.objects.all()

        for category in all_categoris_tags: # separamos por categorias
            agrups_artics = artics.filter(tags=category)
            artics_of_category = []
            artics_aroup_list = defaultdict(list) # articulos de la misma lista de precios
            for artic in agrups_artics: # se obtinee el precio y las imagenes correspondiente al cliente para cad articulo

                current_img_path = artic.imgs_path.replace(comon_folder, "")
                if not current_img_path in exclude_lists and not artic.code in exclude_codes: # los q no tiene imagnes asignadas no hay q mostrarlos
                    
                    current_artic = ModelArticOnePrice().create_from_artic(artic,list_number) # obtiene el precio correspndiente

                    if artic.imgs_path:

                        try:
                            images = os.listdir(artic.imgs_path + "/xl/media") 
                            
                        except FileNotFoundError:
                            images = []
                    else:
                        images = []

                    path_images = []
                    for image in images:
                        path_images.append('/' + artic.imgs_path + "/xl/media/" + image)

                    # artics_of_category.append((current_artic, path_images))
                    # artics_of_category.sort(
                    #         key=lambda item: item[0].description
                    #     )

                    artics_aroup_list[current_img_path].append((current_artic, path_images))

            # Convertimos el diccionario agrupado en la estructura deseada
            for img_path, articles in artics_aroup_list.items():
                articles.sort(key=lambda item: item[0].description)  # Ordenar los artículos
                artics_of_category.append({
                    "name": img_path,
                    "artics": articles
                })
            artics_one_price[category.name] = artics_of_category


        return render(request, 'core/search_artic.html',{'artics': artics_one_price})


class ViewSetCuil(View):
    

    def get(self, request, *args, **kwargs):
        
        
        return render(request, 'core/set_cuil.html')

    def post(self, request, *args, **kwargs):
        # Obtiene el CUIL del formulario enviado
        cuil = request.POST.get('cuil')
        print(cuil)
        # Valida el CUIL (opcional, puedes agregar más validaciones)
        if not cuil or not cuil.isdigit() or len(cuil) == 12:
            print("no es valido")
            messages.error(request, 'Ingrese solo 11 digitos. Quite los guiones.')
            # Si el CUIL no es válido, vuelve a la misma página con un mensaje de error
            return render(request, 'core/set_cuil.html')
        print("es valido")
        # Redirige a la raíz con valores extra en la URL
        return redirect(f"/?cuil={cuil}")

        

def vincule_imgs(request):
     # Ruta donde buscar los archivos
    directory_path = "Y:\ACTUALIZAR PRECIOS\LISTAS"
    
    # Listar los archivos .xlsx en el directorio
    xlsx_files = [
        file for file in os.listdir(directory_path) 
        if file.endswith('.xlsx') and os.path.isfile(os.path.join(directory_path, file))
    ]


    for file in xlsx_files:
        folder_imgs = extraer_imagenes_excel(directory_path+ '/' + file, "media/artics_imgs")
        # obtener codgiso
        artics = get_artcis_from_xlsx(directory_path+ '/' + file)
        
        for code in artics:
            try:
                current_db_artic = ModelArtic.objects.get(code=code)
                current_db_artic.imgs_path = folder_imgs
                current_db_artic.save()
                print(f"nueva ruta para {code}: {current_db_artic.imgs_path}")
            except:
                print(f"error codigo[{code}] inexistente en la base de datos")


    
    return HttpResponse("ok")

        

@method_decorator(csrf_exempt, name='dispatch')
class SiaacFileUploadView(View):
    def post(self, request, *args, **kwargs):
        # Obtén el archivo
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file provided'}, status=400)

        file = request.FILES['file']

        # Obtén el parámetro sistem
        sistem = request.POST.get('sistem')
        if sistem not in ['siaac3', 'siaacfe', 'common']:
            return JsonResponse({'error': 'Invalid sistem value'}, status=400)

        # Define dónde guardar el archivo
        upload_dir = f'siaac_files/{sistem}/'
        os.makedirs(upload_dir, exist_ok=True)
        save_path = os.path.join(upload_dir, file.name)

        # Guarda el archivo
        with open(save_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        from libs.siaacTools import reed_artics, update_artics # ESTO ES ASI PORQUE SINO HAY IMPORTACION REDUNDANTE y da un error
        siaac_artics = reed_artics()
        update_artics(siaac_artics)

        return JsonResponse({'message': 'File uploaded successfully', 'filename': file.name, 'sistem': sistem}, status=200)



def create_tags(request):
    def listar_archivos_y_carpetas(ruta):
        """
        Lista todos los archivos y carpetas de una ruta dada.

        :param ruta: Ruta del directorio que se desea listar.
        :return: Dos listas: una con los archivos y otra con las carpetas.
        """
        archivos = []
        carpetas = []

        try:
            for elemento in os.listdir(ruta):
                elemento_path = os.path.join(ruta, elemento)
                if os.path.isfile(elemento_path):
                    archivos.append(elemento)
                elif os.path.isdir(elemento_path):
                    carpetas.append(elemento)
        except FileNotFoundError:
            print(f"La ruta {ruta} no existe.")
        except PermissionError:
            print(f"Permiso denegado para acceder a {ruta}.")

        return carpetas, archivos


    (folders, files) = listar_archivos_y_carpetas("Y:/ACTUALIZAR PRECIOS/DB/LISTAS Drive")

    for file in files:
        file_name = file.replace(".xlsx", "")
        if file_name[-1] == ".":
            file_name = file_name[:-1]
        artics_agroup = ModelArtic.objects.filter(imgs_path=file)
        for current_artic in artics_agroup:
            current_artic.add_tag("Otros")


    for folder in folders:
        (sub_folders, files) = listar_archivos_y_carpetas(f"Y:/ACTUALIZAR PRECIOS/DB/LISTAS Drive/{folder}")


        for file in files:
            file_name = file.replace(".xlsx", "")
            if file_name[-1] == ".":
                file_name = file_name[:-1]
            artics_agroup = ModelArtic.objects.filter(imgs_path__icontains=file_name)


            for current_artic in artics_agroup:
                txt_tag = folder
                current_artic.add_tag(txt_tag)


    return HttpResponse("ok")


