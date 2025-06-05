"""File system utilities, e.g., deleting temporary files."""

import os


def delete_file(file_path: str) -> None:
    """
    Delete a file from the filesystem if it exists.

    Args:
        file_path (str): Full path to the file.
    """
    if os.path.exists(file_path):
        os.remove(file_path)
