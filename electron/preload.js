const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  openProxyBrowser: () => ipcRenderer.invoke('start-proxy')
});