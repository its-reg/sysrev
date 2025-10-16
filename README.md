why hello there!
 
## Setup virtual environment

Windows (PowerShell):

```powershell
# create venv (if not already created)
py -3.12 -m venv .venv

# activate in PowerShell
.\.venv\Scripts\Activate.ps1

# If Activate.ps1 is blocked by ExecutionPolicy, run commands with the venv python instead:
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -r requirements.txt
```

To allow running Activate.ps1 (optional, run as Administrator if required):

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

If you prefer bash or WSL, activate with:

```bash
source .venv/bin/activate
```

That's it — the project contains a `.venv` in the repository root. Use the venv's python directly if activation is blocked.

## Installed packages

These packages were installed into `.venv`:

- rispy==0.10.0
- pandas==2.3.3
- systematic-reviewpy==0.0.1
