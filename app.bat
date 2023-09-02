@echo on

IF NOT "%1"=="" (
	goto %~1 
) ELSE (
	call init.bat check
	goto run
)

:update
call git restore .
call git pull
goto init

:init
call init.bat init
goto run

:run
call venv\Scripts\activate
call python main.py

:end