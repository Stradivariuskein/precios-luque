import re
from fractions import Fraction
def parse_medida_pulgadas(desc: str):
    # Regex mejorada que captura cosas como 3/8 x 3"1/4, 3/8 x 3 1/4, etc.
    match = re.search(r'(\d+/?\d*)\s*[xX]\s*([^\s*]+)', desc)

    # if "3/16" in desc:
    #     print(desc)
    if not match:
        return (float('inf'), float('inf'))
    # if "3/16" in desc:
    #     print(match.groups())
    grosor_str, largo_str = match.groups()

    def convertir(valor: str):
        # Normalizamos el string: quitamos comillas, reemplazamos puntos por espacios y eliminamos dobles espacios
        valor = valor.replace('"', ' ').replace(',', '.').replace('”', ' ').strip()
        valor = re.sub(r'\s+', ' ', valor)  # Elimina espacios repetidos

        partes = valor.split()
        total = 0

        for parte in partes:
            try:
                total += float(Fraction(parte))
            except ValueError:
                continue

        return total

    grosor = convertir(grosor_str)
    largo = convertir(largo_str)

    return (grosor, largo)

# Función que extrae la medida del string en formato (nXn)
def extraer_medida_fix(descripcion):
    match = re.search(r'\((\d+)X(\d+)\)', descripcion)
    if match:
        ancho = int(match.group(1))
        largo = int(match.group(2))
        return (ancho, largo)
    return (0, 0)  # Si no se encuentra, lo manda al principio
