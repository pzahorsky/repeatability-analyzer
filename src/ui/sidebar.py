import streamlit as st
import data_handler as dh

# -----------------------
# --- SIDEBAR BUTTONS ---
# -----------------------

def data_upload():
   return st.sidebar.file_uploader("📁 Upload CSV file", type="csv")

def subboard_selector(subboards):
   return st.sidebar.multiselect(
      "Select Sub-Boards",
      options = subboards,
      key="subboard_selection",
   )

def component_selector(components):
   return st.sidebar.multiselect(
      "Select Components",
      options = components,
      key="component_selection"
   )

def algorithm_selector(algorithm):
   return st.sidebar.multiselect(
      "Select Algorithms",
      options = algorithm,
      key="algorithm,_selection"
   )

def sample_val_selector(sample_vals):
   return st.sidebar.multiselect(
      "Select Sample Values",
      options = sample_vals,
      key="sample_vals_selection"
   )


