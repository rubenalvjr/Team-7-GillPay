Team 7 — GillPay

A simple finance tracking application built for the Texas A&M MS-MIS program.

Contributors

Matthew Bennett

Enoch Adegbola

Ally Herleth

Jo Ann Kern

Ruben Alvarez

![Alt text](images/Goofy%20Goldfishes%20Updated%20Logo.png)



Requirements

Python 3.13+ recommended (3.11+ should work)

Tkinter available on the system

Windows: included with the official python.org installer

macOS: included with the official python.org installer

Linux: install python3-tk via your package manager


Quick Start
Windows (recommended)

Double-click run.bat.

The launcher will:

create .venv_local if missing

upgrade pip and install dependencies from requirements.txt (or minimal defaults)

launch the GUI with python -m gui.app

If script execution is blocked, open PowerShell and run:

powershell -ExecutionPolicy Bypass -NoProfile -File .\Run.ps1





macOS / Linux

Make the script executable once, then run it:

chmod +x run.sh
./run.sh






The script creates .venv_local, installs dependencies, and runs python -m gui.app.

Alternative: Manual Setup
# Create and activate a virtual environment
python3 -m venv .venv_local
# macOS/Linux:
. .venv_local/bin/activate
# Windows PowerShell:
# .\.venv_local\Scripts\Activate.ps1

# Install requirements
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Launch the GUI
python -m gui.app

CLI Mode (optional)

You can use a simple CLI for quick data entry and reports:

python -m main




Menu options:

Add Transaction

Account Summary

Expense by Category Report

Spending by Month Report

Charts (Matplotlib)

Launch GUI

Exit





Data File

GillPay reads and writes data/gillpay_data.csv.

CSV schema

transaction,category,description,amount,date


transaction: income or expense (case-insensitive)

category: drop down selection or "Other" brings up a free-form text box (for example, groceries, rent)

description: free-form text

amount: numeric; the application normalizes expenses to negative values

date: YYYY/MM/DD (for example, 2025/09/30)

Example:

income,salary,Paycheck,2500,2025/09/30
expense,groceries,HEB,120.53,2025/09/29


The repository ignores data/gillpay_data.csv. Commit a sample file such as data/sample_gillpay_data.csv if you want a demo dataset.

Packaging (Windows)



Troubleshooting

ImportError for src...
Launch using the provided scripts or python -m gui.app so package imports resolve correctly.

Tkinter not found

Ubuntu/Debian: sudo apt install python3-tk

Fedora: sudo dnf install python3-tkinter

macOS: use the official Python.org installer

PowerShell script blocked
Use run.bat or run:

powershell -ExecutionPolicy Bypass -NoProfile -File .\Run.ps1


CSV date errors
Dates must be YYYY/MM/DD. Invalid dates are coerced to NaT and excluded from month summaries.





License

Academic project for course use. Not licensed for production use.