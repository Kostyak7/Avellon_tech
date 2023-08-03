@echo on

IF not EXIST "save_data" (
	goto init
)
IF not EXIST "__avellon_cash__" (
	goto init	
)
IF not EXIST "projects" (
	goto init
)


IF not "%1"=="" (
	goto %~1 
) ELSE (
	goto run
)


:init
python -m venv venv
call venv\Scripts\activate
call pip install --upgrade pip
call pip install -r requirements.txt
call deactivate
IF not EXIST "projects" (
	mkdir projects
)
IF not EXIST "save_data" (
	mkdir save_data
)
IF not EXIST "__avellon_cash__" (
	mkdir __avellon_cash__
)

:run
call venv\Scripts\activate
call python main.py

:end