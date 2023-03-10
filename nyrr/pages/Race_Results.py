import logging
import streamlit as st
from pandas import DataFrame


def has_basic_data() -> bool:
    """
    Check here if required session values exist. They are defined in Main page.
    :return:
    """
    return 'race data' in st.session_state and 'all race distances' in st.session_state


def filter_by_distance(race_data: DataFrame, distance: str, verbose: bool = False) -> DataFrame:
    """
    Quert data from an existing Panda DataFrame and return a new filtered instance
    :param race_data:  Original dataframe
    :param distance: Distance to use as a filter
    :param verbose: Show extra messages on the console
    :return: Filtered dataframe
    """
    query = f"Distance == '{distance}'"
    if verbose:
        logging.info(f"Distance query: {query}")
    return race_data.query(inplace=False, expr=query)


if __name__ == "__main__":

    if not has_basic_data():
        st.title(f"NYRR Race results")
        st.write("Please go to the main page and load the race results you want to study")
    else:
        distance_chosen = st.radio(
            label="Refine your distance distance",
            options=st.session_state['all race distances'],
            index=0,
            key="distance chosen"
        )

        filtered_data_frame: DataFrame = filter_by_distance(
            race_data=st.session_state['race data'],
            distance=st.session_state['distance chosen'],
            verbose=True
        )
        st.title(f"NYRR Race results table ({len(filtered_data_frame)} races)")
        st.dataframe(
            data=filtered_data_frame,
            use_container_width=True
        )

        tab1, tab2 = st.tabs(["NYRR place by type", "NYRR Age-graded Percent"])
        with tab1:
            st.line_chart(
                st.session_state['race data'],
                x="Event Date",
                y=["Overall Place", "Gender Place", "Age-Group Place", "Age-Graded Place"]
            )
        with tab2:
            st.title(f"NYRR Age-graded Percent")
            st.line_chart(
                st.session_state['race data'],
                x="Event Date",
                y=["Age-Graded Percent"]
            )
