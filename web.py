# streamlit_viewer.py
import streamlit as st

st.title("Real-time Surveillance Feed (using st.video)")

# MJPEG stream URL from Flask server
stream_url = "http://localhost:5001/video"

# Display MJPEG stream in Streamlit using st.video()
st.video(stream_url)
