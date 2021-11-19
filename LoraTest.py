"""
    Testeo de modulo LoRa RFM96x utilizando librerias de adafruit
"""
#Importamos las lbirerias necesarias

import time
from digitalio import DigitalInOut, Direction, Pull
import adafruit_rfm9x
import busio
import board


#Para debugging
import pdb

"""
    main function
"""
def main():

    print("Raspberry LoRa Gateway version 0.1")
    
    """Iniciamos el modulo RFM9x"""
    CS = DigitalInOut(board.CE1)
    RESET = DigitalInOut(board.D25)
    #creamos objeto SPI
    spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
    
    #Configure radio settings
       
    try:
        #creamos objeto rfm9x 
        rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, 915.0)
        print("RFM9x conectado con exito")
    except RuntimeError as error:
        print("RFM9x Error: ", error)
        exit()
    
    rfm9x.signal_bandwidth = 125000
    rfm9x.coding_rate = 4 
    rfm9x.spreading_factor = 7   
    rfm9x.enable_crc = True
    rfm9x.tx_power = 13 

    paquete_previo = None

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

if __name__ == "__main__":
    main()
