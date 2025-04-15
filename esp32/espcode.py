import network
import time
import ujson
from machine import Pin, PWM
import urequests as requests
from umqtt.simple import MQTTClient

# ====== MQTT Parameters ======
client_id = "ahmad-led"
broker = "broker.emqx.io"
user = ""
password = ""
topic = "/NOVA/elramaa/buzzer"

# ====== WiFi Connection ======
wifi_client = network.WLAN(network.STA_IF)
wifi_client.active(True)
print("Connecting device to WiFi...")
wifi_client.connect('Ahmd', '12345678')

while not wifi_client.isconnected():
    print("Connecting...")
    time.sleep(1)
print("WiFi Connected!")
print(wifi_client.ifconfig())

# ====== MQTT Server Connection ======
print("Connecting to MQTT server... ", end="")
client = MQTTClient(client_id, broker, user=user, password=password)
client.connect()
print('Connected to MQTT')

# ====== Setup Buzzer & LED ======
p23 = Pin(23, Pin.OUT)
buzzer = PWM(p23)
buzzer.duty(0)
buzzer.deinit()

led = Pin(13, Pin.OUT)

# ====== Bell Sound ======
def ding_dong():
    buzzer.init()
    buzzer.freq(1047)
    buzzer.duty(1023)
    time.sleep(0.5)
    buzzer.duty(0)
    time.sleep(0.1)

    buzzer.freq(784)
    buzzer.duty(300)
    time.sleep(0.5)
    buzzer.duty(0)
    buzzer.deinit()

# ====== Emergency Alarm + LED Blink ======
def emergency_alarm(duration=10):
    buzzer.init()
    buzzer.freq(1500)
    end_time = time.ticks_ms() + int(duration * 1000)

    while time.ticks_ms() < end_time:
        buzzer.duty(1023)
        led.value(1)
        time.sleep(0.2)
        buzzer.duty(0)
        led.value(0)
        time.sleep(0.2)

    buzzer.deinit()
    led.value(0)

# ====== MQTT Message Handler ======
def listener(b_topic, b_msg):
    topic = str(b_topic, 'utf-8')
    msg = str(b_msg, 'utf-8')
    print("Received:", msg)

    if msg.lower() == 'paket':
        ding_dong()
        client.publish(topic, "Ada paket")

    elif msg.lower() == 'bahaya':
        emergency_alarm(10)
        client.publish(topic, "Ada bahaya")

# ====== Subscribe and Loop ======
client.set_callback(listener)
client.subscribe(topic)

print("Menunggu pesan MQTT...")

while True:
    client.wait_msg()
