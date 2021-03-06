@SETLOCAL
@SET APP_DIR=%~dp0
@SET PIPENV_PIPFILE=%APP_DIR%\Pipfile
@SET PIPENV_VENV_IN_PROJECT=1

@REM --- check venv ---
@FOR /F %%V in ('py -m pipenv --venv') DO @SET _venv=%%V
@IF NOT EXIST "%_venv%" GOTO :novenv

@REM --- run python in venv ---
@FOR /F %%P in ('py -m pipenv --py') DO @%%P %APP_DIR%\main.py %*
@GOTO end

:novenv
@ECHO Python virtual environement not found

:end
@ENDLOCAL