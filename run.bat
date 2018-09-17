@SETLOCAL
@CALL venv\Scripts\activate
@IF %ERRORLEVEL% EQU 0 GOTO :run
@CALL create-venv.bat
@CALL venv\Scripts\activate
:run
@python --version
@python run.py %*
@ENDLOCAL