"""Dump Omnifocus database to JSON.

Author: Glyph Lefkowitz
Source: https://gist.github.com/glyph/e51d1809bf1edcb5e8f5dceb48f99ccb
"""

import json
import tempfile
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import IO

import click
from google.cloud import bigquery, storage

from omnimetrics._database import OMNIFOCUS, load_tasks


@click.group()
def omnimetrics():
    """Top-level omnimetrics command."""


@omnimetrics.command()
@click.argument("output", type=click.File("w"))
def dump_file(output: IO[str]) -> None:
    _dump_omnifocus(output)


@omnimetrics.command()
@click.option("--filename", default="omnifocus-%Y%m%d-%H%M%S.json", type=str)
@click.argument("directory", type=click.Path(file_okay=False, dir_okay=True, exists=True))
def dump(filename: str, directory: str) -> None:
    now = datetime.now()
    filename = now.strftime(filename)
    path = Path(directory).joinpath(filename)
    with path.open("w") as output:
        _dump_omnifocus(output)


def _dump_omnifocus(output: IO[str]) -> None:
    for task in load_tasks(OMNIFOCUS.default_document):
        task_dict = asdict(task)
        output.write(json.dumps(task_dict, default=jsonify))
        output.write("\n")


@omnimetrics.command()
@click.option("--gcs-bucket-prefix", type=str, default="")
@click.option("--filename", default="omnifocus-%Y%m%d-%H%M%S.json", type=str)
@click.argument("gcs-bucket", type=str)
@click.argument("destination-table", type=str)
def run_pipeline(gcs_bucket_prefix: str, filename: str, gcs_bucket: str, destination_table: str) -> None:
    """Extract data from Omnifocus and load it to GCS and BigQuery.

    The BigQuery destination table needs to exist, and needs to be partitioned.
    """
    now = datetime.now()
    with tempfile.NamedTemporaryFile("w") as temp_file:
        # Extract Omnifocus data to a file
        _dump_omnifocus(temp_file)
        # Load it to GCS
        storage_client = storage.Client()
        bucket = storage_client.bucket(gcs_bucket)
        filename = now.strftime(filename)
        gcs_path = str(Path(gcs_bucket_prefix) / Path(filename))
        blob = bucket.blob(gcs_path)
        blob.upload_from_filename(temp_file.name)
    # TODO: Create the table if it doesn't exist.
    _load_to_bigquery(gcs_bucket, gcs_path, f"{destination_table}${now.strftime('%Y%m%d')}")


def _load_to_bigquery(gcs_bucket: str, gcs_path: str, destination_table: str) -> None:
    gcs_url = f"gs://{gcs_bucket}/{gcs_path}"
    bigquery_client = bigquery.Client()
    job = bigquery_client.load_table_from_uri(
        [gcs_url],
        destination_table,
        job_config=bigquery.LoadJobConfig(
            autodetect=True,
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            schema_update_options=[
                bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION,
                bigquery.SchemaUpdateOption.ALLOW_FIELD_RELAXATION,
            ],
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND
        )
    )
    job.result()


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
