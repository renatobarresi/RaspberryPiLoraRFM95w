"""
    Codigo de prueba del ftp para el gateway LoRa 
    
    Se utiliza protocolo FTP y LoRa, en la version siguiente se podria utilizar MQTT
    
    TODO:
    -String format a variable "datos"
    -Corregir bug por formateo en procesar_paquete

    Autor: Renato Barresi
"""

#Para debugging
import pdb

from ftplib import FTP
from datetime import datetime
import time
from digitalio import DigitalInOut, Direction, Pull
import adafruit_rfm9x
import busio
import board

FTP_SERVER_IP = "IP"
FTP_SERVER_USER = "USER"
FTP_SERVER_PASS = "PASS"
FTP_SERVER_PORT = "PORT"
FTP_SERVER_PATH = "PATH"

LOCALIDAD = "AgroUNA"

tab = "20"

cabezera_estacion = format("Timestamp", tab) + format("Temp[C]", tab) + format("Humid[%]", tab) + format("Presion[bar]",tab) + format("Wind Speed[Km/h]", tab) + format("Max WS[Km/h]", tab) + format("Wind Dir[°]", tab) + format("UV index[mW/cm^2]", tab) + "\n"

def upload_text_file(host, user, passwd, ftp_dir, file_name):

    ftp = FTP(host, user, passwd)
    ftp.cwd(ftp_dir)               
   
    archivo = open(file_name, 'rb') 

    if archivo.mode == 'rb':
        print("Subiendo archivo a: " + ftp.pwd())
        print(ftp.storlines('STOR '+ file_name, archivo))
    else:
        print("Modo de lectura inadecuado")

    archivo.close()
    
    ftp.quit()

"""
 Description: Funcion encargada de concatenar los datos en un archivo
 
 Params: Header --> cabezera del archivo, data --> datos a escribir en archivo, name_estacion--> nombre de la estacion

 Return: none
"""
def escribir_archivo(header, data, name_estacion):
    
    flag = False

    try:
        archivo = open(name_estacion, "r")
        print("El archivo ya existe")
        archivo.close()
    except FileNotFoundError:
        flag = True
    
    if flag == True:
        print("Escribiendo cabezera..")
        archivo = open(name_estacion, "a")
        print(archivo.write(header))
        archivo.close()
    print("Escribiendo data..")
    archivo = open(name_estacion, "a+")
    archivo.write(data)
    archivo.close()

"""
    Procesa los datos en bruto recibidos del datalogger
    params: raw_data -> bytearray recibido
    returns: hum -> humedad, temp -> temperatura, pres -> presion, uvIndex -> In             tensidad UV 
"""
def procesar_paquete(raw_data):
    #formato de bytearray temp;hum;presion;uv
    data = raw_data.decode(errors = 'ignore')
    data = data.partition("\n")[0][2:]
    #print(data)
    data = data.split(";")
    print(data)
    
    temp = data[0]
    hum = data[1]
    pres = data[2]
    wind_speed = data[3]
    max_wind_speed = data[4]
    angle = data[5]
    uvIndex = data[6]
    uvIndex = uvIndex.split("\x00")[0]
    
    print(temp, hum, pres, wind_speed, max_wind_speed, angle, uvIndex)
        
    return temp, hum, pres, wind_speed, max_wind_speed, angle, uvIndex

def main():
    print("--Ftp file upload test--" )
    
    """Recibir datos de la estacion"""
    #inicializamos al modem LoRa
    print("Inicializando modulo RFM9x")
    
    CS = DigitalInOut(board.CE1)
    RESET = DigitalInOut(board.D25)
    #creamos objeto SPI
    spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
    
    try:
        #creamos objeto rfm9x 
        rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, 433.0 )
        print("RFM9x conectado con exito")
    except RuntimeError as error:
        print("RFM9x Error: ", error)
        exit()
    
    rfm9x.signal_bandwidth = 125000
    rfm9x.coding_rate = 4 
    rfm9x.spreading_factor = 7   
    rfm9x.enable_crc = True
    rfm9x.tx_power = 13
    print("Esperando paquete...")
    while True:
        while True:
            #pdb.set_trace()
            paquete = None
            paquete = rfm9x.receive(with_header = True, timeout=2.0)
            #rfm9x.send("hola")
            if paquete is not None:
                #print("OK")
                print("Received (raw header): ", [hex(x) for x in paquete[0:4]])
                print("Received (raw payload): {0}".format(paquete[4:]))
                print("Received RSSI: {0}".format(rfm9x.last_rssi))
                break

        """Si dest_address es igual a address gateway """
        
        
        """Procesar paquete"""
        try:
            temp, hum, pres, vel_viento, max_speed, angle, uvIndex = procesar_paquete(paquete)
        except Exception:
            temp = "NaN"
            hum = "NaN"
            pres = "NaN"
            vel_viento = "NaN"
            max_speed = "NaN"
            angle = "NaN"
            uvIndex = "NaN"

        print(temp, hum, pres, vel_viento, max_speed, angle, uvIndex)
        """Subir datos a ftp """

        estacion = LOCALIDAD
        tiempo  = datetime.now().strftime("%Y-%m-%d %H:%M")
        fecha1 = datetime.now().strftime("%Y-%m-%d")
        nombre =  estacion + fecha1 + ".txt"

       # data = nombre + "\t" + "-100\t" + "12V\t" + tiempo + "\t" + temp  + "\t" + hum + "\t" + pres + "\t" + uvIndex + "\r\n" 
        
        data = format(tiempo, tab) + format(temp, tab) + format(hum, tab) + format(pres, tab) + format(vel_viento, tab) + format(max_speed, tab) + format(angle, tab) + format(uvIndex, tab) + "\n"

        escribir_archivo(cabezera_estacion, data, nombre)
        upload_text_file(FTP_SERVER_IP, FTP_SERVER_USER, FTP_SERVER_PASS, FTP_SERVER_PATH, nombre)

if __name__ == "__main__":
    while True:
        try:
            main()
        except RuntimeError as error:
            continue
