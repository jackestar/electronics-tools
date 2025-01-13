import itertools
import sys

comercial_res = [1, 5, 6.4, 7.4, 10, 15, 27, 33, 40, 47, 50, 56, 82, 100, 150, 220, 330, 470, 390, 560, 1e3, 2e3, 2.2e3, 2.7e3, 3.3e3, 4.7e3, 3.8e3, 10e3, 22e3, 33e3, 47e3, 100e3, 220e3, 330e3, 680e3, 1e6, 1.8e6, 2.2e6, 6.2e6]
comercial_cap = [1e-9, 12e-9, 22e-9, 27e-9, 100e-9, 100e-9, 0.22e-6, 0.33e-6, 0.47e-6, 1e-6, 4.7e-6, 4.7e-6, 10e-6, 22e-6, 27e-6, 33e-6,33e-6, 47e-6, 47e-6, 47e-6, 100e-6, 100e-6, 100e-6, 100e-6, 220e-6, 220e-6, 220e-6, 470e-6, 470e-6, 1800e-6, 1e-6, 20e-6, 330e-12, 22e-12]


def producto_cercano(lista1: list, lista2: list, valor: float,show:bool):
    """
    Retorna las combinaciones mas próximas al valor
    """

    mejor_diferencia = float('inf')
    valores = []
    longitud = 0
    for x, y in itertools.product(lista1, lista2):
        diferencia = abs(valor-x*y)
        # la función len retorna 2 si hay dos tuplas o una tupla con dos elementos
        if diferencia < mejor_diferencia:
            if (show):
                valores.append([x, y])
                longitud += 1
            else:
                valores = [x, y]
                longitud = 1
            mejor_diferencia = diferencia
        elif diferencia == mejor_diferencia:
            longitud += 1
            valores.append([x, y])
    print("R\tC")
    if longitud>1:
        for resultados in valores:
            cadena = [sufijo(val) for val in resultados]
            print(f"{cadena[0]}\t{cadena[1]}")
    else:
        cadena = [sufijo(val) for val in valores]
        print(f"{cadena[0]}\t{cadena[1]}")

def sufijo(v:float):
    sufijo = ""
    if abs(v) > 999:
        v /= 1e3
        sufijo = "k"
    elif abs(v) < 1e-9:
        v *= 1e12
        sufijo = "p"
    elif abs(v) < 1e-6:
        v *= 1e9
        sufijo = "n"
    elif abs(v) < 1e-3:
        v *= 1e6
        sufijo = "μ"
    elif abs(v) < 1.0:
        v *= 1e3
        sufijo = "m"

    return f"{v:.3f}{sufijo}"

number = 0
show = False
arg_len = len(sys.argv)
MESSAGE = "Uso: rc <number> [--show-all]\n"

if arg_len > 3:
    print(f"Demasiados argumentos\n{MESSAGE}")
elif arg_len > 1:
    if arg_len == 3:
        show = sys.argv[2] == "--show-all"
    try:
        number = float(sys.argv[1])
    except ValueError:
        print(f"Ingrese un Numero Valido\n{MESSAGE}")

    if (number!=0):
        producto_cercano(comercial_res, comercial_cap, number, show)
else:
    print(f"Ingrese un valor como argumento\n{MESSAGE}")
