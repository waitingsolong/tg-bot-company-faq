import logs
import logging
import streamlit as st
import asyncio
from gather_info import initialize, gather_info_streamlit, faq_streamlit

# Initialize OpenAI API
initialize()

st.set_page_config(page_title="Company Info Bot", layout="wide")

# Initialize session state variables
if "page" not in st.session_state:
    st.session_state.page = "Bot"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "gather_info_status" not in st.session_state:
    st.session_state.gather_info_status = "idle"

async def show_chat_interface():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask a question about the company"):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        try:
            response = await faq_streamlit(prompt)
            if response:
                st.chat_message("assistant").markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            else:
                st.error("No response from FAQ.")
        except Exception as e:
            logging.error(f"Error during FAQ: {e}")
            st.error(f"Error during FAQ: {e}")

def gather_info(company_url):
    st.session_state.gather_info_status = "running"
    try:
        asyncio.run(gather_info_streamlit(company_url))
    except Exception as e:
        st.session_state.gather_info_status = "failed"
        logging.error(f"Error gathering info: {e}")
        st.error(f"Error gathering info: {e}")

if st.session_state.page == "Bot":
    st.title("Company Info Bot")

    company_name = st.text_input("Company Name", value="ExxonMobil")
    company_url = st.text_input("Company URL", value="https://corporate.exxonmobil.com/")
    
    if st.button("Gather Info"):
        gather_info(company_url)
        st.session_state.page = "Gather Info"

if st.session_state.page == "Gather Info":
    st.title("Gather Info")

    if st.session_state.gather_info_status == "running":
        st.write("Gathering information, please wait...")
    elif st.session_state.gather_info_status == "completed":
        st.write("Information gathered successfully!")
        st.session_state.page = "Chat"
    elif st.session_state.gather_info_status == "failed":
        st.write("Failed to gather information. Please try again.")
        if st.button("Back to Bot"):
            st.session_state.page = "Bot"

if st.session_state.page == "Chat":
    st.title("Chat with the Bot")
    st.write("Ask questions!")
    asyncio.run(show_chat_interface())
