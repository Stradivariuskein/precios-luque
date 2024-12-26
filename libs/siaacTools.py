from shutil import copy
from re import findall
import os

from django.db import transaction

from apps.core.models import ModelArtic

#RUTE_SIAAC ="X:/SIAAC3/"
RUTE_SIAAC_FILES = os.getcwd() + "/siaac_files/"




#RUTE_ARTIC = f"{RUTE_SIAAC}ARTIC.DBF" 
RUTE_FILES_SIAAC = RUTE_SIAAC_FILES
INDEX_CODE = 11
INDEX_DESCRIPTION = [11,64]
INDEX_PRICE1 = [78,88]
INDEX_PRICE5 = [126,136]
LEN_LINE = 200
# quita los caracteres q no son legible y los reeemplaza
def normalizar(linea):
    linea = linea.replace('¤', 'ñ')
    linea = linea.replace('§', '°')
    linea = linea.replace('ø', '°')
    linea = linea.replace('£', 'Ú')
    linea = linea.replace('¥', 'ñ')
    linea_aux = linea.upper().replace('CAO', 'CAÑO')
    if linea_aux != linea:
        linea = linea_aux[:67] + linea_aux[68:]

    return linea
def displace_line(line,displace,dot_pos):
    break_line = dot_pos+displace-6
    if displace > 0:
        line = line[:break_line] + ' '*displace + line[break_line:]
    elif displace < 0:
        displace = abs(displace)

        for i in range(break_line,INDEX_DESCRIPTION[0],-1):
            if line[i-1] == ' ':
                line = line[:i-1] + line[i:]
                displace -= 1
                if displace <= 0:
                    break
        
    return line

def correct_line(line):
    dots = [71,84,96,108,120,132]

    for index in dots:
        if line[index] != '.':
            res = line[index-3:index+3].find('.')
            if res > -1:
                dot_pos = index-3+res
                displace = index - dot_pos
                line = displace_line(line,displace,dot_pos)

    return line
def get_price_mi(line):
    return float(line[INDEX_PRICE1[0]:INDEX_PRICE1[1]].strip())

def get_price_ma(line):
    return float(line[INDEX_PRICE5[0]:INDEX_PRICE5[1]].strip())

def get_code(line):
    return line[:INDEX_CODE].strip()

def get_all_artics():
    try:

        with open(RUTE_FILES_SIAAC+"articDB.txt", "r") as f_artics:
            dic_artics = {}
            for line in f_artics:
                dic_artics[get_code(line)] = {
                'priceMa': get_price_ma(line),
                'priceMi': get_price_mi(line)
                }
        return dic_artics
    except Exception as e:
        print(e)
        return reed_artics()

def reed_artics():
    #PASA EL ARCHIVO DE LOS ARTICULOS DE SISTEMA A UN ARCHIVO DE TEXTO FACIL DE LEER
    #copy(RUTE_ARTIC,RUTE_FILES_SIAAC+"ARTIC.DBF")
    file = open(RUTE_FILES_SIAAC+"common/ARTIC.DBF", errors="ignore")
    articdb = open(RUTE_FILES_SIAAC+"articDB.txt", "w")
    for i in range(0,6):
    #se descarta las pimeras lineas
        linea = file.readline()


    linea = file.readline(2)
    linea = file.readline(LEN_LINE)
    len_linea = LEN_LINE
    dic_artics = {}
    whith_max_line = 184
    index_fin_desc = -131
    index_ini_price = 86

    while linea != "":

        linea = normalizar(linea)

        final_mayus = findall("[A-Z]$", linea)
        final_dahs = findall("[A-Z]+-.{0,6}$", linea)
        
        if final_mayus or final_dahs: # si termina en una letra la quito y corrijo el largo de la cadena
            
            offset = -1           
            while linea[offset-1] != ' ':
                offset -= 1
            lineaAux = linea[offset:]
            linea = linea[:index_fin_desc+offset] + " " + linea[68:offset] + '\n' 
            articLine = linea[:index_fin_desc].lstrip('\x00').lstrip() + linea[index_ini_price:]
            linea = lineaAux + file.readline(len_linea+offset) # ajusto la siguiente lectura con el offset
            
            
        else:
            articLine = linea[:index_fin_desc].lstrip('\x00').lstrip() + linea[index_ini_price:] + '\n'
            linea = file.readline(len_linea)
            offset = whith_max_line - len(articLine)
            if offset > 0:
                articLine = articLine[:-1] + ' '*offset + '\n'
        
        
        
        len_artic = len(articLine)
        while len_artic > whith_max_line:
            articLine = articLine[:INDEX_DESCRIPTION[1]] + articLine[INDEX_DESCRIPTION[1]+1:]
            len_artic = len(articLine)
        while len_artic < whith_max_line:
            articLine = articLine[:INDEX_DESCRIPTION[1]-1] + ' ' + articLine[INDEX_DESCRIPTION[1]-1:]
            len_artic = len(articLine)

        articLine = correct_line(articLine)
        
        try:
            price1 = float(float(articLine[INDEX_PRICE1[0]:INDEX_PRICE1[1]].strip()))
        except ValueError:
            price1 = 0

        if price1 != 0:
            

            split_code = articLine[:11].strip().split(' ')
            if len(split_code) > 1:
                artic_cod = split_code[0]
                artic_desc = articLine[:11].strip().split(' ')[-1] + articLine[11:67].strip()
            else:
                artic_cod = articLine[:INDEX_CODE].strip()
                artic_desc = articLine[INDEX_DESCRIPTION[0]:INDEX_DESCRIPTION[1]].strip()
            artic_price_mi = float(articLine[INDEX_PRICE1[0]:INDEX_PRICE1[1]].strip())
            artic_price_ma = float(articLine[INDEX_PRICE5[0]:INDEX_PRICE5[1]].strip())
            
            articdb.write(articLine)
            
            dic_artics[artic_cod] = {
                'description': artic_desc,
                'priceMa': artic_price_ma,
                'priceMi': artic_price_mi
                }


    file.close()
    articdb.close()
    return dic_artics

def update_artics(artics):
    with transaction.atomic():
        
        db_artics = ModelArtic.objects.all()
        
        to_update = []
        no_changes = []

        
        # verifico q los precios esten actualizados, si no los actualiza
        for code, data in artics.items():
            current_artic_db = db_artics.filter(code=code).first()
                
            # si el articulo no existe lo crea
            if current_artic_db:
            
                diff_ma = abs(round(current_artic_db.priceMa,1) - round(data['priceMa'],1))
                diff_mi = abs(round(current_artic_db.priceMi,1) - round(data['priceMi'],1))
                if diff_ma > 0.19  or diff_mi > 0.19:
                    
                    current_artic_db.priceMa = data['priceMa']
                    current_artic_db.priceMi = data['priceMi']
                
                if current_artic_db.description != data['description']:
                    current_artic_db.description = data['description']
                current_artic_db.save()
            else:
                new_artic = ModelArtic(code=code, description=data['description'], priceMa=data['priceMa'], priceMi=data['priceMi'])
                new_artic.save()

            

    return {
        'to_update': to_update,
        'no_changes': no_changes
        }


if __name__ == '__main__':
    print(reed_artics()['F-004/1'])