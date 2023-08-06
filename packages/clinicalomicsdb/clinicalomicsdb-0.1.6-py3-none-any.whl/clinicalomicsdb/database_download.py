# Copyright 2022 Chang In Moon changin.moon@bcm.edu
# will implement a better structure for downloading data in future versions...
# we want to try import a csv file that contains each study name and it's box link
import io
import pandas as pd
from .file_download import download_text as _download_text #add .
from .exceptions import BaseError, BaseWarning, InvalidParameterError, NoInternetError, OldPackageVersionWarning #add .

def get_dataset_link():
    dataset_link_url = "https://bcm.box.com/shared/static/1rs6wid9em7tewjpqchnar4wlr75l3ml.csv"
    try:
        dataset_link_text = _download_text(dataset_link_url)
    except NoInternetError:
        raise NoInternetError("Insufficient internet to download available dataset info. Check your internet connection.") from None
    return pd.read_csv(io.StringIO(dataset_link_text), header=0, index_col=0)

def download(dataset):
    dataset = dataset.lower()
    link = get_dataset_link()
    # if the dataset is not specified or not found in the csv file list, return an error.    

    return link