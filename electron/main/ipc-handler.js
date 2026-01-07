const { ipcMain } = require('electron');
const fs = require('fs');
const path = require('path');

function setupIPC() {
  const settingsPath = path.join(__dirname, '../../config/settings.json');

  ipcMain.handle('get-settings', async () => {
    if (fs.existsSync(settingsPath)) {
      return JSON.parse(fs.readFileSync(settingsPath, 'utf-8'));
    }
    return {};
  });

  ipcMain.on('save-settings', (event, config) => {
    fs.writeFileSync(settingsPath, JSON.stringify(config, null, 2));
  });
}

module.exports = { setupIPC };