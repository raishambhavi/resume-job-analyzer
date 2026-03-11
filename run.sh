#!/bin/bash
# Run the app using this project's venv (avoids path/python mismatch)
cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
  echo "No venv found. Create it first:"
  echo "  python3 -m venv venv"
  echo "  ./venv/bin/python -m pip install -r requirements.txt"
  exit 1
fi

# Install deps with the SAME Python that will run the app
./venv/bin/python -m pip install -q -r requirements.txt

# Run
./venv/bin/python app.py
