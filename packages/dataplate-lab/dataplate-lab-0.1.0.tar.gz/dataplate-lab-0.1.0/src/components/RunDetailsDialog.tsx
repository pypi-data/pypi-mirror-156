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

import React from 'react';
import { Run, RunResponse, ErrorResponse, DataPlateConfig } from '../server';
import { showDialog, Dialog } from '@jupyterlab/apputils';

import { sectionClass, labeledRowClass, kvContainer } from '../style/RunDetailsDialog';

async function loadDescription(jobName: string, serverURL: string, accessKey: string): Promise<Run> {
  const settings = ServerConnection.makeSettings();

  const request: DataPlateConfig = {
      serverURL: serverURL,
      accessKey: accessKey,
    };

  const response = await ServerConnection.makeRequest(
        URLExt.join(settings.baseUrl, 'dataplate-lab', 'run', jobName),
        { method: 'POST' , body: JSON.stringify(request)},
        settings,
      );

  if (!response.ok) {
    const error = (await response.json()) as ErrorResponse;
    if (error.error) {
      throw Error(error.error.message);
    } else {
      throw Error(JSON.stringify(error));
    }
  }

  const data = (await response.json()) as RunResponse;
  return data.run;
}

/**
 * Process the date string returned by the server for the start time into something we can
 * present in the UI. One option is that the server will not yet have set a date. This happens
 * if we've kicked off the job but SageMaker processing is still starting it.
 *
 * @param d The date string returned by the server
 * @param status The processing job status
 */
export function processDate(d: string, status: string): string {
  if (d == null) {
    if (status === 'InProgress') {
      return 'Starting';
    } else {
      return '';
    }
  } else {
    const c = d.toString().match(/^([-: \d]+)(\.\d+)?([+-])(\d+):(\d+)/);
    if (Array.isArray(c)) {
      if (c.length >0) {
        const date: Date = new Date(c[1].replace(/-/g, '/'));
        let offset: number = parseInt(c[4]) * 60 + parseInt(c[5]);
        if (c[3] === '-') {
          offset = -offset;
        }
        offset += date.getTimezoneOffset();
        date.setMinutes(date.getMinutes() - offset);
        const result: string = date.toLocaleString();
        return result;
      }
      else{
        // var length = d.length-7;
        var date = parseInt((d.toString()));//.substring(6,length)
        return (new Date(date).toLocaleString());
      }
    }
    else{
      // var length = d.length-7;
      var date = parseInt((d.toString()));//.substring(6,length)
      return (new Date(date).toLocaleString());
    }
  }
}


export function processRuntime(d: string, status: string): string {
  if (d == null) {
    if (status === 'InProgress') {
      return 'Starting';
    } else {
      return '';
    }
  } else {
    const c = d.toString().match(/^([-: \d]+)(\.\d+)/);
    if (Array.isArray(c)) {
      if (c.length >0) {
        return(d.toString())
      }
      else{
        var date = parseInt((d.toString()));
        var date_date = new Date(date)
        var offset = date_date.getTimezoneOffset();

        let cur_min :number = date_date.getHours() * 60 + date_date.getMinutes()
        var new_date = new Date(date_date)
        new_date.setHours(0)
        new_date.setMinutes(cur_min + offset);
        var datastr = new_date.toTimeString()
        datastr = datastr.split(' ')[0]
        var length = datastr.length;
        if (datastr.endsWith('AM') || datastr.endsWith('PM')){
            return (datastr.slice(0,length-3));
        }
        else{
            return (datastr)
        }
      }
    }
    else{
        var date = parseInt((d.toString()));
        var date_date = new Date(date)
        var offset = date_date.getTimezoneOffset();

        let cur_min :number = date_date.getHours() * 60 + date_date.getMinutes()
        var new_date = new Date(date_date)
        new_date.setHours(0)
        new_date.setMinutes(cur_min + offset);
        var datastr = new_date.toTimeString()
        datastr = datastr.split(' ')[0]
        var length = datastr.length;
        if (datastr.endsWith('AM') || datastr.endsWith('PM')){
            return (datastr.slice(0,length-3));
        }
        else{
            return (datastr)
        }
    }
  }
}

export function showRunDetails(jobName: string, serverURL: string, accessKey: string): () => Promise<void> {
  return async () => {
    let run: Run;
    let error: string;

    try {
      run = await loadDescription(jobName,serverURL,accessKey);
    } catch (e) {
      error = e.message;
    }

    let title: string;
    if (run) {
      if (run.Rule) {
        title = `Execution from rule "${run.Rule}"`;
      } else {
        title = `On-demand notebook execution`;
      }
    } else {
      title = 'Error retrieving details';
    }
    showDialog({
      title: title,
      body: <RunDetailsDialogBody jobName={jobName} description={run} error={error} />,
      buttons: [Dialog.okButton({ label: 'Close' })],
    });
  };
}

interface LabeledRowProps {
  label: string;
  content: string | JSX.Element;
}

const LabeledRow: React.SFC<LabeledRowProps> = (props) => {
  return (
    <tr className={labeledRowClass}>
      <td>{props.label}:</td>
      <td>{props.content}</td>
    </tr>
  );
};
interface RunDetailsDialogBodyProps {
  jobName: string;
  description: Run;
  error: string;
}

interface RunDetailsDialogBodyState {
  runDescription: Run | null;
  error?: string;
}
export class RunDetailsDialogBody extends React.Component<RunDetailsDialogBodyProps, RunDetailsDialogBodyState> {
  constructor(props: RunDetailsDialogBodyProps) {
    super(props);
    this.state = { runDescription: props.description, error: props.error };
  }

  render() {
    if (this.state.error) {
      return <span>Error loading run description: {this.state.error}</span>;
    }
    const desc = this.state.runDescription;
    if (!desc) {
      return <span>Loading...</span>;
    }
    let status: string;
    if (desc.Status === 'Failed') {
      status = `${desc.Status} (${desc.Failure})`;
    } else {
      status = desc.Status;
    }

    const s3Locations = (
      <div className={kvContainer}>
        <div>Input:</div>
        <div>{desc.Input}</div>
        <div>Output:</div>
        <div>{desc.Result}</div>
      </div>
    );
    const params = this.formatParameters(desc.Parameters);

    return (
      <div>
        <div className={sectionClass}>
          <header>
            Notebook &ldquo;{desc.Notebook}&rdquo; run at {processDate(desc.Created, desc.Status)}
          </header>
          <table>
            <LabeledRow label="Status" content={status} />
            <LabeledRow label="Parameters" content={params} />
          </table>
        </div>
        <div className={sectionClass}>
          <header>Timings:</header>
          <table>
            <LabeledRow label="Started" content={processDate(desc.Start, desc.Status)} />
            <LabeledRow label="Ended" content={processDate(desc.End, desc.Status)} />
            <LabeledRow label="Run time" content={processRuntime(desc.Elapsed, desc.Status)} />
          </table>
        </div>
        <div className={sectionClass}>
          <header>Processing job info:</header>
          <table>
            <LabeledRow label="Job name" content={desc.Job} />
            <LabeledRow label="Instance type" content={desc.Instance} />
            <LabeledRow label="S3 locations" content={s3Locations} />
            <LabeledRow label="Container image" content={desc.Image} />
            <LabeledRow label="IAM role" content={desc.Role} />
          </table>
        </div>
      </div>
    );
  }

  private formatParameters(params: string) {
    try {
      // eslint-disable-next-line  @typescript-eslint/no-explicit-any
      const parsed = JSON.parse(params) as Record<string, any>;
      return (
        <div>
          {Object.entries(parsed).map(([k, v]) => (
            <p key={`param-${k}`}>{`${k}: ${JSON.stringify(v)}`}</p>
          ))}
        </div>
      );
    } catch (SyntaxError) {
      return params;
    }
  }
}
