# Rename app folder to ProxyForge

All **references** to "Wargaming ERP" and paths like `Wargaming_ERP/` have been updated to **ProxyForge** in docs, README, app title, and migration paths.

The **folder** `Wargaming_ERP` could not be renamed automatically (it was in use). Do this manually:

1. **Close** Cursor/IDE and any terminal that’s using the project (or at least don’t have that folder open).
2. In File Explorer (or PowerShell), **rename** the folder:
   - From: `WahapediaExport\Wargaming_ERP`
   - To: `WahapediaExport\ProxyForge`
3. **Tell Git** about the rename (from repo root):
   ```powershell
   cd C:\Users\slimm\Desktop\WahapediaExport
   git add -A
   git status
   ```
   Git should show the old folder as deleted and the new one as added (or as a rename). Then commit:
   ```powershell
   git commit -m "Rename Wargaming_ERP folder to ProxyForge"
   ```

After renaming, run the app with: `streamlit run ProxyForge/app.py`

You can delete this file (RENAME_FOLDER.md) after you’re done.
