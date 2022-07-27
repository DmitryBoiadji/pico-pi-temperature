import network
import socket
import time
import machine
import utime
import urequests as requests

from machine import Pin

ssid = '{YOR_SSID}'
password = '{PASSWORD}'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    time.sleep(1)

if wlan.status() != 3:
    raise RuntimeError('network connection failed')
else:
    print('connected')
    status = wlan.ifconfig()
    print('ip = ' + status[0])

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(1)

while True:
    try:

        #Getting temperature from the sensor.
        sensor_temp = machine.ADC(4)
        conversion_factor = 3.3 / (65535)

        reading = sensor_temp.read_u16() * conversion_factor
        temperature = 27 - (reading - 0.706) / 0.001721
        temperature = round(temperature, 2)

        #Sending data to Prometheus pusher api gateway
        headers = {'X-Requested-With': 'Python requests', 'Content-type': 'text/xml'}
        url = "http://{Prometheus_IP}:9091/metrics/job/pico_stat/sensors/temperature"
        data = "sensors{pico=\"pi\"} " + str(temperature) + "\n"
        r = requests.post(url, headers=headers, data=data)
        print(r.reason)
        print(r.status_code)
        print(temperature)

        time.sleep(60);

    except OSError as e:
        print(e)
