const { contextBridge, ipcRenderer } = require('electron');

// Expose APIs to renderer process
contextBridge.exposeInMainWorld('electronAPI', {
  // Có thể thêm các hàm giao tiếp tại đây
  minimizeWindow: () => ipcRenderer.send('minimize-window'),
  maximizeWindow: () => ipcRenderer.send('maximize-window'),
  closeWindow: () => ipcRenderer.send('close-window'),
  
  // Thêm các API khác nếu cần
  logMessage: (message) => {
    console.log(`From renderer: ${message}`);
  }
});

// Có thể thêm các hàm xử lý khác ở đây nếu cần
window.addEventListener('DOMContentLoaded', () => {
  console.log('DOM đã sẵn sàng trong quá trình renderer');
});
