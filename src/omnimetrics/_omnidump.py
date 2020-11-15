"""Dump Omnifocus database to JSON.

Author: Glyph Lefkowitz
Source: https://gist.github.com/glyph/e51d1809bf1edcb5e8f5dceb48f99ccb
"""

from omnimetrics._database import OMNIFOCUS, load_tasks

import attr


def main():
    for task in load_tasks(OMNIFOCUS.defaultDocument()):
        print(attr.asdict(task))


"""
Here's what we need to do.

- use default_document to get the whole database
- use `flattened` versions to get at the actual contents
  - `flattened_tasks`
  - `flattened_folders`
  - `flattened_tags`
  - `flattened_projects`

- build types for each of those flattened versions
  - https://omni-automation.com/omnifocus/OF-API.html#Task
  - folder
  - tag
  - project

- serialisers for each of these
  - JSON
  - Avro? https://avro.apache.org/docs/1.10.0/gettingstartedpython.html

- Figure out how to use launchd to run a script daily
- Create a Terraform module that:
  - creates a GCP project
  - creates a GCS bucket
  - creates a BigQuery dataset

- Create a script that uploads the serialised, flattened things to GCS

- Create another script that loads those flattened things to BigQuery

- Build a dbt module that transforms the raw data into something useful

- Build a DataStudio dashboard based on that data.

Strategy

- don't worry about serialising *everything* to start with
- also don't worry about fully correctly exporting any given type
- focus on getting all the pieces working end-to-end, such that we're exporting *something* from omnifocus to bigquery
"""
