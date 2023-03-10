from io import StringIO
from pathlib import Path
from typing import List
import traceback
import sys

import streamlit as st
import pandas as pd
from pandas import DataFrame
from pandas.errors import EmptyDataError

DATE_COLUMN = 'Event Date'


def load_data(raw_data: [Path, StringIO], verbose: bool = False) -> DataFrame:
    data: DataFrame
    if isinstance(raw_data, StringIO) or isinstance(raw_data, Path):
        try:
            data = pd.read_csv(raw_data)
        except EmptyDataError:
            if verbose:
                traceback.print_exc()
                st.warning("Will return an empty DataFrame from load_data", file=sys.stderr)
            return DataFrame()
    else:
        raise ValueError(f"I don't now how to handle {raw_data}")
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data


def get_distances(df: DataFrame) -> List:
    if 'Distance' in df:
        return [x for x in set(df.get(["Distance"]).to_dict(orient='list')['Distance'])]
    return []
