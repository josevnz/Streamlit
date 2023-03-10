"""
This is a Streamlit application that shows how to make the Flavor wheel created
by [SAAC](https://sca.coffee/research/coffee-tasters-flavor-wheel?page=resources&d=scaa-flavor-wheel)
> Originally published in 1995, the Coffee Taster's Flavor Wheel—one of the most iconic resources in the coffee
> industry—has been the industry standard for over two decades. In 2016, this valuable resource was updated in
> collaboration with World Coffee Research (WCR).
Author: @josevnz@fosstodon.org
"""
from io import StringIO
from csv import DictReader
import streamlit as st
from streamlit_elements import mui, elements
from streamlit_elements import nivo

MARGIN = {'top': 1, 'right': 1, 'bottom': 1, 'left': 1}
COLORS = {'scheme': 'spectral'}
BORDER_COLOR = {'theme': 'background'}
ARC_LABELS_TEXT_COLOR = {
    'from': 'color',
    'modifiers': [
        ['darker', 1.4]
    ]
}
CHILD_COLOR = {
    'from': 'color',
    'modifiers': [
        ['brighter', 0.13]
    ]
}


def load_data(raw: StringIO) -> dict[str, any]:
    """
    Parse flat CSV metadata and convert it to format suitable for Graphic rendering
    :param raw:
    :return:
    """
    hierarchy = {}
    with raw:
        reader = DictReader(raw)
        for row in reader:
            basic = row["Basic"]
            middle = row["Middle"]
            final = row["Final"]
            if basic not in hierarchy:
                hierarchy[basic] = {}
            if middle not in hierarchy[basic]:
                hierarchy[basic][middle] = set([])
            hierarchy[basic][middle].add(final)
    flavor = {
        'name': 'flavors',
        'children': [],
    }
    for basic in hierarchy:
        basic_flavor = {
            'name': basic,
            'loc': 1,
            'children': []
        }
        for middle in hierarchy[basic]:
            middle_flavor = {
                'name': middle,
                'loc': 1,
                'children': []
            }
            for final in hierarchy[basic][middle]:
                if final:
                    final_flavor = {
                        'name': final,
                        'loc': 1,
                        'children': []
                    }
                    middle_flavor['children'].append(final_flavor)
            basic_flavor['children'].append(middle_flavor)
        flavor['children'].append(basic_flavor)
    return flavor


if __name__ == "__main__":

    st.title(f'Wheel of Coffee flavor, choose a file')

    """
    > Originally published in 1995, the Coffee Taster's Flavor Wheel—one of the most iconic resources in the coffee 
    > industry—has been the industry standard for over two decades. In 2016, this valuable resource was updated 
    > in collaboration with World Coffee Research (WCR). The foundation of this work, 
    > the [World Coffee Research Sensory Lexicon](http://worldcoffeeresearch.org/read-more/news/174-world-coffee-research-sensory-lexicon), is the product of dozens of professional 
    > sensory panelists, scientists, coffee buyers, and roasting companies collaborating via 
    > WCR and SCA. This is the largest and most collaborative piece of research on coffee 
    > flavor ever completed, inspiring a new set of vocabulary for industry professionals.
    """

    data_load_state = st.text('No data loaded yet...')
    uploaded_file = st.file_uploader(
        label="Choose the flavor wheel metadata file",
        type=['csv'],
        accept_multiple_files=False,
        key="uploader"
    )
    raw_data = None
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        raw_data = StringIO(bytes_data.decode('utf-8'))
        data_load_state.text(f"Loaded flavor data")
        st.success('File successfully uploaded', icon="✅")
    if raw_data:
        flavor_data = load_data(raw_data)
        """
        Read the wheel from center to the outermost level
        """
        with elements("nivo_charts"):
            with mui.Box(sx={"height": 900}):
                nivo.Sunburst(
                    data=flavor_data,
                    margin=MARGIN,
                    width=850,
                    height=500,
                    id="name",
                    value="loc",
                    cornerRadius=1,
                    borderColor=BORDER_COLOR,
                    colorBy="id",
                    colors=COLORS,
                    childColor=CHILD_COLOR,
                    inheritColorFromParent=False,
                    enableArcLabels=True,
                    arcLabel='id',
                    arcLabelsSkipAngle=7,
                    arcLabelsTextColor=ARC_LABELS_TEXT_COLOR
                )
