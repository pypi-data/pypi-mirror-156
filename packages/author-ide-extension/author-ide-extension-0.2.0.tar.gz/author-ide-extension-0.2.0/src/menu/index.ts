import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { IMainMenu } from '@jupyterlab/mainmenu';
import { Menu, Widget } from '@lumino/widgets';
import { Dialog, showDialog } from '@jupyterlab/apputils';
import { INotebookTracker } from '@jupyterlab/notebook';
import { show_spinner } from '../dialog';
import { loadLabContents } from '../tools';
import { axiosHandler } from '../handler';

export const menu: JupyterFrontEndPlugin<void> = {
  id: 'author-ide-extension:menu',
  autoStart: true,
  requires: [IMainMenu, INotebookTracker],
  activate: (app: JupyterFrontEnd, mainMenu: IMainMenu, notebookTracker: INotebookTracker) => {

    console.log('Activated Author-ide-extension menu plugin!');

    const editLabFromToken = 'edit-lab-from-token';
    app.commands.addCommand(editLabFromToken, {
    label: 'Edit a Lab',
    execute: () => {
      showTokenDialog(notebookTracker);
    }
    })

    const { commands } = app;

    // Create a new menu
    const menu: Menu = new Menu({ commands });
    menu.title.label = 'Skills Network';
    mainMenu.addMenu(menu, { rank: 80 });

    // Add command to menu
    menu.addItem({
    command: editLabFromToken,
    args: {}
    });

    const showTokenDialog = (notebookTracker: INotebookTracker) => {
      // Generate Dialog body
      let bodyDialog = document.createElement('div');
      let nameLabel = document.createElement('label');
      nameLabel.textContent = "Enter your authorization token: "
      let tokenInput = document.createElement('input');
      tokenInput.className = "jp-mod-styled";
      bodyDialog.appendChild(nameLabel);
      bodyDialog.appendChild(tokenInput);

      showDialog({
        title: "Edit a Lab",
        body: new Widget({node: bodyDialog}),
        buttons: [Dialog.cancelButton(), Dialog.okButton()]
      }).then(async result => {
        if (result.button.accept){
          show_spinner('Loading up your lab...');
          let panel = notebookTracker.currentWidget;
          if (panel === null){
            throw Error('Error loading lab')
          }
          await loadLabContents(panel, axiosHandler(tokenInput.value));
        }
      })
      .catch();
    };
  }
};
