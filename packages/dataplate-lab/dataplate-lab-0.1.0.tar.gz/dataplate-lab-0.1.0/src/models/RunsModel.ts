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

import { ServerConnection } from '@jupyterlab/services';
import { URLExt } from '@jupyterlab/coreutils';

import { IDisposable } from '@lumino/disposable';
import { Poll } from '@lumino/polling';
import { ISignal, Signal } from '@lumino/signaling';

import {ListRunsResponse, Run, ErrorResponse, DataPlateConfig} from '../server';

export interface RunsUpdate {
  runs: Run[] | null;
  error: string;
}

export class RunsModel implements IDisposable {

  get serverURL(): string {
    return this._serverURL;
  }

  get accessKey(): string {
    return this._accessKey;
  }

  constructor() {
    this._active = false;
    this._refreshing = false;
    this._serverURL = "";
    this._accessKey = "";

    const interval = 30 * 1000; // TODO: make this a setting

    const poll = new Poll({
      factory: () => this.refresh(),
      frequency: {
        interval: interval,
        backoff: true,
        max: 300 * 1000,
      },
      standby: 'when-hidden',
    });
    this._poll = poll;
  }

  setDataplateServerKey(serverUrl: string, accessKey: string): void {
    this._serverURL = serverUrl;
    this._accessKey = accessKey;
  }

  setActive(active: boolean): void {
    this._active = active;
    if (active) {
      this.refresh();
    }
  }

  async refresh(): Promise<void> {
    this.getRuns().then((result: RunsUpdate) => {
      if (result) {
        this._runs = result.runs;
        this._runsChanged.emit(result);
      }
    });
  }

  private async getRuns(): Promise<RunsUpdate> {
    if (this._active && !this._refreshing) {
      this._refreshing = true;
      try {
        const settings = ServerConnection.makeSettings();

        const request: DataPlateConfig = {
          serverURL: this.serverURL,
          accessKey: this.accessKey,
        };

        // const response = await ServerConnection.makeRequest(
        //   URLExt.join(settings.baseUrl, 'dataplate-lab', 'runs'),
        //   { method: 'GET' },
        //   settings,
        // );

        // console.log(`sending request with ${JSON.stringify(request)}`);
        const response = await ServerConnection.makeRequest(
          URLExt.join(settings.baseUrl, 'dataplate-lab', 'runs'),
          { method: 'POST', body: JSON.stringify(request) },
          settings,
        );

        if (!response.ok) {
          const error = (await response.json()) as ErrorResponse;
          if (error.error) {
            return { runs: null, error: error.error.message };
          } else {
            return { runs: null, error: JSON.stringify(error) };
          }
        }

        const data = (await response.json()) as ListRunsResponse;
        return { runs: data.runs, error: null };
      } finally {
        this._refreshing = false;
      }
    }
  }

  get runs(): Run[] {
    return this._runs;
  }

  /**
   * A signal emitted when the current list of runs changes.
   */
  get runsChanged(): ISignal<RunsModel, RunsUpdate> {
    return this._runsChanged;
  }

  /**
   * Get whether the model is disposed.
   */
  get isDisposed(): boolean {
    return this._isDisposed;
  }

  /**
   * Dispose of the resources held by the model.
   */
  dispose(): void {
    if (this.isDisposed) {
      return;
    }
    this._isDisposed = true;
    if (this._poll) {
      this._poll.dispose();
    }
    Signal.clearData(this);
  }

  private _runs: Run[];
  private _isDisposed = false;
  private _runsChanged = new Signal<RunsModel, RunsUpdate>(this);

  private _poll: Poll;
  private _refreshing: boolean;
  private _active: boolean;
  private _serverURL: string;
  private _accessKey: string;
}
