from utils import generar_clave_y_compases, generar_melodia_con_mensaje, mostrar_melodia_en_texto
#from os import system('clear')

def main():
    mensaje = "hola"
    clave, compases = generar_clave_y_compases(mensaje)
    melodia_codificada = generar_melodia_con_mensaje(mensaje, clave, compases)
    mostrar_melodia_en_texto(melodia_codificada)

if __name__ == "__main__":
    main()