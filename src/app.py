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
viewer, columns, metrics, scope, prelim, analysis, tolerance, results, export = ui_main.init_ui(
    state.has_value("data"),
    state.get_value("rename_columns"),
    state.get_value("sidebar_pipeline_done"),
    state.get_value("metrics_sel_done"),
    state.get_value("scope_sel_done"),
    state.get_value("fail_analysis_enabled")
)

# ---> UI RENDER
if viewer is not None:
    ui_main.render_view(viewer, state.get_value("data"))

if columns is not None:
    ui_main.rename_columns(columns)

if metrics is not None:
    ui_main.render_metrics(metrics)

    if not state.get_value("metrics_sel_done"):
        state.reset_states({
            "scope_sel_done" : False,
            "fail_analysis_enabled": False
        })

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
    viewer_mode = "prelim"

    if metrics is not None:
        data = dh.usl_lsl_glob_per(data, metrics["glob_limits"])
        data = dh.analytics(data, metrics["metrics"])
        state.set_value("data", data)

        data_prelim = dh.data_prelim_results(data, metrics["metrics"],
                                             viewer_mode)
        state.set_value("data_prelim", data_prelim)
        
        prelim_failed_rows = dh.prelim_failed_rows(data_prelim, 
                                                   metrics["metrics"],
                                                   viewer_mode)
        state.set_value("prelim_failed_rows", prelim_failed_rows)
        ui_main.render_prelim_results(data_prelim, metrics["metrics"], 
                                      prelim, results, viewer_mode)
"""
# CURENTLY SET TO ANALYZE ONLY PRELIM DATA !!!
if analysis is not None:
    data_prelim = state.get_value("data_prelim")
    prelim_failed_rows = state.get_value("prelim_failed_rows")
    metrics = state.get_value("metrics")

    data_prelim_failed = dh.data_for_analysis(data, prelim_failed_rows)
    figs = plt.fail_analysis_plotter(data_prelim_failed, metrics["metrics"])
    ui_main.render_fail_analysis(data_prelim_failed,
                                 analysis,
                                 figs,
                                 metrics)
"""
if tolerance is not None:
    data = state.get_value("data")
    tol_elements = dh.tolerances_elements(data)
    
    ui_main.render_tolerances(tolerance, tol_elements)
    data = dh.data_after_tolerances()
    state.set_value("data", data)

if results is not None:
    data = state.get_value("data")
    data_prelim = state.get_value("data_prelim")
    viewer_mode = "final"
    
    if state.get_value("tolerances_applied") is not None:
        data_results = dh.data_prelim_results(data, metrics["metrics"],
                                             viewer_mode)
        failed_rows = dh.prelim_failed_rows(data_results, metrics["metrics"], 
                                            viewer_mode)
        state.set_value("failed_rows", failed_rows)
        ui_main.render_prelim_results(data_results, metrics["metrics"], 
                                      prelim, results, viewer_mode)
    else:
        viewer_mode = "prelim_in_final"
        ui_main.render_prelim_results(data_prelim, metrics["metrics"], 
                                      prelim, results, viewer_mode)


# CURENTLY SET TO EXPORT ONLY PRELIM DATA !!!
if export is not None:
    viewer_mode = "final"
    data_prelim = state.get_value("data_prelim")
    metrics = state.get_value("metrics")

    export_plot = plt.results_export_plotter(data_prelim, 
                                             metrics["metrics"])
    ui_main.render_export_results(data,
                                  export_plot, 
                                  export, 
                                  metrics["metrics"])

            



    
    






    



    




