"""Streamlit entrypoint for GPX Racer."""

import streamlit as st

st.set_page_config(page_title="GPX Racer", layout="wide")

st.title("GPX Racer")
st.write(
    "Upload two GPX routes and race them on the map page. "
    "Use the sidebar controls to sync movement, animate the race, and align starts."
)
st.page_link("pages/1_Race_Map.py", label="Open Race Map")
