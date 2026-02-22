import streamlit as st
import ui.sidebar as ui_side
import ui.main as ui_main
import data_handler as dh
import plotter as plt


# --- DATA LOAD ---
data = None
data_raw = ui_side.data_upload()

if data_raw:
    try:
        data = dh.data_load(data_raw)
    except ValueError as e:
        st.error(str(e))

if data is None:
    st.session_state.clear()

sidebar_pipe_done = False
components = None
algorithms = None
sample_vals = None
if "metrics_sel_done" not in st.session_state:
    st.session_state.metrics_sel_done = False
if "scope_sel_done" not in st.session_state:
    st.session_state.scope_sel_done = False
if "fail_analysis_enabled" not in st.session_state:
    st.session_state.fail_analysis_enabled = False

# --- SUBBOARD SELECTION ---
if data is not None:

    subboards = ui_side.subboard_selector(
        dh.get_subboards(data)
    )
    if subboards:
        data = dh.subboards_selected(data, subboards)

        # --- COMPONENT SELECTION ---
        components = ui_side.component_selector(
            dh.get_components(data)
        )
        if components:
            data = dh.components_selected(data, components)

            # --- ALGORITHM SELECTION ---
            algorithms = ui_side.algorithm_selector(
                dh.get_algorithms(data)
            )
            if algorithms:
                data = dh.algorithms_selected(data, algorithms)

                # --- SAMPLE VALUE SELECTION ---
                sample_vals = ui_side.sample_val_selector(
                    dh.get_sample_vals(data)
                )
                if sample_vals:
                    data = dh.sample_vals_selected(data, sample_vals)
                    sidebar_pipe_done = True

# --- UI INIT ---
viewer, metrics, scope, prelim, analysis, export = ui_main.init_ui(
    has_data = data is not None,
    sidebar_pipe_done = sidebar_pipe_done,
    metrics_sel_done = st.session_state.metrics_sel_done,
    scope_sel_done = st.session_state.scope_sel_done,
    fail_analysis_enabled = st.session_state.fail_analysis_enabled,
)

# --- UI RENDER ---
if viewer is not None:
    ui_main.render_view(viewer, data)

if metrics is not None:
    enabled_metrics = ui_main.render_metrics(metrics)
    
if scope is not None and components:
        pins = dh.scope_pins(data,components)
        if pins:
            selected_pins = ui_main.render_scope(scope,pins)
            data = dh.data_after_scope(data,selected_pins)
 
if prelim is not None and selected_pins:
    data = dh.usl_lsl_glob_per(data, enabled_metrics["limits"])
    data = dh.analytics(data, enabled_metrics["metrics"])
    data_for_prelim = dh.data_prelim_results(
                                             data,
                                             enabled_metrics["metrics"])
    failed_rows = dh.prelim_failed_rows(data_for_prelim,
                                        enabled_metrics["metrics"],
                                    )
    has_fails = bool(failed_rows)
    st.session_state.fail_analysis_enabled = has_fails
    ui_main.render_prelim_results(data_for_prelim,
                                  enabled_metrics["metrics"],
                                  prelim,
                                  failed_rows)

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

   
   
            



    
    






    



    




