@echo on

call git restore .
call git pull
call app.bat init

:end