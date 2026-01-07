@echo off
echo [AiPlugs] Installing Node.js dependencies...
call npm install

echo [AiPlugs] Installing Python dependencies...
pip install -r python/requirements.txt

echo [AiPlugs] Installation Complete.
pause