"""Upload files to GCS.

Note: There's nothing about this that is remotely related to OmniFocus.
It's just a thing that uploads files in a directory to GCS and deletes them afterwards.
It is intended to be used with `QueueDirectories` in launchd.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from google.cloud.storage.bucket import Bucket


@dataclass(frozen=True)
class Upload:
    local_file: Path
    destination: str

    def upload(self, bucket: Bucket) -> None:
        blob = bucket.blob(self.destination)
        blob.upload_from_filename(self.local_file)


def iter_uploads(local_directory: Path, upload_prefix: Path) -> Iterable[Upload]:
    local_dir = Path(local_directory)
    for filename in local_dir.iterdir():
        if filename.name.startswith("."):
            continue
        if filename.is_dir():
            continue
        yield Upload(filename, str(upload_prefix / filename.name))
