import board
import busio
import digitalio
import adafruit_rfm9x

spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = digitalio.DigitalInOut(board.CE1)
reset = digitalio.DigitalInOut(board.D25)

rfm9x = adafruit_rfm9x.RFM9x(spi, cs, reset, 433.0)

rfm9x.signal_bandwidth = 125000
rfm9x.coding_rate = 4
rfm9x.spreading_factor = 7
rfm9x.enable_crc = True
rfm9x.tx_power = 20

while True:
    print("Sending packet...")
    rfm9x.send(b'Hello World!')
    packet = rfm9x.receive()
    if packet is not None:
        packet_text = str(packet, 'ascii')
        print('Received: {0}'.format(packet_text))

