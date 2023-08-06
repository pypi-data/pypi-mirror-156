"use strict";
(self["webpackChunk_educational_technology_collective_etc_jupyterlab_notebook_state_provider"] = self["webpackChunk_educational_technology_collective_etc_jupyterlab_notebook_state_provider"] || []).push([["lib_index_js"],{

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
    const requestUrl = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.URLExt.join(settings.baseUrl, 'etc-jupyterlab-notebook-state-provider', // API Namespace
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
/* harmony export */   "ETCJupyterLabNotebookState": () => (/* binding */ ETCJupyterLabNotebookState),
/* harmony export */   "ETCJupyterLabNotebookStateProvider": () => (/* binding */ ETCJupyterLabNotebookStateProvider),
/* harmony export */   "IETCJupyterLabNotebookStateProvider": () => (/* binding */ IETCJupyterLabNotebookStateProvider),
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _handler__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./handler */ "./lib/handler.js");
/* harmony import */ var _lumino_coreutils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/coreutils */ "webpack/sharing/consume/default/@lumino/coreutils");
/* harmony import */ var _lumino_coreutils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_coreutils__WEBPACK_IMPORTED_MODULE_0__);



class ETCJupyterLabNotebookState {
    constructor({ notebookPanel }) {
        var _a;
        this._notebook = notebookPanel.content;
        this._cellState = new WeakMap();
        this._seq = 0;
        this._session_id = _lumino_coreutils__WEBPACK_IMPORTED_MODULE_0__.UUID.uuid4();
        this.updateCellState();
        //  The notebook loaded; hence, update the cell state.
        (_a = this._notebook.model) === null || _a === void 0 ? void 0 : _a.cells.changed.connect((sender, args) => {
            if (args.type == "add" || args.type == "set") {
                this.updateCellState();
                //  A cell was added; hence, update the cell state.
            }
        }, this);
    }
    updateCellState() {
        this._notebook.widgets.forEach((cell) => {
            if (!this._cellState.has(cell)) {
                this._cellState.set(cell, { changed: true, output: this.createCellOutput(cell) });
                //  It's a new cell; hence, the changed state is set to true.
                ////  This is a new cell; hence, add handlers that check for changes in the inputs and outputs.
                cell.inputArea.model.value.changed.connect((sender, args) => {
                    let state = this._cellState.get(cell);
                    if (state !== undefined) {
                        state.changed = true;
                        //  The input area changed; hence, the changed state is set to true.
                    }
                });
                if (cell.model.type == "code") {
                    cell.model.outputs.changed.connect((sender, args) => {
                        if (args.type == "add") {
                            //  An output has been added to the cell; hence, compare the current state with the new state.
                            let state = this._cellState.get(cell);
                            if (state !== undefined) {
                                let output = this.createCellOutput(cell);
                                if (output !== (state === null || state === void 0 ? void 0 : state.output)) {
                                    //  The output has changed; hence, set changed to true and update the output state.
                                    state.changed = true;
                                    state.output = output;
                                }
                                else {
                                    //  The output hasn't changed; hence, leave the state as is.
                                }
                            }
                        }
                    });
                }
            }
        });
    }
    createCellOutput(cell) {
        //  Combine the cell outputs into a string in order to check for changes.
        let output = "";
        if (cell.model.type == "code") {
            let outputs = cell.model.outputs;
            for (let index = 0; index < outputs.length; index++) {
                for (let key of Object.keys(outputs.get(index).data).sort()) {
                    output = output + JSON.stringify(outputs.get(index).data[key]);
                }
            }
            return output;
        }
        return "";
    }
    getNotebookState() {
        var _a;
        let nbFormatNotebook = (_a = this._notebook.model) === null || _a === void 0 ? void 0 : _a.toJSON();
        for (let index = 0; index < this._notebook.widgets.length; index++) {
            let cell = this._notebook.widgets[index];
            let cellState = this._cellState.get(cell);
            if (cellState === undefined) {
                throw new Error(`The cell at index ${index} is not tracked.`);
            }
            if (cellState.changed === false) {
                //  The cell has not changed; hence, the notebook format cell will contain just its id.
                nbFormatNotebook.cells[index] = { id: this._notebook.widgets[index].model.id };
            }
            else {
                nbFormatNotebook.cells[index]['id'] = this._notebook.widgets[index].model.id;
            }
        }
        for (let index = 0; index < this._notebook.widgets.length; index++) {
            let cell = this._notebook.widgets[index];
            let cellState = this._cellState.get(cell);
            if (cellState !== undefined) {
                cellState.changed = false;
            }
            //  The cell state is going to be captured; hence, set the state to not changed.
            //  We need to be certain that all the cells were processed prior to making any changes to their state;
            //  hence, this operation is done in a loop separate from the loop above.
        }
        let state = {
            session_id: this._session_id,
            seq: this._seq,
            notebook: nbFormatNotebook
        };
        this._seq = this._seq + 1;
        //  We've made changes to the state at this point; 
        //  hence, it's really important that nothing throws between now and recording the message.
        //  We need all the messages in order to reconstruct the Notebook at each event;
        //  hence, we need all the messages in order to reconstruct the Notebook at each event. :-)
        return state;
    }
}
class ETCJupyterLabNotebookStateProvider {
    constructor() {
        this._notebookPanelMap = new WeakMap();
    }
    getNotebookState({ notebookPanel }) {
        let notebookState = this._notebookPanelMap.get(notebookPanel);
        return notebookState === null || notebookState === void 0 ? void 0 : notebookState.getNotebookState();
    }
    addNotebookPanel({ notebookPanel }) {
        let etcJupyterLabNotebookState = new ETCJupyterLabNotebookState({ notebookPanel });
        this._notebookPanelMap.set(notebookPanel, etcJupyterLabNotebookState);
    }
}
const PLUGIN_ID = "@educational-technology-collective/etc_jupyterlab_notebook_state_provider:plugin";
const IETCJupyterLabNotebookStateProvider = new _lumino_coreutils__WEBPACK_IMPORTED_MODULE_0__.Token(PLUGIN_ID);
/**
 * Initialization data for the @educational-technology-collective/etc_jupyterlab_notebook_state extension.
 */
const plugin = {
    id: PLUGIN_ID,
    autoStart: true,
    provides: IETCJupyterLabNotebookStateProvider,
    activate: async (app) => {
        const VERSION = await (0,_handler__WEBPACK_IMPORTED_MODULE_1__.requestAPI)("version");
        console.log(`${PLUGIN_ID}, ${VERSION}`);
        return new ETCJupyterLabNotebookStateProvider();
    }
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ })

}]);
//# sourceMappingURL=lib_index_js.911d376bc86359f405f0.js.map