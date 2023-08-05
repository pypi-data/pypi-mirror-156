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

import * as React from 'react';

import { DatasetsModel, DatasetsUpdate } from '../models/DatasetsModel';
import {Dataset} from '../server';
import { SimpleTable, SimpleTablePage } from './SimpleTable';
import { tableEmptyClass } from '../style/tables';


export interface DatasetListProps {
  model: DatasetsModel;
}

interface DatasetListState {
  datasets: Dataset[];
  error: string;
}

const Headers = ['Name', 'Type'];

export class DatasetList extends React.Component<DatasetListProps, DatasetListState> {
  constructor(props: DatasetListProps) {
    super(props);
    this.state = { datasets: props.model.datasets, error: null };

    props.model.datasetsChanged.connect(this.onDatasetsChanged, this);
  }

  private onDatasetsChanged(_: DatasetsModel, datasetInfo: DatasetsUpdate): void {
    this.setState({ datasets: datasetInfo.datasets, error: datasetInfo.error });
  }

  componentWillUnmount(): void {
    this.props.model.datasetsChanged.disconnect(this.onDatasetsChanged, this);
  }

  private extractRow = (dataset: Dataset): (string | JSX.Element)[] => {

    return [
      dataset.name,
      dataset.type,
    ];
  };

  render(): JSX.Element {
    let content: JSX.Element;
    if (this.state.datasets) {
      // sometimes it seems that render gets called before the constructor ???
      const rows = this.state.datasets.map(this.extractRow);
      if (rows.length === 0) {
        content = <div className={tableEmptyClass}>No Datasets are allowed</div>;
      } else {
        content = <SimpleTable headings={Headers} rows={rows} />;
      }
    } else if (this.state.error) {
      content = <div className={tableEmptyClass}>Error retrieving datasets: {this.state.error}</div>;
    } else {
      content = <div className={tableEmptyClass}>Loading datasets...</div>;
    }
    return <SimpleTablePage title="My Allowed Dataset List">{content}</SimpleTablePage>;
  }

}
