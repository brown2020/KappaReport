#!/usr/bin/env python3
"""
Kappa Light Chain Report Generator
Generates a comprehensive PDF report analyzing kappa light chain measurements
with pre- and post-venetoclax treatment modeling.
"""

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime
from pathlib import Path


def load_data(data_file="data.json"):
    """Load measurement data from JSON file."""
    try:
        with open(data_file, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Data file '{data_file}' not found. Please ensure it exists."
        )
    except json.JSONDecodeError:
        raise ValueError(
            f"Invalid JSON in '{data_file}'. Please check the file format."
        )


def load_notes(notes_file="notes.json"):
    """Load analysis notes from JSON file."""
    try:
        with open(notes_file, 'r') as f:
            notes = json.load(f)
        return notes
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Notes file '{notes_file}' not found. Please ensure it exists."
        )
    except json.JSONDecodeError:
        raise ValueError(
            f"Invalid JSON in '{notes_file}'. Please check the file format."
        )


def format_notes(notes_data, **kwargs):
    """Format notes with dynamic values."""
    formatted_sections = []
    
    for section in notes_data["sections"]:
        section_text = f"{section['title']}\n"
        for line in section["content"]:
            formatted_line = line.format(**kwargs)
            section_text += f"   {formatted_line}\n"
        formatted_sections.append(section_text)
    
    return "\n".join(formatted_sections)


def main():
    # -- Data Loading ------------------------------------------------------
    print("Loading data from JSON files...")
    data = load_data()
    notes_data = load_notes()
    
    # Extract data from JSON - new structure with individual entries
    measurements = data["measurements"]
    settings = data["settings"]
    
    # Convert measurements to separate arrays
    dates = [m["date"] for m in measurements]
    kappa = [m["kappa"] for m in measurements]
    lambda_ = [m["lambda"] for m in measurements]
    
    # Validate data
    if not measurements:
        raise ValueError("No measurements found in data file")
    
    # -- Data Preparation --------------------------------------------------
    df = pd.DataFrame({
        "Date": pd.to_datetime(dates),
        "Kappa": kappa,
        "Lambda": lambda_
    })
    df["Ratio"] = (df["Kappa"] / df["Lambda"]).round(2)
    df["Delta"] = df["Kappa"].diff().fillna(0).round(1)
    df["% Change"] = (
        (df["Kappa"].pct_change().fillna(0) * 100)
        .round(1).astype(str) + "%"
    )

    # -- Model Fitting ----------------------------------------------------
    split_date = datetime.fromisoformat(settings["split_date"])
    df_pre = df[df["Date"] <= split_date]
    df_post = df[df["Date"] >= split_date]

    def gompertz(x, A, B, C):
        return A * np.exp(-B * np.exp(-C * x))

    x_pre = (df_pre["Date"] - df_pre["Date"].min()).dt.days.values
    popt_g, _ = curve_fit(
        gompertz, x_pre, df_pre["Kappa"],
        p0=[df_pre["Kappa"].max(), 1, 0.05], maxfev=10000
    )

    def exp_model(x, A, k):
        return A * np.exp(-k * x)

    x_post = (df_post["Date"] - df_post["Date"].min()).dt.days.values
    popt_e, _ = curve_fit(
        exp_model, x_post, df_post["Kappa"], bounds=(0, [1000, 1])
    )

    # Projections
    end = datetime.fromisoformat(settings["projection_end_date"])
    pre_dates = pd.date_range(df_pre["Date"].min(), end)
    post_dates = pd.date_range(df_post["Date"].min(), end)
    proj_pre = gompertz((pre_dates - df_pre["Date"].min()).days, *popt_g)
    proj_post = exp_model(
        (post_dates - df_post["Date"].min()).days, *popt_e
    )

    # Thresholds
    vgpr = settings["vgpr_threshold"]
    cr = settings["cr_threshold"]
    vgpr_date = post_dates[np.where(proj_post < vgpr)[0][0]]
    cr_date = post_dates[np.where(proj_post < cr)[0][0]]

    # -- PDF Report Generation -------------------------------------------
    # Create output directory in current working directory
    output_dir = Path.cwd()
    latest_date = df["Date"].max().strftime("%Y-%m-%d")
    filename = f"Kappa_Report_Through_{latest_date}_DetailedNotes.pdf"
    pdf_path = output_dir / filename
    
    print("Generating report...")
    print(f"Output location: {pdf_path}")
    
    # Configure matplotlib for better PDF output
    plt.rcParams['font.size'] = 9
    plt.rcParams['axes.titlesize'] = 11
    plt.rcParams['axes.labelsize'] = 9
    plt.rcParams['legend.fontsize'] = 8
    
    with PdfPages(pdf_path) as pdf:
        # Page 1: Linear Scale Chart
        # 8.5x11" page with 0.5" margins: 7.5" wide x 10" tall usable area
        fig, ax = plt.subplots(figsize=(7.5, 5.5))
        ax.plot(df["Date"], df["Kappa"], 'o', markersize=4, label="Observed")
        ax.plot(pre_dates, proj_pre, '--', color='green', linewidth=2,
                label="Pre-Ven Gompertz")
        ax.plot(post_dates, proj_post, '--', color='blue', linewidth=2,
                label="Post-Ven Exp")
        ax.axhline(vgpr, color='purple', linestyle=':', linewidth=1.5,
                   label=f"VGPR (<{vgpr} mg/L)")
        ax.axhline(cr, color='red', linestyle=':', linewidth=1.5,
                   label=f"CR (<{cr} mg/L)")
        ax.axvline(vgpr_date, color='purple', linestyle=':', alpha=0.7,
                   label=f"VGPR by {vgpr_date:%b %d, %Y}")
        ax.axvline(cr_date, color='red', linestyle=':', alpha=0.7,
                   label=f"CR by {cr_date:%b %d, %Y}")
        ax.set_title("Kappa Light Chain: Linear Scale with Projections", 
                    fontsize=12, fontweight='bold', pad=15)
        ax.set_xlabel("Date", fontsize=10)
        ax.set_ylabel("Kappa (mg/L)", fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=7, loc='upper right')
        
        # Improve date formatting
        fig.autofmt_xdate()
        plt.tight_layout()
        pdf.savefig(bbox_inches='tight', dpi=300)
        plt.close()

        # Page 2: Log Scale Chart
        fig, ax = plt.subplots(figsize=(7.5, 5.5))
        ax.semilogy(df["Date"], df["Kappa"], 'o', markersize=4, label="Observed")
        ax.semilogy(pre_dates, proj_pre, '--', color='green', linewidth=2,
                    label="Pre-Ven Gompertz")
        ax.semilogy(post_dates, proj_post, '--', color='blue', linewidth=2,
                    label="Post-Ven Exp")
        ax.axhline(vgpr, color='purple', linestyle=':', linewidth=1.5,
                   label=f"VGPR (<{vgpr} mg/L)")
        ax.axhline(cr, color='red', linestyle=':', linewidth=1.5,
                   label=f"CR (<{cr} mg/L)")
        ax.axvline(vgpr_date, color='purple', linestyle=':', alpha=0.7,
                   label=f"VGPR by {vgpr_date:%b %d, %Y}")
        ax.axvline(cr_date, color='red', linestyle=':', alpha=0.7,
                   label=f"CR by {cr_date:%b %d, %Y}")
        ax.set_title("Kappa Light Chain: Log Scale with Projections", 
                    fontsize=12, fontweight='bold', pad=15)
        ax.set_xlabel("Date", fontsize=10)
        ax.set_ylabel("Kappa (mg/L, log scale)", fontsize=10)
        ax.grid(True, which='both', alpha=0.3)
        ax.legend(fontsize=7, loc='upper right')
        
        fig.autofmt_xdate()
        plt.tight_layout()
        pdf.savefig(bbox_inches='tight', dpi=300)
        plt.close()

        # Page 3: Compressed Data Table
        fig, ax = plt.subplots(figsize=(7.5, 9.5))
        ax.axis("off")
        
        # Create table with optimized column widths for 7.5" page
        tbl = [["Date", "Kappa", "Lambda", "Ratio", "Δ", "%Δ"]] + [
            [row["Date"].strftime("%m/%d"), f"{row['Kappa']:.1f}", 
             f"{row['Lambda']:.1f}", f"{row['Ratio']:.1f}", 
             f"{row['Delta']:+.1f}", row["% Change"]]
            for _, row in df.iterrows()
        ]
        
        # Optimized table for 7.5" width
        table = ax.table(
            cellText=tbl, loc="center", cellLoc="center", 
            colWidths=[0.15, 0.18, 0.18, 0.15, 0.15, 0.15]
        )
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 1.4)
        
        # Style header row
        for i in range(len(tbl[0])):
            table[(0, i)].set_facecolor('#40466e')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # Alternate row colors for better readability
        for i in range(1, len(tbl)):
            if i % 2 == 0:
                for j in range(len(tbl[0])):
                    table[(i, j)].set_facecolor('#f8f9fa')
        
        plt.title("Free Light Chain Results", fontsize=14, 
                 fontweight='bold', pad=25)
        plt.tight_layout()
        pdf.savefig(bbox_inches='tight', dpi=300)
        plt.close()

        # Page 4: Detailed Notes
        formatted_notes = format_notes(
            notes_data,
            proj_pre_final=proj_pre[-1],
            vgpr=vgpr,
            cr=cr,
            vgpr_date=vgpr_date,
            cr_date=cr_date
        )
        
        fig, ax = plt.subplots(figsize=(7.5, 10))
        ax.axis("off")
        
        # Title at top
        fig.text(0.1, 0.95, notes_data["title"], 
                fontsize=12, fontweight="bold")
        
        # Notes content starting right after title
        fig.text(0.1, 0.90, formatted_notes, fontsize=8, va="top",
                wrap=True, verticalalignment='top')
        
        plt.tight_layout()
        pdf.savefig(bbox_inches='tight', dpi=300)
        plt.close()

    print(f"Report generated successfully: {pdf_path}")
    print(f"File size: {pdf_path.stat().st_size / 1024:.1f} KB")
    print("Pages formatted for 8.5x11\" portrait with 0.5\" margins")


if __name__ == "__main__":
    main() 