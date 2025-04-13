# # main.py
# import streamlit as st
# import cv2
# from ultralytics import YOLO
# import numpy as np

# from paho.mqtt import client as mqtt_client

# # MQTT Server Parameters
# MQTT = {
#     "client_id": "elrama-NOVA",
#     "broker": "broker.emqx.io",
#     "user": "ramael",
#     "password": "elrama",
#     "topic": "/HSC032/elrama/buzzer",
# }

# def connect_mqtt():
#     def on_connect(client, userdata, flags, reason_code, properties):
#         print(f"Connected with result code {reason_code}")
#         client.subscribe(MQTT['topic'])

#     mqttc = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2)
#     mqttc.on_connect = on_connect
#     mqttc.connect(MQTT['broker'], 1883, 60)

#     # mqttc.loop_forever()

#     return mqttc

# client = connect_mqtt()

# def send_notif_to_buzzer():
#     client.publish(MQTT['topic'], 'buzzer on')

# # Load model
# box_model = YOLO("model1.pt")
# crime_model = YOLO("crime_model.pt")
# weapon_model = YOLO("weapon_model.pt")
# model = YOLO("yolo11n.pt")

# # ESP32-CAM stream URL
# ESP32_STREAM_URL = "http://192.168.204.161:81/stream"

# # Streamlit UI
# st.title("🏠 Housing Security System")
# frame_placeholder = st.empty()


# # Stream processing
# cap = cv2.VideoCapture(1)

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         st.warning("No video from ESP32-CAM")
#         break

#     frame = cv2.resize(frame, (640, 480))
    
#     results = model(frame, conf=0.6)
#     annotated1 = results[0].plot()


#     box_results = box_model(annotated1, conf=0.8)
#     annotated2 = box_results[0].plot()

#     print(box_results[0].boxes.cls)

#     if 1 in box_results[0].boxes.cls:
#         send_notif_to_buzzer()

#     # box_results[0]

#     # crime_results = crime_model(annotated2)
#     # annotated3 = crime_results[0].plot()

#     # weapon_results = weapon_model(annotated3)
#     # annotated4 = weapon_results[0].plot()

#     frame_placeholder.image(annotated2, channels="BGR")

# detection_server.py
from flask import Flask, Response
import cv2
from ultralytics import YOLO

app = Flask(__name__)
cap = cv2.VideoCapture(0)  # Open webcam
model = YOLO("yolo11n.pt")  # Load YOLO model

def generate():
    while True:
        success, frame = cap.read()
        if not success:
            break

        # Perform detection on the frame
        results = model(frame)
        annotated_frame = results[0].plot()  # Annotated frame with detection results

        # Display the frame in an OpenCV window (optional)
        cv2.imshow("Detection Window", annotated_frame)

        # Wait for a keypress to close the window (optional)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # Encode frame as JPEG to stream it to the browser
        _, buffer = cv2.imencode('.jpg', annotated_frame)
        frame_bytes = buffer.tobytes()

        # Yield the frame for MJPEG streaming
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video')
def video():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
