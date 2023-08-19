@echo on

IF "%1"=="init" (
	goto %~1 
) ELSE (
	call init.bat check
	goto run
)

:init
call init.bat init

:run
call venv\Scripts\activate
call python converter.py

:end