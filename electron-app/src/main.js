const { app, Menu, BrowserWindow } = require('electron');
const WindowManager = require('./windowsManager');
const path = require('path');
const { spawn, exec } = require('child_process');

app.setName('KGraph Nexus');

let apiProcess = null;

function startApiProcess() {

    if (apiProcess != null) {
        console.log('apiProcess is already running.');
        return;
    }

    // pythonAppPath = '/Users/hadfield/Local/vital-git/kgraph-nexus/electron-app/python-app/dist/app/app'

    let pythonAppPath;

    if (app.isPackaged) {
    // In production, the path is inside the application bundle
        // pythonAppPath = path.join(app.getAppPath(), 'Resources', 'app', 'python-app');
        pythonAppPath = path.join(process.resourcesPath, 'python-app');
    } else {
    // In development, the path is relative to the project directory
        pythonAppPath = path.join(__dirname, '..', 'python-app', 'dist', 'app');
    }

    console.log(`pythonAppPath: ${pythonAppPath}`);

    apiProcess = spawn(pythonAppPath + "/app", {
        // cwd: '../python-app',
        // cwd: path.join(__dirname, './python-app/dist/app'),
        // shell: true,
        // env: { ...process.env }
    });

    apiProcess.stdout.on('data', (data) => {
        console.log(`stdout: ${data}`);
    });

    apiProcess.stderr.on('data', (data) => {
        console.error(`stderr: ${data}`);
    });

    apiProcess.on('close', (code) => {
        console.log(`child process exited with code ${code}`);
        apiProcess = null;
    });
}

function stopApiProcess() {
    if (apiProcess) {
        apiProcess.kill();
        apiProcess = null;
    }
}

function restartApiProcess() {
    stopApiProcess();
    startApiProcess();
}

global.sharedObject = { startApiProcess, stopApiProcess, restartApiProcess };


const windowManager = new WindowManager();
let windowCount = 0;

function createWindow() {

    windowCount += 1;

    const windowName = `Window ${windowCount}`;

    console.log(`Creating ${windowName}...`);

    const winRef = windowManager.create({
        name: windowName,

        loadingView: {
            url: '',
        },

        browserWindow: {
            width: 1200,
            height: 800,
            show: false, // Initially hidden
            webPreferences: {
                // nodeIntegration: true,
            },
        },
    });

    pythonAppURL = 'http://127.0.0.1:9000/'

    // winRef.loadURL(`file://${path.join(__dirname, 'index.html')}`);

    winRef.loadURL(pythonAppURL);


    winRef.webContents.on('did-finish-load', () => {
        console.log('Content has finished loading');
        winRef.show();
    });

    winRef.once('ready-to-show', () => {
        console.log('Window is ready to show');
        winRef.show();
        updateWindowMenu();
    });


    winRef.on('show', () => {
        console.log('Window is shown');
    });

    winRef.on('closed', () => {
        console.log('Window is closed');
        updateWindowMenu();
    });

    return winRef;
}

function updateWindowMenu() {
  const windows = windowManager.getAll();
  const windowMenuItems = Object.values(windows).map((win) => ({
    label: win._name,
    click: () => {
      if (win.isMinimized()) win.restore();
      win.focus();
    },
  }));

  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'New Window',
          accelerator: 'CmdOrCtrl+N',
          click: () => {
            console.log('New Window menu item clicked');
            createWindow();
          },
        },
        { role: 'quit' },
      ],
    },
    {
      label: 'Window',
      submenu: windowMenuItems,
    },
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}



function createMenu() {
    const template = [
        {
            label: 'File',
            submenu: [
                {
                    label: 'New Window',
                    accelerator: 'CmdOrCtrl+N',
                    click: () => {
                        createWindow();
                    }
                },
                { role: 'quit' },
                {
                    label: 'Window',
                    submenu: []
                },
            ]
        }
    ];

    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);
}


function waitForServerToBeReady(url, retries) {
    return new Promise((resolve, reject) => {
        function attemptFetch(remainingRetries) {
            fetch(url)
                .then(res => {
                    if (res.ok) resolve();
                    else throw new Error(`Server responded with status: ${res.status}`);
                })
                .catch(error => {
                    if (remainingRetries > 0) {
                        setTimeout(() => attemptFetch(remainingRetries - 1), 1000); // wait 1 second and retry
                    } else {
                        reject(error);
                    }
                });
        }
        attemptFetch(retries);
    });
}

app.on('ready', () => {

    startApiProcess();

    setTimeout(() => {

         waitForServerToBeReady('http://127.0.0.1:9000', 10)
        .then(() => {
            createWindow();
            createMenu();
        })
        .catch(err => {
            console.error('Server did not become ready', err);
        });

    }, 1000); // Delay in milliseconds
});


app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    console.log('App is activated');
    if (windowManager.windows.size === 0) {
        createWindow();
    }
});


app.on('before-quit', (event) => {
    if (apiProcess) {
        apiProcess.kill('SIGTERM'); // Sends SIGTERM to the child process
    }
});

// Optionally, ensure cleanup is complete before app completely exits
app.on('will-quit', (event) => {
    if (apiProcess) {
        apiProcess.kill('SIGKILL'); // Force kills the child process
    }
});
