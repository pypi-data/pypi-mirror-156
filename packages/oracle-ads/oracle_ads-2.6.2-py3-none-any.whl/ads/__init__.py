#!/usr/bin/env python
# -*- coding: utf-8 -*--

# Copyright (c) 2020, 2022 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/

from __future__ import print_function, division, absolute_import
import os
import logging
import sys

import oci

import matplotlib.font_manager  # causes matplotlib to regenerate its fonts
import json

import ocifs
from ads.common.decorator.deprecate import deprecated
from ads.common.ipython import configure_plotting, _log_traceback
from ads.feature_engineering.accessor.series_accessor import ADSSeriesAccessor
from ads.feature_engineering.accessor.dataframe_accessor import ADSDataFrameAccessor


os.environ["GIT_PYTHON_REFRESH"] = "quiet"

__version__ = ""
with open(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "ads_version.json")
) as version_file:
    __version__ = json.load(version_file)["version"]

debug_mode = os.environ.get("DEBUG_MODE", False)
documentation_mode = os.environ.get("DOCUMENTATION_MODE", "False") == "True"
oci_config_path = oci.config.DEFAULT_LOCATION  # "~/.oci/config"
oci_key_profile = "DEFAULT"
test_mode = os.environ.get("TEST_MODE", False)
resource_principal_mode = bool(os.environ.get("RESOURCE_PRINCIPAL_MODE", False))
orig_ipython_traceback = None


def set_auth(
    auth="api_key", oci_config_location=oci.config.DEFAULT_LOCATION, profile="DEFAULT"
):
    """
    Enable/disable resource principal identity or keypair identity in a notebook session.

    Parameters
    ----------
    auth: {'api_key', 'resource_principal'}, default 'api_key'
         Enable/disable resource principal identity or keypair identity in a notebook session
    oci_config_location: str, default oci.config.DEFAULT_LOCATION, which is '~/.oci/config'
        config file location
    profile: str, default 'DEFAULT'
         profile name for api keys config file
    """
    global resource_principal_mode
    global oci_config_path
    global oci_key_profile
    oci_key_profile = profile
    if os.path.exists(os.path.expanduser(oci_config_location)):
        oci_config_path = oci_config_location
    else:
        logging.warning(
            f"{oci_config_location} file not exists, default value oci.config.DEFAULT_LOCATION used instead"
        )
        oci_config_path = oci.config.DEFAULT_LOCATION
    if auth == "api_key":
        resource_principal_mode = False
    elif auth == "resource_principal":
        resource_principal_mode = True


def getLogger(name="ads"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.WARNING)
    return logger


logger = getLogger(__name__)
logger.addHandler(logging.NullHandler())

# All warnings are logged by default
logging.captureWarnings(True)


def set_debug_mode(mode=True):
    """
    Enable/disable printing stack traces on notebook.

    Parameters
    ----------
    mode: bool (default True)
         Enable/disable print stack traces on notebook

    """
    global debug_mode
    debug_mode = mode
    import IPython

    if debug_mode:
        from ads.common.ipython import orig_ipython_traceback

        IPython.core.interactiveshell.InteractiveShell.showtraceback = (
            orig_ipython_traceback
        )
    else:
        IPython.core.interactiveshell.InteractiveShell.showtraceback = _log_traceback


@deprecated("2.3.1")
def set_documentation_mode(mode=False):
    """
    This method is deprecated and will be removed in future releases.
    Enable/disable printing user tips on notebook.

    Parameters
    ----------
    mode: bool (default False)
        Enable/disable print user tips on notebook
    """
    global documentation_mode
    documentation_mode = mode


@deprecated("2.3.1")
def set_expert_mode():
    """
    This method is deprecated and will be removed in future releases.
    Enables the debug and documentation mode for expert users all in one method.
    """
    set_debug_mode(True)
    set_documentation_mode(False)


#
# ***FOR TESTING PURPOSE ONLY***
#
def _set_test_mode(mode=False):
    """
    Enable/disable intercept the automl call and rewrite it to always use
    the two algorithms (LogisticRegression for classification and LinearRegression for regression).
    Enable only during tests to reduce nb convert notebook tests run time.

    Parameters
    ----------
    mode: bool (default False)
         Enable/disable the ability to intercept automl call

    """
    global test_mode
    test_mode = mode


def hello():
    """
    Imports Pandas, sets the documentation mode, and prints a fancy "Hello".
    """
    import pandas

    global documentation_mode
    global debug_mode

    print(
        f"""

  O  o-o   o-o
 / \\ |  \\ |
o---o|   O o-o
|   ||  /     |
o   oo-o  o--o

ADS SDK version: {__version__}
Pandas version: {pandas.__version__}
Debug mode: {debug_mode}
"""
    )


configure_plotting()
