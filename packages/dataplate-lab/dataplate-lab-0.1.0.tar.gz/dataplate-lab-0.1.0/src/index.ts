/* Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License"). You
 * may not use this file except in compliance with the License. A copy of
 * the License is located at
 *
 *     http://aws.amazon.com/apache2.0/
 *
 * or in the "license" file accompanying this file. This file is
 * distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
 * ANY KIND, either express or implied. See the License for the specific
 * language governing permissions and limitations under the License.
 */

import { ILayoutRestorer, JupyterFrontEnd, JupyterFrontEndPlugin, ILabShell } from '@jupyterlab/application';

import { ICommandPalette, MainAreaWidget, WidgetTracker } from '@jupyterlab/apputils';
import { IStateDB } from '@jupyterlab/statedb';

import { IRenderMimeRegistry } from '@jupyterlab/rendermime';

import { RunsWidget } from './widgets/RunsWidget';
import { RulesWidget } from './widgets/RulesWidget';
import { ScheduleWidget } from './widgets/ScheduleWidget';
import { DatasetsWidget } from './widgets/DatasetsWidget';
import { RunsModel } from './models/RunsModel';
import registerSharingIcons from './style/icons';
import { RulesModel } from './models/RulesModel';
import { DatasetsModel } from './models/DatasetsModel';

function activate(
  app: JupyterFrontEnd,
  shell: ILabShell,
  palette: ICommandPalette,
  restorer: ILayoutRestorer,
  rendermime: IRenderMimeRegistry,
  stateDB: IStateDB,
) {
  console.log('JupyterLab extension dataplate-lab is activated!');

  let runsWidget: MainAreaWidget<RunsWidget>;
  let rulesWidget: MainAreaWidget<RulesWidget>;
  let datasetsWidget: MainAreaWidget<DatasetsWidget>;
  const runsModel = new RunsModel();
  const rulesModel = new RulesModel();
  const datasetsModel = new DatasetsModel();

  registerSharingIcons();

  const tracker = new WidgetTracker<MainAreaWidget<RunsWidget>>({
    namespace: 'dataplate-labs',
  });
  // Track and restore the widget state
  const tracker1 = new WidgetTracker<MainAreaWidget<RulesWidget>>({
    namespace: 'dataplate-lab_schedules',
  });
  const tracker2 = new WidgetTracker<MainAreaWidget<DatasetsWidget>>({
    namespace: 'dataplate-lab_datasets',
  });

  // Add the list runs command
  const command = 'dataplate-lab:open_list_runs';
  app.commands.addCommand(command, {
    label: 'List Notebook Runs',
    execute: () => {
      if (!runsWidget) {
        const content = new RunsWidget(app, rendermime, runsModel);
        runsWidget = new MainAreaWidget({ content });
        runsWidget.id = 'dataplate-lab_list_runs';
        runsWidget.title.iconClass = 'scheduler-tab-icon fa fa-clock-o';
        runsWidget.title.label = 'Notebook Runs';
        runsWidget.title.closable = true;
        runsWidget.disposed.connect(() => {
          runsWidget = undefined;
        });
      }
      if (!tracker.has(runsWidget)) {
        // Track the state of the widget for later restoration
        tracker.add(runsWidget);
      }
      if (!runsWidget.isAttached) {
        // Attach the widget to the main work area if it's not there
        app.shell.add(runsWidget, 'main');
      }
      // refresh the list on the widget
      runsWidget.content.update();

      // Activate the widget
      app.shell.activateById(runsWidget.id);
    },
  });

  // Add the command to the palette.
  palette.addItem({ command, category: 'DataPlate Notebook Commands' });

  const command1 = 'dataplate-lab:open_list_schedules';
  app.commands.addCommand(command1, {
    label: 'List Notebook Schedules',
    execute: () => {
      if (!rulesWidget) {
        const content = new RulesWidget(rulesModel);
        rulesWidget = new MainAreaWidget({ content });
        rulesWidget.id = 'dataplate-lab_list_schedules';
        rulesWidget.title.iconClass = 'scheduler-tab-icon fa fa-clock-o';
        rulesWidget.title.label = 'Notebook Schedules';
        rulesWidget.title.closable = true;
        rulesWidget.disposed.connect(() => {
          rulesWidget = undefined;
        });
      }

      if (!tracker1.has(rulesWidget)) {
        // Track the state of the widget for later restoration
        tracker1.add(rulesWidget);
      }
      if (!rulesWidget.isAttached) {
        // Attach the widget to the main work area if it's not there
        app.shell.add(rulesWidget, 'main');
      }
      // refresh the list on the widget
      rulesWidget.content.update();

      // Activate the widget
      app.shell.activateById(rulesWidget.id);
    },
  });

  // Add the command to the palette.
  palette.addItem({ command: command1, category: 'DataPlate Notebook Commands' });

  const command2 = 'dataplate-lab:open_list_datasets';
  app.commands.addCommand(command2, {
    label: 'List My Allowed Datasets',
    execute: () => {
      if (!datasetsWidget) {
        const content = new DatasetsWidget(datasetsModel);
        datasetsWidget = new MainAreaWidget({ content });
        datasetsWidget.id = 'dataplate-lab_list_datasets';
        datasetsWidget.title.iconClass = 'scheduler-tab-icon fa fa-database';
        datasetsWidget.title.label = 'Allowed Datasets';
        datasetsWidget.title.closable = true;
        datasetsWidget.disposed.connect(() => {
          datasetsWidget = undefined;
        });
      }

      if (!tracker2.has(datasetsWidget)) {
        // Track the state of the widget for later restoration
        tracker2.add(datasetsWidget);
      }
      if (!datasetsWidget.isAttached) {
        // Attach the datasetsWidget to the main work area if it's not there
        app.shell.add(datasetsWidget, 'main');
      }
      // refresh the list on the widget
      datasetsWidget.content.update();

      // Activate the widget
      app.shell.activateById(datasetsWidget.id);
    },
  });

  // Add the command to the palette.
  palette.addItem({ command: command2, category: 'DataPlate Datasets Commands' });

  // Create the schedule widget sidebar
  const scheduleWidget = new ScheduleWidget(app, shell, runsModel, rulesModel, datasetsModel, stateDB);
  scheduleWidget.id = 'jp-schedule';
  scheduleWidget.title.iconClass = 'jp-SideBar-tabIcon fa fa-dot-circle-o fa-2x scheduler-sidebar-icon';
  scheduleWidget.title.caption = 'Schedule';

  // Let the application restorer track the running panel for restoration of
  // application state (e.g. setting the running panel as the current side bar
  // widget).
  restorer.add(scheduleWidget, 'schedule-sidebar');

  // Rank has been chosen somewhat arbitrarily to give priority to the running
  // sessions widget in the sidebar.
  app.shell.add(scheduleWidget, 'left', { rank: 200 });

  // Track and restore the widget states
  restorer.restore(tracker, {
    command,
    name: () => 'dataplate-lab',
  });
  restorer.restore(tracker1, {
    command: command1,
    name: () => 'dataplate-lab_schedules',
  });
  restorer.restore(tracker2, {
    command: command2,
    name: () => 'dataplate-lab_datasets',
  });
}

/**
 * Initialization data for the dataplate-lab extension.
 */
const extension: JupyterFrontEndPlugin<void> = {
  id: 'dataplate-lab:plugin',
  autoStart: true,
  requires: [ILabShell, ICommandPalette, ILayoutRestorer, IRenderMimeRegistry, IStateDB],
  activate: activate,
};

export default extension;
