import json
import logging
from datetime import datetime, timedelta
from json.decoder import JSONDecodeError
import os
import textwrap

import requests
import streamlit as st
from pandas import DataFrame, Series, Timestamp
from numpy import float64
from requests import HTTPError, RequestException

MINUTES_BACK = 60
DEFAULT_TIME_BACK = timedelta(minutes=-MINUTES_BACK)
DEFAULT_QUERY = 'node_memory_MemFree_bytes'
STEP_DURATION = "30s"


@st.cache_data
def full_url(url: str, has_time_range: bool = True) -> str:
    if has_time_range:
        return f"{url}/api/v1/query_range"  # Range query
    return f"{url}/api/v1/query"  # Instant query


def get_metrics(
        the_payload: dict[str, any],
        url: str,
        start_range: datetime = None,
        end_range: datetime = None
) -> (dict[any, any], int):
    new_query = {}
    new_query.update(the_payload)
    if start_range and end_range:
        new_query['start'] = start_range.timestamp()
        new_query['end'] = end_range.timestamp()
        new_query['step'] = STEP_DURATION
    logging.info("url=%s, params=%s", url, new_query)
    response = requests.get(url=url, params=new_query)
    return response.json(), response.status_code


def transform(m_data: dict[any, any]) -> DataFrame:
    """
    Convert a Prometheus data structure into a Panda DataFrame
    :param m_data:
    :return: DataFrame
    """
    df = DataFrame({
        mtr['metric']['instance']: Series(
            data=[float64(vl[1]) for vl in mtr['values']],
            index=[Timestamp(vl[0], unit='s') for vl in mtr['values']],
            name="Free memory (bytes)"
        ) for mtr in m_data['data']['result']
    })
    logging.info(f"Columns: {df.columns}")
    logging.info(f"Index: {df.index}")
    logging.info(f"Index: {df}")
    return df


if __name__ == "__main__":

    st.title("Realtime Prometheus monitoring")
    data_load_state = st.text('No data loaded yet...')
    if 'PROMETHEUS_URL' not in os.environ:
        st.markdown("## Please define the following environment variable and restart this application (example below):")
        st.code(textwrap.dedent(f"""
        PROMETHEUS_URL="http://raspberrypi:9090/"
        export PROMETHEUS_URL
        streamlit run {__file__}
        """))
        st.markdown(
            "New to Prometheus?. Please check the [Official](https://prometheus.io/docs/prometheus/latest/querying/api/) documentation")
        data_load_state.error("No data was loaded.")
    else:
        code = 0
        metrics = {}
        try:
            PROM_URL = full_url(os.environ['PROMETHEUS_URL'], has_time_range=True)
            st.info(f"Using '{PROM_URL}'")
            query = DEFAULT_QUERY
            payload = {'query': query}
            # First query we boostrap with a reasonable time range
            END: datetime = datetime.now()
            START = END + DEFAULT_TIME_BACK
            if payload:
                (graph, raw) = st.tabs(["Time Series", "Debugging"])
                metrics, code = get_metrics(
                    url=PROM_URL,
                    the_payload=payload,
                    start_range=START,
                    end_range=END,
                )
                data: DataFrame = DataFrame()
                if code == 200:
                    now = datetime.now()
                    data_load_state.info(f"Metrics data refreshed ({now}).")
                    logging.info(f"Metrics data refreshed ({now}).")
                    try:
                        data = transform(m_data=metrics)
                        with graph:
                            st.title("Time series")
                            # See auto-refresh dilemma: https://github.com/streamlit/streamlit/issues/168
                            if st.button('Click to refresh!'):
                                st.write("Refreshing")
                                st.experimental_rerun()
                            st.line_chart(data=data)

                    except ValueError as val:
                        st.exception(val)
                    with raw:
                        if not data.empty:
                            st.title("DataFrame for Free memory (bytes)")
                            st.dataframe(data)
                        st.title("Query:")
                        st.markdown(f"```{query}, start={START}, end={END}```")
                        st.title("Prometheus data:")
                        st.json(metrics)
                else:
                    st.warning(f"Hmm, invalid query?: {query}")
                    st.warning(json.dumps(metrics, indent=True))
        except (HTTPError, JSONDecodeError, RequestException, KeyError) as exp:
            st.error(f"There was a problem while running the query (HTTP_CODE={code})...")
            if isinstance(exp, KeyError):
                st.code(f"Metrics={json.dumps(metrics, indent=True)}...")
            st.exception(exp)
