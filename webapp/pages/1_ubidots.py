import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="SIGAP Dashboard", layout="wide")

# st.write('<iframe src="https://stem.ubidots.com/app/dashboards/public/dashboard/tGw88bvE676IZBezlSO4G65Zrb-1OPJBUC_Vd_OI008?navbar=true&contextbar=false" width="100%" height="100%"></iframe>')
components.iframe("https://stem.ubidots.com/app/dashboards/public/dashboard/tGw88bvE676IZBezlSO4G65Zrb-1OPJBUC_Vd_OI008?navbar=true&contextbar=false", height=800, scrolling=True)