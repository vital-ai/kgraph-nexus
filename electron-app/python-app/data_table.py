from dash import dash_table


def create_data_table(df):
    return dash_table.DataTable(
        id='data-table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'),
        style_table={'height': '100%', 'overflowY': 'auto'}
    )
