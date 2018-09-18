@SETLOCAL
@CALL pipenv install --deploy
@CALL pipenv run python run.py %*
@ENDLOCAL