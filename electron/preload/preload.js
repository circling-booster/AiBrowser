const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  onStatusUpdate: (callback) => ipcRenderer.on('status-update', (_event, value) => callback(value)),
  onLogEntry: (callback) => ipcRenderer.on('log-entry', (_event, value) => callback(value)),
  getSettings: () => ipcRenderer.invoke('get-settings'),
  saveSettings: (config) => ipcRenderer.send('save-settings', config)
});