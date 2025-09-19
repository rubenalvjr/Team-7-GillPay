# Team 7 GillPay Project

Team 7 finance tracking application for Texas A&M Master MIS Program.

# Contributors
 - Matthew Bennett
 - Enoch Adegbola
 - Ally Herleth
 - Jo Ann Kern
 - Ruben Alvarez


# GillPay — How to Run

## Windows (easiest)
1) Double-click `run.bat`.
   - It will create `.venv_local`, install dependencies from `requirements.txt`, and launch the app.

## macOS / Linux
python3 -m venv .venv_local
source .venv_local/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python gui/app.py

Notes
- Requires Python 3.13+.
- On Linux, install Tk if missing (e.g., Ubuntu: `sudo apt install python3-tk`).
- Do **not** use or ship a prebuilt `.venv`.
