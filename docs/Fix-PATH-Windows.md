# Fix PATH for MySQL and Python (Windows)

If `mysql`, `python`, or `py` are not recognized in PowerShell or Command Prompt, add the correct folders to your **user** PATH. This does not require admin rights.

---

## 1. Open Environment Variables

1. Press **Win**, type **environment variables**.
2. Click **Edit the system environment variables** (or **Edit environment variables for your account**).
3. In the window that opens, click **Environment Variables**.

---

## 2. Edit User PATH

1. Under **User variables for [your name]**, select **Path**.
2. Click **Edit**.
3. You’ll see a list of folders. Use **New** to add; select a line and **Delete** to remove bad entries.

---

## 3. Add These Entries (click New for each)

**MySQL (so `mysql` works):**
```
C:\Program Files\MySQL\MySQL Server 8.0\bin
```
If you have a different MySQL version (e.g. 8.4), use that folder instead, but keep `\bin` at the end.

**Python (so `python` works):**
```
C:\Users\slimm\AppData\Local\Python\pythoncore-3.14-64
```
```
C:\Users\slimm\AppData\Local\Python\pythoncore-3.14-64\Scripts
```
The **Scripts** folder is where `streamlit`, `pip`, etc. live; adding it lets you run `streamlit` from the command line.

If your Python is elsewhere (e.g. `C:\Users\slimm\AppData\Local\Programs\Python\Python314`), add that folder and its `Scripts` subfolder instead.

---

## 4. Remove Bad Entries (optional)

If you see duplicate or wrong paths (e.g. old Python version, typo, or a path that no longer exists):

- Select that line and click **Delete**.
- Don’t delete Windows system paths (e.g. `C:\Windows\System32`) unless you know what they are.

---

## 5. Save and Restart Terminal

1. Click **OK** on the Edit window.
2. Click **OK** on Environment Variables.
3. Click **OK** on System Properties.
4. **Close all PowerShell or Command Prompt windows** and open a new one.

PATH is read when the terminal starts; a new window is required for changes to apply.

---

## 6. Check That It Worked

In a **new** PowerShell window, run:

```powershell
mysql --version
python --version
streamlit --version
```

If you see version numbers, PATH is set correctly.

---

## If Python Is Still Not Found

Your Python might be in a different folder. To find it:

```powershell
Get-ChildItem -Path $env:LOCALAPPDATA -Recurse -Filter "python.exe" -ErrorAction SilentlyContinue 2>$null | Select-Object -First 3 FullName
```

Use the **folder that contains** `python.exe` (e.g. `C:\Users\slimm\AppData\Local\Python\pythoncore-3.14-64`). Add that folder and its `Scripts` subfolder (if it exists) to PATH as in step 3.

---

## Summary of Paths to Add

| Purpose | Path to add |
|--------|-------------|
| MySQL 8.0 | `C:\Program Files\MySQL\MySQL Server 8.0\bin` |
| Python (run scripts) | `C:\Users\slimm\AppData\Local\Python\pythoncore-3.14-64` |
| Python Scripts (streamlit, pip) | `C:\Users\slimm\AppData\Local\Python\pythoncore-3.14-64\Scripts` |

After editing PATH, always open a **new** terminal before testing.
