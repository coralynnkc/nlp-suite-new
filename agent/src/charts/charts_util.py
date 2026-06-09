# Written by Yuhang Feng November 2019-April 2020
# Written by Yuhang Feng November 2019-April 2020
# Edited by Roberto Franzosi, Tony May 2022
# Edited by Samir Kaddoura, March 2023
import io
import logging
import os
import re
from collections import Counter

import charts_Excel_util
import charts_Plotly_util
import IO_csv_util
import IO_user_interface_util
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import statistics_csv_util
from plotly.subplots import make_subplots


from charts_colormap_util import (
    cmaps,
    colormap,
    extract_file_name,
    fixed_transform,
    fixed_transform_helper,
    further_group,
    get_transformation_choice,
    interpolate_colors,
    main_colormap,
    rate_prop,
    rate_prop_helper,
    read_filename_color,
    renamedf,
    select_and_counting,
    special_sql_commands,
    sql_commands,
    timechart,
    visualize_colormap_data,
    where_data,
)
from charts_data_helpers import (
    add_missing_IDs,
    build_timed_alert_message,
    complete_sentence_index,
    get_dataRange,
    get_data_to_be_plotted_NO_counts,
    get_data_to_be_plotted_with_counts,
    get_xaxis_yaxis_values,
    header_check,
    process_sentenceID_record,
)
from charts_types import (
    boxplot,
    multiple_barchart,
    process_and_aggregate_data,
    Sankey,
    separator,
    Sunburst,
    Sunburst_Treemap,
    transform_data,
    Treemap,
    visualize_data,
)
from charts_viz_core import (
    prepare_data_to_be_plotted_inExcel,
    run_all,
    visualize_chart,
    visualize_chart_byGroup,
    visualize_chart_bySent,
)
