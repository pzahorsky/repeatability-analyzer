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
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import utils

import io
import re
import matplotlib.pyplot as plt
import pandas as pd

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

### Metrics Header - Plot to .png ###
def render_formula(formula, fontsize=18):
    
    with plt.style.context("default"):
        fig, ax = plt.subplots(figsize=(3, 1))
        ax.axis("off")
        ax.text(0.5, 0.62, formula, fontsize=fontsize, ha="center", va="baseline")

        buffer = io.BytesIO()
        plt.savefig(buffer, format="png", dpi=300, bbox_inches="tight",
                    pad_inches=0.15, facecolor="white")
        plt.close(fig)
        buffer.seek(0)
        
        return buffer

### Metrics Header ###
def build_header_metrics_tolerances(story, styles, metrics):

    FORMULAS = {
        "Cp":  {"formula": r"$C_p = \dfrac{USL - LSL}{6\sigma}$", "w": 48, "h": 19},
        "Cpk": {"formula": r"$C_{pk} = \min\left(\dfrac{USL - \mu}{3\sigma}, \dfrac{\mu - LSL}{3\sigma}\right)$", "w": 70, "h": 20},
        "Cg":  {"formula": r"$C_g = \dfrac{USL - LSL}{6\sigma_g}$", "w": 50, "h": 20},
        "Cgk": {"formula": r"$C_{gk} = \min\left(\dfrac{USL - \mu_g}{3\sigma_g}, \dfrac{\mu_g - LSL}{3\sigma_g}\right)$", "w": 75, "h": 20},
        "Lim": {"formula": r"$USL, LSL = \mu \pm \mu \cdot \frac{p}{100}$", "w": 50, "h": 20},
    }

    label = metrics_label(metrics)
    if not label:
        return

    selected_metrics = label.split("/")
    selected_metrics.append("Lim")   # vždy 3 kusy (2 alebo 3? -> tu bude 3 v jednom riadku)

    images = []
    col_widths = []

    story.append(
        Paragraph(
            "The calculations presented in this report are based on the following formulas.",
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
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))

    story.append(table)
    story.append(Spacer(0,8 * mm))

    
def build_info_subheader(story, styles, data, metrics):
    
    sample_value_reg = r"Sample Value \d+"

    sample_value_cols = [
        col for col in data.columns if re.search(sample_value_reg, col)]
    
    components = data["Component"].unique()
    components_num = len(components)
    component_list = ', '.join(components)

    subboards_num = len(data["Sub-board"].unique())
    if subboards_num == 1:
        subboards_num = "single"
        subboard_str = "board"
    else:
        subboard_str = "sub-boards"
    
    sample_num = len(sample_value_cols)
    measurement_num = data.shape[0]

    label = metrics_label(metrics)
    if not label:
        return

    selected_metrics = label.split("/")
    
    if "Cp" in selected_metrics or "Cpk" in selected_metrics:
        story.append(
            Paragraph(
                f"The Cp/Cpk capability evaluation comprised {sample_num} boards, "
                f"each measured {measurement_num} times, resulting in "
                f"{sample_num * measurement_num} total measurements. "
                f"The study encompassed {subboards_num} {subboard_str} and {components_num} components. "
            )
        )

    if "Cg" in selected_metrics or "Cgk" in selected_metrics:
        story.append(
            Paragraph(
                f"The Cg/Cgk measurement system capability evaluation was performed on a single product, "
                f"measured {measurement_num} times, resulting in {measurement_num} total measurements. "
                f"The study encompassed {subboards_num} {subboard_str} and {components_num} components. "
            )
    )

    story.append(Spacer(0,2 * mm))
    story.append(
        Paragraph(
            f"The inspected components per {subboard_str} are detailed below."
        )
    )
    story.append(Spacer(0,1 * mm))
    story.append(
        Paragraph(
            f"{component_list}"
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
    story.append(Spacer(1,6 * mm))

    # Sub Header Text
    build_header_metrics_tolerances(story, styles, metrics)
    build_info_subheader(story, styles, data, metrics)

    # Plot to Document
    img_buffer = fig_to_buffer(fig)
    story.append(Image(img_buffer, width=160*mm, height=100*mm))
    plt.close(fig)

    # Next page - Landscape Table
    story.append(NextPageTemplate("landscape"))
    story.append(PageBreak())
    header, rows = dataframe_to_head_and_rows(data)

    land_content_w = land_w - doc.leftMargin - doc.rightMargin

    build_results_table(
        story,
        land_content_w,
        header,
        rows,
        numeric_cols=[2,5,6,7,8,9,10]
    )



    doc.build(story)

    pdf_buffer.seek(0)
    return pdf_buffer.read()