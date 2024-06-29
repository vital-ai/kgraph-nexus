'use strict';

const _ = require('lodash');
const { BrowserWindow, BrowserView } = require('electron');
const windowStateKeeper = require('./windowState');

class WindowsManager {
  constructor(options = {}) {
    this.options = options;
    this.windows = {};
  }

  create(options) {
    const {
      name = 'anonymous',
      loadingView = {},
      browserWindow: browserWindowOptions = {},
      openDevTools = false,
      preventOriginClose = false,
      storageKey = undefined,
      storagePath = undefined,
    } = options;

    let stateFromStorage = {};
    if (storageKey) {
      const initWindowState = {
        defaultWidth: browserWindowOptions.width,
        defaultHeight: browserWindowOptions.height,
        file: storageKey + '.json',
      };
      if (storagePath) {
        initWindowState.path = storagePath;
      }
      stateFromStorage = windowStateKeeper(initWindowState);
      console.log('Window state loaded from storage:', stateFromStorage);

    }

    const window = new BrowserWindow(Object.assign({
      acceptFirstMouse: true,
    }, browserWindowOptions, _.pick(stateFromStorage, [
      'x',
      'y',
      'width',
      'height',
    ])));

    this._setGlobalUserAgent(window, options);
    window._name = name;

    if (loadingView.url) {
      this._setLoadingView(window, options);
    }

    window.on('close', (event) => {
      if (preventOriginClose) {
        event.preventDefault();
        return;
      }
      delete this.windows[window.id];
    });

    window.webContents.on('dom-ready', () => {

      console.log('DOM ready');

      if (openDevTools) {
        window.openDevTools();
      }
    });

    window.webContents.on('did-finish-load', () => {
      console.log('Window content loaded');
    });

    this.windows[window.id] = window;

    if (storageKey) {
      window.stateFromStorage = stateFromStorage;
      window.storageKey = storageKey;
      stateFromStorage.manage(window);
    }

    return window;
  }

  _setGlobalUserAgent(window, options) {
    const ua = options.globalUserAgent || WindowsManager.GLOBAL_USER_AGENT;
    if (!ua) return;

    const originalLoadURL = window.loadURL.bind(window);
    window.loadURL = (url, options = {}) => {
      options.userAgent = ua;
      originalLoadURL(url, options);
    };
  }

  _setLoadingView(window, options) {
    const loadingViewOptions = options.loadingView;
    const preventOriginNavigate = options.preventOriginNavigate || false;
    let loadingView = new BrowserView();

    const loadLoadingView = () => {
      console.log('loadLoadingView');
      const [viewWidth, viewHeight] = window.getSize();
      window.setBrowserView(loadingView);
      loadingView.setBounds({ x: 0, y: 0, width: viewWidth, height: viewHeight });
      loadingView.webContents.loadURL(loadingViewOptions.url);
    };

    const removeLoadingView = () => {
      if (!loadingView.webContents.isDestroyed()) {
        loadingView.webContents.destroy();
      }
      if (!window.isDestroyed()) {
        window.removeBrowserView(loadingView);
      }

      console.log('Loading view removed');

    };

    loadLoadingView();

    window.on('resize', _.debounce(() => {
      if (!loadingView.webContents.isDestroyed() && !window.isDestroyed()) {
        const [viewWidth, viewHeight] = window.getSize();
        loadingView.setBounds({ x: 0, y: 0, width: viewWidth, height: viewHeight });
      }
    }, 500));

    window.webContents.on('will-navigate', (event) => {
      if (preventOriginNavigate) {
        event.preventDefault();
        return;
      }
      if (!window.isDestroyed() && !loadingView.webContents.isDestroyed()) {
        window.setBrowserView(loadingView);
      } else {
        loadingView = new BrowserView();
        loadLoadingView();
      }

      console.log('Window will navigate');

    });




    window.webContents.on('dom-ready', removeLoadingView);
    window.webContents.on('crashed', removeLoadingView);
    window.webContents.on('unresponsive', removeLoadingView);
    window.webContents.on('did-fail-load', removeLoadingView);
  }

  get(name) {
    return Object.values(this.windows).find(window => window._name === name);
  }

  getById(id) {
    return this.windows[id];
  }

  getAll() {
    return Object.values(this.windows);
  }

  clone(window) {
    return window;
  }
}

WindowsManager.setGlobalUserAgent = (ua) => {
  WindowsManager.GLOBAL_USER_AGENT = ua;
};

module.exports = WindowsManager;