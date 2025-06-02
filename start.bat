@echo off

echo [1] start uvicorn server...
start "uvicorn" cmd /k "uvicorn app.main:app --host 0.0.0.0 --port 8080"

echo [2] wait for uvicorn to start...
timeout /t 5 /nobreak >nul

echo [3] check ngrok auth...
ngrok authtoken >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Authorizing ngrok...
    for /f "tokens=2 delims==" %%A in ('findstr NGROK_AUTH_TOKEN .env') do set NGROK_AUTH_TOKEN=%%A
    set NGROK_AUTH_TOKEN=%NGROK_AUTH_TOKEN: =%
    ngrok config add-authtoken %NGROK_AUTH_TOKEN%
) else (
    echo ngrok already authorized.
)

echo [4] start ngrok tunnel for port 8080...
start "ngrok" cmd /k "ngrok http 8080"

echo Uvicorn + Ngrok started. Please wait for a few minutes for webhook link :)
pause
