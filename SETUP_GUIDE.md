# Step-by-step setup guide

Follow these steps in order so you can run **Resume × Role Fit** on your computer and later share it online.

---

## Part 1: Install the software you need

You only need **Python 3** to run this project.

**Optional:** Image upload (photo/screenshot) uses OCR and requires extra installs. If you skip OCR, you can still use **Paste / PDF / DOCX / TXT / Link** normally.

### On macOS

1. **Install Xcode Command Line Tools** (needed for some Python features like `venv`):
   - Open **Terminal** (search “Terminal” in Spotlight).
   - Run:
     ```bash
     xcode-select --install
     ```
   - Click **Install** in the popup and wait for it to finish.

2. **Install Python 3** (if you don’t have it):
   - Option A – From [python.org](https://www.python.org/downloads/): download the macOS installer, run it, and follow the steps. Make sure you check “Add Python to PATH” if asked.
   - Option B – Using Homebrew (if you use it):
     ```bash
     brew install python
     ```

3. **Check that Python is installed**:
   ```bash
   python3 --version
   ```
   You should see something like `Python 3.11.x` or `Python 3.12.x`.

4. **(Optional) Install OCR for image uploads** (only needed for image input):
   - If you use Homebrew:
     ```bash
     brew install tesseract
     ```
   - Then (inside your activated `venv`) install Python packages:
     ```bash
     pip install Pillow pytesseract
     ```

### On Windows

1. **Install Python 3**:
   - Go to [python.org/downloads](https://www.python.org/downloads/).
   - Download the latest **Python 3** installer for Windows.
   - Run the installer and **check the box “Add Python to PATH”** at the bottom.
   - Click “Install Now” and finish the setup.

2. **Check that Python is installed**:
   - Open **Command Prompt** or **PowerShell** and run:
     ```bash
     python --version
     ```
   You should see something like `Python 3.11.x` or `Python 3.12.x`.

3. **(Optional) Install OCR for image uploads** (only needed for image input):
   - Download the Windows installer from the official Tesseract project releases, install it, and ensure `tesseract` is available in PATH.
   - If you don’t want OCR setup, use Paste / PDF / DOCX instead.
   - Then (inside your activated `venv`) install Python packages:
     ```bash
     pip install Pillow pytesseract
     ```

---

## Part 2: Run the project on your computer

Do these steps in **Terminal** (macOS) or **Command Prompt / PowerShell** (Windows).

### Step 1: Go to the project folder

```bash
cd "/Users/shambhavirai/Desktop/Cursor Projects/resume-job-analyzer"
```

(On Windows, use your actual path, for example: `cd C:\Users\YourName\Desktop\resume-job-analyzer`.)

### Step 2: Create a virtual environment (recommended)

This keeps the project’s dependencies separate from the rest of your system.

- **macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```
- **Windows (Command Prompt):**
  ```bash
  python -m venv venv
  venv\Scripts\activate
  ```
- **Windows (PowerShell):**
  ```bash
  python -m venv venv
  venv\Scripts\Activate.ps1
  ```

When the virtual environment is active, you’ll see `(venv)` at the start of the line in your terminal.

### Step 3: Install dependencies

With the virtual environment still active:

```bash
pip install -r requirements.txt
```

Wait until it finishes without errors.

### Step 4: Start the app

```bash
python app.py
```

You should see something like:

```
 * Running on http://127.0.0.1:5000
```

### Step 5: Open the app in your browser

1. Open your browser (Chrome, Safari, Firefox, etc.).
2. In the address bar, type: **http://127.0.0.1:5000** and press Enter.
3. You should see the **Resume × Role Fit** page.
4. Paste your resume in the first box and a job description in the second, then click **Analyze fit**.

To stop the app, go back to the terminal and press **Ctrl + C**.

---

## If something goes wrong

- **“python3: command not found”** (Mac) or **“python is not recognized”** (Windows)  
  → Python is not installed or not on your PATH. Repeat the Python install steps and make sure you checked “Add to PATH” on Windows.

- **“xcode-select: error”** (Mac)  
  → Run `xcode-select --install` and complete the installation.

- **“No module named 'flask'”**  
  → Activate the virtual environment again (`source venv/bin/activate` or `venv\Scripts\activate`) and run `pip install -r requirements.txt` again.

- **Port 5000 already in use**  
  → Another program is using port 5000. Close that program or change the port in `app.py` (e.g. `app.run(debug=True, port=5001)`).

---

## Next: share and showcase your project

See **SHOWCASE.md** for where to put your code and how to deploy the app so others can use it and you can show it in your portfolio.
