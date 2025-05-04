from paho.mqtt import client as mqtt_client

# MQTT Server Parameters
MQTT = {
    "client_id": "elrama-NOVA",
    "broker": "broker.emqx.io",
    "user": "ramael",
    "password": "elrama",
    "topic": "/NOVA/elramaa/buzzer",
}

def connect_mqtt():
    def on_connect(client, userdata, flags, reason_code, properties):
        print(f"Connected with result code {reason_code}")
        client.subscribe(MQTT['topic'])

    mqttc = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2)
    mqttc.on_connect = on_connect
    mqttc.connect(MQTT['broker'], 1883, 60)

    return mqttc