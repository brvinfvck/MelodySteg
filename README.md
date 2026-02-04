# MelodySteg

Script que permite el envío de mensajes de texto mediante generación de ondas de audio.
Utiliza un esquema de codificación para convertir el texto en frecuencias de audio haciendo uso de un algortimo esteganográfico.


# Cómo funciona

1. Codificación de texto: cada carácter se mapea a una frecuencia única
2. Transmisión: La aplicación devuelve un fichero .wav al usuario con su mensaje integrado
3. Recepción: El receptor decodifica las frecuencias de vuelta al texto, habiendo obtenido previamente una  clave (a,b) y el numero de compases generados.
4. Visualización: Incluye gráficos y espectrograma que permiten analizar el wav generado. La salida del programa devuelve el mensaje decodificado al receptor.

## Cambio reciente (receptor)

El receptor ya no necesita que ingreses manualmente `(a,b)`:
- Si proporcionas una contraseña (`--pw`), el programa deriva `(a,b)` automáticamente.
- Si no usas `--pw` y existe `claves.txt`, tomará `(a,b)` desde ese archivo.

El numerador (tiempos por compás) también se intenta inferir automáticamente desde el audio (si no se indicó `--numerador`).

# Requisitos
    
    pip install -r requirements.txt

    fluidsynth -> apt-get install fluidsynth

    soundfont ->  apt install fluid-soundfont-gm
