const { app, BrowserWindow, ipcMain, Menu, Tray, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const isDev = require('electron-is-dev');
const fs = require('fs');
const axios = require('axios');

// Giữ tham chiếu đến cửa sổ để tránh bị thu gom rác
let mainWindow;
let pythonProcess;
let tray = null;
let isQuitting = false;

const findPythonPath = () => {
  if (isDev) {
    // Trong môi trường phát triển
    return {
      pythonPath: 'python',
      scriptPath: path.join(__dirname, '..', 'run.py')
    };
  } else {
    // Trong môi trường production (đã đóng gói)
    const resourcesPath = process.resourcesPath;
    
    // Đường dẫn đến python.exe trong thư mục resources/python
    // Thay đổi đường dẫn từ 'app/python/python.exe' thành 'python/python.exe'
    return {
      pythonPath: path.join(resourcesPath, 'python', 'python.exe'),
      scriptPath: path.join(resourcesPath, 'app', 'run.py')
    };
  }
};

// Khởi chạy tiến trình Python
const startPythonProcess = () => {
  const { pythonPath, scriptPath } = findPythonPath();
  
  console.log(`Khởi động Python: ${pythonPath} ${scriptPath}`);
  
  // Tạo thư mục Python trong resources nếu cần
  if (!isDev) {
    const pythonDir = path.join(process.resourcesPath, 'app', 'python');
    if (!fs.existsSync(pythonDir)) {
      fs.mkdirSync(pythonDir, { recursive: true });
    }
  }

  // Đặt biến môi trường để Python biết đang chạy từ Electron
  const env = Object.assign({}, process.env, {
    ELECTRON_RUN: '1',
    PYTHONIOENCODING: 'utf-8'  // Đảm bảo Python sử dụng UTF-8 cho I/O
  });

  // Spawn quy trình Python
  pythonProcess = spawn(pythonPath, [scriptPath], {
    stdio: ['ignore', 'pipe', 'pipe'],
    detached: false,
    env: env
  });

  // Xử lý dữ liệu đầu ra từ Python với encoding UTF-8
  pythonProcess.stdout.setEncoding('utf-8');
  pythonProcess.stderr.setEncoding('utf-8');

  pythonProcess.stdout.on('data', (data) => {
    console.log(`Python stdout: ${data}`);
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`Python stderr: ${data}`);
  });

  pythonProcess.on('error', (error) => {
    console.error(`Không thể khởi động tiến trình Python: ${error}`);
    dialog.showErrorBox('Lỗi', `Không thể khởi động JARVIS: ${error.message}`);
  });

  pythonProcess.on('close', (code) => {
    console.log(`Tiến trình Python thoát với mã: ${code}`);
    if (code !== 0 && !isQuitting) {
      dialog.showErrorBox('Lỗi', `JARVIS đã thoát bất ngờ với mã lỗi: ${code}`);
    }
  });

  // Đợi khoảng 2 giây cho Python khởi động
  return new Promise((resolve) => {
    setTimeout(resolve, 2000);
  });
};

// Tạo cửa sổ chính
const createWindow = async () => {
  // Tạo cửa sổ
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    show: false, // Không hiển thị cho đến khi sẵn sàng
    icon: path.join(__dirname, 'build', 'icons', 'icon.ico')
  });

  // Xử lý thoát
  mainWindow.on('close', (event) => {
    if (!isQuitting) {
      event.preventDefault();
      mainWindow.hide();
      return false;
    }
  });

  // Tải URL
  if (isDev) {
    // Trong môi trường phát triển, tải từ server của Eel
    mainWindow.loadURL('http://localhost:8000/index.html');
    
    // Mở DevTools trong môi trường phát triển
    mainWindow.webContents.openDevTools({ mode: 'detach' });
  } else {
    // Trong môi trường đóng gói, tải từ server của Eel
    // Chúng ta vẫn sử dụng URL vì Eel đã khởi động server
    mainWindow.loadURL('http://localhost:8000/index.html');
  }

  // Hiển thị cửa sổ khi đã sẵn sàng
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // Tạo tray icon
  const trayIcon = path.join(__dirname, 'build', 'icons', 'tray.ico');
  tray = new Tray(trayIcon);
  const contextMenu = Menu.buildFromTemplate([
    { 
      label: 'Mở JARVIS', 
      click: () => mainWindow.show() 
    },
    { 
      label: 'Thoát', 
      click: () => {
        isQuitting = true;
        app.quit();
      } 
    }
  ]);
  
  tray.setToolTip('JARVIS AI Assistant');
  tray.setContextMenu(contextMenu);
  
  tray.on('click', () => {
    mainWindow.isVisible() ? mainWindow.hide() : mainWindow.show();
  });
};

// Kiểm tra kết nối đến server Python
const checkPythonServer = async () => {
  try {
    await axios.get('http://localhost:8000/is_alive');
    return true;
  } catch (error) {
    return false;
  }
};

// Khởi tạo ứng dụng
app.whenReady().then(async () => {
  // Khởi động tiến trình Python
  try {
    await startPythonProcess();
    
    // Kiểm tra xem Python server đã sẵn sàng chưa
    let serverReady = false;
    let retries = 0;
    
    while (!serverReady && retries < 10) {
      try {
        serverReady = await checkPythonServer();
        if (serverReady) break;
      } catch (error) {
        console.log('Đang đợi server Python sẵn sàng...');
      }
      
      await new Promise(resolve => setTimeout(resolve, 1000));
      retries++;
    }
    
    if (!serverReady) {
      console.warn('Không thể kết nối đến server Python sau nhiều lần thử. Tiếp tục khởi động ứng dụng...');
    }
    
    // Tạo cửa sổ
    createWindow();
  } catch (error) {
    console.error('Lỗi khi khởi động:', error);
    dialog.showErrorBox('Lỗi khởi động', `Không thể khởi động JARVIS: ${error.message}`);
    app.quit();
  }
});

// Thêm xử lý cho IPC từ renderer
ipcMain.on('minimize-window', () => {
  if (mainWindow) mainWindow.minimize();
});

ipcMain.on('maximize-window', () => {
  if (mainWindow) {
    if (mainWindow.isMaximized()) {
      mainWindow.unmaximize();
    } else {
      mainWindow.maximize();
    }
  }
});

ipcMain.on('close-window', () => {
  if (mainWindow) mainWindow.hide();
});

// Xử lý đóng toàn bộ ứng dụng trên macOS
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Xử lý kích hoạt lại ứng dụng trên macOS
app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  } else {
    mainWindow.show();
  }
});

// Xử lý khi thoát ứng dụng
app.on('before-quit', () => {
  isQuitting = true;
  
  // Thêm lệnh xóa thư mục face_data
  try {
    const facePath = path.join(process.env.LOCALAPPDATA, 'AI-Assistant', 'face_data');
    if (fs.existsSync(facePath)) {
      console.log('Xóa thư mục face_data trước khi thoát');
      // Thực thi batch script để xóa thư mục face_data
      if (process.platform === 'win32') {
        const batchPath = path.join(process.resourcesPath, 'app', 'electron', 'build', 'cleanup.bat');
        if (fs.existsSync(batchPath)) {
          console.log('Thực thi cleanup script:', batchPath);
          spawn('cmd', ['/c', batchPath], { detached: true });
        }
      }
    }
  } catch (error) {
    console.error('Lỗi khi xóa thư mục face_data:', error);
  }
  
  // Đóng tiến trình Python khi thoát ứng dụng
  if (pythonProcess) {
    // Thử kết thúc tiến trình một cách nhẹ nhàng
    if (process.platform === 'win32') {
      spawn('taskkill', ['/pid', pythonProcess.pid, '/f', '/t']);
    } else {
      pythonProcess.kill('SIGTERM');
    }
  }
});
