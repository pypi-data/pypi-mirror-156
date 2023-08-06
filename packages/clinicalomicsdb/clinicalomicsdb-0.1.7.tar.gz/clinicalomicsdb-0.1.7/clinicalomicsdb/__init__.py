#   Copyright 2022 Chang In Moon changin.moon@bcm.edu
__version__ = '0.1.7'

import io
import pandas as pd
from .database_download import download, get_dataset_link
from .file_download import download_text as _download_text
from .exceptions import BaseError, BaseWarning, InvalidParameterError, NoInternetError, OldPackageVersionWarning


def list_datasets():
    """List all available datasets."""

    dataset_list_url = "https://bcm.box.com/shared/static/hfm7swxvy4x48j9a8novny2432gh750u.csv"

    try:
        dataset_list_text = _download_text(dataset_list_url)
    except NoInternetError:
        raise NoInternetError("Insufficient internet to download available dataset info. Check your internet connection.") from None

    return pd.read_csv(io.StringIO(dataset_list_text), header=0, encoding='utf-8-sig')
