import pandas as pd
import numpy as np


# -------------------
# ----- SIDEBAR -----
# -------------------

# --- DATA LOADER ---
def data_load(up_data) -> pd.DataFrame:
    if up_data is None:
        raise ValueError("No file uploaded")
    
    try:
        df = pd.read_csv(up_data)
    except pd.errors.EmptyDataError:
        raise ValueError("CSV file is empty")
    except pd.errors.ParserError:
        raise ValueError("CSV file is malformed")
    except UnicodeDecodeError:
        raise ValueError("Unsupported file encoding")
    except Exception as e:
        raise ValueError(f"Failed to load CSV file: {e}")
    
    if df.empty:
        raise ValueError("CSV contains no rows")
    
    return df


# --- SUB BOARD FILTER --- 
def get_subboards(data):
    return sorted(data["Sub-board"].dropna().unique())

def subboards_selected(data, selection):
    return data[data["Sub-board"].isin(selection)]

# --- COMPONENT FILTER ---
def get_components(data):
    return sorted(data["Component"].dropna().unique())

def components_selected(data, selection):
    return data[data["Component"].isin(selection)]

# --- ALGORITHM FILTER ---
def get_algorithms(data):
    return sorted(data["Algorithm Name"].dropna().unique())

def algorithms_selected(data, selection):
    return data[data["Algorithm Name"].isin(selection)]

# --- SAMPLE VALUE FILTER ---
def get_sample_vals(data):
    return sorted(data["Sample Name"].dropna().unique())

def sample_vals_selected(data, selection):
    return data[data["Sample Name"].isin(selection)]

# -----------------    
# --- SCOPE TAB ---
# -----------------

def scope_pins(data, components):
    scoped = data[data["Component"].isin(components)].dropna()
    
    return (
        scoped
        .groupby("Component")["Pin Id"]
        .apply(lambda s: sorted(s.dropna().unique()))
        .to_dict()
    )

# ---------------------------------------
# --- DATA FILTER AFTER PIN SELECTION ---
# ---------------------------------------

def data_after_scope(data, comps_and_pins):
    mask = data.apply(
        lambda row: (
            row["Component"] in comps_and_pins
            and row["Pin Id"] in comps_and_pins[row["Component"]]
        ),
        axis=1
    )

    return data[mask]

# ---------------------
# --- ANALYTIC FUNC ---
# ---------------------

def usl_lsl_glob_per(data, limits):
    data = data.copy()

    mean = data["Average"].abs()
    usl = limits["USL"] / 100
    lsl = limits["LSL"] / 100

    data["USL_glob"] = mean * (1 + usl)
    data["LSL_glob"] = mean * (1 - lsl)

    return data

def analytics(data, enabled_metrics):
    data = data.copy()

    def capability(usl,lsl,sigma):
        return (usl - lsl) / (6 * sigma)
    
    def capability_k(usl,lsl,sigma,mean):
        return pd.concat([
            (usl - mean) / (3 * sigma),
            (mean - lsl) / (3 * sigma)
        ], axis=1).min(axis=1)
    
    usl = data["USL_glob"]
    lsl = data["LSL_glob"]
    sigma = data["Standard Deviation"]
    mean = data["Average"]
    
    if enabled_metrics["cp"] or enabled_metrics["cg"]:
        cp_cg = capability(usl,lsl,sigma)
        if enabled_metrics["cp"]:
            data["Cp"] = cp_cg
        if enabled_metrics["cg"]:
            data["Cg"] = cp_cg

    if enabled_metrics["cpk"] or enabled_metrics["cgk"]:
        cpk_cgk = capability_k(usl,lsl,sigma,mean)
        if enabled_metrics["cpk"]:
            data["Cpk"] = cpk_cgk
        if enabled_metrics["cgk"]:
            data["Cgk"] = cpk_cgk
    return data

# ----------------------------------
# --- PRELIM RESULTS DATA FILTER ---
# ----------------------------------

def data_prelim_results(data, metrics):
    basic_columns = ["Sub-board", "Component", "Pin Id",
                     "Algorithm Name", "Sample Name",
                     "Element Name",
                     "Standard Deviation", "Average",
                     "USL_glob", "LSL_glob"]
    for metric, value in metrics.items():
        if value:
            basic_columns.append(metric.capitalize())

    return data[basic_columns]

def prelim_failed_rows(data, enabled_metrics):
    LIMITS = {
        "cp": 1.33,
        "cpk": 1.33,
        "cg": 1.33,
        "cgk": 1.33,
    }

    METRIC_COL_MAP = {
        "cp": "Cp",
        "cpk": "Cpk",
        "cg": "Cg",
        "cgk": "Cgk",
    }

    failed_rows = set()

    for idx, row in data.iterrows():
        for m, enabled in enabled_metrics.items():
            if not enabled or m not in METRIC_COL_MAP:
                continue
            if row[METRIC_COL_MAP[m]] < LIMITS[m]:
                failed_rows.add(idx)
                break

    return failed_rows

def data_for_analysis(data, failed_rows):
    data_failed = data.loc[data.index.isin(list(failed_rows))]
    
    return data_failed

# ----------------------------------
# ---- ANALYSIS FAIL EXTRACTION ----
# ----------------------------------
def fail_extractor(data):

    usl = data["usl"]
    lsl = data["lsl"]
    sigma_all = data["stdev"]
    values = data["values"]
    outliers = data["outliers"]

    def cp(usl, lsl, sigma):
        return (usl - lsl) / (6 * sigma) if sigma > 0 else np.nan

    sigma_all = np.std(values, ddof=1)
    cp_all = cp(usl, lsl, sigma_all)

    rows = []

    for v in values:
        reduced = np.delete(values, np.where(values == v)[0][0])

        if len(reduced) < 2:
            continue

        sigma_r = np.std(reduced, ddof=1)
        cp_r = cp(usl, lsl, sigma_r)

        rows.append({
            "Sample Value": v,
            "Is Outlier": v in outliers,
            "Cp_all": cp_all,
            "Cp_without": cp_r,
            "Cp_delta": cp_r - cp_all
        })


    impact_df = (
        pd.DataFrame(rows)
        .sort_values("Cp_delta", ascending=False)
        .reset_index(drop=True)
    )
    return impact_df


        


    
    

    
