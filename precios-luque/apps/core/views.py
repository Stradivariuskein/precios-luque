from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.views.generic import View
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

import os
from collections import defaultdict

from .models import ModelArtic, ModelArticOnePrice, ModelImgArtic, ModelTag, ModelClient, TokenCreateClient
from libs.xlsx_img_extract import extraer_imagenes_excel
from libs.xlsxTools import get_artcis_from_xlsx
from libs.pdf_generator import generate_artics_pdf

import os
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib import messages

from utils.gmail import send_email_via_gmail_api

from libs.shorter_medidas import parse_medida_pulgadas, extraer_medida_fix


# main / index
class ViewSearchArtic(View):
    

    def get(self, request, *args, **kwargs):
        
        OLD_DESCRIPTION_KEY = "old_description"
        NEW_DESCRIPTION_KEY = "mew_description"
        cuit = request.GET.get('cuil')

        if not cuit:
            print(f"no hay cuit {cuit}")
            messages.error(request, 'Ingrese el cuil que aparece en su factura')
            return redirect("/cuil", request)
        
        query_result = ModelClient.objects.filter(cuil=cuit)

        if not query_result.exists():
            messages.error(request, 'Cuil no registrado')
            return redirect("/cuil", request)

        client = query_result.first()


        artics = ModelArtic.objects.filter(~Q(imgs_path__isnull=True), ~Q(imgs_path=""), active=True)

        artics_one_price = {}

        with open("listas-excepciones.txt", "r") as f:
            exclude_lists = f.read().split("\n") # obtenemos las listas q hay q exluir
            
            comon_folder = "media/artics_imgs/"

        with open("codes-exceptions.txt", "r") as f:
            exclude_codes = f.read().split("\n") # obtenemos los codigos q hay q exluir

        with open("replace-description.txt", "r") as f:
            change_description = f.read().split("\n")
            description_changed = {}
            for artic in change_description:
                split_artic = artic.split(",")
                code = split_artic[0]
                word_to_replace = split_artic[1]
                new_word_to_replace = split_artic[2]
                if not code in description_changed:
                    description_changed[code]= {
                        OLD_DESCRIPTION_KEY: "",
                        NEW_DESCRIPTION_KEY: ""}
                    
                description_changed[code][OLD_DESCRIPTION_KEY] = word_to_replace
                description_changed[code][NEW_DESCRIPTION_KEY] = new_word_to_replace



        #all_categoris_tags = ModelTag.objects.all()
        try:
            categorys_for_client = client.lists_tags.all()
        except:
            return render(request, 'core/search_artic.html')

        if categorys_for_client:
            for category in categorys_for_client: # separamos por categorias
                agrups_artics = artics.filter(tags=category)
                artics_of_category = []
                artics_aroup_list = defaultdict(list) # articulos de la misma lista de precios
                for artic in agrups_artics: # se obtinee el precio y las imagenes correspondiente al cliente para cad articulo

                    current_img_path = artic.imgs_path.replace(comon_folder, "")
                    if not current_img_path in exclude_lists and not artic.code in exclude_codes: # los q no tiene imagnes asignadas no hay q mostrarlos
                    
                        ###### AGREGAR AQUI EL CAMBIO DE DESCRIPCION  #######
                        if artic.code in description_changed:
                            artic.description = artic.description.upper().replace(description_changed[artic.code][OLD_DESCRIPTION_KEY].upper(), description_changed[artic.code][NEW_DESCRIPTION_KEY].upper())

                        current_artic = ModelArticOnePrice().create_from_artic(artic,client.list_number) # obtiene el precio correspndiente

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

                    tag = articles[0][0].tags.first()
                    print(tag)
                    print(img_path)
                    if tag and tag.name.strip() == "Tornillos Pitones Arandelas Tuercas":
                        if img_path.strip() == "FIX NAC":
                            articles.sort(key=lambda item: extraer_medida_fix(item[0].description))
                        elif img_path.strip() == "TUERCAS dismay":
                            articles.sort(key=lambda item: item[0].code)  
                        else:    
                            articles.sort(key=lambda item: parse_medida_pulgadas(item[0].description))  # Ordenar por medida
                        print("ordenando por medida")
                    else:
                        articles.sort(key=lambda item: item[0].code)  # Ordenar por descripción
                        print("ordenando por descripcion")
                    artics_of_category.append({
                        "name": img_path,
                        "artics": articles
                    })
                artics_one_price[category.name] = artics_of_category


            return render(request, 'core/search_artic.html',{'artics': artics_one_price, "cuit": cuit})
        else:
            return render(request, 'core/search_artic.html')
        
class DownloadArticsPDF(View):
    #codigo repetido
    def get(self, request, *args, **kwargs):
        
        OLD_DESCRIPTION_KEY = "old_description"
        NEW_DESCRIPTION_KEY = "mew_description"
        cuit = request.GET.get('cuil')

        if not cuit:
            print(f"no hay cuit {cuit}")
            messages.error(request, 'Ingrese el cuil que aparece en su factura')
            return redirect("/cuil", request)
        
        query_result = ModelClient.objects.filter(cuil=cuit)

        if not query_result.exists():
            messages.error(request, 'Cuil no registrado')
            return redirect("/cuil", request)

        client = query_result.first()


        artics = ModelArtic.objects.filter(~Q(imgs_path__isnull=True), ~Q(imgs_path=""), active=True)

        artics_one_price = {}

        with open("listas-excepciones.txt", "r") as f:
            exclude_lists = f.read().split("\n") # obtenemos las listas q hay q exluir
            
            comon_folder = "media/artics_imgs/"

        with open("codes-exceptions.txt", "r") as f:
            exclude_codes = f.read().split("\n") # obtenemos los codigos q hay q exluir

        with open("replace-description.txt", "r") as f:
            change_description = f.read().split("\n")
            description_changed = {}
            for artic in change_description:
                split_artic = artic.split(",")
                code = split_artic[0]
                word_to_replace = split_artic[1]
                new_word_to_replace = split_artic[2]
                if not code in description_changed:
                    description_changed[code]= {
                        OLD_DESCRIPTION_KEY: "",
                        NEW_DESCRIPTION_KEY: ""}
                    
                description_changed[code][OLD_DESCRIPTION_KEY] = word_to_replace
                description_changed[code][NEW_DESCRIPTION_KEY] = new_word_to_replace



        #all_categoris_tags = ModelTag.objects.all()
        try:
            categorys_for_client = client.lists_tags.all()
        except:
            return render(request, 'core/search_artic.html')

        if categorys_for_client:
            for category in categorys_for_client: # separamos por categorias
                agrups_artics = artics.filter(tags=category)
                artics_of_category = []
                artics_aroup_list = defaultdict(list) # articulos de la misma lista de precios
                for artic in agrups_artics: # se obtinee el precio y las imagenes correspondiente al cliente para cad articulo

                    current_img_path = artic.imgs_path.replace(comon_folder, "")
                    if not current_img_path in exclude_lists and not artic.code in exclude_codes: # los q no tiene imagnes asignadas no hay q mostrarlos
                    
                        ###### AGREGAR AQUI EL CAMBIO DE DESCRIPCION  #######
                        if artic.code in description_changed:
                            artic.description = artic.description.upper().replace(description_changed[artic.code][OLD_DESCRIPTION_KEY].upper(), description_changed[artic.code][NEW_DESCRIPTION_KEY].upper())

                        current_artic = ModelArticOnePrice().create_from_artic(artic,client.list_number) # obtiene el precio correspndiente

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

                    tag = articles[0][0].tags.first()

                    if tag and tag.name.strip() == "Tornillos Pitones Arandelas Tuercas":
                        if img_path.strip() == "FIX NAC":
                            articles.sort(key=lambda item: extraer_medida_fix(item[0].description))
                        elif img_path.strip() == "TUERCAS dismay":
                            articles.sort(key=lambda item: item[0].code)  
                        else:    
                            articles.sort(key=lambda item: parse_medida_pulgadas(item[0].description))  # Ordenar por medida

                    else:
                        articles.sort(key=lambda item: item[0].code)  # Ordenar por descripción

                    artics_of_category.append({
                        "name": img_path,
                        "artics": articles
                    })
                artics_one_price[category.name] = artics_of_category

        # Generar PDF
        pdf_buffer = generate_artics_pdf(artics_one_price)

        # Enviar como descarga
        return HttpResponse(pdf_buffer, content_type='application/pdf', headers={
            'Content-Disposition': 'attachment; filename="listado_articulos.pdf"'
        })

class ViewSetCuil(View):
    

    def get(self, request, *args, **kwargs):
        
        return render(request, 'core/set_cuil.html')

    def post(self, request, *args, **kwargs):
        # Obtiene el CUIL del formulario enviado
        cuil = request.POST.get('cuil')
        print(cuil)
        # Valida el CUIL (opcional, puedes agregar más validaciones)
        if not cuil or not cuil.isdigit() or len(cuil) != 11:
            print(len(cuil))
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

@method_decorator(transaction.atomic, name='post')
class CreateClientView(View):
    def get(self, request):
        tags = ModelTag.objects.all()
        param_token = request.GET.get("token", None)
        if not param_token:
            context = {"msj": "Error: Falta el token"}
            return render(request, 'core/create_client_message.html', context)
        try:
            token = TokenCreateClient.objects.get(token=param_token)
        except TokenCreateClient.DoesNotExist:
            context = {"msj": "Error: Token invalido"}
            return render(request, 'core/create_client_message.html', context)

        # Obtené valores desde la URL (query parameters)
        initial_data = {
            'cuil': request.GET.get('cuil', ''),
            'name': request.GET.get('name', ''),
            'empress_name': request.GET.get('empress', ''),
            'tel': request.GET.get('phone', ''),
            'email': request.GET.get('email', ''),
            'bussines': request.GET.get('bussines', ''),
            'message': request.GET.get('message', ''),
        }

        return render(request, 'core/create_client.html', {
        "tags": ModelTag.objects.all(),
        "list_number_choices": ModelClient.LIST_NUMBER_CHOICES,
        "bussines_choices": ModelClient.BUSSINES_CHOISES,
        "initial":initial_data
    })


    def post(self, request):
        param_token = request.GET.get("token", None)
        if not param_token:
            context = {"msj": "Error: Falta el token"}
            return render(request, 'core/create_client_message.html', context)

        try:
            token = TokenCreateClient.objects.get(token=param_token)
        except TokenCreateClient.DoesNotExist:
            context = {"msj": "Error: Token invalido"}
            return render(request, 'core/create_client_message.html', context)

        # Extraer datos del formulario
        cuil = request.POST.get('cuil')
        name = request.POST.get('name')
        empress_name = request.POST.get('empress_name')
        tel = request.POST.get('tel')
        email = request.POST.get('email')
        bussines = request.POST.get('bussines')
        message = request.POST.get('message')
        list_number = request.POST.get('list_number')
        tags_input = request.POST.get('lists_tags')  # Ej: "1,2,3"

        if not cuil or not cuil.isdigit() or len(cuil) != 11:
            return render(request, 'core/new_client_request.html', {
                'error': 'CUIT invalido. Ingrese solo 11 digitos. Quite los guiones.',
                'form': request.POST,
                "tags": tags,
                "list_number_choices": ModelClient.LIST_NUMBER_CHOICES,
            })

        # Verificar existencia de cliente
        if ModelClient.objects.filter(cuil=cuil).exists():
            error_msg = "Ya existe un cliente registrado con ese CUIL."
            initial_data = {
                'cuil': cuil,
                'name': name,
                'empress_name': empress_name,
                'tel': tel,
                'email': email,
                'bussines': bussines,
                'message': message,
                'list_number': list_number,
            }
            tags = ModelTag.objects.all()

            return render(request, 'core/create_client.html', {
                "error": error_msg,
                "initial": initial_data,
                "tags": tags,
                "list_number_choices": ModelClient.LIST_NUMBER_CHOICES,
            })

        # Crear cliente dentro de una transacción atómica
        with transaction.atomic():
            client = ModelClient.objects.create(
                cuil=cuil,
                name=name,
                empress_name=empress_name,
                tel=tel,
                email=email,
                bussines=bussines,
                message=message,
                list_number=list_number
            )

            if tags_input:
                tag_ids = [int(i.strip()) for i in tags_input.split(',') if i.strip().isdigit()]
                tags = ModelTag.objects.filter(id__in=tag_ids)
                client.lists_tags.set(tags)

            token.delete()

            content = (
            f"Hola {name}, tu solicitud fue aceptada exitosamente. Puedes acceder a nuestra lista de precios a través del siguiente enlace.\n\n"
            f"https://precios.alanluque.com/?cuil={cuil}\n\n"
            "wp: +5491130753001\n"
            "tel: 11 4460-2005\n"
            )
            
            send_email_via_gmail_api(email, "Lista de preciso LUQUE", content)
        context = {"msj": f"Cliente Creado exitosamente.", "link": f"https://precios.alanluque.com/?cuil={cuil}"}
        return render(request, 'core/create_client_message.html', context)



class ClientSuccess(View):
    def get(self, request):
        return render(request, 'core/clientsuccess.html')


class NewClientRequest(View):
    def get(self, request):
        context = {"bussines_choices": ModelClient.BUSSINES_CHOISES}
        return render(request, 'core/new_client_request.html', context)

    def post(self, request):
        cuil = request.POST.get('cuil').replace(' ', '')
        client = ModelClient.objects.filter(cuil=cuil)
        if client.exists():
            return redirect(f"/?cuil={client.first().cuil}")
        name = request.POST.get('name').strip()
        empress_name = request.POST.get('empress_name').strip()
        bussines = request.POST.get('bussines').strip()
        message = request.POST.get('message').strip()
        tel = request.POST.get('tel').replace(' ', '')
        email = request.POST.get('email').replace(' ', '')

        if not cuil or not cuil.isdigit() or len(cuil) != 11:
            return render(request, 'core/new_client_request.html', {
                'error': 'CUIT invalido. Ingrese solo 11 digitos. Quite los guiones.',
                'form': request.POST,
                "bussines_choices": ModelClient.BUSSINES_CHOISES
            })

        if not all([cuil, name, empress_name, tel, email]):
            return render(request, 'core/new_client_request.html', {
                'error': 'Todos los campos son obligatorios.',
                'form': request.POST,
                "bussines_choices": ModelClient.BUSSINES_CHOISES
            })
        token = TokenCreateClient.objects.create(token=TokenCreateClient.generate_token())
        content = (
            f"CUIL: {cuil}\n"
            f"Nombre: {name}\n"
            f"Empresa: {empress_name}\n"
            f"Negocio: {bussines}\n"
            f"Teléfono: {tel}\n"
            f"Email: {email}\n"
            f"Mensaje: {message}\n\n"
            f"Ingrese al siguinte link para dar de alta\n"
            f"https://precios.alanluque.com/createclient?cuil={cuil}&name={name.replace(' ', '%20')}&empress={empress_name.replace(' ', '%20')}&bussines={bussines.replace(' ', '%20')}&phone={tel}&email={email}&message={message.replace(' ', '%20')}&token={token.token}"
        )

        send_message = send_email_via_gmail_api("luquearti@gmail.com", "Nueva solicitud de cliente", content)
        
        if not send_message:
            context = {"msj": f"Error: email-error"}
            return render(request, 'core/request_client_message.html', context)
        
        return redirect("clientsuccess")


