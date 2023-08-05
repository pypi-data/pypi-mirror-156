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

import {ListRulesResponse, Rule, ErrorResponse, DataPlateConfig} from '../server';

export interface RulesUpdate {
  rules: Rule[] | null;
  error: string;
}

export class RulesModel implements IDisposable {
  get serverURL(): string {
    return this._serverURL;
  }

  get accessKey(): string {
    return this._accessKey;
  }

  constructor() {
    this._refreshing = false;
    this._active = false;
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
    this.getRules().then((result: RulesUpdate) => {
      if (result) {
        this._rules = result.rules;
        this._rulesChanged.emit(result);
      }
    });
  }

  private async getRules(): Promise<RulesUpdate> {
    if (this._active && !this._refreshing) {
      this._refreshing = true;
      try {
        const settings = ServerConnection.makeSettings();
        // const response = await ServerConnection.makeRequest(
        //   URLExt.join(settings.baseUrl, 'dataplate-lab', 'schedules'),
        //   { method: 'GET' },
        //   settings,
        // );
        const request: DataPlateConfig = {
          serverURL: this.serverURL,
          accessKey: this.accessKey,
        };
        // console.log(`sending request with ${JSON.stringify(request)}`);
        const response = await ServerConnection.makeRequest(
          URLExt.join(settings.baseUrl, 'dataplate-lab', 'schedules'),
          { method: 'POST', body: JSON.stringify(request) },
          settings,
        );

        if (!response.ok) {
          const error = (await response.json()) as ErrorResponse;
          return { rules: null, error: error.error.message };
        }

        const data = (await response.json()) as ListRulesResponse;
        return { rules: data.schedules, error: null };
      } finally {
        this._refreshing = false;
      }
    }
  }

  get rules(): Rule[] {
    return this._rules;
  }

  /**
   * A signal emitted when the current list of runs changes.
   */
  get rulesChanged(): ISignal<RulesModel, RulesUpdate> {
    return this._rulesChanged;
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

  private _rules: Rule[];
  private _isDisposed = false;
  private _rulesChanged = new Signal<RulesModel, RulesUpdate>(this);

  private _poll: Poll;
  private _refreshing: boolean;
  private _active: boolean;
  private _serverURL: string;
  private _accessKey: string;
}
