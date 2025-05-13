# Project Overview
<img src="images/logo.jpeg" width="200" height="200" /><br />
**SIGAP (Sistem Intelijen Garda Aman Pintar)** adalah suatu sistem pemantauan yang dilengkapi dengan AI untuk mendeteksi hal-hal mencurigakan dan melaporkannya secara langsung. Sistem ini menggunakan kamera dan esp32 untuk saling berkomunikasi dan dilengkapi dengan dashboard menggunakan streamlit dan ubidots.

# Hardware
- Webcam
- ESP32
- Buzzer
- Led

# Software
- YOLO untuk deteksi dan train model deteksi
- Ubidots untuk dashboard
- Streamlit untuk dashboard dengan ekstra fitur
- Python-3.10

# Technology Used
- OpenCV
- YOLO
- Supervision
- MQTT
- Face Recognition
- MongoDB

# YOLO Dataset Source
[I get the dataset from here](https://universe.roboflow.com/realm-43m3c/object-g1hep/)

# How To Run
1. First, install the dependencies for camera and dashboard app.
	```
	$ cd camera
	$ pip install -r requirements.txt
	$ cd dashboard
	$ pip install -r requirements.txt
	```
2. Second, run the stream detection application inside camera folder.<br/>
	```
	$ cd camera
	$ python main.py
	```
3. Third, run the streamlit. Configure the ip cam to view live stream of the webcam.
	```
	$ cd dashboard
	$ streamlit run Dashboard.py
	```