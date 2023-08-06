#   Copyright 2022 Chang In Moon changin.moon@bcm.edu
__version__ = '0.1.0'

import io
import pandas as pd
from .file_download import download_text as _download_text
from .exceptions import BaseError, BaseWarning, InvalidParameterError, NoInternetError, OldPackageVersionWarning


def list_datasets():
    """List all available datasets."""

    dataset_list_url = "https://bcm.box.com/s/aog492dfwmeo6z61q505qcobwdksn2fa"

    try:
        dataset_list_text = _download_text(dataset_list_url)
    except NoInternetError:
        raise NoInternetError("Insufficient internet to download available dataset info. Check your internet connection.") from None

    return pd.read_csv(io.StringIO(dataset_list_text), sep="\t", index_col=0)

