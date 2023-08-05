"use strict";
(self["webpackChunkjupyterlab_skip_traceback"] = self["webpackChunkjupyterlab_skip_traceback"] || []).push([["lib_index_js"],{

/***/ "./lib/SkipTracebackWidget.js":
/*!************************************!*\
  !*** ./lib/SkipTracebackWidget.js ***!
  \************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ SkipTracebackWidget)
/* harmony export */ });
/* harmony import */ var _style_index_css__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../style/index.css */ "./style/index.css");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_rendermime__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/rendermime */ "webpack/sharing/consume/default/@jupyterlab/rendermime");
/* harmony import */ var _jupyterlab_rendermime__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_rendermime__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _jupyterlab_apputils_lib_clipboard__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @jupyterlab/apputils/lib/clipboard */ "./node_modules/@jupyterlab/apputils/lib/clipboard.js");




const BTN_BASE_CLASS = 'minimal jp-Button';
const COPY_CLASS = `fa fa-fw fa-copy ${BTN_BASE_CLASS} right-align`;
const TOGGLE_CLOSED_CLASS = `fa fa-caret-right jp-ToolbarButtonComponent ${BTN_BASE_CLASS}`;
const TOGGLE_OPENED_CLASS = `fa fa-caret-down jp-ToolbarButtonComponent ${BTN_BASE_CLASS}`;
const SHORT_ERROR_CLASS = 'short-error';
const RED_BOLD_TEXT_CLASS = 'red-bold-text';
class SkipTracebackWidget extends _lumino_widgets__WEBPACK_IMPORTED_MODULE_1__.Widget {
    constructor(options) {
        super();
        this._mimeType = options.mimeType;
        this._sanitizer = options.sanitizer;
    }
    static setDefaults(newDefaults) {
        SkipTracebackWidget._defaults = Object.assign(Object.assign({}, SkipTracebackWidget._defaults), newDefaults);
    }
    _toggleTraceback() {
        if (this._toggleBtn && this._tracebackNode) {
            const isToggled = this._toggleBtn.className === TOGGLE_CLOSED_CLASS;
            if (isToggled) {
                this._toggleBtn.className = TOGGLE_OPENED_CLASS;
                this._shortError.innerHTML = '';
                this.node.appendChild(this._tracebackNode);
            }
            else {
                this._toggleBtn.className = TOGGLE_CLOSED_CLASS;
                this._shortError.innerHTML = `<span class="${RED_BOLD_TEXT_CLASS}">${this._data.ename}</span>: ${this._data.evalue}`;
                this.node.removeChild(this._tracebackNode);
            }
        }
    }
    _copyTraceback() {
        if (this._tracebackNode) {
            _jupyterlab_apputils_lib_clipboard__WEBPACK_IMPORTED_MODULE_3__.Clipboard.copyToSystem(this._tracebackNode.textContent || '');
        }
    }
    renderModel(model) {
        this._data = model.data[this._mimeType];
        const toggleBtn = document.createElement('button');
        toggleBtn.className = TOGGLE_CLOSED_CLASS;
        toggleBtn.onclick = this._toggleTraceback.bind(this);
        this._toggleBtn = toggleBtn;
        const shortError = document.createElement('pre');
        shortError.className = SHORT_ERROR_CLASS;
        shortError.innerHTML = '';
        shortError.onclick = this._toggleTraceback.bind(this);
        this._shortError = shortError;
        const copyBtn = document.createElement('button');
        copyBtn.className = COPY_CLASS;
        copyBtn.onclick = this._copyTraceback.bind(this);
        copyBtn.title = 'Copy full traceback to clipboard';
        const span = document.createElement('div');
        span.className = 'skip-traceback';
        span.appendChild(copyBtn);
        span.appendChild(toggleBtn);
        span.appendChild(shortError);
        const traceback = document.createElement('pre');
        const rt = (0,_jupyterlab_rendermime__WEBPACK_IMPORTED_MODULE_2__.renderText)({
            host: traceback,
            sanitizer: this._sanitizer,
            // It should look like stderr
            source: model.data['application/vnd.jupyter.stderr'] ||
                this._data.traceback.join('\n'),
        });
        const tbDiv = document.createElement('div');
        tbDiv.className = 'jp-RenderedText';
        tbDiv.setAttribute('data-mime-type', 'application/vnd.jupyter.stderr');
        tbDiv.appendChild(traceback);
        // End hack due to issue
        this._tracebackNode = tbDiv;
        this.node.appendChild(span);
        if (!SkipTracebackWidget._defaults.collapsed) {
            this._toggleTraceback();
        }
        // Don't finish until we render the text
        return rt;
    }
}
SkipTracebackWidget._defaults = {
    collapsed: true,
};


/***/ }),

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__),
/* harmony export */   "rendererFactory": () => (/* binding */ rendererFactory)
/* harmony export */ });
/* harmony import */ var _jupyterlab_rendermime__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/rendermime */ "webpack/sharing/consume/default/@jupyterlab/rendermime");
/* harmony import */ var _jupyterlab_rendermime__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_rendermime__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _SkipTracebackWidget__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./SkipTracebackWidget */ "./lib/SkipTracebackWidget.js");
/* harmony import */ var _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/settingregistry */ "webpack/sharing/consume/default/@jupyterlab/settingregistry");
/* harmony import */ var _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_2__);



/**
 * The default mime type for the extension.
 */
const MIME_TYPE = 'application/vnd.jupyter.error';
const PLUGIN_NAME = 'jupyterlab-skip-traceback';
/**
 * A mime renderer factory for jupyter_exec_error data.
 */
const rendererFactory = {
    safe: true,
    mimeTypes: [MIME_TYPE],
    createRenderer: (options) => new _SkipTracebackWidget__WEBPACK_IMPORTED_MODULE_1__["default"](options),
};
/**
 * Extension definition.
 */
const extension = {
    id: 'jupyterlab-skip-traceback:rendermime',
    rendererFactory,
    rank: 0,
    dataType: 'json',
};
const extensionSettings = {
    id: `${PLUGIN_NAME}:plugin`,
    autoStart: true,
    requires: [_jupyterlab_rendermime__WEBPACK_IMPORTED_MODULE_0__.IRenderMimeRegistry, _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_2__.ISettingRegistry],
    activate: function (app, rendermime, settingRegistry) {
        function updateSettings(settings) {
            const enabled = settings.get('enabled').composite;
            if (enabled) {
                // Safe to do multiple times as the code replaces the current one
                rendermime.addFactory(extension.rendererFactory, extension.rank);
            }
            else {
                // We assume we were the only mime render ever installed and nothing removed us already
                extension.rendererFactory.mimeTypes.forEach((type) => rendermime.removeMimeType(type));
            }
            const collapsed = settings.get('collapsed').composite;
            _SkipTracebackWidget__WEBPACK_IMPORTED_MODULE_1__["default"].setDefaults({ collapsed });
        }
        settingRegistry.load(`${PLUGIN_NAME}:settings`).then((settings) => {
            updateSettings(settings);
            settings.changed.connect(updateSettings);
        }, (err) => {
            console.error(`Could not load settings, so did not active ${PLUGIN_NAME}: ${err}`);
        });
        // eslint-disable-next-line no-console
        console.log('JupyterLab extension jupyterlab-skip-traceback is activated!');
    },
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (extensionSettings);


/***/ }),

/***/ "./node_modules/@jupyterlab/apputils/lib/clipboard.js":
/*!************************************************************!*\
  !*** ./node_modules/@jupyterlab/apputils/lib/clipboard.js ***!
  \************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "Clipboard": () => (/* binding */ Clipboard)
/* harmony export */ });
/* harmony import */ var _lumino_coreutils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/coreutils */ "webpack/sharing/consume/default/@lumino/coreutils");
/* harmony import */ var _lumino_coreutils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_coreutils__WEBPACK_IMPORTED_MODULE_0__);
// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.

/**
 * The clipboard interface.
 */
var Clipboard;
(function (Clipboard) {
    /**
     * Get the application clipboard instance.
     */
    function getInstance() {
        return Private.instance;
    }
    Clipboard.getInstance = getInstance;
    /**
     * Set the application clipboard instance.
     */
    function setInstance(value) {
        Private.instance = value;
    }
    Clipboard.setInstance = setInstance;
    /**
     * Copy text to the system clipboard.
     *
     * #### Notes
     * This can only be called in response to a user input event.
     */
    function copyToSystem(clipboardData) {
        const node = document.body;
        const handler = (event) => {
            const data = event.clipboardData || window.clipboardData;
            if (typeof clipboardData === 'string') {
                data.setData('text', clipboardData);
            }
            else {
                clipboardData.types().map((mimeType) => {
                    data.setData(mimeType, clipboardData.getData(mimeType));
                });
            }
            event.preventDefault();
            node.removeEventListener('copy', handler);
        };
        node.addEventListener('copy', handler);
        generateEvent(node);
    }
    Clipboard.copyToSystem = copyToSystem;
    /**
     * Generate a clipboard event on a node.
     *
     * @param node - The element on which to generate the event.
     *
     * @param type - The type of event to generate.
     *   `'paste'` events cannot be programmatically generated.
     *
     * #### Notes
     * This can only be called in response to a user input event.
     */
    function generateEvent(node, type = 'copy') {
        // http://stackoverflow.com/a/5210367
        // Identify selected text.
        let sel = window.getSelection();
        // Save the current selection.
        const savedRanges = [];
        for (let i = 0, len = (sel === null || sel === void 0 ? void 0 : sel.rangeCount) || 0; i < len; ++i) {
            savedRanges[i] = sel.getRangeAt(i).cloneRange();
        }
        // Select the node content.
        const range = document.createRange();
        range.selectNodeContents(node);
        if (sel) {
            sel.removeAllRanges();
            sel.addRange(range);
        }
        // Execute the command.
        document.execCommand(type);
        // Restore the previous selection.
        sel = window.getSelection();
        if (sel) {
            sel.removeAllRanges();
            for (let i = 0, len = savedRanges.length; i < len; ++i) {
                sel.addRange(savedRanges[i]);
            }
        }
    }
    Clipboard.generateEvent = generateEvent;
})(Clipboard || (Clipboard = {}));
/**
 * The namespace for module private data.
 */
var Private;
(function (Private) {
    /**
     * The application clipboard instance.
     */
    Private.instance = new _lumino_coreutils__WEBPACK_IMPORTED_MODULE_0__.MimeData();
})(Private || (Private = {}));
//# sourceMappingURL=clipboard.js.map

/***/ }),

/***/ "./node_modules/css-loader/dist/cjs.js!./style/base.css":
/*!**************************************************************!*\
  !*** ./node_modules/css-loader/dist/cjs.js!./style/base.css ***!
  \**************************************************************/
/***/ ((module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _node_modules_css_loader_dist_runtime_cssWithMappingToString_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../node_modules/css-loader/dist/runtime/cssWithMappingToString.js */ "./node_modules/css-loader/dist/runtime/cssWithMappingToString.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_cssWithMappingToString_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_cssWithMappingToString_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../node_modules/css-loader/dist/runtime/api.js */ "./node_modules/css-loader/dist/runtime/api.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__);
// Imports


var ___CSS_LOADER_EXPORT___ = _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default()((_node_modules_css_loader_dist_runtime_cssWithMappingToString_js__WEBPACK_IMPORTED_MODULE_0___default()));
// Module
___CSS_LOADER_EXPORT___.push([module.id, ".skip-traceback {\n  background-color: var(--jp-rendermime-error-background);\n  font-family: var(--jp-code-font-family);\n  color: var(--jp-content-font-color1);\n}\n\n.skip-traceback > button {\n  background-color: transparent;\n  padding: 1px;\n  margin: 2px;\n  display: inline;\n  border: 0;\n}\n\n.skip-traceback > button:hover {\n  background-color: #ffb9b9;\n}\n\n.skip-traceback > button:active {\n  background-color: #ff9090;\n}\n\n.skip-traceback > .short-error {\n  display: inline;\n}\n\n.skip-traceback > .fa-copy {\n  border: dotted;\n  border-width: 1px;\n}\n\n.skip-traceback > .fa-caret-right, .skip-traceback > .fa-caret-down  {\n  /*To fix shifting of text to the right when toggled*/\n  width:17px;\n  height:17px;\n}\n\n.skip-traceback  > .right-align {\n  float: right;\n}\n\n.skip-traceback  .red-bold-text {\n  color: #b22b31;\n  font-weight: bold;\n}", "",{"version":3,"sources":["webpack://./style/base.css"],"names":[],"mappings":"AAAA;EACE,uDAAuD;EACvD,uCAAuC;EACvC,oCAAoC;AACtC;;AAEA;EACE,6BAA6B;EAC7B,YAAY;EACZ,WAAW;EACX,eAAe;EACf,SAAS;AACX;;AAEA;EACE,yBAAyB;AAC3B;;AAEA;EACE,yBAAyB;AAC3B;;AAEA;EACE,eAAe;AACjB;;AAEA;EACE,cAAc;EACd,iBAAiB;AACnB;;AAEA;EACE,oDAAoD;EACpD,UAAU;EACV,WAAW;AACb;;AAEA;EACE,YAAY;AACd;;AAEA;EACE,cAAc;EACd,iBAAiB;AACnB","sourcesContent":[".skip-traceback {\n  background-color: var(--jp-rendermime-error-background);\n  font-family: var(--jp-code-font-family);\n  color: var(--jp-content-font-color1);\n}\n\n.skip-traceback > button {\n  background-color: transparent;\n  padding: 1px;\n  margin: 2px;\n  display: inline;\n  border: 0;\n}\n\n.skip-traceback > button:hover {\n  background-color: #ffb9b9;\n}\n\n.skip-traceback > button:active {\n  background-color: #ff9090;\n}\n\n.skip-traceback > .short-error {\n  display: inline;\n}\n\n.skip-traceback > .fa-copy {\n  border: dotted;\n  border-width: 1px;\n}\n\n.skip-traceback > .fa-caret-right, .skip-traceback > .fa-caret-down  {\n  /*To fix shifting of text to the right when toggled*/\n  width:17px;\n  height:17px;\n}\n\n.skip-traceback  > .right-align {\n  float: right;\n}\n\n.skip-traceback  .red-bold-text {\n  color: #b22b31;\n  font-weight: bold;\n}"],"sourceRoot":""}]);
// Exports
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (___CSS_LOADER_EXPORT___);


/***/ }),

/***/ "./node_modules/css-loader/dist/cjs.js!./style/index.css":
/*!***************************************************************!*\
  !*** ./node_modules/css-loader/dist/cjs.js!./style/index.css ***!
  \***************************************************************/
/***/ ((module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _node_modules_css_loader_dist_runtime_cssWithMappingToString_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../node_modules/css-loader/dist/runtime/cssWithMappingToString.js */ "./node_modules/css-loader/dist/runtime/cssWithMappingToString.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_cssWithMappingToString_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_cssWithMappingToString_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../node_modules/css-loader/dist/runtime/api.js */ "./node_modules/css-loader/dist/runtime/api.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _node_modules_css_loader_dist_cjs_js_base_css__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! -!../node_modules/css-loader/dist/cjs.js!./base.css */ "./node_modules/css-loader/dist/cjs.js!./style/base.css");
// Imports



var ___CSS_LOADER_EXPORT___ = _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default()((_node_modules_css_loader_dist_runtime_cssWithMappingToString_js__WEBPACK_IMPORTED_MODULE_0___default()));
___CSS_LOADER_EXPORT___.i(_node_modules_css_loader_dist_cjs_js_base_css__WEBPACK_IMPORTED_MODULE_2__["default"]);
// Module
___CSS_LOADER_EXPORT___.push([module.id, "\n", "",{"version":3,"sources":[],"names":[],"mappings":"","sourceRoot":""}]);
// Exports
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (___CSS_LOADER_EXPORT___);


/***/ }),

/***/ "./style/index.css":
/*!*************************!*\
  !*** ./style/index.css ***!
  \*************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _node_modules_style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! !../node_modules/style-loader/dist/runtime/injectStylesIntoStyleTag.js */ "./node_modules/style-loader/dist/runtime/injectStylesIntoStyleTag.js");
/* harmony import */ var _node_modules_style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_node_modules_style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _node_modules_css_loader_dist_cjs_js_index_css__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! !!../node_modules/css-loader/dist/cjs.js!./index.css */ "./node_modules/css-loader/dist/cjs.js!./style/index.css");

            

var options = {};

options.insert = "head";
options.singleton = false;

var update = _node_modules_style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0___default()(_node_modules_css_loader_dist_cjs_js_index_css__WEBPACK_IMPORTED_MODULE_1__["default"], options);



/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (_node_modules_css_loader_dist_cjs_js_index_css__WEBPACK_IMPORTED_MODULE_1__["default"].locals || {});

/***/ })

}]);
//# sourceMappingURL=lib_index_js.aafb0b3c3b980e9cefc5.js.map