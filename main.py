import network 
from sanduhr import Sanduhr
from webserver import webserver
from geheim import ssid, pwd

sanduhr = Sanduhr()

def init_webserver():
    webserver(lambda str: sanduhr.draw_time_from_str(str)).run_server()

def init_wifi_sta():
    station = network.WLAN(network.STA_IF)
    ap = network.WLAN(network.AP_IF)
    ap.active(False)
    station.active(True)
    station.connect(ssid, pwd)
    while not station.isconnected():
        machine.idle() # save power while waiting
    print('WLAN connection succeeded!')
    station.ifconfig()
    
def init_wifi_ap():
    ap = network.WLAN(network.AP_IF)
    station = network.WLAN(network.STA_IF)
    station.active(False)
    ap.active(True)
    print('WLAN spanned!')
    print(ap.ifconfig())

# init_webserver()
