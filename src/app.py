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
        state.set_value("data_loaded",data)
    except ValueError as e:
        st.error(str(e))

# ---> SIDEBAR FILTER PIPELINE
if state.has_value("data_loaded"):

    data = state.get_value("data_loaded")

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
    
    state.set_value("data_pipeline", data)

# ---> UI INIT
ui = ui_main.init_ui()

if ui["viewer"] is not None:
    ui_main.render_view(ui["viewer"], state.get_value("data_pipeline"))

if ui["columns"] is not None:
    ui_main.rename_columns(ui["columns"])

if ui["metrics"] is not None:
    ui_main.render_metrics(ui["metrics"])

if ui["scope"] is not None:
    elements = dh.scope_elements(
        state.get_value("data_pipeline"),
        state.get_value("components"))
    if elements:
        selected_elements = ui_main.render_scope(ui["scope"], elements)
        data = dh.data_after_scope(state.get_value("data_pipeline")
                                   ,selected_elements)
        state.set_value("data_scope", data)

if ui["prelim"] is not None:
    metrics = state.get_value("metrics")
    data = state.get_value("data_scope")
    viewer_mode = "prelim"

    if metrics is not None:
        data = dh.usl_lsl_glob_per(data, metrics["glob_limits"])
        state.set_value("data_before_analytics", data)
        data = dh.analytics(data, metrics["metrics"])
        state.set_value("data_analytics", data)

        data_prelim = dh.data_prelim_results(data, metrics["metrics"],
                                             viewer_mode)
        state.set_value("data_prelim", data_prelim)
        
        prelim_failed_rows = dh.prelim_failed_rows(data_prelim, 
                                                   metrics["metrics"],
                                                   viewer_mode)
        state.set_value("prelim_failed_rows", prelim_failed_rows)
        ui_main.render_prelim_results(data_prelim, metrics["metrics"], 
                                      ui["prelim"], ui["results"], 
                                      viewer_mode)

# CURENTLY SET TO ANALYZE ONLY PRELIM DATA !!!        
if ui["analysis"] is not None:
    with ui["analysis"]:
        st.radio("Data Input",
                 options=["Preliminary", "Final"],
                 horizontal=True,
                 key = "analysis_mode",
                 label_visibility = "collapsed"
                )

    mode = state.get_value("analysis_mode")
    metrics = state.get_value("metrics")
    
    if mode == "Preliminary":
        data_analytics = state.get_value("data_analytics")
        data_prelim = state.get_value("data_prelim")
        prelim_failed_rows = state.get_value("prelim_failed_rows")

        data_prelim_failed = dh.data_for_analysis(data_analytics, 
                                                  prelim_failed_rows)
        figs = plt.fail_analysis_plotter(data_prelim_failed, metrics["metrics"],
                                         mode)
        ui_main.render_fail_analysis(data_prelim_failed,
                                 ui["analysis"],
                                 figs,
                                 metrics)
    
    elif mode == "Final":
        data_analytics_tolerances = state.get_value("data_tolerances_analytics")
        data_final = state.get_value("data_tolerances")
        final_failed_rows = state.get_value("failed_rows")
        
        if data_analytics_tolerances is not None:
            data_final_failed = dh.data_for_analysis(data_analytics_tolerances,
                                                     final_failed_rows)
            figs = plt.fail_analysis_plotter(data_final_failed, metrics["metrics"],
                                             mode)
            ui_main.render_fail_analysis(data_final_failed,
                                     ui["analysis"],
                                     figs,
                                     metrics)
        else:
            st.subheader("No tolerances applied")

if ui["tolerance"] is not None:
    data_for_analytics = state.get_value("data_before_analytics")

    if state.get_value("data_tolerances") is None:
        data = data_for_analytics.copy()
        data = data.rename(columns={
            "USL_glob": "Usl",
            "LSL_glob": "Lsl"
        })
    else: 
        data = state.get_value("data_tolerances").copy()

    tol_elements = dh.tolerances_elements(data)

    tolerances_applied = ui_main.render_tolerances(ui["tolerance"], 
                                                   tol_elements)
    state.set_value("tolerances_applied", tolerances_applied)
    
    if tolerances_applied:    
        data = dh.data_after_tolerances(data)
        state.set_value("data_tolerances", data)

        data = dh.data_tolerances_analytics(data, data_for_analytics)
        state.set_value("data_tolerances_analytics", data)

if ui["results"] is not None:
    data_prelim = state.get_value("data_prelim")

    if state.get_value("tolerances_applied"):
        viewer_mode = "final"

        data_final = state.get_value("data_tolerances")
        data_final = dh.data_prelim_results(data_final, metrics["metrics"],
                                             viewer_mode)
        failed_rows = dh.prelim_failed_rows(data_final, metrics["metrics"], 
                                            viewer_mode)
        state.set_value("failed_rows", failed_rows)
        state.set_value("data_tolerances", data_final)

        
        ui_main.render_prelim_results(data_final, metrics["metrics"], 
                                      ui["prelim"], ui["results"],
                                      viewer_mode)
        
    else:
        viewer_mode = "prelim_in_final"

        data_final = state.get_value("data_prelim")
        ui_main.render_prelim_results(data_prelim, metrics["metrics"], 
                                      ui["prelim"], ui["results"], 
                                      viewer_mode)


# CURENTLY SET TO EXPORT ONLY PRELIM DATA !!!
if ui["export"] is not None:
    data_prelim = state.get_value("data_prelim")
    metrics = state.get_value("metrics")

    export_plot = plt.results_export_plotter(data_prelim, 
                                             metrics["metrics"])
    ui_main.render_export_results(data_prelim,
                                  export_plot, 
                                  ui["export"], 
                                  metrics["metrics"])

# STATES DEBUG
"""
st.write({
    "data_pipeline": st.session_state.get("data_pipeline"),
    "rename_columns": st.session_state.get("rename_columns"),
    "sidebar_pipeline_done": st.session_state.get("sidebar_pipeline_done"),
    "metrics_sel_done": st.session_state.get("metrics_sel_done"),
    "scope_sel_done": st.session_state.get("scope_sel_done"),
    "fail_analysis_enabled": st.session_state.get("fail_analysis_enabled"),
})
  """    



    
    






    



    




