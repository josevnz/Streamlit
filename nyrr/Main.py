import sys
from pathlib import Path
from io import StringIO
import streamlit as st

from running import get_distances, load_data

if __name__ == "__main__":
    data_load_state = st.text('No data loaded yet...')
    raw_data = None
    if len(sys.argv) == 2:
        st.title(f'NYRR Race results, using {sys.argv[1]}')
        race_file = Path(sys.argv[1])
        if race_file.exists():
            with open(race_file, 'r') as race_data:
                raw_data = race_data.read()
        st.success('File successfully read', icon="✅")
    else:
        st.title(f'NYRR Race results, choose a file')
        uploaded_file = st.file_uploader(
            label="Choose the race results file",
            type=['csv'],
            accept_multiple_files=False,
            key="uploader"
        )
        if uploaded_file is not None:
            bytes_data = uploaded_file.getvalue()
            raw_data = StringIO(bytes_data.decode('utf-8'))
            data_load_state.text(f"Loaded race data")
            st.success('File successfully uploaded', icon="✅")
    if raw_data:
        dataframe = load_data(raw_data)
        distances = get_distances(dataframe)
        st.session_state['race data'] = dataframe
        st.session_state['all race distances'] = distances
        if 'distance chosen' in st.session_state:
            del st.session_state['distance chosen']
        data_load_state.text(f"Loaded race data was loaded ({len(dataframe)} races, {len(distances)} distances).")
