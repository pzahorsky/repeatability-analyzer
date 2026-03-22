import streamlit as st

import state
import ui.sidebar as ui_side
import ui.main as ui_main
import data_handler as dh
import plotter as plt

# ---> APP STATE INIT <---
state.init_state()

# ---> RENAME COLUMNS <---
if ui_side.rename_columns():
    state.set_value("rename_columns", True)

# ---> DATA LOADER <---
data_uploaded = ui_side.data_upload()

if data_uploaded is None:
    state.clear_states()
    st.stop()

if data_uploaded:
    try:
        data = dh.data_load(data_uploaded)
        state.set_value("data",data)
    except ValueError as e:
        st.error(str(e))

# ---> SIDEBAR FILTER PIPELINE
if state.has_value("data"):

    data = state.get_value("data")

    state.set_value("sidebar_pipeline_done", False)

    subboards = ui_side.subboard_selector(
                    dh.get_subboards(data)
                    )
    state.set_value("subboards", subboards)

    if subboards:
        data = dh.subboards_selected(data, subboards)

        components = ui_side.component_selector(
                    dh.get_components(data)
        )
        state.set_value("components", components)

        if components:
            data = dh.components_selected(data, components)

            algorithms = ui_side.algorithm_selector(
                dh.get_algorithms(data)
            )
            state.set_value("algorithms", algorithms)

            if algorithms:
                data = dh.algorithms_selected(data, algorithms)

                sample_vals = ui_side.sample_val_selector(
                    dh.get_sample_vals(data)
                )
                state.set_value("sample_vals", sample_vals)

                if sample_vals:
                    data = dh.sample_vals_selected(data, sample_vals)

                    state.set_value("sidebar_pipeline_done", True)
    
    state.set_value("data", data)

# ---> UI INIT
viewer, columns, metrics, scope, prelim, tolerance = ui_main.init_ui(
    state.has_value("data"),
    state.get_value("rename_columns"),
    state.get_value("sidebar_pipeline_done"),
    state.get_value("metrics_sel_done"),
    state.get_value("scope_sel_done")
)

# ---> UI RENDER
if viewer is not None:
    ui_main.render_view(viewer, state.get_value("data"))

if columns is not None:
    ui_main.rename_columns(columns)

if metrics is not None:
    ui_main.render_metrics(metrics)

if scope is not None:
    elements = dh.scope_elements(
        state.get_value("data"),
        state.get_value("components"))
    if elements:
        selected_elements = ui_main.render_scope(scope, elements)
        data = dh.data_after_scope(state.get_value("data")
                                   ,selected_elements)
        state.set_value("data", data)

if prelim is not None:
    metrics = state.get_value("metrics")
    data = state.get_value("data")

    data = dh.usl_lsl_glob_per(data, metrics["glob_limits"])
    data = dh.analytics(data, metrics["metrics"])
    state.set_value("data", data)

    data_prelim = dh.data_prelim_results(data, metrics["metrics"])
    state.set_value("data_prelim", data_prelim)
    
    dh.prelim_failed_rows(data_prelim, metrics["metrics"])
    ui_main.render_prelim_results(data_prelim, metrics["metrics"], prelim)

if tolerance is not None:
    pass

"""
# --- UI INIT ---
analysis, export = ui_main.init_ui(
    fail_analysis_enabled = st.session_state.fail_analysis_enabled,
)

# --- UI RENDER ---
 

if analysis is not None and has_fails:
    data_failed = dh.data_for_analysis(data, failed_rows)
    figs = plt.fail_analysis_plotter(data_failed,enabled_metrics["metrics"])
    ui_main.render_fail_analysis(data_failed,
                                 analysis,
                                 figs,
                                 enabled_metrics["metrics"])
    
if export is not None:
    export_plot = plt.results_export_plotter(data_for_prelim, 
                                             enabled_metrics["metrics"])
    ui_main.render_export_results(data,
                                  export_plot, 
                                  export, 
                                  enabled_metrics["metrics"])
"""
   
   
            



    
    






    



    




