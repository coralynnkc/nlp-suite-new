import pandas as pd
from excel_plotly_charts import run_excel_plotly_charts


def test_excel_plotly_charts_bar(fixture_csv, tmp_output):
    input_data = pd.read_csv(fixture_csv, encoding="utf-8-sig", on_bad_lines="skip")
    run_excel_plotly_charts(
        inputFilename=str(fixture_csv),
        outputDir=str(tmp_output),
        csv_field_visualization_var="valence",
        X_axis_var="Word",
        csv_file_field_Y_axis_list=["valence"],
        charts_type_options="bar",
        chart_package="Plotly",
        data_transformation="No transformation",
        inputFileData=input_data,
    )
