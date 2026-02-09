import streamlit as st

@st.cache_data(show_spinner=False)
def cached_call(_func, *args):
    return _func(*args)
