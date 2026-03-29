import streamlit as st

def clear_states():
    st.session_state.clear()

def reset_states(r_states):
    for state, value in r_states.items():
        st.session_state[state] = value

def init_state():
    default = {
        "data": None,
        "data_loaded": None,
        "data_pipeline": None,
        "data_scope": None,
        "data_before_analytics": None,
        "data_analytics": None,
        "data_prelim": None,
        "data_tolerances": None,
        "data_tolerances_analytics": None,
        "subboards": None,
        "components": None,
        "algorithms": None,
        "sample_vals": None,
        "sidebar_pipeline_done": False,
        "rename_columns": False,
        "Change_Sub-Board": "Sub-board",
        "Change_Component": "Component",
        "Change_Algorithm": "Algorithm Name",
        "Change_Sample_Value": "Sample Name",
        "Change_Element_Id": "Element Id",
        "Change_Element_Name": "Element Name",
        "Change_Mean": "Average",
        "Change_StDev": "Standard Deviation",
        "Change_Samples": "Sample Value",
        "last_loaded_config_name": None,
        "metrics_sel_done": False,
        "metrics": None,
        "scope_sel_done": False,
        "prelim_active": False,
        "prelim_failed_rows": None,
        "failed_rows": None,
        "fail_analysis_enabled": False,
        "analysis_mode": "Preliminary",
        "tolerances_active": False,
        "tolerances_dict": {},
        "tolerances_applied": False,
        "results_active": False,
        "export_active": False,
        "rename_columns_valid": False
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

def enforce_state_rules():
    s = st.session_state

    if not s.get("sidebar_pipeline_done", False):
        s["metrics_sel_done"] = False
        s["scope_sel_done"] = False
        s["fail_analysis_enabled"] = False
        s["tolerances_applied"] = False

    if not s.get("metrics_sel_done", False):
        s["scope_sel_done"] = False
        s["fail_analysis_enabled"] = False
        s["tolerances_applied"] = False

    if not s.get("scope_sel_done", False):
        s["fail_analysis_enabled"] = False
        s["tolerances_applied"] = False

    if not s.get("prelim_failed_rows"):
        s["fail_analysis_enabled"] = False
