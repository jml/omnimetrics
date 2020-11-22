"""Dump Omnifocus database to JSON.

Author: Glyph Lefkowitz
Source: https://gist.github.com/glyph/e51d1809bf1edcb5e8f5dceb48f99ccb
"""

import json
from dataclasses import asdict
from datetime import datetime
from typing import IO

import click

from omnimetrics._database import OMNIFOCUS, load_tasks


@click.group()
def omnimetrics():
    """Top-level omnimetrics command."""


@omnimetrics.command()
@click.argument("output", type=click.File("w"))
def dump(output: IO[str]) -> None:
    for task in load_tasks(OMNIFOCUS.defaultDocument()):
        task_dict = asdict(task)
        try:
            output.write(json.dumps(task_dict, default=jsonify))
        except ValueError:
            import pdb; pdb.set_trace()
            raise
        output.write("\n")



def jsonify(o):
    if isinstance(o, datetime):
        return o.isoformat()
    return o


"""
Here's what we need to do.

- [x] use default_document to get the whole database
- [ ] use `flattened` versions to get at the actual contents
  - [x] `flattened_tasks`
  - [ ] `flattened_folders`
  - [ ] `flattened_tags`
  - [ ] `flattened_projects`

- build types for each of those flattened versions
  - [x] https://omni-automation.com/omnifocus/OF-API.html#Task
  - [ ] folder
  - [ ] tag
  - [ ] project

- serialisers for each of these
  - [x] JSON
  - [ ] Avro? https://avro.apache.org/docs/1.10.0/gettingstartedpython.html

- [x] Figure out how to use launchd to run a script daily
  - [x] https://www.launchd.info/
  - [x] Put a plist file in ~/Library/LaunchAgents

- [ ] Create a Terraform module that:
  - [ ] creates a GCP project
  - [x] creates a GCS bucket
  - [ ] creates a BigQuery dataset

- [ ] Create a script that uploads the serialised, flattened things to GCS

- [ ] Create another script that loads those flattened things to BigQuery

- [ ] Build a dbt module that transforms the raw data into something useful

- [ ] Build a DataStudio dashboard based on that data.

Strategy

- don't worry about serialising *everything* to start with
- also don't worry about fully correctly exporting any given type
- focus on getting all the pieces working end-to-end, such that we're exporting *something* from omnifocus to bigquery
"""
