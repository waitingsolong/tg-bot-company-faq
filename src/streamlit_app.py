import streamlit as st
from app import app_page
from handlers import bot_page

st.set_page_config(page_title="My App", layout="wide")

page = st.sidebar.selectbox("Select a page", ["App Info", "Bot Info"])

if page == "App Info":
    app_page()
elif page == "Bot Info":
    bot_page()
