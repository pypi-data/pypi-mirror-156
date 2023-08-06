/* eslint-disable prettier/prettier */
/* eslint-disable @typescript-eslint/explicit-module-boundary-types */
/* eslint-disable @typescript-eslint/ban-types */
import { DocumentRegistry } from '@jupyterlab/docregistry';
import { IDocumentManager } from '@jupyterlab/docmanager';
import { ToolbarButton } from '@jupyterlab/apputils';
import { IDisposable, DisposableDelegate } from '@lumino/disposable';
import { IMainMenu } from '@jupyterlab/mainmenu';
import { getFileContents, loadLabContents } from '../tools';
import { axiosHandler, postLabModel } from '../handler';
import { Globals } from '../config';
import { ATLAS_TOKEN } from '../config';

import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import {
  NotebookPanel,
  INotebookModel,
  INotebookTracker
} from '@jupyterlab/notebook';

/**
 * The plugin registration information.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  activate,
  id: 'skillsnetwork-authoring-extension:plugin',
  autoStart: true,
  requires: [INotebookTracker, IDocumentManager, IMainMenu]
};

/**
 * A notebook widget extension that adds a button to the toolbar.
 */
export class ButtonExtension
  implements DocumentRegistry.IWidgetExtension<NotebookPanel, INotebookModel>
{
  /**
   * Create a new extension for the notebook panel widget.
   *
   * @param panel Notebook panel
   * @param context Notebook context
   * @returns Disposable on the added button
   */
  createNew(
    panel: NotebookPanel,
    context: DocumentRegistry.IContext<INotebookModel>
  ): IDisposable {
    const start = async () => {
      // Get the current file contents
      const file = await getFileContents(panel, context);
      console.log(file);
      // POST to Atlas the file contents/lab model
      postLabModel(axiosHandler(Globals.token), file);
    };

    const button = new ToolbarButton({
      className: 'publish-lab-button',
      label: 'Publish',
      onClick: start,
      tooltip: 'Publish Lab'
    });

    panel.toolbar.insertItem(10, 'publish', button);
    return new DisposableDelegate(() => {
      button.dispose();
    });
  }
}

/**
 * Activate the extension.
 *
 * @param app Main application object
 */
async function activate(
  app: JupyterFrontEnd,
  mainMenu: IMainMenu,
) {

  console.log("Activated skillsnetwork-authoring-extension button plugin!");
  // Add the Publish widget to the lab environment
  app.docRegistry.addWidgetExtension('Notebook', new ButtonExtension());

  // TO DO: Change logic so that we check if the file exists first before trying to open it...
  // TO DO: Add logic to rename the default file opened to lab's name

  // Attempt to open the lab
  await app.commands.execute('docmanager:open', {
    path: 'Untitled.ipynb',
    kernel: { name: 'python'} })
  // The lab was created in a previous session, open up the existing lab
  .then(async (widget) => {
    console.log('Successfully got existing file');
    // Only try to load up lab when author is not in local authoring env
    // TODO: Refactor this and make it better :')
    let token = ATLAS_TOKEN();
    if (token !== null || token !== 'NO_TOKEN'){
      // Load the contents of the lab into the notebook
      await loadLabContents(widget, axiosHandler(), Globals.author_env)
        .then(()=> widget.show())
        .catch();
    }
  })
  // This is the user's first session, create the lab first and open it for them
  .catch(async () => {
    console.log('Could not open file. Creating new file.');
    // Create a new notebook with Panel
    const nbPanel: NotebookPanel = await app.commands.execute(
      'notebook:create-new',
      { kernelName: 'python', activate: true }
    );
    console.log('Created a new file!');
    let token = ATLAS_TOKEN();
    // Load the contents of the lab into the notebook
    if (token !== null || token !== 'NO_TOKEN'){
      await loadLabContents(nbPanel, axiosHandler(), Globals.author_env)
      .then(() => nbPanel.show());
    //bPanel.revealed;
    }
  });
}

/**
 * Export the plugin as default.
 */
export default plugin;
