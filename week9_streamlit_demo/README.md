# Streamlit App Starter Repo

This repository is a Streamlit app starter repo for students.

## Overview

Students can use this repo to clone a starter Streamlit application, open it in VS Code, sync dependencies with `uv`, and run the app locally.

## Getting Started

1. Create a new folder for the project and open it in VS Code.
2. Open the VS Code terminal.
3. In the terminal, clone the repo into that folder and change into it:

```powershell
git clone https://github.com/ntu-mara-db-prog/week9_streamlit_demo.git .
```

4. Sync the environment with `uv`:

```powershell
uv sync
```

5. Run the app locally:

```powershell
uv run streamlit run src/week9_streamlit_starter.py
```

This should show the same output as the deployed app at:

https://st-dashboard-starter.streamlit.app/

* Please "wake" it up if if it is sleeping.