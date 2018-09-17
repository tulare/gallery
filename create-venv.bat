@SETLOCAL
@echo %0
@py.exe -m venv --clear venv
@venv\Scripts\python -m pip install --upgrade pip setuptools wheel
@venv\Scripts\python -m pip install --find-links=wheels --upgrade -r run.req
@venv\Scripts\python -m pip list
@ENDLOCAL