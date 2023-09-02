@echo on

:check
IF not EXIST "save_data" (
	goto init
)
IF not EXIST "__avellon_cache__" (
	goto init	
)
IF not EXIST "projects" (
	goto init
)
IF not EXIST "venv" (
	goto init
)
goto end


:init
python -m venv venv
call venv\Scripts\activate
call pip install -r requirements.txt
call deactivate
IF not EXIST "projects" (
	mkdir projects
)
IF not EXIST "save_data" (
	mkdir save_data
)
IF not EXIST "__avellon_cache__" (
	mkdir __avellon_cache__
)
IF not EXIST "projects/test_1" (
	mkdir projects\test_1
)

:end