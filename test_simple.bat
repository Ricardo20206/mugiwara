@echo off
echo Test du code Python...
python -c "from chronobio_client.strategy import Strategy; s = Strategy(); print('OK - Strategy importe correctement')"
echo.
echo Test termine!
pause
