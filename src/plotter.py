import matplotlib.pyplot as plt
import re
import streamlit as st
import numpy as np

def fail_analysis_plotter(data, metrics):

    cols = ["Sub-board", "Component", "Algorithm Name", 
                  "Sample Name", "Pin Id", "Standard Deviation",
                  "Average", "USL_glob", "LSL_glob"]

    sample_value_reg = r"Sample Value \d+"

    sample_value_cols = [
        col for col in data.columns if re.search(sample_value_reg, col)]
    
    cols += sample_value_cols

    selector_cols = ["Sub-board", "Component", "Algorithm Name", 
                     "Sample Name", "Pin Id"]
    
    metric_col_map = {
    "cp": "Cp_glob",
    "cpk": "Cpk_glob",
    "cg": "Cg_glob",
    "cgk": "Cgk_glob"
}

    for metric, value in metrics.items():
        if value:
            selector_cols.append(metric_col_map[metric])
    

    col_uniques = {
        col: sorted(data[col].unique())
        for col in selector_cols
    }

    ready_to_plot = all(
       len(values) > 0
        for values in col_uniques.values()
)
    if not ready_to_plot:
        return None
    
    plots = {}

    grouped = data.groupby(selector_cols)

    for keys, group in grouped:
        plt.style.use("dark_background")
        fig, ax = plt.subplots(figsize=(12, 6))

        # --- X for plot
        values = (
            group[sample_value_cols]
            .astype(float)
            .to_numpy()
            .ravel()
        )
        values = values[~np.isnan(values)]

        # --- IQR Outlier Detection ---
        q1, q3 = np.percentile(values, [25, 75])
        iqr = q3 - q1
        low_thr = q1 - 1.5 * iqr
        high_thr = q3 + 1.5 * iqr

        core = values[(values >= low_thr) & (values <= high_thr)]
        outliers = values[(values < low_thr) | (values > high_thr)]

        # --- IQR not found anything, highlight extremes (Cp killers proxy)
        if len(outliers) == 0 and len(values) >= 5:
            mu = float(np.mean(values))
            sd = float(np.std(values, ddof=1)) if len(values) > 1 else 0.0
            if sd > 0:
                z = np.abs((values - mu) / sd)
                top_n = min(3, len(values))   # napr. top 3
                idx = np.argsort(z)[-top_n:]
                outliers = values[idx]        # použijeme ich len na zvýraznenie (nie ako "IQR outliers")

        # --- Histogram ---
        n = len(values)
        bins = min(30, max(10, int(np.sqrt(n))))
        ax.hist(core, bins=bins, alpha=0.85, label="Core distribution")
        if len(outliers):
            ax.hist(outliers, bins=bins, alpha=0.95, color="red", label="Outliers")

        if len(outliers):
            ymin, ymax = ax.get_ylim()
            _, bin_edges = np.histogram(values, bins=bins)
            bin_width = bin_edges[1] - bin_edges[0]

            for v in outliers:
                ax.add_patch(
                    plt.Rectangle(
                        (v - bin_width / 2, ymin),
                        bin_width,
                        ymax - ymin,
                        color="red",
                        alpha=0.8,
                        zorder=4
                    )
                )
                ax.text(
                    v,
                    ymax * 0.95,
                    f"{v:.2f}",
                    color="white",
                    ha="center",
                    va="top",
                    fontsize=10,
                    rotation=90,
                    zorder=5
                )

        # >>> ADDED (keep legend entry for outliers even without ax.hist(outliers))
        ax.plot([], [], color="red", linewidth=6, label="Outliers")
    # <<< ADDED

        # --- Limits ---
        lsl = group["LSL_glob"].iloc[0]
        usl = group["USL_glob"].iloc[0]

        sd = float(np.std(values, ddof=1)) if len(values) > 1 else 0.0

        # --- Tolerance Range ---
        ax.axvspan(lsl, usl, alpha=0.06, color="green", label="Spec window")
        if len(outliers) == 0 and len(values) >= 5:
            ax.axvspan(mu - 3*sd, mu + 3*sd, alpha=0.08, label="±3σ")

        # USL / LSL ticks
        ax.axvline(usl, linestyle="--", linewidth=1.5, color="orange", label=f"USL - {usl:.2f}")
        ax.axvline(lsl, linestyle="--", linewidth=1.5, color="orange", label=f"LSL - {lsl:.2f}")

        # Mean
        mean_val = float(np.mean(values))
        ax.axvline(mean_val, linestyle=":", linewidth=1.5, color="yellow", label=f"Mean - {mean_val:.2f}")

        # --- Rug & Outliers ---
        if len(outliers):
            y_min, y_max = ax.get_ylim()
            rug_y = np.full_like(outliers, y_min + 0.02 * (y_max - y_min))
            ax.plot(outliers, rug_y, "|", color="red", markersize=18, markeredgewidth=2)

        # --- Axes & Labels ---
        pad = (usl - lsl) * 0.25
        ax.set_xlim(lsl - pad, usl + pad)

        title = " - ".join(str(k) for k in keys)
        ax.set_title(f"Outliers: {len(outliers)} / {len(values)} (IQR)")

        ax.set_xlabel("Measured Value")
        ax.set_ylabel("Count")
        ax.grid(True, alpha=0.15)
        ax.legend(fontsize=11)

        plots[title] = {
            "fig": fig,
            "data": {
                "values": values,
                "outliers": outliers,
                "usl": usl,
                "lsl": lsl,
                "mean": mean_val,
                "stdev":sd
            }
        }

    return plots

def results_export_plotter(data, metrics):

    fig = None

    def cp_cpk_plotter(data, metrics):

        values = None
        cp_values = None
        cpk_values = None
        
        if metrics.get("Cp"):
            cp_values = data["Cp"].values
            values = cp_values
        if metrics.get("Cpk"):
            cpk_values = data["Cpk"].values
            if cp_values is None:
                values = cpk_values

        x = np.arange(1, len(values) + 1)

        fig, ax = plt.subplots(figsize=(10, 6))

        # Threshold lines
        if metrics.get("Cp"):
            ax.axhline(1.33, linestyle="--", 
                    label="Cp Acceptance Threshold",
                    color="#15db89",
                    linewidth = 1)
        if metrics.get("Cpk"):
            ax.axhline(1.67, linestyle=":", 
                    label="Cpk Acceptance Threshold",
                    color="seagreen",
                    linewidth = 2)

        if metrics.get("Cp"):
            ax.scatter(x, cp_values, label="Cp",
                        color= "#2dd2d2")
            ax.set_title("Cp Overview – All Characteristics")
            ax.set_ylabel("Cp")
            
        if metrics.get("Cpk"):
            ax.scatter(x, cpk_values, label="Cpk",
                    color="#f7c96e")
            ax.set_title("Cpk Overview – All Characteristics")
            ax.set_ylabel("Cpk")

        if metrics.get("Cp") and metrics.get("Cpk"):
            ax.set_title("Cp/Cpk Overview – All Characteristics")
            ax.set_ylabel("Cp/Cpk")

        ax.set_xlabel("Measurement Index")

        ax.set_xlim(0, len(values) + 1)
        ax.set_ylim(0,8)
        ax.legend()

        return fig
    
    def cg_cgk_plotter(data, metrics):
        values = None
        cg_values = None
        cgk_values = None
        
        if metrics.get("cg"):
            cg_values = data["Cg"].values
            values = cg_values
        if metrics.get("cgk"):
            cgk_values = data["Cgk"].values
            if cg_values is None:
                values = cgk_values

        x = np.arange(1, len(values) + 1)

        fig, ax = plt.subplots(figsize=(10, 6))

        # Threshold lines
        ax.axhline(1.33, linestyle="--", 
                label="Cg Acceptance Threshold",
                color="#15db89",
                linewidth = 1)
        ax.axhline(1.67, linestyle=":", 
                label="Cgk Acceptance Threshold",
                color="seagreen",
                linewidth = 2)

        if metrics.get("cg"):
            ax.scatter(x, cg_values,
                        label="Cg",
                        color= "#2dd2d2")
        if metrics.get("cgk"):
            ax.scatter(x, cgk_values,
                    label="Cgk",
                    color="#f7c96e")

        ax.set_title("Cg Overview – All Characteristics")
        ax.set_xlabel("Measurement Index")
        ax.set_ylabel("Cg")

        ax.set_xlim(0, len(values) + 1)
        ax.set_ylim(0,8)
        ax.legend()

        return fig
    
    if metrics.get("cp") or metrics.get("cpk"):
        fig = cp_cpk_plotter(data, metrics)

    if metrics.get("cg") or metrics.get("cgk"):
        fig = cg_cgk_plotter(data, metrics)           
    
    return fig


    

    

    
    