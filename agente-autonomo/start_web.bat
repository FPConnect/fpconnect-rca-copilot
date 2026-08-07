@echo off
setlocal EnableDelayedExpansion

set PORT=8012
if not "%1"=="" set PORT=%1
set LISTEN_HOST=127.0.0.1

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Carrega variaveis de .env (se existir)
if exist ".env" (
	for /f "usebackq tokens=* delims=" %%L in (".env") do (
		set "LINE=%%L"
		if not "!LINE!"=="" (
			if not "!LINE:~0,1!"=="#" (
				for /f "tokens=1,* delims==" %%A in ("!LINE!") do (
					set "%%A=%%B"
				)
			)
		)
	)
	if "%1"=="" if not "%PORT%"=="" set PORT=%PORT%
)

if not "%AGENTE_AUTONOMO_HOST%"=="" set "LISTEN_HOST=%AGENTE_AUTONOMO_HOST%"

echo [agente-autonomo] Iniciando servidor web em %LISTEN_HOST%:%PORT%...

REM Dependencias minimas (silencioso)
set "PYTHON_EXE=%AGENTE_AUTONOMO_PYTHON%"
if "%PYTHON_EXE%"=="" set "PYTHON_EXE=python"
if "%AGENTE_AUTONOMO_DISABLE_EMBEDDED_BROWSER%"=="" set "AGENTE_AUTONOMO_DISABLE_EMBEDDED_BROWSER=0"

"%PYTHON_EXE%" -c "import agent_core" >NUL 2>NUL
if errorlevel 1 "%PYTHON_EXE%" -m pip install --no-build-isolation -e . >NUL 2>NUL

"%PYTHON_EXE%" -c "import anthropic, google.generativeai" >NUL 2>NUL
if errorlevel 1 "%PYTHON_EXE%" -m pip install --no-build-isolation -e .[llms] >NUL 2>NUL

"%PYTHON_EXE%" -c "import fastapi, uvicorn" >NUL 2>NUL
if errorlevel 1 "%PYTHON_EXE%" -m pip install fastapi uvicorn >NUL 2>NUL

"%PYTHON_EXE%" -c "import playwright" >NUL 2>NUL
if errorlevel 1 "%PYTHON_EXE%" -m pip install playwright >NUL 2>NUL

if not exist "%LOCALAPPDATA%\ms-playwright" "%PYTHON_EXE%" -m playwright install chromium >NUL 2>NUL

start "" "http://localhost:%PORT%/"

"%PYTHON_EXE%" -m uvicorn web.server:app --host %LISTEN_HOST% --port %PORT%

endlocal
