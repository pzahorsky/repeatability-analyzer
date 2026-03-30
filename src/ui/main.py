import streamlit as st
import json

import pandas as pd
import base64
import data_handler as dh
import report as rp
import re


# ---> UI INIT <---
def init_ui():
    tab_defs = [
        {
            "key": "viewer",
            "label": "📑 Data Viewer",
            "show": st.session_state.get("data_pipeline") is not None,
        },
        {
            "key": "columns",
            "label": "🛠️ Rename columns",
            "show": st.session_state.get("rename_columns", False),
        },
        {
            "key": "metrics",
            "label": "📊 Metrics",
            "show": st.session_state.get("sidebar_pipeline_done", False),
        },
        {
            "key": "scope",
            "label": "🔍 Scope",
            "show": st.session_state.get("metrics_sel_done", False),
        },
        {
            "key": "prelim",
            "label": "📋 Prelim Results",
            "show": st.session_state.get("scope_sel_done", False),
        },
        {
            "key": "analysis",
            "label": "⚠️ Fail Analysis",
            "show": st.session_state.get("fail_analysis_enabled", False),
        },
        {
            "key": "tolerance",
            "label": "📏 Tolerances",
            "show": st.session_state.get("scope_sel_done", False),
        },
        {
            "key": "results",
            "label": "📈 Results",
            "show": st.session_state.get("scope_sel_done", False),
        },
        {
            "key": "export",
            "label": "💾 Export Results",
            "show": st.session_state.get("scope_sel_done", False),
        },
    ]

    visible_tabs = [tab for tab in tab_defs if tab["show"]]

    if not visible_tabs:
        return {
            "viewer": None,
            "columns": None,
            "metrics": None,
            "scope": None,
            "prelim": None,
            "analysis": None,
            "tolerance": None,
            "results": None,
            "export": None,
        }

    tab_labels = [tab["label"] for tab in visible_tabs]
    created_tabs = st.tabs(tab_labels)

    ui = {
        "viewer": None,
        "columns": None,
        "metrics": None,
        "scope": None,
        "prelim": None,
        "analysis": None,
        "tolerance": None,
        "results": None,
        "export": None,
    }

    for tab_def, tab_obj in zip(visible_tabs, created_tabs):
        with tab_obj:
            if tab_def["key"] == "viewer":
                ui["viewer"] = st.empty()
            else:
                ui[tab_def["key"]] = st.container()

    return ui

# ---> DATA VIEWER <---
def render_view(viewer, data):
    if data is None:
        return

    n = len(data)
    height = min(40 + n * 35,700)
    with viewer:
        st.set_page_config(layout="wide")
        st.dataframe(
            data,
            width="stretch",
            height=height)
        
# ---> RENAME COLUMNS <---
def rename_columns(columns):

    data = st.session_state["data_loaded"]

    if "loaded_rename_config" in st.session_state:
            loaded = st.session_state["loaded_rename_config"]

            st.session_state["Change_Sub-Board"] = loaded.get("Sub-Board", "")
            st.session_state["Change_Component"] = loaded.get("Component", "")
            st.session_state["Change_Algorithm"] = loaded.get("Algorithm", "")
            st.session_state["Change_Sample_Value"] = loaded.get("Sample Value", "")
            st.session_state["Change_Element_Id"] = loaded.get("Element Id", "")
            st.session_state["Change_Element_Name"] = loaded.get("Element Name", "")
            st.session_state["Change_Mean"] = loaded.get("Mean", "")
            st.session_state["Change_StDev"] = loaded.get("StDev", "")
            st.session_state["Change_Samples"] = loaded.get("Sample Value Columns", "")

            del st.session_state["loaded_rename_config"]

    with columns:    
        static_text, input_text, static_text2, input_text2 = st.columns([1,1,1,1])
        static_text.markdown("**Reference Column Name**")
        input_text.markdown("**New Column Name**")
        static_text2.markdown("**Reference Column Name**")
        input_text2.markdown("**New Column Name**")
        
        static_text, input_text, static_text2, input_text2 = st.columns([1,1,1,1])  
        static_text.text("Sub-Board")
        input_text.text_input("Sub-Board", key="Change_Sub-Board",
                               value = "Sub-board", 
                               label_visibility = "collapsed")
        static_text2.text("Element Id")
        input_text2.text_input("Element Id", key="Change_Element_Id",
                               value = "Element Id", 
                               label_visibility = "collapsed")

        static_text, input_text, static_text2, input_text2 = st.columns([1,1,1,1])  
        static_text.text("Component")
        input_text.text_input("Component", key="Change_Component",
                               value = "Component", 
                               label_visibility = "collapsed")
        static_text2.text("Element Name")
        input_text2.text_input("Element Name", key = "Change_Element_Name",
                               value = "Element Name",
                               label_visibility = "collapsed")

        static_text, input_text, static_text2, input_text2 = st.columns([1,1,1,1])  
        static_text.text("Algorithm")
        input_text.text_input("Algorithm", key="Change_Algorithm",
                               value = "Algorithm Name", 
                               label_visibility = "collapsed")
        static_text2.text("Mean")
        input_text2.text_input("Mean", key="Change_Mean",
                               value = "Average",
                               label_visibility = "collapsed")      

        static_text, input_text, static_text2, input_text2 = st.columns([1,1,1,1])  
        static_text.text("Sample Value")
        input_text.text_input("Sample Value", key="Change_Sample_Value",
                               value = "Sample Name", 
                               label_visibility = "collapsed")
        static_text2.text("Standard Deviation")
        input_text2.text_input("StDev", key = "Change_StDev",
                              value = "Standard Deviation",
                              label_visibility = "collapsed")
        
        static_text, input_text, static_text2, input_text2 = st.columns([1,1,1,1])
        static_text.text("Measured Values")
        input_text.text_input("Sample Value Columns", key = "Change_Samples",
                              value = "Sample Value",
                              label_visibility = "collapsed")
        
        st.markdown("---")

        load_config, save_config, close_window, rgap= st.columns([1,1,1,1])

        config_file = load_config.file_uploader(
            "📁 Upload Configuration file file", type="json")
        save_config.markdown("💾 Save configuration to file")
        
        if config_file is not None and st.session_state.get("last_loaded_config_name") != config_file.name:
            config = json.load(config_file)

            st.session_state["loaded_rename_config"] = {
                "Sub-Board": config.get("Sub-Board",""),
                "Component": config.get("Component", ""),
                "Algorithm": config.get("Algorithm", ""),
                "Sample Value": config.get("Sample Value", ""),
                "Sample Value Columns": config.get("Sample Value Columns", ""),
                "Element Id": config.get("Element Id", ""),
                "Element Name": config.get("Element Name", ""),
                "Mean": config.get("Mean", ""),
                "StDev": config.get("StDev", "")
            }
            st.session_state["last_loaded_config_name"] = config_file.name
            st.rerun()

        rename_map = {
            "Sub-Board": st.session_state.get("Change_Sub-Board", ""),
            "Component": st.session_state.get("Change_Component", ""),
            "Algorithm": st.session_state.get("Change_Algorithm", ""),
            "Sample Value": st.session_state.get("Change_Sample_Value", ""),
            "Sample Value Columns": st.session_state.get("Change_Samples", ""),
            "Element Id": st.session_state.get("Change_Element_Id", ""),
            "Element Name": st.session_state.get("Change_Element_Name", ""),
            "Mean": st.session_state.get("Change_Mean", ""),
            "StDev": st.session_state.get("Change_StDev", "")
        }

        # ---> GUARD - INCORECT COLUMN NAMES <---
        mapped_values = {
            key: value.strip()
            for key, value in rename_map.items()
            if isinstance(value, str) and value.strip()
        }

        data_columns = set(data.columns)

        missing_mapped = {}

        for key, value in mapped_values.items():

            if key == "Sample Value Columns":
                pattern = re.escape(value)
                matches = [col for col in data.columns if re.search(pattern, col)]

                if not matches:
                    missing_mapped[key] = value

                st.session_state["matched_sample_columns"] = matches

            else:
                if value not in data_columns:
                    missing_mapped[key] = value

        empty_mapped = [
            key for key, value in rename_map.items()
            if not isinstance(value, str) or not value.strip()
        ]

        if empty_mapped:
            st.warning("Empty mappings:")
            for key in empty_mapped:
                st.markdown(f"- {key}")

        if missing_mapped:
            st.error("Mapped columns not found in dataset:")
            for key, value in missing_mapped.items():
                st.markdown(f"- **{key}** → `{value}`")

        mapping_valid = not empty_mapped and not missing_mapped
        st.session_state["rename_columns_valid"] = mapping_valid
        # ---> GUARD ENDS HERE <---
        
        json_bytes = json.dumps(rename_map, indent=4).encode("utf-8")

        save_config.download_button(
            "Save",
            data=json_bytes,
            file_name="rename_columns.json",
            mime="application/json",
            use_container_width=True
)
        close_window.markdown("🔚 Close Configurator")
        close_tab = close_window.button("Close", use_container_width=True)

        if close_tab:
            if not st.session_state.get("rename_columns_valid", False):
                st.error("Cannot close configurator. Some mappings are empty or missing in dataset.")
                st.stop()
            else:
                st.session_state["rename_columns"] = False
                st.session_state["rename_columns_confirmed"] = True
                st.session_state["last_loaded_config_name"] = None
                st.rerun()
                   
# ---> METRICS <---
def render_metrics(metrics):
    
    with metrics:

        # --- HEADER ---
        h1, h2, h3, h4 = st.columns([1.5, 5, 3.5, 1], vertical_alignment="center")
        h1.markdown("**Metric**")
        h2.markdown("**Description**")
        h3.markdown("**Formula**")
        h4.markdown("**Enable**")

        st.divider()

        metrics_dict = {
            "metrics": {},
            "glob_limits": {},
        }

        rows = [
            {
                "key": "cp",
                "name": "Cp",
                "desc": (
                    "Cp (Process Capability Index) compares the process spread (6σ) "
                    "to the specification width (USL − LSL), assuming the process is centered."
                ),
                "formula": r"$C_p = \dfrac{USL - LSL}{6\sigma}$",
            },
            {
                "key": "cpk",
                "name": "Cpk",
                "desc": (
                    "Cpk considers both process spread and centering by comparing the "
                    "distance to the nearest specification limit."
                ),
                "formula": (
                    r"$C_{pk} = \min\left("
                    r"\dfrac{USL - \mu}{3\sigma},"
                    r"\dfrac{\mu - LSL}{3\sigma}"
                    r"\right)$"
                ),
            },
            {
                "key": "cg",
                "name": "Cg",
                "desc": (
                    "Cg (Gauge Capability) evaluates the measuring system variation "
                    "relative to the tolerance width."
                ),
                "formula": r"$C_g = \dfrac{USL - LSL}{6\sigma_{g}}$",
            },
            {
                "key": "cgk",
                "name": "Cgk",
                "desc": (
                    "Cgk evaluates both the variation and bias of the measuring system "
                    "relative to the specification limits."
                ),
                "formula": (
                    r"$C_{gk} = \min\left("
                    r"\dfrac{USL - \mu_g}{3\sigma_g},"
                    r"\dfrac{\mu_g - LSL}{3\sigma_g}"
                    r"\right)$"
                ),
            },
        ]

        def _update_metrics_state():
            st.session_state.metrics_sel_done = any(
                st.session_state.get(f"metric_enabled{r['key']}", False)
                for r in rows
            )

        for row in rows:
            metric_id = row["key"]

            disabled = (
                (metric_id in ["cp", "cpk"] and any(st.session_state.get(f"metric_enabled{k}", False) for k in ["cg", "cgk"]))
                or
                (metric_id in ["cg", "cgk"] and any(st.session_state.get(f"metric_enabled{k}", False) for k in ["cp", "cpk"]))
            )
            
            c1, c2, c3, c4 = st.columns([1.5, 4.5, 4, 1])

            c1.markdown(f"**{row['name']}**")
            c2.caption(row["desc"])
            c3.markdown(row["formula"], unsafe_allow_html=True)

            metrics_dict["metrics"][metric_id] = c4.checkbox(
                "",
                key=f"metric_enabled{metric_id}",
                disabled=disabled,
                on_change=_update_metrics_state)

            st.markdown("---")
        
        st.markdown("---")
        c1, c2, c3, c4, c5= st.columns([1.5, 4.5, 2.5, 1.25, 1.25])

        c1.markdown("**USL, LSL**")
        c2.caption("Global preliminary tolerance limits defining the acceptable minimum and maximum values. "
                   "Defined as a percentage relative to a reference value (e.g. the mean).")
        c3.markdown(r"$USL, LSL = \mu \pm \mu \cdot \frac{p}{100}$")
        tolerance_usl = c4.number_input(
                            "",
                            min_value=0.0,
                            max_value=100.0,
                            value=10.0,
                            step=1.0,
                            key="usl_input",
                            label_visibility="collapsed"
                        )
        tolerance_lsl = c5.number_input(
                            "",
                            min_value=0.0,
                            max_value=100.0,
                            value=10.0,
                            step=1.0,
                            key="lsl_input",
                            label_visibility="collapsed"
                        )
        metrics_dict["glob_limits"]["USL"] = tolerance_usl
        metrics_dict["glob_limits"]["LSL"] = tolerance_lsl

        st.session_state["metrics"] = metrics_dict

# ---> SCOPE <---
def render_scope(scope, elements):
    with scope:

        c0, c1 = st.columns([0.15, 8])
        
        with c1:
            all_elements = st.button(
                                 "Select all elements for selected components")
        
        st.markdown("---")

        c1, c2 = st.columns([2,8])
        c1.markdown("**Components**")
        c2.markdown("**Elements**")

        selection_dict = {}

        for component, elements in elements.items():

            int_elements = [int(p) for p in elements]

            key = f"multiselect_{component}"

            if all_elements:
                st.session_state[key] = int_elements
            
            c1, c2 = st.columns([2,8],vertical_alignment="center")

            c1.markdown(f"**{component}**")
            selected_elements = c2.multiselect(
                                "",
                                options=int_elements,
                                key=key
                            )
            selection_dict[component] = selected_elements
            st.markdown("---")

        return selection_dict

# ---> PRELIM RESULTS <--- 
def render_prelim_results(data, enabled_metrics, prelim, results, viewer_mode):

    if data is None:
        return
    
    if viewer_mode == "prelim":
        failed_rows = st.session_state["prelim_failed_rows"]
        if failed_rows:
            st.session_state["fail_analysis_enabled"] = True
        else:
            st.session_state["fail_analysis_enabled"] = False
    elif viewer_mode == "final":
        failed_rows = st.session_state["failed_rows"]
        analysis_enabled = st.session_state["fail_analysis_enabled"]
    elif viewer_mode == "prelim_in_final":
        failed_rows = st.session_state["prelim_failed_rows"]
        analysis_enabled = st.session_state["fail_analysis_enabled"]
        
    n = len(data)
    height = min(40 + n * 35, 700)

    def style_capability_row(row):
        styles = [""] * len(row)

        if row.name not in failed_rows:
            return ["background-color: rgba(46, 204, 113, 0.15)"] * len(row)

        for i, col in enumerate(row.index):
            for m, enabled in enabled_metrics.items():
                if enabled and col in ["Cp_glob", "Cpk_glob", "Cg_glob", "Cgk_glob"]:
                    if row[col] < 1.33:
                        styles[i] = (
                            "background-color: rgba(231, 76, 60, 0.35);"
                            "font-weight: 600;"
                        )
        return styles

    styled_data = data.style.apply(style_capability_row, axis=1)

    if viewer_mode == "prelim":
        with prelim:
            st.dataframe(styled_data, height=height)
    if viewer_mode == "final":
        with results:
            st.dataframe(styled_data, height=height)
    if viewer_mode == "prelim_in_final":
        with results:
            st.subheader("Adittional Tolerances not applied"
                     " - Showing Preliminary Results")
            st.dataframe(styled_data, height=height)

# ---> FAIL ANALYSIS <---
def render_fail_analysis(data, analysis, figs, metrics):

    if "step_idx" not in st.session_state:
        st.session_state.step_idx = 0
    
    def title_to_df(title: str) -> pd.DataFrame:
        parts = [p.strip() for p in title.split(" - ")]
        
        mean_col = st.session_state["Change_Mean"]
        stdev_col = st.session_state["Change_StDev"]

        info_row = {
            "Sub-board": int(parts[0]),
            "Component": parts[1],
            "Algorithm": parts[2],
            "Output": parts[3],
            "Element Id": int(float(parts[4])),
        } 

        data_cop = data.copy()

        for col, val in info_row.items():
            if col == "Algorithm":
                col = "Algorithm Name"
            if col == "Output":
                col = "Sample Name"
            data_cop = data_cop[data_cop[col] == val]

        mean_val = data_cop[mean_col].iloc[0]
        stdev_val = data_cop[stdev_col] .iloc[0]
        count_row = 5
        calc_row = {
            "Mean":mean_val,
            "StDev":stdev_val
        }
        
        for metric, value in metrics["metrics"].items():
            if value:
                metric = metric.capitalize()
                calc_row[metric] = parts[count_row]
                count_row += 1

        return pd.DataFrame([info_row]), pd.DataFrame([calc_row])
    
    def style_row(row):
        styles = [""] * len(row)
        for i, col in enumerate(row.index):
            if col in ["Cp", "Cpk"]:
                try:
                    val = float(row[col])
                except (TypeError, ValueError):
                    continue
                styles[i] = (
                    "background-color: rgba(46,204,113,0.25)"
                    if val >= 1.33
                    else "background-color: rgba(231,76,60,0.35)"
                    )
        return styles

    with analysis:

        if figs is None or len(figs) == 0:
            st.warning("No data for analysis")
            return

        titles = list(figs.keys())
        n = len(titles)

        # safety
        st.session_state.step_idx = max(0, min(st.session_state.step_idx, n - 1))

        title = titles[st.session_state.step_idx]
        plot = figs[title]
        fig = plot["fig"]
        ctx = plot["data"]

        # COUNTS ONLY WITH ONE OUTLIER VALUE
        data_fail_extracted = dh.fail_extractor(ctx)

        c1, c2 = st.columns([5.5, 4.5])

        info_table, calc_table = title_to_df(title)

        # -------- LEFT: GRAPH --------
        with c1:
            st.dataframe(info_table,
                         hide_index=True, 
                         use_container_width=True)
            
            st.pyplot(fig, use_container_width=True)

        with c1:
            counter , c_prev, c_next, space = st.columns([1.25,2,2,1.25])

        with c_prev:
            st.button(
                "◄ Previous",
                use_container_width=True,
                disabled=st.session_state.step_idx == 0,
                on_click=lambda: st.session_state.update(
                    step_idx=st.session_state.step_idx - 1
                ),
            )

        with c_next:
            st.button(
                "► Next",
                use_container_width=True,
                disabled=st.session_state.step_idx == n - 1,
                on_click=lambda: st.session_state.update(
                    step_idx=st.session_state.step_idx + 1
                ),
            )
        with counter:
            st.caption(f"{st.session_state.step_idx + 1} / {n}")

        # -------- RIGHT: TABLE --------
        with c2:

            st.dataframe(calc_table.style.apply(style_row, axis=1),
                         hide_index=True, 
                         use_container_width=True)

            st.markdown("")

            st.dataframe(data_fail_extracted,
                         hide_index=True)

# ---> TOLERANCES <---
def render_tolerances(tolerance, tol_elements):

    tolerances_dict = st.session_state["tolerances_dict"]

    with tolerance:
        c1, c2, c3, c4 = st.columns([1,1,1.25,2])
        c1.markdown("**Sample Value**")
        c2.markdown("**Elements**")
        c3.markdown("**Symmetric / Asymmetric**")
        with c4:
            sc1, sc2, sc3, sc4, sc5 = st.columns([1,1,1,1,1])
            sc1.markdown("**Target**")
            sc2.markdown("**Type**")
            sc3.markdown("**Delta**")
            sc4.markdown("**USL**")
            sc5.markdown("**LSL**")

        st.markdown("---")

        for sample_name, element in tol_elements.items():

            if sample_name not in tolerances_dict:
                tolerances_dict[sample_name] = {}

            elements = [e for e in element]
            
            key_select = f"select_{sample_name}"
            key_radio = f"radio_{sample_name}"
            key_target = f"target_{sample_name}"
            key_type = f"type_{sample_name}"
            key_delta = f"delta_{sample_name}"
            key_usl = f"usl_{sample_name}"
            key_lsl = f"lsl_{sample_name}"

            c1, c2, c3, c4 = st.columns([1,1,1.25,2])
            c1.markdown(f"{sample_name}")
            selected_elements = c2.selectbox(
                                "",
                                options = elements,
                                key = key_select,
                                label_visibility = "collapsed"
                            )

            with c3:
                c3c1, c3c2, c3c3 = st.columns([1,2,1])
             
                tolerance_type = c3c2.radio(
                                    "Tolerance Type",
                                    options=["Sym", "Asym"],
                                    horizontal=True,
                                    key = key_radio,
                                    label_visibility = "collapsed"

                                )
            
            with c4:
                
                usl = None
                lsl = None

                c4c1, c4c2, c4c3, c4c4, c4c5 = st.columns([1,1,1,1,1])

                if tolerance_type == "Sym":
                    target = c4c1.text_input(f"target_{sample_name}",
                                    label_visibility = "collapsed",
                                    key = key_target,)
                    
                    type = c4c2.selectbox(f"type_{sample_name}",
                                label_visibility = "collapsed",
                                options = ["Const", "%"],
                                key = key_type)
                    delta = c4c3.text_input(f"delta_{sample_name}",
                                    label_visibility = "collapsed",
                                    key = key_delta)

                    target = float(target) if target.strip() else None
                    delta = float(delta) if delta.strip() else None

                    if type == "Const":
                        if target is not None and delta is not None:
                            usl = target + delta
                            lsl = target - delta
                    elif type == "%":
                        if target is not None and delta is not None:
                            usl = target + target*(delta / 100)
                            lsl = target - target*(delta / 100)

                    c4c4.text(f"{usl}")
                    c4c5.text(f"{lsl}")

                elif tolerance_type == "Asym":
                    target = None
                    usl = c4c4.text_input(f"usl_{sample_name}",
                                           label_visibility = "collapsed",
                                           key = key_usl)
                    lsl = c4c5.text_input(f"lsl_{sample_name}",
                                          label_visibility = "collapsed",
                                          key = key_lsl)
                    
                    usl = int(usl) if usl.strip() else None
                    lsl = int(lsl) if lsl.strip() else None

            if usl is not None and lsl is not None:
                tolerances_dict[sample_name][selected_elements] = {
                    "target": target,
                    "usl": usl,
                    "lsl": lsl
                }

    tolerances_applied = any(
        element.get("usl") is not None and not pd.isna(element.get("usl")) and
        element.get("lsl") is not None and not pd.isna(element.get("lsl"))
        for sample in tolerances_dict.values()
        for element in sample.values()
        )
    

    st.session_state["tolerances_applied"] = tolerances_applied

    return tolerances_applied

# ---> EXPORT < ---             
def render_export_results(data, fig, export, metrics):

    def show_pdf(pdf_bytes: bytes, height: int = 800):
        b64 = base64.b64encode(pdf_bytes).decode("utf-8")
        st.components.v1.html(
            f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="{height}" style="border:none;"></iframe>',
            height=height,
    )

    with export:

        c1, c2, c3 = st.columns([3,3,3])

        with c1:
            customer_name = st.text_input("Customer Name")
        with c2:
            product_name = st.text_input("Product Name")
        with c3:
            creator_name = st.text_input("Created By")

        if st.button("Generate PDF", type="primary"):
            st.session_state.pdf_bytes = rp.build_pdf(data,
                                                      metrics,
                                                      fig, 
                                                      customer_name,
                                                      product_name,
                                                      creator_name)
        pdf_bytes = st.session_state.get("pdf_bytes")
        if pdf_bytes:
            #show_pdf(pdf_bytes)

            st.download_button(
            "Download PDF",
            data=pdf_bytes,
            file_name="report.pdf",
            mime="application/pdf",
        )


            
            
        




