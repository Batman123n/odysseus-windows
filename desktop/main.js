const { app, BrowserWindow, Tray, Menu, Notification, dialog } = require("electron");
const { spawn } = require("child_process");
const path = require("path");
const fs = require("fs");

let win;
let tray;
let backendProcess;

function startBackend() {
  let rootDir = app.isPackaged 
    ? (process.env.PORTABLE_EXECUTABLE_DIR || path.dirname(app.getPath("exe")))
    : path.join(__dirname, "..");
  
  // Upward search: if venv/binary isn't here, look in parent folders (up to 3 levels).
  for (let i = 0; i < 3; i++) {
    if (fs.existsSync(path.join(rootDir, "venv")) || fs.existsSync(path.join(rootDir, "server.exe")) || fs.existsSync(path.join(rootDir, "build", "server.dist", "server.exe"))) break;
    const parent = path.dirname(rootDir);
    if (parent === rootDir) break; 
    rootDir = parent;
  }

  const binaryPath = path.join(rootDir, "server.exe");
  const buildBinaryPath = path.join(rootDir, "build", "server.dist", "server.exe");
  const venvPy = path.join(rootDir, "venv", "Scripts", "python.exe");
  
  let command;
  let args;

  if (fs.existsSync(binaryPath)) {
    console.log("Using compiled native binary...");
    command = binaryPath;
    args = [];
  } else if (fs.existsSync(buildBinaryPath)) {
    console.log("Using compiled native binary from build folder...");
    command = buildBinaryPath;
    args = [];
  } else if (fs.existsSync(venvPy)) {
    console.log("Using Python from venv...");
    command = venvPy;
    args = ["server.py"]; // Use our new server.py instead of -m uvicorn app:app
  } else {
    const errorMsg = `Odysseus backend not found.\n\nExpected: server.exe or ${venvPy}\n\nPlease place the Odysseus.exe in your project root.`;
    console.error(errorMsg);
    dialog.showErrorBox("Backend Initialization Error", errorMsg);
    return;
  }

  console.log(`Starting backend: ${command} ${args.join(" ")} in ${rootDir}...`);
  backendProcess = spawn(command, args, {
    cwd: rootDir,
    env: { ...process.env, PYTHONUTF8: "1" }
  });

  backendProcess.stdout.on("data", (data) => console.log(`[Backend] ${data}`));
  backendProcess.stderr.on("data", (data) => console.error(`[Backend ERR] ${data}`));

  backendProcess.on("close", (code) => {
    console.log(`Backend process exited with code ${code}`);
  });
}

function createWindow() {
  win = new BrowserWindow({
    width: 1400,
    height: 900,
    autoHideMenuBar: true,
    title: "Odysseus",
    backgroundColor: "#000000",
    show: false, // Show when ready
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true
    }
  });

  // Wait for backend to be ready (simple retry)
  const checkBackend = setInterval(() => {
    fetch("http://127.0.0.1:7000/api/health")
      .then(() => {
        win.loadURL("http://127.0.0.1:7000");
        win.show();
        clearInterval(checkBackend);
      })
      .catch(() => {
        console.log("Waiting for backend...");
      });
  }, 1000);

  // Close to tray
  win.on("close", (e) => {
    if (!app.isQuiting) {
      e.preventDefault();
      win.hide();
    }
    return false;
  });
}

function createTray() {
  // Match user preference: no custom icon
  tray = new Tray(null);

  const menu = Menu.buildFromTemplate([
    { label: "Show Odysseus", click: () => win.show() },
    { type: "separator" },
    { label: "Quit", click: () => {
        app.isQuiting = true;
        app.quit();
    }}
  ]);

  tray.setToolTip("Odysseus AI");
  tray.setContextMenu(menu);
  tray.on("double-click", () => win.show());
}

app.whenReady().then(() => {
  startBackend();
  createWindow();
  createTray();
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    // We stay running in tray
  }
});

app.on("quit", () => {
  if (backendProcess) {
    console.log("Shutting down backend...");
    // On Windows, we need to be aggressive with process tree killing
    // but for now simple kill might work if it's a direct child
    backendProcess.kill();
  }
});
