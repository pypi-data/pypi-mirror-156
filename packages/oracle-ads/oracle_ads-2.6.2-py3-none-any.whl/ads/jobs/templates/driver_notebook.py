#!/usr/bin/env python
# -*- coding: utf-8; -*-

# Copyright (c) 2021, 2022 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/
"""This module runs a Jupyter Python notebook with nbconvert and print the outputs.
This is a driver script auto-generated by Oracle ADS.

The following environment variables are used:
JOB_RUN_NOTEBOOK:
    The relative path of the jupyter Python notebook to be executed.
NOTEBOOK_EXCLUDE_TAGS:
    Optional, a list of tags serialized to JSON string.
    Notebook cells with one of the tags will be excluded from running.
NOTEBOOK_ENCODING:
    Optional, the encoding for opening the notebook.
OUTPUT_URI:
    Optional, object storage URI for saving files from the output directory.
"""
import logging
import json
import os
import subprocess
from typing import Optional
from urllib.parse import urlparse

import nbformat
import oci
from nbconvert.preprocessors import ExecutePreprocessor


logger = logging.getLogger(__name__)


class ADSExecutePreprocessor(ExecutePreprocessor):
    """Customized Execute Preprocessor for running notebook."""

    def __init__(self, exclude_tags=None, **kw):
        """Initialize the preprocessor

        Parameters
        ----------
        exclude_tags : list, optional
            A list of cell tags, notebook cells with any of these cell tag will be skipped.
            Defaults to None.
        """
        self.exclude_tags = exclude_tags
        super().__init__(**kw)

    @staticmethod
    def _print_cell_outputs(cell):
        """Prints the outputs of a notebook cell."""
        for output in cell.outputs:
            output_type = output.get("output_type")
            if output_type == "stream":
                # stream outputs includes line break already
                print(output.text, end="")
            elif output_type == "execute_result":
                # execute_result may contain text/plain
                text = output.get("data", {}).get("text/plain", [])
                # The value could be str or list of str
                if isinstance(text, list):
                    for line in text:
                        print(line)
                else:
                    print(text)

    def preprocess_cell(self, cell, resources, *args, **kwargs):
        """Runs the notebook cell and print out the outputs"""
        # Skip the cell if any of the cell tags matching an exclude tag.
        if self.exclude_tags:
            # Log an error message if there is an error reading the cell tags,
            # and continue to run the cell.
            try:
                cell_tags = cell.get("metadata", {}).get("tags", [])
                for tag in cell_tags:
                    if tag in self.exclude_tags:
                        return cell, resources
            except Exception as ex:
                logger.error("An error occurred when reading cell tags: %s", str(ex))
        # Run the cell
        cell, resources = super().preprocess_cell(cell, resources, *args, **kwargs)
        # Print cell output
        if hasattr(cell, "outputs"):
            # Log a message if there is an error getting the cell output,
            # and continue to run the next cell.
            try:
                self._print_cell_outputs(cell)
            except Exception as ex:
                logger.error("An error occurred when reading cell outputs: %s", str(ex))
        return cell, resources


class OCIHelper:
    @staticmethod
    def init_oci_client(client_class):
        """Initializes OCI client with API key or Resource Principal.

        Parameters
        ----------
        client_class :
            The class of OCI client to be initialized.
        """
        if os.environ.get("OCI_RESOURCE_PRINCIPAL_VERSION"):
            logger.info(
                "Initializing %s with Resource Principal...", client_class.__name__
            )
            client = client_class(
                {}, signer=oci.auth.signers.get_resource_principals_signer()
            )
        else:
            logger.info("Initializing %s with API Key...", {client_class.__name__})
            client = client_class(oci.config.from_file())
        return client

    @staticmethod
    def copy_outputs(output_dir: str, output_uri: dict) -> None:
        """Copies the output files to object storage bucket.

        Parameters
        ----------
        output_dir : str
            Path of the output directory containing files to be copied.
        output_uri : str
            URI of the object storage path to store the output files.
        """
        output_dir = os.path.abspath(os.path.expanduser(output_dir))
        if not os.path.exists(output_dir):
            logger.error("Output directory %s not found.", output_dir)
            return
        if not output_uri:
            logger.error(
                "OUTPUT_URI is not defined in environment variable. No file is copied."
            )
            return
        logger.info("Copying files in %s to %s...", output_dir, output_uri)
        parsed = urlparse(output_uri)
        bucket_name = parsed.username
        namespace = parsed.hostname
        prefix = parsed.path
        oci_os_client = OCIHelper.init_oci_client(
            oci.object_storage.ObjectStorageClient
        )

        if not prefix:
            prefix = ""
        prefix = prefix.strip("/")

        for path, _, files in os.walk(output_dir):
            for name in files:
                file_path = os.path.join(path, name)

                with open(file_path, "rb") as pkf:
                    # Get the relative path of the file to keep the directory structure
                    relative_path = os.path.relpath(file_path, output_dir)
                    if prefix:
                        file_prefix = os.path.join(prefix, relative_path)
                    else:
                        # Save file to bucket root if prefix is empty.
                        file_prefix = relative_path

                    logger.debug(
                        f"Saving {relative_path} to {bucket_name}@{namespace}/{file_prefix}"
                    )

                    oci_os_client.put_object(
                        namespace,
                        bucket_name,
                        file_prefix,
                        pkf,
                    )


def run_notebook(
    notebook_path: str,
    working_dir: Optional[str] = None,
    exclude_tags: Optional[list] = None,
) -> None:
    """Runs a notebook

    Parameters
    ----------
    notebook_path : str
        The path of the notebook
    working_dir : str, optional
        The working directory for running the notebook, by default None.
        If this is None, the same directory of the notebook_path will be used.
    exclude_tags : list, optional
        Tags for excluding cells, by default None
    """
    # Read the notebook
    encoding = os.environ.get("NOTEBOOK_ENCODING", "utf-8")
    with open(notebook_path, encoding=encoding) as f:
        nb = nbformat.read(f, as_version=4)

    # Working/Output directory
    if not working_dir:
        working_dir = os.path.dirname(notebook_path)

    # The path of the output notebook with results/plots
    notebook_filename_out = os.path.join(working_dir, os.path.basename(notebook_path))

    ep = ADSExecutePreprocessor(exclude_tags=exclude_tags, kernel_name="python")

    from nbconvert.preprocessors import CellExecutionError

    try:
        ep.preprocess(nb, {"metadata": {"path": working_dir}})
    except CellExecutionError:
        msg = "Error executing the notebook.\n\n"
        msg += f'See notebook "{notebook_filename_out}" for the traceback.'
        logger.error(msg)
        raise
    finally:
        with open(notebook_filename_out, mode="w", encoding=encoding) as f:
            nbformat.write(nb, f)


def run_driver() -> None:
    """Runs the driver to execute a notebook."""
    try:
        # Ignore the error as conda-unpack may not exists
        subprocess.check_output("conda-unpack", stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as ex:
        logger.debug("conda-unpack exits with non-zero return code %s", ex.returncode)
        logger.debug(ex.output)
    notebook_file_path = os.path.join(
        os.path.dirname(__file__), os.environ.get("JOB_RUN_NOTEBOOK")
    )
    output_dir = os.path.join(os.path.dirname(__file__), "outputs")
    # Create the output directory
    os.makedirs(output_dir, exist_ok=True)
    # Exclude tags
    tags = os.environ.get("NOTEBOOK_EXCLUDE_TAGS")
    if tags:
        tags = json.loads(tags)
        logger.info("Excluding cells with any of the following tags: %s", tags)
    # Run the notebook
    run_notebook(notebook_file_path, working_dir=output_dir, exclude_tags=tags)
    # Save the outputs
    OCIHelper.copy_outputs(output_dir, os.environ.get("OUTPUT_URI"))


if __name__ == "__main__":
    run_driver()
