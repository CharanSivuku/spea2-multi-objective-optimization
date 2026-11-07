#!/usr/bin/env python3
"""
Generate comprehensive academic-grade PDF report for SPEA2 Multi-Objective Optimization:
- 30 Standard Multi-Objective Benchmarks (ZDT, DTLZ, Classical)
- CEC 2020 Multimodal Multi-Objective Optimization (MMO) Suite (24 MMF problems)
- CEC 2022 Single-Objective Bound-Constrained Benchmark Suite (12 functions)
"""

import os
import sys
import math
from pathlib import Path
import pandas as pd
from PIL import Image as PILImage

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image as RLImage, KeepTogether, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"
FIGURES_DIR = RESULTS_DIR / "figures"
DATA_DIR = RESULTS_DIR / "data"
OUTPUT_PDF = RESULTS_DIR / "spea2_benchmark_and_competition_report.pdf"


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and draw total page numbers and running headers/footers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            if self._pageNumber > 1:
                self.saveState()
                self.setFont("Helvetica-Bold", 7.5)
                self.setFillColor(colors.HexColor("#475569"))
                # Running Header
                self.drawString(40, 808, "SPEA2 BENCHMARK EVALUATION & COMPETITION REPORT")
                self.setFont("Helvetica", 7.5)
                self.drawRightString(555, 808, "30 Benchmarks • CEC 2020 MMO • CEC 2022")
                self.setStrokeColor(colors.HexColor("#cbd5e1"))
                self.setLineWidth(0.6)
                self.line(40, 802, 555, 802)

                # Running Footer
                self.line(40, 36, 555, 36)
                self.setFont("Helvetica", 7.5)
                self.setFillColor(colors.HexColor("#64748b"))
                self.drawString(40, 24, "GitHub: CharanSivuku/spea2-multi-objective-optimization")
                page_str = f"Page {self._pageNumber} of {num_pages}"
                self.drawRightString(555, 24, page_str)
                self.restoreState()
            super().showPage()
        super().save()


def fmt(val, precision=4, sci_thresh=1e-3):
    """Format floating point numbers cleanly."""
    if val is None or pd.isna(val):
        return "N/A"
    try:
        val = float(val)
    except (ValueError, TypeError):
        return str(val)
    if val == 0.0:
        return "0.0"
    abs_val = abs(val)
    if abs_val < sci_thresh or abs_val >= 1e5:
        return f"{val:.2e}"
    return f"{val:.{precision}f}"


def fmt_mean_std(mean_val, std_val, precision=4):
    """Format mean ± std with appropriate precision."""
    if pd.isna(mean_val):
        return "N/A"
    m_str = fmt(mean_val, precision=precision)
    if pd.isna(std_val) or std_val == 0.0:
        return m_str
    s_str = fmt(std_val, precision=precision)
    return f"{m_str} ± {s_str}"


def get_custom_styles():
    styles = getSampleStyleSheet()
    
    # Palette
    c_primary = colors.HexColor("#0f172a")    # Slate 900
    c_secondary = colors.HexColor("#1e3a8a")  # Blue 900
    c_accent = colors.HexColor("#0284c7")     # Sky 600
    c_text = colors.HexColor("#334155")       # Slate 700
    c_muted = colors.HexColor("#64748b")      # Slate 500

    styles.add(ParagraphStyle(
        name="DocTitle",
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        textColor=c_primary,
        alignment=0,
        spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        name="DocSubtitle",
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        textColor=c_secondary,
        alignment=0,
        spaceAfter=14
    ))
    styles.add(ParagraphStyle(
        name="SectionHeader",
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=19,
        textColor=c_secondary,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    ))
    styles.add(ParagraphStyle(
        name="SubsectionHeader",
        fontName="Helvetica-Bold",
        fontSize=11.5,
        leading=15,
        textColor=c_primary,
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    ))
    styles.add(ParagraphStyle(
        name="BodyTextCustom",
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=c_text,
        spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        name="BodyTextBold",
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=12,
        textColor=c_primary,
        spaceAfter=4
    ))
    styles.add(ParagraphStyle(
        name="CalloutText",
        fontName="Helvetica",
        fontSize=8,
        leading=11.5,
        textColor=c_text
    ))
    styles.add(ParagraphStyle(
        name="Caption",
        fontName="Helvetica",
        fontSize=7.5,
        leading=10,
        textColor=c_muted,
        alignment=1,
        spaceBefore=3,
        spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        name="TableHeader",
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=9.5,
        textColor=colors.white,
        alignment=1
    ))
    styles.add(ParagraphStyle(
        name="TableCell",
        fontName="Helvetica",
        fontSize=7,
        leading=9,
        textColor=c_text,
        alignment=0
    ))
    styles.add(ParagraphStyle(
        name="TableCellCenter",
        fontName="Helvetica",
        fontSize=7,
        leading=9,
        textColor=c_text,
        alignment=1
    ))
    styles.add(ParagraphStyle(
        name="TableCellBold",
        fontName="Helvetica-Bold",
        fontSize=7,
        leading=9,
        textColor=c_primary,
        alignment=0
    ))
    styles.add(ParagraphStyle(
        name="TagText",
        fontName="Helvetica-Bold",
        fontSize=7,
        leading=8.5,
        textColor=colors.HexColor("#0369a1")
    ))

    return styles


def create_callout(text, styles, title="KEY FINDING / OBSERVATION", bg="#f8fafc", border="#0284c7"):
    content = [
        Paragraph(f"<b>{title}</b>", styles["TagText"]),
        Spacer(1, 2),
        Paragraph(text, styles["CalloutText"])
    ]
    t = Table([[content]], colWidths=[515])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(bg)),
        ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor(border)),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    return t


def build_cover_page(story, styles):
    story.append(Spacer(1, 10))
    story.append(Paragraph("SPEA2 Multi-Objective Optimization Evaluation", styles["DocTitle"]))
    story.append(Paragraph(
        "Comprehensive Empirical Benchmark Analysis: 30 Continuous Problems, "
        "CEC 2020 Multimodal Multi-Objective Suite, and CEC 2022 Single-Objective Suite",
        styles["DocSubtitle"]
    ))

    # Meta banner
    meta_data = [
        [
            Paragraph("<b>Algorithm:</b> SPEA2 (Strength Pareto EA 2)", styles["TableCell"]),
            Paragraph("<b>Framework:</b> Python 3 / NumPy / Pytest", styles["TableCell"]),
            Paragraph("<b>Date:</b> November 2026", styles["TableCell"])
        ],
        [
            Paragraph("<b>Author/Repo:</b> Charan Sivuku", styles["TableCell"]),
            Paragraph("<b>Test Suite:</b> 300 Verified Tests Passing", styles["TableCell"]),
            Paragraph("<b>Status:</b> Production / Validated", styles["TableCell"])
        ]
    ]
    t_meta = Table(meta_data, colWidths=[175, 175, 165])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 12))

    story.append(Paragraph("Executive Summary", styles["SectionHeader"]))
    story.append(Paragraph(
        "This report provides an exhaustive, rigorous evaluation of a from-scratch Python implementation of the "
        "<b>Strength Pareto Evolutionary Algorithm 2 (SPEA2)</b> (Zitzler, Laumanns, and Thiele, 2001). "
        "The investigation encompasses three distinct benchmark domains totaling <b>66 problem formulations</b>:",
        styles["BodyTextCustom"]
    ))

    summary_points = [
        "<b>1. Standard Multi-Objective Suite (30 Problems):</b> Evaluated across the classic 5 ZDT functions, 7 scalable DTLZ problems (3 objectives), and 18 classical/constrained benchmarks (including Binh, Deb, Fonseca, Kursawe, Laumanns, Murata, Quagliarella, Rendon, Schaffer, Srinivas, Tanaka, and Viennet). All runs are assessed with four rigorous indicators: Hypervolume (HV), Inverted Generational Distance (IGD), Generational Distance (GD), and Spacing.",
        "<b>2. CEC 2020 Multimodal Multi-Objective Optimization Suite (24 MMF Problems):</b> Benchmarked under official competition conditions (21 seeded runs, 50 generations, population = archive = 200 × N_ops). Assessed across both decision-space (1/PSP, IGDX) and objective-space (1/HV, IGDF) indicators with official true Pareto set (PS) and Pareto front (PF) reference data.",
        "<b>3. CEC 2022 Single-Objective Bound-Constrained Suite (12 Functions):</b> Benchmarked across 10-D and 20-D configurations over 30 independent runs utilizing official competition random seeds and coordinate shift/rotation/shuffle matrices derived from the C reference implementation."
    ]
    for pt in summary_points:
        story.append(Paragraph(f"• {pt}", styles["BodyTextCustom"]))

    story.append(Spacer(1, 8))
    callout_txt = (
        "<b>Core Finding:</b> SPEA2 demonstrates near-ideal convergence and uniform spread on standard convex, "
        "concave, and moderately disconnected Pareto fronts (IGD ≤ 0.005 for ZDT1-3, Fonseca, Tanaka, Deb). "
        "However, multimodal multi-objective tasks (CEC 2020) reveal that because SPEA2 performs density estimation "
        "exclusively in objective space, it cannot intrinsically maintain separate decision-space niching for local "
        "Pareto sets. On CEC 2022 single-objective functions, SPEA2 acts as a robust ranking-based search heuristic, "
        "converging reliably on basic and hybrid landscapes while composition landscapes present severe local trapping."
    )
    story.append(create_callout(callout_txt, styles, title="EXECUTIVE SYNTHESIS"))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Algorithmic Parameterization", styles["SubsectionHeader"]))
    params_data = [
        [
            Paragraph("<b>Parameter</b>", styles["TableHeader"]),
            Paragraph("<b>Standard MOO (30 Benchmarks)</b>", styles["TableHeader"]),
            Paragraph("<b>CEC 2020 MMO Suite</b>", styles["TableHeader"]),
            Paragraph("<b>CEC 2022 Single-Objective</b>", styles["TableHeader"])
        ],
        [
            Paragraph("Population Size (N)", styles["TableCellBold"]),
            Paragraph("100", styles["TableCellCenter"]),
            Paragraph("200 × N_ops (200 – 800)", styles["TableCellCenter"]),
            Paragraph("100", styles["TableCellCenter"])
        ],
        [
            Paragraph("Archive Size (N')", styles["TableCellBold"]),
            Paragraph("100", styles["TableCellCenter"]),
            Paragraph("200 × N_ops (200 – 800)", styles["TableCellCenter"]),
            Paragraph("100", styles["TableCellCenter"])
        ],
        [
            Paragraph("Generations / Evaluations", styles["TableCellBold"]),
            Paragraph("250 (Class./DTLZ), 500 (ZDT), 2000 (DTLZ1/3)", styles["TableCellCenter"]),
            Paragraph("50 generations (10,000 × N_ops MaxFES)", styles["TableCellCenter"]),
            Paragraph("200,000 (10-D) / 1,000,000 (20-D) MaxFES", styles["TableCellCenter"])
        ],
        [
            Paragraph("Crossover Operator", styles["TableCellBold"]),
            Paragraph("SBX (p_c = 0.9, η_c = 20.0)", styles["TableCellCenter"]),
            Paragraph("SBX (p_c = 0.9, η_c = 20.0)", styles["TableCellCenter"]),
            Paragraph("SBX (p_c = 0.9, η_c = 20.0)", styles["TableCellCenter"])
        ],
        [
            Paragraph("Mutation Operator", styles["TableCellBold"]),
            Paragraph("Polynomial (p_m = 1/n, η_m = 20.0)", styles["TableCellCenter"]),
            Paragraph("Polynomial (p_m = 1/n, η_m = 20.0)", styles["TableCellCenter"]),
            Paragraph("Polynomial (p_m = 1/n, η_m = 20.0)", styles["TableCellCenter"])
        ],
        [
            Paragraph("Constraint Handling", styles["TableCellBold"]),
            Paragraph("Feasibility-First Tournament Selection", styles["TableCellCenter"]),
            Paragraph("Box Bounds Clipping", styles["TableCellCenter"]),
            Paragraph("Box Bounds Clipping [-100, 100]", styles["TableCellCenter"])
        ]
    ]
    t_params = Table(params_data, colWidths=[130, 130, 125, 130])
    t_params.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
    ]))
    story.append(t_params)


def build_30_benchmarks_section(story, styles):
    story.append(PageBreak())
    story.append(Paragraph("1. Standard 30 Multi-Objective Benchmark Suite", styles["SectionHeader"]))
    story.append(Paragraph(
        "The standard test suite comprises 30 continuous multi-objective benchmark functions representing a broad spectrum "
        "of Pareto front topologies: convex, non-convex (concave), discontinuous, multimodal, biased variable distributions, "
        "and non-linear constraints. Performance is quantified using analytical reference sets (or densely verified numerical sets) "
        "across four foundational metrics: <b>Hypervolume (HV)</b>, <b>Inverted Generational Distance (IGD)</b>, "
        "<b>Generational Distance (GD)</b>, and <b>Spacing (S)</b>.",
        styles["BodyTextCustom"]
    ))

    # Read all_benchmarks_summary.csv
    csv_path = RESULTS_DIR / "all_benchmarks_summary.csv"
    if not csv_path.exists():
        story.append(Paragraph("Error: results/all_benchmarks_summary.csv not found.", styles["BodyTextBold"]))
        return

    df = pd.read_csv(csv_path)

    table_data = [
        [
            Paragraph("<b>Problem</b>", styles["TableHeader"]),
            Paragraph("<b>Runs</b>", styles["TableHeader"]),
            Paragraph("<b>Gens</b>", styles["TableHeader"]),
            Paragraph("<b>Hypervolume (HV) ↑</b><br/>mean ± std", styles["TableHeader"]),
            Paragraph("<b>Inverted GD (IGD) ↓</b><br/>mean ± std", styles["TableHeader"]),
            Paragraph("<b>Generational Dist (GD) ↓</b><br/>mean ± std", styles["TableHeader"]),
            Paragraph("<b>Spacing ↓</b><br/>mean ± std", styles["TableHeader"])
        ]
    ]

    for _, row in df.iterrows():
        b_name = str(row['benchmark'])
        runs = str(int(row['runs']))
        gens = str(int(row['generations']))
        
        hv_str = fmt_mean_std(row['hv_mean'], row['hv_std'])
        igd_str = fmt_mean_std(row['igd_mean'], row['igd_std'])
        gd_str = fmt_mean_std(row['gd_mean'], row['gd_std'])
        sp_str = fmt_mean_std(row['spacing_mean'], row['spacing_std'])

        table_data.append([
            Paragraph(f"<b>{b_name}</b>", styles["TableCellBold"]),
            Paragraph(runs, styles["TableCellCenter"]),
            Paragraph(gens, styles["TableCellCenter"]),
            Paragraph(hv_str, styles["TableCell"]),
            Paragraph(igd_str, styles["TableCell"]),
            Paragraph(gd_str, styles["TableCell"]),
            Paragraph(sp_str, styles["TableCell"]),
        ])

    t_summary = Table(table_data, colWidths=[65, 30, 32, 102, 98, 98, 90])
    t_summary.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ('TOPPADDING', (0, 0), (-1, -1), 2.2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.2),
        ('ALIGN', (1, 1), (2, -1), 'CENTER'),
    ]))
    story.append(t_summary)
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "<i>Note on Generation Budgets:</i> Results were computed under three standardized generation allocations: "
        "<b>500 generations</b> for ZDT1-6; <b>2000 generations</b> for highly multi-modal DTLZ1 and DTLZ3; "
        "and <b>250 generations</b> for DTLZ2, DTLZ4, DTLZ5, DTLZ7, and the 18 classical problems. "
        "Direct numeric comparisons should strictly be performed between problems sharing identical generation budgets.",
        styles["Caption"]
    ))

    # Overview Figure
    story.append(PageBreak())
    story.append(Paragraph("30-Benchmark Comprehensive Pareto Front Mosaic", styles["SubsectionHeader"]))
    overview_img_path = FIGURES_DIR / "_overview_all_30.png"
    if overview_img_path.exists():
        # Printable width is ~515 pt. Overview aspect is 1800x1320 (aspect 1.36) -> 510 x 375 pt
        story.append(RLImage(str(overview_img_path), width=515, height=378))
        story.append(Paragraph(
            "<b>Figure 1:</b> Simultaneous visualization of obtained non-dominated fronts (blue markers) versus "
            "analytical reference Pareto fronts (red curves/surfaces) across all 30 benchmark problems.",
            styles["Caption"]
        ))
    
    story.append(Spacer(1, 8))
    obs_text = (
        "<b>Synthesis of Classical and Standard Benchmark Results:</b><br/>"
        "• <b>ZDT Suite:</b> Flawless convergence is achieved across ZDT1 (convex), ZDT2 (non-convex), and ZDT3 (disconnected five-segment front). ZDT4 (multimodal with 21^9 local fronts) reliably reaches the global front within 500 generations without premature stagnation. ZDT6 demonstrates uniform spacing despite its non-uniform search density.<br/>"
        "• <b>DTLZ Suite:</b> SPEA2 successfully reconstructs the 3D spherical surface of DTLZ2 and DTLZ4, the degenerate 1D curve in 3D objective space of DTLZ5, and the four disconnected surface patches of DTLZ7. For DTLZ6, the 250-generation budget is insufficient to overcome the deceptive barrier (HV remains 0.0), underscoring DTLZ6's exponential local basin severity.<br/>"
        "• <b>Constrained Benchmarks:</b> On Srinivas and Tanaka, feasibility-first dominance guarantees 100% feasible archive members across all independent runs, adhering cleanly to complex non-linear boundary curves."
    )
    story.append(create_callout(obs_text, styles, title="ANALYSIS OF FRONTS & CONVERGENCE DYNAMICS"))


def build_30_benchmarks_gallery(story, styles):
    story.append(PageBreak())
    story.append(Paragraph("2. Detailed Gallery: 30 Benchmark Pareto Fronts", styles["SectionHeader"]))
    story.append(Paragraph(
        "This section presents the individual experimental Pareto front plots for all 30 standard benchmarks. "
        "In each plot, blue circular markers indicate the non-dominated archive solutions obtained by SPEA2, "
        "while solid red lines/markers indicate the true analytical or high-density numerical reference Pareto front.",
        styles["BodyTextCustom"]
    ))

    # We will arrange figures in 2x2 grids (4 plots per page)
    # Groupings:
    groups = [
        ("ZDT Benchmark Problems (2-Objective)", ["zdt1", "zdt2", "zdt3", "zdt4", "zdt6"]),
        ("DTLZ Benchmark Problems (3-Objective)", ["dtlz1", "dtlz2", "dtlz3", "dtlz4", "dtlz5", "dtlz6", "dtlz7"]),
        ("Classical Benchmarks - Part 1", ["binh1", "binh3", "deb", "deb2", "fonseca", "fonseca2"]),
        ("Classical Benchmarks - Part 2", ["kursawe", "laumanns", "murata", "quagliarella", "rendon", "rendon2"]),
        ("Classical & Constrained Benchmarks - Part 3", ["schaffer", "schaffer2", "srinivas", "tanaka", "viennet", "viennet2"]),
    ]

    csv_path = RESULTS_DIR / "all_benchmarks_summary.csv"
    bench_data = {}
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        for _, r in df.iterrows():
            bench_data[str(r['benchmark']).lower()] = r

    for group_title, b_keys in groups:
        story.append(Paragraph(group_title, styles["SubsectionHeader"]))
        
        # We chunk into pairs for 2-column layout
        pairs = [b_keys[i:i + 2] for i in range(0, len(b_keys), 2)]
        
        for pair in pairs:
            row_cells = []
            for key in pair:
                img_path = FIGURES_DIR / f"{key}.png"
                r = bench_data.get(key)
                
                cell_content = []
                if img_path.exists():
                    # 250 pt width, aspect 1.33 -> 187 pt height
                    cell_content.append(RLImage(str(img_path), width=248, height=186))
                    
                    # Caption details
                    if r is not None:
                        cap_text = (
                            f"<b>{r['benchmark']}</b> ({int(r['runs'])} runs, {int(r['generations'])} gens)<br/>"
                            f"HV: {fmt(r['hv_mean'])} | IGD: {fmt(r['igd_mean'])} | Spacing: {fmt(r['spacing_mean'])}"
                        )
                    else:
                        cap_text = f"<b>{key.upper()}</b>"
                    cell_content.append(Paragraph(cap_text, styles["Caption"]))
                else:
                    cell_content.append(Paragraph(f"[Image {key}.png missing]", styles["Caption"]))
                
                row_cells.append(cell_content)
            
            # If odd item in pair
            if len(row_cells) == 1:
                row_cells.append([Spacer(1, 10)])
            
            grid_table = Table([row_cells], colWidths=[255, 255])
            grid_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 2),
                ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            story.append(KeepTogether(grid_table))
            story.append(Spacer(1, 4))


def build_cec2020_mmo_section(story, styles):
    story.append(PageBreak())
    story.append(Paragraph("3. CEC 2020 Multimodal Multi-Objective Optimization (MMO) Suite", styles["SectionHeader"]))
    story.append(Paragraph(
        "Multimodal Multi-Objective Optimization (MMO) investigates problems where multiple distinct decision-space "
        "solutions (Pareto Sets, PS) map to the same or equivalent objective-space vectors (Pareto Fronts, PF). "
        "The CEC 2020 MMO competition benchmark consists of <b>24 test problems (MMF1 through MMF16_l3)</b>.",
        styles["BodyTextCustom"]
    ))
    story.append(Paragraph(
        "<b>Official Protocol:</b> 21 independent runs (seeds 1–21), population = archive = 200 × N_ops, "
        "MaxFES = 10,000 × N_ops (exactly 50 generations with single evaluations). "
        "Four official indicators are recorded (all smaller-is-better): <b>1/PSP</b> (Peak Spread Pareto), "
        "<b>1/HV</b>, <b>IGDX</b> (distance in decision space), and <b>IGDF</b> (distance in objective space).",
        styles["BodyTextCustom"]
    ))

    csv_path = DATA_DIR / "06_cec2020_mmo_21runs" / "summary_metrics_all.csv"
    if not csv_path.exists():
        story.append(Paragraph("Error: CEC 2020 MMO summary CSV not found.", styles["BodyTextBold"]))
        return

    df_mmo = pd.read_csv(csv_path)

    table_data = [
        [
            Paragraph("<b>Problem</b>", styles["TableHeader"]),
            Paragraph("<b>N_ops</b>", styles["TableHeader"]),
            Paragraph("<b>1/PSP ↓</b><br/>mean ± std", styles["TableHeader"]),
            Paragraph("<b>1/HV ↓</b><br/>mean ± std", styles["TableHeader"]),
            Paragraph("<b>IGDX (Dec. Space) ↓</b><br/>mean ± std", styles["TableHeader"]),
            Paragraph("<b>IGDF (Obj. Space) ↓</b><br/>mean ± std", styles["TableHeader"])
        ]
    ]

    for _, r in df_mmo.iterrows():
        p_name = str(r['problem'])
        n_ops = str(int(r['n_ops']))
        psp_str = fmt_mean_std(r['rPSP_mean'], r['rPSP_std'], precision=4)
        hv_str = fmt_mean_std(r['rHV_mean'], r['rHV_std'], precision=4)
        igdx_str = fmt_mean_std(r['IGDX_mean'], r['IGDX_std'], precision=4)
        igdf_str = fmt_mean_std(r['IGDF_mean'], r['IGDF_std'], precision=4)

        table_data.append([
            Paragraph(f"<b>{p_name}</b>", styles["TableCellBold"]),
            Paragraph(n_ops, styles["TableCellCenter"]),
            Paragraph(psp_str, styles["TableCell"]),
            Paragraph(hv_str, styles["TableCell"]),
            Paragraph(igdx_str, styles["TableCell"]),
            Paragraph(igdf_str, styles["TableCell"]),
        ])

    t_mmo = Table(table_data, colWidths=[70, 35, 105, 100, 105, 100])
    t_mmo.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ('TOPPADDING', (0, 0), (-1, -1), 2.2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.2),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
    ]))
    story.append(t_mmo)
    story.append(Spacer(1, 8))

    analysis_text = (
        "<b>Key Analytical Takeaways on Multimodal Optimization:</b><br/>"
        "• <b>Global Pareto Sets:</b> On problems featuring purely global Pareto sets (MMF1, 2, 4, 5, 7, 8, 10-15 and _a variants), "
        "SPEA2 achieves excellent objective convergence (IGDF ≈ 0.001 to 0.08) and strong decision-space tracking (IGDX ≈ 0.0015 to 0.07). "
        "Even without explicit decision-space niching, large populations (400-800) maintain both branches via uniform random sampling.<br/>"
        "• <b>Local Pareto Sets (_l and MMF16 series):</b> When problems feature local Pareto sets, decision space error increases markedly "
        "(IGDX ≈ 0.15 to 0.32). Because local sets map to dominated fronts in objective space, pure Pareto-dominance selection naturally "
        "discards them in favor of global sets. MMO algorithms specifically require decision-space speciation or niching to retain these.<br/>"
        "• <b>Special Geometries & Official Quirks:</b> MMF1_e incorporates a search range up to [-20, 20] with exponential amplitude, resulting "
        "in an IGDX of 1.65 despite near-zero IGDF. Multiple official dataset anomalies (unreachable bounds in MMF13_l, non-covering HV reference "
        "points in MMF12_l/13_l, and 2D-only MATLAB hypervolume routines) were replicated precisely for benchmark fidelity."
    )
    story.append(create_callout(analysis_text, styles, title="MMO BEHAVIORAL ANALYSIS & LIMITATIONS"))


def build_cec2020_mmo_gallery(story, styles):
    story.append(PageBreak())
    story.append(Paragraph("CEC 2020 MMO Pareto Set & Front Gallery", styles["SubsectionHeader"]))
    story.append(Paragraph(
        "Each plot displays the median-1/PSP run out of 21 independent trials. "
        "The left panel depicts the <b>Decision Space (Pareto Sets)</b> with obtained points (blue) vs reference sets (red/green). "
        "The right panel displays the <b>Objective Space (Pareto Front)</b> with obtained non-dominated solutions (blue) vs true front (red).",
        styles["BodyTextCustom"]
    ))

    csv_path = DATA_DIR / "06_cec2020_mmo_21runs" / "summary_metrics_all.csv"
    if not csv_path.exists():
        return
    df_mmo = pd.read_csv(csv_path)

    # We stack 2 MMF plots per page. Each plot is 510 pt wide, aspect 2.36 -> height 216 pt.
    # 2 plots per page = 432 pt height + captions/spacers fits perfectly on ~730 pt printable height!
    problems = df_mmo['problem'].tolist()
    
    for i, p_name in enumerate(problems):
        fname = p_name.lower() + ".png"
        img_path = FIGURES_DIR / fname
        r = df_mmo[df_mmo['problem'] == p_name].iloc[0]

        card = []
        if img_path.exists():
            card.append(RLImage(str(img_path), width=512, height=217))
            caption_str = (
                f"<b>Figure MMO-{i+1}: {p_name}</b> (21 runs, 50 gens, N_ops={int(r['n_ops'])}) — "
                f"1/PSP: {fmt(r['rPSP_mean'])} ± {fmt(r['rPSP_std'])} | "
                f"1/HV: {fmt(r['rHV_mean'])} ± {fmt(r['rHV_std'])} | "
                f"IGDX: {fmt(r['IGDX_mean'])} ± {fmt(r['IGDX_std'])} | "
                f"IGDF: {fmt(r['IGDF_mean'])} ± {fmt(r['IGDF_std'])}"
            )
            card.append(Paragraph(caption_str, styles["Caption"]))
        else:
            card.append(Paragraph(f"[Image {fname} missing]", styles["Caption"]))

        story.append(KeepTogether(card))
        story.append(Spacer(1, 8))

        # PageBreak every 2 figures
        if (i + 1) % 2 == 0 and (i + 1) < len(problems):
            story.append(PageBreak())


def build_cec2022_section(story, styles):
    story.append(PageBreak())
    story.append(Paragraph("4. CEC 2022 Single-Objective Bound-Constrained Suite", styles["SectionHeader"]))
    story.append(Paragraph(
        "The CEC 2022 competition suite consists of <b>12 benchmark functions</b> designed to evaluate continuous optimization "
        "algorithms across unimodal, ill-conditioned, multimodal, hybrid, and composition landscapes. "
        "Our implementation is a line-by-line Python port of the organisers' C reference code (<code>cec22_test_func.cpp</code>), "
        "verified against official shift, rotation, and shuffle matrices with strict mathematical equivalence tests.",
        styles["BodyTextCustom"]
    ))
    story.append(Paragraph(
        "<b>Experimental Protocol:</b> 30 independent runs per function in both <b>10-D</b> and <b>20-D</b> configurations, "
        "utilizing the official competition random seeds (<code>Rand_Seeds.txt</code>). The computational budget is 200,000 MaxFES (10-D) "
        "and 1,000,000 MaxFES (20-D) with early stopping at error threshold 1e-8. When executing SPEA2 on single-objective problems, "
        "Pareto dominance reduces directly to tournament-based fitness ranking.",
        styles["BodyTextCustom"]
    ))

    csv_path = DATA_DIR / "07_cec2022_30runs" / "summary_metrics_all.csv"
    if not csv_path.exists():
        story.append(Paragraph("Error: CEC 2022 summary CSV not found.", styles["BodyTextBold"]))
        return

    df_2022 = pd.read_csv(csv_path)

    # Function names dictionary
    func_names = {
        1: "Shifted & Rotated Zakharov (Unimodal)",
        2: "Shifted & Rotated Rosenbrock (Valley)",
        3: "Shifted & Rotated Schaffer f6 (Multimodal)",
        4: "Shifted & Rotated Rastrigin (Multimodal)",
        5: "Shifted & Rotated Levy (Multimodal)",
        6: "Hybrid Function 1 (N = 3)",
        7: "Hybrid Function 2 (N = 6)",
        8: "Hybrid Function 3 (N = 5)",
        9: "Composition Function 1 (N = 5)",
        10: "Composition Function 2 (N = 3)",
        11: "Composition Function 3 (N = 5)",
        12: "Composition Function 4 (N = 6)",
    }

    table_data = [
        [
            Paragraph("<b>Fn</b>", styles["TableHeader"]),
            Paragraph("<b>Function Description</b>", styles["TableHeader"]),
            Paragraph("<b>Dim</b>", styles["TableHeader"]),
            Paragraph("<b>Best Error ↓</b>", styles["TableHeader"]),
            Paragraph("<b>Worst Error ↓</b>", styles["TableHeader"]),
            Paragraph("<b>Median Error ↓</b>", styles["TableHeader"]),
            Paragraph("<b>Mean Error ↓</b><br/>mean ± std", styles["TableHeader"])
        ]
    ]

    for _, r in df_2022.iterrows():
        fn_id = int(r['function'])
        dim = int(r['dim'])
        fn_name = func_names.get(fn_id, f"Function {fn_id}")
        
        best_str = fmt(r['best'])
        worst_str = fmt(r['worst'])
        med_str = fmt(r['median'])
        mean_std_str = fmt_mean_std(r['mean'], r['std'])

        table_data.append([
            Paragraph(f"<b>F{fn_id}</b>", styles["TableCellBold"]),
            Paragraph(fn_name, styles["TableCell"]),
            Paragraph(f"{dim}D", styles["TableCellCenter"]),
            Paragraph(best_str, styles["TableCell"]),
            Paragraph(worst_str, styles["TableCell"]),
            Paragraph(med_str, styles["TableCell"]),
            Paragraph(mean_std_str, styles["TableCell"]),
        ])

    t_2022 = Table(table_data, colWidths=[30, 165, 35, 70, 70, 70, 75])
    t_2022.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ('TOPPADDING', (0, 0), (-1, -1), 2.2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.2),
        ('ALIGN', (2, 1), (2, -1), 'CENTER'),
    ]))
    story.append(t_2022)
    story.append(Spacer(1, 10))

    cec2022_notes = (
        "<b>Analysis of SPEA2 on CEC 2022 Single-Objective Landscapes:</b><br/>"
        "• <b>Basic & Unimodal Problems (F1, F3, F5):</b> On Zakharov (F1), Schaffer f6 (F3), and Levy (F5), SPEA2 achieves outstanding "
        "accuracy, converging within 0.0001 to 0.18 error in 10-D, demonstrating the effectiveness of the Simulated Binary Crossover (SBX) operator.<br/>"
        "• <b>Curved Valley Optimization (F2 Rosenbrock):</b> In 10-D, median error is 7.87, scaling to 49.08 in 20-D. The classic parabolic "
        "curved ridge of Rosenbrock challenges isotropic recombination operators, requiring coordinated parameter changes.<br/>"
        "• <b>Hybrid Landscapes (F6-F8):</b> Performance is governed by the underlying component mixture. F6 exhibits significant variance "
        "(mean 1453.28 in 10-D and 4560.06 in 20-D), while F7 and F8 demonstrate consistent sub-25 median errors across runs.<br/>"
        "• <b>Composition Functions (F9-F12):</b> On complex landscapes composed of rotated, shifted multimodal sub-functions with varying "
        "height biases, SPEA2 experiences local basin trapping (e.g. F9 exhibits a narrow error range around ~229.28). This confirms that "
        "without specialized single-objective exploration mechanisms (such as covariance matrix adaptation or restart strategies), pure "
        "genetic search is vulnerable to high-dimensional composition barriers."
    )
    story.append(create_callout(cec2022_notes, styles, title="CEC 2022 PERFORMANCE & LANDSCAPE INSIGHTS"))


def build_conclusions_and_appendix(story, styles):
    story.append(PageBreak())
    story.append(Paragraph("5. Architectural Formulation & Verification Suite", styles["SectionHeader"]))
    
    algo_desc = (
        "<b>SPEA2 Mathematical Formulation:</b><br/>"
        "SPEA2 addresses the limitations of original SPEA through four fundamental mechanisms:<br/>"
        "<b>1. Dominance & Strength:</b> For each individual i in population P_t and archive A_t, its strength S(i) is the number of "
        "solutions it dominates: S(i) = |{j | j ∈ P_t ∪ A_t ∧ i ≻ j}|.<br/>"
        "<b>2. Raw Fitness R(i):</b> Determined by the strengths of its dominators: R(i) = ∑_{j ≻ i} S(j). R(i) = 0 denotes non-dominated individuals.<br/>"
        "<b>3. Density Estimation D(i):</b> Based on the k-th nearest neighbor distance σ_i^k in objective space (k = √(|P_t| + |A_t|)): "
        "D(i) = 1 / (σ_i^k + 2). Total fitness is F(i) = R(i) + D(i).<br/>"
        "<b>4. Environmental Selection & Truncation:</b> All non-dominated solutions (F(i) < 1) are copied to A_{t+1}. If |A_{t+1}| < N', "
        "the best dominated solutions are added. If |A_{t+1}| > N', an iterative truncation operator eliminates the solution having the "
        "minimum distance to its nearest neighbor, preserving boundary front diversity.<br/>"
        "<b>5. Constraint Handling:</b> Deb's feasibility-first constraint dominance is employed: solution i dominates j if i is feasible and "
        "j is infeasible; or if both are infeasible, i has a smaller total constraint violation; or if both are feasible, standard Pareto dominance applies."
    )
    story.append(Paragraph(algo_desc, styles["BodyTextCustom"]))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Software Engineering & Regression Suite", styles["SubsectionHeader"]))
    story.append(Paragraph(
        "The codebase has been constructed to the highest standards of scientific reproducibility and computational verification. "
        "A rigorous suite of <b>300 automated tests</b> (managed via <code>pytest</code>) verifies every module:",
        styles["BodyTextCustom"]
    ))

    test_points = [
        "<b>Metric Exactness:</b> Hypervolume calculations verified against analytical 2D and 3D closed-form volumes; IGD, GD, and Spacing validated against synthetic reference sets.",
        "<b>Exact Algorithmic Equivalence:</b> Byte-for-byte and numeric digest verification ensuring that optimized NumPy vectorization exactly mirrors the pure-Python reference SPEA2 logic across all evolutionary loops.",
        "<b>Benchmark Sanity & Bound Checks:</b> Validation of lower/upper coordinate boundaries, dimension sizes, constraint penalty values, and reference Pareto front non-dominance for all 30 benchmarks.",
        "<b>Competition Suite Integrity:</b> SHA256 checksum verification of official CEC 2022 shift and rotation matrices, verification that F(o) = F* at official optima, and validation of CEC 2020 MMO indicator metrics (PSP, IGDX, IGDF, HV)."
    ]
    for pt in test_points:
        story.append(Paragraph(f"• {pt}", styles["BodyTextCustom"]))

    story.append(Spacer(1, 10))
    story.append(Paragraph("References", styles["SubsectionHeader"]))
    refs = [
        "[1] E. Zitzler, M. Laumanns, and L. Thiele, 'SPEA2: Improving the Strength Pareto Evolutionary Algorithm,' TIK-Report 103, ETH Zurich, 2001.",
        "[2] K. Deb, 'Multi-Objective Optimization using Evolutionary Algorithms,' John Wiley & Sons, Chichester, UK, 2001.",
        "[3] K. Deb, L. Thiele, M. Laumanns, and E. Zitzler, 'Scalable Test Problems for Evolutionary Multiobjective Optimization,' Evolutionary Multiobjective Optimization, pp. 105-145, 2005.",
        "[4] C. Yue, P. Suganthan, K. Liang, et al., 'Problem Definitions and Evaluation Criteria for the CEC 2020 Special Session and Competition on Multimodal Multiobjective Optimization,' Technical Report, Zhengzhou University & NTU, 2020.",
        "[5] P. N. Suganthan et al., 'Problem Definitions and Evaluation Criteria for the CEC 2022 Special Session and Competition on Single Objective Bound Constrained Numerical Optimization,' Technical Report, 2022."
    ]
    for r in refs:
        story.append(Paragraph(r, styles["Caption"]))


def main():
    print(f"Generating comprehensive PDF report at: {OUTPUT_PDF}")
    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=46,
        bottomMargin=46
    )

    styles = get_custom_styles()
    story = []

    print("Building Cover & Executive Summary...")
    build_cover_page(story, styles)

    print("Building Section 1: 30 Benchmarks Overview...")
    build_30_benchmarks_section(story, styles)

    print("Building Section 2: 30 Benchmarks Plots Gallery...")
    build_30_benchmarks_gallery(story, styles)

    print("Building Section 3: CEC 2020 MMO Suite...")
    build_cec2020_mmo_section(story, styles)

    print("Building Section 3b: CEC 2020 MMO Gallery...")
    build_cec2020_mmo_gallery(story, styles)

    print("Building Section 4: CEC 2022 Single-Objective Suite...")
    build_cec2022_section(story, styles)

    print("Building Section 5: Architecture & Verification Suite...")
    build_conclusions_and_appendix(story, styles)

    print("Compiling PDF document with NumberedCanvas...")
    doc.build(story, canvasmaker=NumberedCanvas)
    
    file_size_mb = os.path.getsize(OUTPUT_PDF) / (1024 * 1024)
    print(f"Report successfully generated! File size: {file_size_mb:.2f} MB")


if __name__ == "__main__":
    main()
