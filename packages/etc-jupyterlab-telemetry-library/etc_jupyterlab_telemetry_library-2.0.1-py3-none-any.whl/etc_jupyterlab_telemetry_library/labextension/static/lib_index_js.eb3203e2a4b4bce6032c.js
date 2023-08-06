"use strict";
(self["webpackChunk_educational_technology_collective_etc_jupyterlab_telemetry_library"] = self["webpackChunk_educational_technology_collective_etc_jupyterlab_telemetry_library"] || []).push([["lib_index_js"],{

/***/ "./lib/events.js":
/*!***********************!*\
  !*** ./lib/events.js ***!
  \***********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "NotebookSaveEvent": () => (/* binding */ NotebookSaveEvent),
/* harmony export */   "CellExecutionEvent": () => (/* binding */ CellExecutionEvent),
/* harmony export */   "NotebookScrollEvent": () => (/* binding */ NotebookScrollEvent),
/* harmony export */   "ActiveCellChangeEvent": () => (/* binding */ ActiveCellChangeEvent),
/* harmony export */   "NotebookOpenEvent": () => (/* binding */ NotebookOpenEvent),
/* harmony export */   "CellAddEvent": () => (/* binding */ CellAddEvent),
/* harmony export */   "CellRemoveEvent": () => (/* binding */ CellRemoveEvent),
/* harmony export */   "CellErrorEvent": () => (/* binding */ CellErrorEvent)
/* harmony export */ });
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/notebook */ "webpack/sharing/consume/default/@jupyterlab/notebook");
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @lumino/signaling */ "webpack/sharing/consume/default/@lumino/signaling");
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_lumino_signaling__WEBPACK_IMPORTED_MODULE_1__);


// export class NotebookCloseEvent {
//     private _notebookClosed: Signal<NotebookCloseEvent, any> = new Signal(this);
//     // private _notebookPanel: NotebookPanel;
//     // private _notebook: Notebook;
//     constructor({ notebookPanel, config }: INotebookEventOptions) {
//         // this._notebookPanel = notebookPanel;
//         // this._notebook = notebookPanel.content;
//         if (config['mentoracademy.org/schemas/events/1.0.0/NotebookCloseEvent']['enable']) {
//             (async () => {
//                 try {
//                     await notebookPanel.revealed;
//                     console.log(notebookPanel.id);
//                     let node = document.querySelector(`[data-id="${notebookPanel.id}"] .lm-TabBar-tabCloseIcon`);
//                     node?.addEventListener('click', () => {
//                         console.log(notebookPanel.content.widgets);
//                     })
//                 }
//                 catch (e) {
//                     console.error(e);
//                 }
//             })();
//         }
//     }
//     onDisposed() {
//         Signal.disconnectAll(this);
//     }
//     // private onNotebookDisposed(): void {
//     //     console.log('private onNotebookDisposed(): void {');
//     //     let cells = this._notebook.widgets.map((cell: Cell<ICellModel>, index: number) =>
//     //         ({ id: cell.model.id, index: index })
//     //     );
//     //     this._notebookClosed.emit({
//     //         event_name: "close_notebook",
//     //         cells: cells,
//     //         notebookPanel: this._notebookPanel
//     //     });
//     // }
//     get notebookClosed(): ISignal<NotebookCloseEvent, any> {
//         return this._notebookClosed
//     }
// }
class NotebookSaveEvent {
    constructor({ notebookPanel, config }) {
        this._notebookSaved = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal(this);
        this._notebookPanel = notebookPanel;
        notebookPanel.disposed.connect(this.onDisposed, this);
        if (config.notebook_save_event) {
            (async () => {
                try {
                    await notebookPanel.revealed;
                    notebookPanel.context.saveState.connect(this.onSaveState, this);
                }
                catch (e) {
                    console.error(e);
                }
            })();
        }
    }
    onDisposed() {
        _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal.disconnectAll(this);
    }
    onSaveState(context, saveState) {
        let cell;
        let cells;
        let index;
        if (saveState.match("completed")) {
            cells = [];
            for (index = 0; index < this._notebookPanel.content.widgets.length; index++) {
                cell = this._notebookPanel.content.widgets[index];
                if (this._notebookPanel.content.isSelectedOrActive(cell)) {
                    cells.push({ id: cell.model.id, index });
                }
            }
            this._notebookSaved.emit({
                event_name: "save_notebook",
                cells: cells,
                notebookPanel: this._notebookPanel
            });
        }
    }
    get notebookSaved() {
        return this._notebookSaved;
    }
}
class CellExecutionEvent {
    constructor({ notebookPanel, config }) {
        this._cellExecuted = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal(this);
        this._notebookPanel = notebookPanel;
        this._notebook = notebookPanel.content;
        notebookPanel.disposed.connect(this.onDisposed, this);
        if (config.notebook_cell_execution_event) {
            (async () => {
                try {
                    await notebookPanel.revealed;
                    _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__.NotebookActions.executed.connect(this.onExecuted, this);
                }
                catch (e) {
                    console.error(e);
                }
            })();
        }
    }
    onDisposed() {
        _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal.disconnectAll(this);
    }
    onExecuted(_, args) {
        if (args.notebook.model === this._notebook.model) {
            let cells = [
                {
                    id: args.cell.model.id,
                    index: this._notebook.widgets.findIndex((value) => value == args.cell)
                }
            ];
            this._cellExecuted.emit({
                event_name: "cell_executed",
                cells: cells,
                notebookPanel: this._notebookPanel
            });
        }
    }
    get cellExecuted() {
        return this._cellExecuted;
    }
}
class NotebookScrollEvent {
    constructor({ notebookPanel, config }) {
        this._notebookScrolled = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal(this);
        this._notebookPanel = notebookPanel;
        this._notebook = notebookPanel.content;
        this._timeout = 0;
        this.onScrolled = this.onScrolled.bind(this);
        notebookPanel.disposed.connect(this.onDisposed, this);
        if (config.notebook_scroll_event) {
            (async () => {
                try {
                    await notebookPanel.revealed;
                    notebookPanel.content.node.addEventListener("scroll", this.onScrolled, false);
                }
                catch (e) {
                    console.error(e);
                }
            })();
        }
    }
    onDisposed() {
        _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal.disconnectAll(this);
    }
    onScrolled(e) {
        e.stopPropagation();
        clearTimeout(this._timeout);
        this._timeout = setTimeout(() => {
            let cells = [];
            let cell;
            let index;
            let id;
            for (index = 0; index < this._notebook.widgets.length; index++) {
                cell = this._notebook.widgets[index];
                let cellTop = cell.node.offsetTop;
                let cellBottom = cell.node.offsetTop + cell.node.offsetHeight;
                let viewTop = this._notebook.node.scrollTop;
                let viewBottom = this._notebook.node.scrollTop + this._notebook.node.clientHeight;
                if (cellTop > viewBottom || cellBottom < viewTop) {
                    continue;
                }
                id = cell.model.id;
                cells.push({ id, index });
            }
            this._notebookScrolled.emit({
                event_name: "scroll",
                cells: cells,
                notebookPanel: this._notebookPanel
            });
        }, 1000);
    }
    get notebookScrolled() {
        return this._notebookScrolled;
    }
}
class ActiveCellChangeEvent {
    constructor({ notebookPanel, config }) {
        this._activeCellChanged = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal(this);
        this._notebookPanel = notebookPanel;
        this._notebook = notebookPanel.content;
        notebookPanel.disposed.connect(this.onDisposed, this);
        if (config.notebook_active_cell_change_event) {
            (async () => {
                try {
                    await notebookPanel.revealed;
                    notebookPanel.content.activeCellChanged.connect(this.onActiveCellChanged, this);
                }
                catch (e) {
                    console.error(e);
                }
            })();
        }
    }
    onDisposed() {
        _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal.disconnectAll(this);
    }
    onActiveCellChanged(send, args) {
        let cells = [
            {
                id: args.model.id,
                index: this._notebook.widgets.findIndex((value) => value == args)
            }
        ];
        this._activeCellChanged.emit({
            event_name: "active_cell_changed",
            cells: cells,
            notebookPanel: this._notebookPanel
        });
    }
    get activeCellChanged() {
        return this._activeCellChanged;
    }
}
class NotebookOpenEvent {
    constructor({ notebookPanel, config }) {
        this._notebookOpened = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal(this);
        this._once = false;
        this._notebookPanel = notebookPanel;
        this._notebook = notebookPanel.content;
        notebookPanel.disposed.connect(this.onDisposed, this);
        if (config.notebook_open_event) {
            if (!this._once) {
                (async () => {
                    try {
                        await notebookPanel.revealed;
                        this.onNotebookOpened();
                    }
                    catch (e) {
                        console.error(e);
                    }
                })();
            }
        }
    }
    onDisposed() {
        _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal.disconnectAll(this);
    }
    onNotebookOpened() {
        let cells = this._notebook.widgets.map((cell, index) => ({ id: cell.model.id, index: index }));
        this._notebookOpened.emit({
            event_name: "open_notebook",
            cells: cells,
            notebookPanel: this._notebookPanel
        });
        this._once = true;
    }
    get notebookOpened() {
        return this._notebookOpened;
    }
}
class CellAddEvent {
    constructor({ notebookPanel, config }) {
        this._cellAdded = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal(this);
        this._notebookPanel = notebookPanel;
        notebookPanel.disposed.connect(this.onDisposed, this);
        if (config.notebook_cell_add_event) {
            (async () => {
                var _a;
                try {
                    await notebookPanel.revealed;
                    (_a = notebookPanel.content.model) === null || _a === void 0 ? void 0 : _a.cells.changed.connect(this.onCellsChanged, this);
                }
                catch (e) {
                    console.error(e);
                }
            })();
        }
    }
    onDisposed() {
        _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal.disconnectAll(this);
    }
    onCellsChanged(sender, args) {
        if (args.type == "add") {
            let cells = [{ id: args.newValues[0].id, index: args.newIndex }];
            this._cellAdded.emit({
                event_name: "add_cell",
                cells: cells,
                notebookPanel: this._notebookPanel
            });
        }
    }
    get cellAdded() {
        return this._cellAdded;
    }
}
class CellRemoveEvent {
    constructor({ notebookPanel, config }) {
        this._cellRemoved = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal(this);
        this._notebookPanel = notebookPanel;
        notebookPanel.disposed.connect(this.onDisposed, this);
        if (config.notebook_cell_remove_event) {
            (async () => {
                var _a;
                try {
                    await notebookPanel.revealed;
                    (_a = notebookPanel.content.model) === null || _a === void 0 ? void 0 : _a.cells.changed.connect(this.onCellsChanged, this);
                }
                catch (e) {
                    console.error(e);
                }
            })();
        }
    }
    onDisposed() {
        _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal.disconnectAll(this);
    }
    onCellsChanged(sender, args) {
        if (args.type == "remove") {
            let cells = [{ id: args.oldValues[0].id, index: args.oldIndex }];
            this._cellRemoved.emit({
                event_name: "remove_cell",
                cells: cells,
                notebookPanel: this._notebookPanel
            });
        }
    }
    get cellRemoved() {
        return this._cellRemoved;
    }
}
class CellErrorEvent {
    constructor({ notebookPanel, config }) {
        this._cellErrored = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal(this);
        this._notebookPanel = notebookPanel;
        notebookPanel.disposed.connect(this.onDisposed, this);
        if (config.notebook_cell_error_event) {
            (async () => {
                try {
                    await notebookPanel.revealed;
                    notebookPanel.sessionContext.iopubMessage.connect(this.onCellErrored, this);
                }
                catch (e) {
                    console.error(e);
                }
            })();
        }
    }
    onDisposed() {
        _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal.disconnectAll(this);
    }
    onCellErrored(_, args) {
        var _a;
        if (args.header.msg_type == "error") {
            let cells = [
                {
                    id: (_a = this._notebookPanel.content.activeCell) === null || _a === void 0 ? void 0 : _a.model.id,
                    index: this._notebookPanel.content.activeCellIndex
                }
            ];
            this._cellErrored.emit({
                event_name: "cell_errored",
                cells: cells,
                notebookPanel: this._notebookPanel
            });
        }
    }
    get cellErrored() {
        return this._cellErrored;
    }
}


/***/ }),

/***/ "./lib/handler.js":
/*!************************!*\
  !*** ./lib/handler.js ***!
  \************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "requestAPI": () => (/* binding */ requestAPI)
/* harmony export */ });
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/coreutils */ "webpack/sharing/consume/default/@jupyterlab/coreutils");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/services */ "webpack/sharing/consume/default/@jupyterlab/services");
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__);


/**
 * Call the API extension
 *
 * @param endPoint API REST end point for the extension
 * @param init Initial values for the request
 * @returns The response body interpreted as JSON
 */
async function requestAPI(endPoint = '', init = {}) {
    // Make request to Jupyter API
    const settings = _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeSettings();
    const requestUrl = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.URLExt.join(settings.baseUrl, 'etc-jupyterlab-telemetry-library', // API Namespace
    endPoint);
    let response;
    try {
        response = await _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeRequest(requestUrl, init, settings);
    }
    catch (error) {
        throw new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.NetworkError(error);
    }
    let data = await response.text();
    if (data.length > 0) {
        try {
            data = JSON.parse(data);
        }
        catch (error) {
            console.log('Not a JSON response body.', response);
        }
    }
    if (!response.ok) {
        throw new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.ResponseError(response, data.message || data);
    }
    return data;
}


/***/ }),

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "IETCJupyterLabTelemetryLibraryFactory": () => (/* binding */ IETCJupyterLabTelemetryLibraryFactory),
/* harmony export */   "ETCJupyterLabTelemetryLibrary": () => (/* binding */ ETCJupyterLabTelemetryLibrary),
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/notebook */ "webpack/sharing/consume/default/@jupyterlab/notebook");
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _lumino_coreutils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @lumino/coreutils */ "webpack/sharing/consume/default/@lumino/coreutils");
/* harmony import */ var _lumino_coreutils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_lumino_coreutils__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _educational_technology_collective_etc_jupyterlab_notebook_state_provider__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @educational-technology-collective/etc_jupyterlab_notebook_state_provider */ "webpack/sharing/consume/default/@educational-technology-collective/etc_jupyterlab_notebook_state_provider");
/* harmony import */ var _educational_technology_collective_etc_jupyterlab_notebook_state_provider__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_educational_technology_collective_etc_jupyterlab_notebook_state_provider__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _events__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./events */ "./lib/events.js");
/* harmony import */ var _handler__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./handler */ "./lib/handler.js");





const PLUGIN_ID = '@educational-technology-collective/etc_jupyterlab_telemetry_library:plugin';
const IETCJupyterLabTelemetryLibraryFactory = new _lumino_coreutils__WEBPACK_IMPORTED_MODULE_1__.Token(PLUGIN_ID);
class ETCJupyterLabTelemetryLibraryFactory {
    constructor({ config }) {
        this._config = config;
    }
    create({ notebookPanel }) {
        return new ETCJupyterLabTelemetryLibrary({ notebookPanel, config: this._config });
    }
}
class ETCJupyterLabTelemetryLibrary {
    constructor({ notebookPanel, config }) {
        this.notebookOpenEvent = new _events__WEBPACK_IMPORTED_MODULE_3__.NotebookOpenEvent({
            notebookPanel: notebookPanel,
            config: config
        });
        this.notebookSaveEvent = new _events__WEBPACK_IMPORTED_MODULE_3__.NotebookSaveEvent({
            notebookPanel: notebookPanel,
            config: config
        });
        this.cellExecutionEvent = new _events__WEBPACK_IMPORTED_MODULE_3__.CellExecutionEvent({
            notebookPanel: notebookPanel,
            config: config
        });
        this.cellErrorEvent = new _events__WEBPACK_IMPORTED_MODULE_3__.CellErrorEvent({
            notebookPanel: notebookPanel,
            config: config
        });
        this.notebookScrollEvent = new _events__WEBPACK_IMPORTED_MODULE_3__.NotebookScrollEvent({
            notebookPanel: notebookPanel,
            config: config
        });
        this.activeCellChangeEvent = new _events__WEBPACK_IMPORTED_MODULE_3__.ActiveCellChangeEvent({
            notebookPanel: notebookPanel,
            config: config
        });
        this.cellAddEvent = new _events__WEBPACK_IMPORTED_MODULE_3__.CellAddEvent({
            notebookPanel: notebookPanel,
            config: config
        });
        this.cellRemoveEvent = new _events__WEBPACK_IMPORTED_MODULE_3__.CellRemoveEvent({
            notebookPanel: notebookPanel,
            config: config
        });
    }
}
/**
 * Initialization data for the @educational-technology-collective/etc_jupyterlab_telemetry_extension extension.
 */
const plugin = {
    id: PLUGIN_ID,
    autoStart: true,
    provides: IETCJupyterLabTelemetryLibraryFactory,
    requires: [_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__.INotebookTracker],
    optional: [_educational_technology_collective_etc_jupyterlab_notebook_state_provider__WEBPACK_IMPORTED_MODULE_2__.IETCJupyterLabNotebookStateProvider],
    activate: async (app, notebookTracker, etcJupyterLabNotebookStateProvider) => {
        const VERSION = await (0,_handler__WEBPACK_IMPORTED_MODULE_4__.requestAPI)("version");
        console.log(`${PLUGIN_ID}, ${VERSION}`);
        const CONFIG = await (0,_handler__WEBPACK_IMPORTED_MODULE_4__.requestAPI)("config");
        let etcJupyterLabTelemetryLibraryFactory = new ETCJupyterLabTelemetryLibraryFactory({ config: CONFIG });
        // // TEST
        // class MessageAdapter {
        //   constructor() { }
        //   log(sender: any, args: any) {
        //     let notebookPanel = args.notebookPanel;
        //     delete args.notebookPanel;
        //     let notebookState = etcJupyterLabNotebookStateProvider.getNotebookState({ notebookPanel: notebookPanel })
        //     let data = {
        //       ...args, ...notebookState
        //     }
        //     console.log("etc_jupyterlab_telemetry_extension", data);
        //   }
        // }
        // let messageAdapter = new MessageAdapter();
        // notebookTracker.widgetAdded.connect(async (sender: INotebookTracker, notebookPanel: NotebookPanel) => {
        //   etcJupyterLabNotebookStateProvider.addNotebookPanel({ notebookPanel });
        //   let etcJupyterLabTelemetryLibrary = etcJupyterLabTelemetryLibraryFactory.create({ notebookPanel });
        //   etcJupyterLabTelemetryLibrary.notebookOpenEvent.notebookOpened.connect(messageAdapter.log);
        //   etcJupyterLabTelemetryLibrary.notebookSaveEvent.notebookSaved.connect(messageAdapter.log);
        //   etcJupyterLabTelemetryLibrary.activeCellChangeEvent.activeCellChanged.connect(messageAdapter.log);
        //   etcJupyterLabTelemetryLibrary.cellAddEvent.cellAdded.connect(messageAdapter.log);
        //   etcJupyterLabTelemetryLibrary.cellRemoveEvent.cellRemoved.connect(messageAdapter.log);
        //   etcJupyterLabTelemetryLibrary.notebookScrollEvent.notebookScrolled.connect(messageAdapter.log);
        //   etcJupyterLabTelemetryLibrary.cellExecutionEvent.cellExecuted.connect(messageAdapter.log);
        //   etcJupyterLabTelemetryLibrary.cellErrorEvent.cellErrored.connect(messageAdapter.log);
        // });
        // // TEST
        return etcJupyterLabTelemetryLibraryFactory;
    }
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ })

}]);
//# sourceMappingURL=lib_index_js.eb3203e2a4b4bce6032c.js.map