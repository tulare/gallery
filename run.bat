@SETLOCAL
@CALL py -m pipenv sync
@CALL py -m pipenv run python run.py %*
@ENDLOCAL