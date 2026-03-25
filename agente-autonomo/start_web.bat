@echo off
setlocal EnableDelayedExpansion

set PORT=8012
if not "%1"=="" set PORT=%1

echo [agente-autonomo] Iniciando servidor web na porta %PORT%...

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

REM Dependencias minimas (silencioso)
c:\python314\python.exe -m pip install -e . >NUL 2>NUL
c:\python314\python.exe -m pip install -e .[llms] >NUL 2>NUL
c:\python314\python.exe -m pip install fastapi uvicorn >NUL 2>NUL
c:\python314\python.exe -m pip install playwright >NUL 2>NUL
c:\python314\python.exe -m playwright install chromium >NUL 2>NUL

start "" "http://localhost:%PORT%/"

c:\python314\python.exe -m uvicorn web.server:app --host 127.0.0.1 --port %PORT%

endlocal
