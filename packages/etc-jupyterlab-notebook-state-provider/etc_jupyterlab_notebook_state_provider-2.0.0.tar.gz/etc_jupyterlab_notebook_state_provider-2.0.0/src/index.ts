import { requestAPI } from "./handler";

import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import {
  NotebookPanel,
  Notebook
} from "@jupyterlab/notebook";

import {
  Cell,
  CodeCell,
  ICellModel
} from "@jupyterlab/cells";

import {
  IObservableList,
  IObservableUndoableList,
  IObservableString
} from "@jupyterlab/observables";

import { IOutputAreaModel } from "@jupyterlab/outputarea";

import { INotebookContent } from "@jupyterlab/nbformat";

import { UUID } from "@lumino/coreutils";

import { Token } from '@lumino/coreutils';

export interface INotebookState {
  session_id: string;
  seq: number;
  notebook: INotebookContent;
}

export class ETCJupyterLabNotebookState {

  private _notebook: Notebook;
  private _cellState: WeakMap<Cell<ICellModel>, { changed: boolean, output: string }>;
  private _seq: number;
  private _session_id: string;

  constructor({ notebookPanel }: { notebookPanel: NotebookPanel }) {

    this._notebook = notebookPanel.content;
    this._cellState = new WeakMap<Cell<ICellModel>, { changed: boolean, output: string }>();
    this._seq = 0;
    this._session_id = UUID.uuid4();

    this.updateCellState();
    //  The notebook loaded; hence, update the cell state.

    this._notebook.model?.cells.changed.connect((
      sender: IObservableUndoableList<ICellModel>,
      args: IObservableList.IChangedArgs<ICellModel>
    ) => {

      if (args.type == "add" || args.type == "set") {

        this.updateCellState();
        //  A cell was added; hence, update the cell state.
      }
    }, this);
  }

  private updateCellState() {

    this._notebook.widgets.forEach((cell: Cell<ICellModel>) => {

      if (!this._cellState.has(cell)) {

        this._cellState.set(cell, { changed: true, output: this.createCellOutput(cell) });
        //  It's a new cell; hence, the changed state is set to true.

        ////  This is a new cell; hence, add handlers that check for changes in the inputs and outputs.
        cell.inputArea.model.value.changed.connect(
          (sender: IObservableString, args: IObservableString.IChangedArgs) => {
            let state = this._cellState.get(cell);
            if (state !== undefined) {
              state.changed = true;
              //  The input area changed; hence, the changed state is set to true.
            }
          });

        if (cell.model.type == "code") {

          (cell as CodeCell).model.outputs.changed.connect(
            (sender: IOutputAreaModel, args: IOutputAreaModel.ChangedArgs
            ) => {
              if (args.type == "add") {
                //  An output has been added to the cell; hence, compare the current state with the new state.
                let state = this._cellState.get(cell);
                if (state !== undefined) {
                  let output = this.createCellOutput(cell);
                  if (output !== state?.output) {
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

  private createCellOutput(cell: Cell<ICellModel>) {
    //  Combine the cell outputs into a string in order to check for changes.

    let output = "";

    if (cell.model.type == "code") {

      let outputs = (cell as CodeCell).model.outputs;

      for (let index = 0; index < outputs.length; index++) {

        for (let key of Object.keys(outputs.get(index).data).sort()) {
          output = output + JSON.stringify(outputs.get(index).data[key]);
        }
      }
      return output;
    }

    return "";
  }

  getNotebookState(): { session_id: string, seq: number, notebook: INotebookContent } {

    let nbFormatNotebook = (this._notebook.model?.toJSON() as INotebookContent);

    for (let index = 0; index < this._notebook.widgets.length; index++) {

      let cell: Cell<ICellModel> = this._notebook.widgets[index];

      let cellState = this._cellState.get(cell);

      if (cellState === undefined) {
        throw new Error(`The cell at index ${index} is not tracked.`);
      }

      if (cellState.changed === false) {
        //  The cell has not changed; hence, the notebook format cell will contain just its id.

        (nbFormatNotebook.cells[index] as any) = { id: this._notebook.widgets[index].model.id };
      }
      else {
        nbFormatNotebook.cells[index]['id'] = this._notebook.widgets[index].model.id;
      }
    }

    for (let index = 0; index < this._notebook.widgets.length; index++) {
      let cell: Cell<ICellModel> = this._notebook.widgets[index];
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
    }

    this._seq = this._seq + 1;
    //  We've made changes to the state at this point; 
    //  hence, it's really important that nothing throws between now and recording the message.

    //  We need all the messages in order to reconstruct the Notebook at each event;
    //  hence, we need all the messages in order to reconstruct the Notebook at each event. :-)

    return state;
  }
}

export class ETCJupyterLabNotebookStateProvider {

  private _notebookPanelMap: WeakMap<NotebookPanel, ETCJupyterLabNotebookState>;

  constructor() {
    this._notebookPanelMap = new WeakMap<NotebookPanel, ETCJupyterLabNotebookState>();
  }

  getNotebookState({ notebookPanel }: { notebookPanel: NotebookPanel }): INotebookState | undefined {

    let notebookState = this._notebookPanelMap.get(notebookPanel);

    return notebookState?.getNotebookState();
  }

  addNotebookPanel({ notebookPanel }: { notebookPanel: NotebookPanel }) {

    let etcJupyterLabNotebookState = new ETCJupyterLabNotebookState({ notebookPanel });

    this._notebookPanelMap.set(notebookPanel, etcJupyterLabNotebookState);
  }
}

const PLUGIN_ID = "@educational-technology-collective/etc_jupyterlab_notebook_state_provider:plugin";

export const IETCJupyterLabNotebookStateProvider = new Token<IETCJupyterLabNotebookStateProvider>(PLUGIN_ID);

export interface IETCJupyterLabNotebookStateProvider {
  getNotebookState({ notebookPanel }: { notebookPanel: NotebookPanel }) : INotebookState | undefined ;
  addNotebookPanel({ notebookPanel }: { notebookPanel: NotebookPanel }) : void;
}

/**
 * Initialization data for the @educational-technology-collective/etc_jupyterlab_notebook_state extension.
 */
const plugin: JupyterFrontEndPlugin<IETCJupyterLabNotebookStateProvider> = {
  id: PLUGIN_ID,
  autoStart: true,
  provides: IETCJupyterLabNotebookStateProvider,
  activate: async (app: JupyterFrontEnd): Promise<IETCJupyterLabNotebookStateProvider> => {

    const VERSION = await requestAPI<string>("version")

    console.log(`${PLUGIN_ID}, ${VERSION}`);    
    
    return new ETCJupyterLabNotebookStateProvider();
  }
};

export default plugin;
