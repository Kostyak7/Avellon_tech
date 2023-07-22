@echo on


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


:run
call venv\Scripts\activate
call python main.py

:end