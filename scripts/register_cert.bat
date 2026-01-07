@echo off
set "CERT_PATH=%USERPROFILE%\.mitmproxy\mitmproxy-ca-cert.cer"

if exist "%CERT_PATH%" (
    echo [AiPlugs] Found certificate. Registering to Root Store...
    certutil -user -addstore "Root" "%CERT_PATH%"
    echo [AiPlugs] Done.
) else (
    echo [AiPlugs] Certificate not found. Run the app once to generate it.
)
pause