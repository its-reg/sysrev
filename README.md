why hello there!
This is very much still a work-in-progress.

My current search strategy:
Ovid MEDLINE(R) ALL <1946 to October 10, 2025>

# Search Terms                   Results
1 Parkinson Disease/             92037
2 parkinson* disease.ti,ab,kf.   137917
3 1 or 2                         152089
4 Geographic Information 
  Systems/                       10282
5 spatial analysis/ 
  or spatial regression/ 
  or spatio-temporal analysis/
  or space-time clustering/      16378
6 (geospatial or space-time 
  or GIS or Geographic 
  information systems).ti,ab,kf. 26623
7 4 or 5 or 6                    45794
8 3 and 7                        88

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

## Installed packages

These packages were installed into `.venv`:

- rispy==0.10.0
- pandas==2.3.3
- systematic-reviewpy==0.0.1
