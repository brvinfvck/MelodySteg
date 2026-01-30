from melodySteg import emisor, receptor

entrada = "entrada"
pw = "pass"
instr = 0
numerador = 3

emisor(entrada, pw, instr, numerador)

ruta = "mensaje.wav"
receptor(pw, numerador, ruta)
