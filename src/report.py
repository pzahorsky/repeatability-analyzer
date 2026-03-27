from reportlab.platypus import (
    BaseDocTemplate,
    PageTemplate,
    Frame,
    NextPageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak
)

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY 
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import utils

import io
import re
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

### Title Header - Helper func ###
def metrics_label(metrics):
    cp = metrics.get("cp")
    cpk = metrics.get("cpk")
    cg = metrics.get("cg")
    cgk = metrics.get("cgk")

    parts = []

    if cp:
        parts.append("Cp")
    if cpk:
        parts.append("Cpk")
    if cg:
        parts.append("Cg")
    if cgk:
        parts.append("Cgk")

    if parts:
        metrics_label = "/".join(parts)
    else:
        metrics_label = ""

    return metrics_label

### Title Header ###
def build_header_title(story, styles, metrics, customer, product):
    
    story.append(
        Paragraph(
            f"{metrics_label(metrics)} Report for {customer} - {product}",
            styles["Title"]
        )
    )

def metrics_subheader(metrics):
    
    cp = metrics.get("cp")
    cpk = metrics.get("cpk")
    cg = metrics.get("cg")
    cgk = metrics.get("cgk")

    if cp:
        cp = "Cp"
        text = cp
    if cpk:
        cpk = "Cpk"
        text = cpk
    if cg:
        cg = "Cg"
        text = cg
    if cgk:
        cgk = "Cgk"
        text = cgk
    if cp and cpk:
        text = f"{cp} and {cpk}"
    if cg and cgk:
        text = f"{cg} and {cgk}"

    if cp or cpk:
        text = (
            f"This report presents a statistical evaluation of process "
            f"capability based on {text} indices. The objective is "
            f"to assess whether the measured process operates within defined "
            f"specification limits and to identify potential sources of "
            f"variability or instability. "
        )
    if cg or cgk:
        text = (
            f"This report presents a statistical evaluation of the measurement " 
            f"system capability based on {text} indices. The objective is "
            f"to assess whether the measurement system is sufficiently precise "
            f"and accurate within defined tolerance limits and to identify "
            f"potential sources of measurement variation or bias. "
        )

    return text

def build_subheader_intro(story, styles, metrics):

    text = metrics_subheader(metrics)

    justified_style = ParagraphStyle(
    name="Justified",
    parent=styles["Normal"],
    alignment=TA_JUSTIFY,
    leading=14,          # riadkovanie (dôležité pre čitateľnosť)
    spaceAfter=10,
)
    story.append(
        Paragraph(text,
                  justified_style
        )
    )

### Metrics Header - Plot to .png ###
def render_formula(formula, fontsize=18):
    
    with plt.style.context("default"):
        fig, ax = plt.subplots(figsize=(3, 1))
        ax.axis("off")
        ax.text(0.5, 0.5, formula, fontsize=fontsize, ha="center", va="center")

        buffer = io.BytesIO()
        plt.savefig(buffer, format="png", dpi=300, bbox_inches="tight",
                    pad_inches=0.0, facecolor="white")
        plt.close(fig)
        buffer.seek(0)
        
        return buffer

### Metrics Header ###
def build_header_metrics_tolerances(story, styles, metrics):

    FORMULAS = {
        "Cp":  {"formula": r"$C_p = \dfrac{USL - LSL}{6\sigma}$", "w": 40, "h": 14.4},
        "Cpk": {"formula": r"$C_{pk} = \min\left(\dfrac{USL - \mu}{3\sigma}, \dfrac{\mu - LSL}{3\sigma}\right)$", "w": 56, "h": 14.4},
        "Cg":  {"formula": r"$C_g = \dfrac{USL - LSL}{6\sigma_g}$", "w": 40, "h": 14.4},
        "Cgk": {"formula": r"$C_{gk} = \min\left(\dfrac{USL - \mu_g}{3\sigma_g}, \dfrac{\mu_g - LSL}{3\sigma_g}\right)$", "w": 56, "h": 14.4},
    }

    label = metrics_label(metrics)
    if not label:
        return

    selected_metrics = label.split("/")

    images = []
    col_widths = []

    story.append(
        Paragraph(
            "The calculations presented in this report are based on the following formulas:",
            styles["Normal"]
        )
    )

    for metric in selected_metrics:
        config = FORMULAS.get(metric)
        if not config:
            continue

        img = render_formula(config["formula"])

        images.append(
            Image(
                img,
                width=config["w"] * mm,
                height=config["h"] * mm
            )
        )
        col_widths.append(config["w"] * mm)

    if not images:
        return

    table = Table([images], colWidths=col_widths, rowHeights=[22*mm])

    table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))

    story.append(table)
    
def build_info_subheader(story, styles, data, metrics):
    col_samples = st.session_state["Change_Samples"]
    col_components = st.session_state["Change_Component"]
    col_subboard = st.session_state["Change_Sub-Board"]

    justified_style = ParagraphStyle(
        name="Justified",
        parent=styles["Normal"],
        alignment=TA_JUSTIFY,
        leading=14,          # riadkovanie (dôležité pre čitateľnosť)
        spaceAfter=10,
)
    
    sample_value_reg = fr"{col_samples} \d+"
    sample_value_cols = [
        col for col in data.columns if re.search(sample_value_reg, col)]
    sample_num = len(sample_value_cols)
    
    components = data[col_components].unique()
    components_num = len(components)
    component_list = ', '.join(components)
    if components_num == 1:
        components_num = "single"
        component_str = "single component"
    else:
        component_str = f"{components_num} components"

    subboards_num = len(data[col_subboard].unique())
    if subboards_num == 1:
        subboards_num = "single"
        subboard_str = f"{subboards_num} sub-board"
    else:
        subboard_str = f"{subboards_num} sub-boards"
    
    if components_num == "single" and subboards_num == "single":
        components_per_board = 1
        components_total = components_per_board * sample_num
    else:
        components_total = components_num * subboards_num * sample_num
    
    measurement_num = data.shape[0]

    label = metrics_label(metrics)
    if not label:
        return

    selected_metrics = label.split("/")
    
    if "Cp" in selected_metrics or "Cpk" in selected_metrics:
        story.append(
            Paragraph(
                f"The Cp/Cpk capability evaluation was performed on measurement system "
                f"data consisting of {sample_num} boards, each containing {subboard_str} "
                f"with {component_str} per sub-board. In total, {components_total} "
                f"components were inspected, resulting in {measurement_num} measurements",
                justified_style
            )
        )

    if "Cg" in selected_metrics or "Cgk" in selected_metrics:
        story.append(
            Paragraph(
                f"The Cg/Cgk capability evaluation was performed on measurement system data "
                f"consisting of {sample_num} inspections of single board, each containing "
                f"{subboard_str} with {component_str} per sub-board.In total, "
                f"{components_total} components were inspected, resulting "
                f"in {measurement_num} measurements.",
                justified_style
            )
    )

    story.append(Spacer(0,1 * mm))
    story.append(
        Paragraph(
            f"The inspected components per single subboard are detailed below."
        )
    )
    story.append(Spacer(0,1 * mm))
    story.append(
        Paragraph(
            f"{component_list}"
        )
    )
    story.append(Spacer(0,5 * mm))
    if "Cp" in selected_metrics or "Cpk" in selected_metrics:
        story.append(
            Paragraph(
                "Figure: Cp and Cpk capability indices calculated for all measurements. "
                "The plot illustrates variability across individual measurements, with "
                "acceptance thresholds indicated by dashed lines. Values below the "
                "thresholds identify potential process capability issues.",
                justified_style
            )
        )
    if "Cg" in selected_metrics or "Cgk" in selected_metrics:
        story.append(
            Paragraph(
                "Figure: Cg and Cgk capability indices calculated for all measurements. "
                "The plot illustrates variability of the measurement system across individual measurements, "
                "with acceptance thresholds indicated by dashed lines. Values below the thresholds "
                "indicate insufficient measurement system capability.",
                justified_style
            )
        )

def fig_to_buffer(fig, dpi=300):

    # Okraje layoutu (aby sa neorezali osi a popisy)
    fig.subplots_adjust(left=0.05, right=0.95, bottom=0.12, top=0.96)

    # Biele pozadie
    fig.patch.set_facecolor("white")

    # Zapnúť a nastaviť okraje (spines)
    for ax in fig.axes:
        ax.set_facecolor("white")
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_color("black")
            spine.set_linewidth(1.0)

        ax.title.set_color("black")
        ax.tick_params(colors="black")
        ax.xaxis.label.set_color("black")
        ax.yaxis.label.set_color("black")

    fig.tight_layout()

    buffer = io.BytesIO()
    fig.savefig(
        buffer,
        format="png",
        dpi=dpi,
        facecolor="white",
        bbox_inches=None,
        pad_inches=0.2  # mierne väčší padding = lepší vizuálny okraj
    )

    buffer.seek(0)
    return buffer

def build_conclusion(story, styles, data, metrics):
    cp = metrics.get("cp")
    cpk = metrics.get("cpk")
    cg = metrics.get("cg")
    cgk = metrics.get("cgk")

    justified_style = ParagraphStyle(
        name="Justified",
        parent=styles["Normal"],
        alignment=TA_JUSTIFY,
        leading=14,          
        spaceAfter=10,
)

    def conclusion_cp_cpk(cp, cpk):
        conclusion = None

        if cp:
            if (data["Cp"] > 1.33).all():
                conclusion = (
                    "All Cp values exceed the defined acceptance thresholds. "
                    "This indicates that the process has sufficient potential capability, "
                    "with variability well within the specified tolerance limits.")
            else:
                conclusion = (
                    (
                    "Cp values below the defined acceptance thresholds were identified. "
                    "This indicates that the process does not have sufficient potential capability, "
                    "as variability exceeds the specified tolerance limits.")
                )
            if cpk:
                if (data["Cp"] > 1.33).all() and (data["Cpk"] > 1.67).all():
                    conclusion = (
                        "All Cp and Cpk values exceed the defined acceptance "
                        "thresholds. This indicates that the process is "
                        "capable, properly centered, and exhibits low "
                        "variability relative to the specified limits.")
                elif not (data["Cp"] > 1.33).all() and (data["Cpk"] > 1.67).all():
                    conclusion = (
                        "Cp values below the defined acceptance thresholds were identified, while Cpk values remain within acceptable limits. "
                        "This suggests that the process is properly centered, but exhibits elevated variability "
                        "relative to the specified tolerance limits.")
                elif (data["Cp"] > 1.33).all() and not (data["Cpk"] > 1.67).all():
                    conclusion = (
                        "Cp values meet the defined acceptance thresholds, while some Cpk values do not. "
                        "This indicates that although process variability is acceptable, the process is not properly centered "
                        "relative to the specified limits."
                    )
                elif not (data["Cp"] > 1.33).all() and not (data["Cpk"] > 1.67).all():
                    conclusion = (
                        "Cp and Cpk values below the defined acceptance thresholds were identified. "
                        "This indicates that the process is not capable, due to excessive variability "
                        "and inadequate centering relative to the specified limits."
                    )
                            
        if cpk and not cp:
            if (data["Cpk"] > 1.67).all():
                conclusion = (
                        "All Cpk values exceed the defined acceptance thresholds. "
                        "This indicates that the process is capable and properly centered, "
                        "with variability well within the specified limits.")
            else:
                conclusion = (
                        "Cpk values below the defined acceptance thresholds were identified. "
                        "This indicates that the process is not capable, likely due to a combination "
                        "of excessive variability and/or improper centering.")
        
        return conclusion

    def conclusion_cg_cgk(cg, cgk):        
        conclusion = None

        if cg:
            if (data["Cg"] > 1.33).all():
                conclusion = (
                    "All Cg values exceed the defined acceptance thresholds. "
                    "This indicates that the measurement system has sufficient precision, "
                    "with measurement variability well within the specified tolerance limits."
                )
            else:
                conclusion = (
                    "Cg values below the defined acceptance thresholds were identified. "
                    "This indicates that the measurement system does not have sufficient precision, "
                    "as measurement variability exceeds the specified tolerance limits."
                )

            if cgk:
                if (data["Cg"] > 1.33).all() and (data["Cgk"] > 1.67).all():
                    conclusion = (
                        "All Cg and Cgk values exceed the defined acceptance thresholds. "
                        "This indicates that the measurement system is both sufficiently precise "
                        "and properly centered, with measurement variability well within the specified limits."
                    )

                elif not (data["Cg"] > 1.33).all() and (data["Cgk"] > 1.67).all():
                    conclusion = (
                        "Cg values below the defined acceptance thresholds were identified, while Cgk values remain within acceptable limits. "
                        "This suggests that the measurement system is properly centered, but exhibits elevated measurement variability."
                    )

                elif (data["Cg"] > 1.33).all() and not (data["Cgk"] > 1.67).all():
                    conclusion = (
                        "Cg values meet the defined acceptance thresholds, while some Cgk values do not. "
                        "This indicates that although measurement precision is acceptable, the measurement system is not properly centered."
                    )

                elif not (data["Cg"] > 1.33).all() and not (data["Cgk"] > 1.67).all():
                    conclusion = (
                        "Cg and Cgk values below the defined acceptance thresholds were identified. "
                        "This indicates that the measurement system is not capable, due to insufficient precision "
                        "and inadequate centering relative to the specified limits."
                    )

        if cgk and not cg:
            if (data["Cgk"] > 1.67).all():
                conclusion = (
                    "All Cgk values exceed the defined acceptance thresholds. "
                    "This indicates that the measurement system is both precise and properly centered, "
                    "with measurement results consistently within the specified tolerance limits."
                )
            else:
                conclusion = (
                    "Cgk values below the defined acceptance thresholds were identified. "
                    "This indicates that the measurement system is not capable, likely due to insufficient precision "
                    "and/or improper centering."
                )

        return conclusion

    story.append(Spacer(0,5 * mm))
    if cp or cpk:
        conclusion = conclusion_cp_cpk(cp, cpk)
        story.append(
            Paragraph(f"Conclusion: {conclusion}", justified_style
            ))
    
    elif cg or cgk:
        conclusion = conclusion_cg_cgk(cg, cgk)
        story.append(
            Paragraph(f"Conclusion: {conclusion}", justified_style
            ))

def dataframe_to_head_and_rows(data):

    data = data.copy()

    data["Status"] = "PASS"
    data.loc[(data["Cp"] < 1.33) | (data["Cpk"] < 1.67), "Status"] = "FAIL"

    col_map = [
        ("Sub-board", "Sub-board"),
        ("Component", "Component"),
        ("Pin Id", "Pin Id"),
        ("Algorithm Name", "Algorithm Name"),
        ("Sample Name", "Sample Name"),
        ("StDev", "Standard Deviation"),
        ("Mean", "Average"),
        ("USL", "USL_glob"),
        ("LSL", "LSL_glob"),
        ("Cp", "Cp"),
        ("Cpk", "Cpk"),
        ("Status", "Status"),
    ]

    header = [h for h, _ in col_map]

    # vyber len stĺpce z df v správnom poradí
    df_out = data[[src for _, src in col_map]].copy()

    # voliteľné: zaokrúhliť čísla, aby tabuľka bola čitateľná
    num_cols = ["Standard Deviation", "Average", "USL_glob", "LSL_glob", "Cp", "Cpk"]
    for c in num_cols:
        if c in df_out.columns:
            s = pd.to_numeric(df_out[c], errors="coerce")
            df_out[c] = s.map(lambda x: "" if pd.isna(x) else f"{x:.3f}")

    df_out["Pin Id"] = df_out["Pin Id"].round().astype(int)

    rows = df_out.values.tolist()
    return header, rows

def build_results_table(story, available_width, header, rows, numeric_cols=None, font_size=7):

    styles = getSampleStyleSheet()
    normal = styles["Normal"]

    table_data = [[Paragraph(str(h), normal) for h in header]]
    table_data += [[Paragraph(str(v), normal) for v in r] for r in rows]

    n = len(header)
    W = available_width

    text_cols = {0, 1, 3, 4, 11}
    num_cols  = set(range(n)) - text_cols

    text_share = 0.55
    num_share  = 1.0 - text_share

    colWidths = []
    for i in range(n):
        if i in text_cols:
            colWidths.append(W * text_share / len(text_cols))
        else:
            colWidths.append(W * num_share / len(num_cols))

    table = Table(table_data, colWidths=colWidths, repeatRows=1)

    ts = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.grey),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), font_size),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 1),
        ("RIGHTPADDING", (0, 0), (-1, -1), 1),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ])

    if numeric_cols:
        for c in numeric_cols:
            ts.add("ALIGN", (c, 1), (c, -1), "RIGHT")

    table.setStyle(ts)
    story.append(Spacer(1, 4*mm))
    story.append(table)

def build_pdf(data, metrics, fig, customer, product):

    pdf_buffer = io.BytesIO()

    doc = BaseDocTemplate(
        pdf_buffer,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm 
    )
    # ----- Portrait Frame -----
    frame_portrait = Frame(
        doc.leftMargin,
        doc.bottomMargin,
        doc.width,
        doc.height,
        id="portrait_frame"
    )

    portrait_template = PageTemplate(
        id="portrait",
        frames=[frame_portrait],
        pagesize=A4
    )
    # ---- Landscape Frame ----
    land_w, land_h = landscape(A4)

    frame_landscape = Frame(
        doc.leftMargin,
        doc.bottomMargin,
        land_w - doc.leftMargin - doc.rightMargin,
        land_h - doc.topMargin - doc.bottomMargin,
        id="landscape_frame"
    )
    landscape_template = PageTemplate(id="landscape", frames=[frame_landscape], pagesize=landscape(A4))

    doc.addPageTemplates([portrait_template, landscape_template])


    styles = getSampleStyleSheet()
    story = []

    # Title Header
    build_header_title(story, styles, metrics, customer, product)
    story.append(Spacer(1,5 * mm))

    build_subheader_intro(story, styles, metrics)

    # Sub Header Text
    build_header_metrics_tolerances(story, styles, metrics)
    build_info_subheader(story, styles, data, metrics)

    # Plot to Document
    img_buffer = fig_to_buffer(fig)
    story.append(Image(img_buffer, width=160*mm, height=100*mm))
    plt.close(fig)
    
    # Conclusion 
    build_conclusion(story, styles, data, metrics)

    # Next page - Landscape Table
    story.append(NextPageTemplate("landscape"))
    story.append(PageBreak())

    """
    header, rows = dataframe_to_head_and_rows(data)

    land_content_w = land_w - doc.leftMargin - doc.rightMargin

    build_results_table(
        story,
        land_content_w,
        header,
        rows,
        numeric_cols=[2,5,6,7,8,9,10]
    )
    """


    doc.build(story)

    pdf_buffer.seek(0)
    return pdf_buffer.read()