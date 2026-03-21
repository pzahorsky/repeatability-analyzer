import streamlit as st

def clear_all_states():
    st.session_state.clear()

def init_state():
    default = {
        "data": None,
        "subboards": None,
        "components": None,
        "algorithms": None,
        "sample_vals": None,
        "sidebar_pipeline_done": False
    }

    for key, value in default.items():
        if key not in st.session_state:
            st.session_state[key] = value

def set_value(key, value):
    st.session_state[key] = value

def get_value(key):
    return st.session_state.get(key)

def has_value(key):
    return st.session_state.get(key) is not None