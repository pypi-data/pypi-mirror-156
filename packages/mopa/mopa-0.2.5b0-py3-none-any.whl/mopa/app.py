"""Dash app for using software"""

import dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash import dcc
from dash import html
import dash_uploader as du
import base64
import pandas as pd
import io
import zipfile
import shutil

import mopa


def create_dashboard():
    """
    Create dash app
    """
    # Initialize app
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

    # Configure uploads
    du.configure_upload(app, r'uploads')

    tab_upload = dcc.Tab(
        label='Upload AWR Files',
        children=[
            dbc.Row(dbc.Col(html.H1('1. Upload Files'))),
            dbc.Row([
                dbc.Col(du.Upload(
                    id='dash-uploader',
                    max_files=2,
                )),
                dbc.Col(html.Div(id='callback-output'),)
            ]),
            dbc.Row(dbc.Col(
                html.Button('Convert AWR Format', id='convert_awr', n_clicks=0)
            ))
        ]
    )

    tab_specs = dcc.Tab(
        label='Column Specification',
        children=[
            dbc.Row(dbc.Col(html.H1('2. Select Column Types'))),
            dbc.Row([
                dbc.Col([
                    html.H2('Decisions'),
                    dcc.Checklist(id='dec-dropdown')
                ]),
                dbc.Col([
                    html.H2('States'),
                    dcc.Checklist(id='state-dropdown')
                ]),
                dbc.Col([
                    html.H2('Objectives'),
                    dcc.Checklist(id='obj-dropdown')
                ])
            ]),
            dbc.Row(dbc.Col(
                html.Button(
                    'Submit Column Types',
                    id='update-vartypes',
                    n_clicks=0
                )
            )),
            dbc.Row(html.Div(html.Iframe(
                id='initial-parallel',
                style={'width': '100%', 'height': '1080px'}
            ))),
        ]
    )

    tab_robustness = dcc.Tab(
        label='Robustness',
        children=[
            dbc.Row(dbc.Col(html.H1('3. Robustness'))),
            dbc.Row(dbc.Col(
                html.Button(
                    'Compute Robustness',
                    id='robust',
                    n_clicks=0
                )
            )),
            dbc.Row(html.Div(html.Iframe(
                id='robust-parallel',
                style={'width': '100%', 'height': '1080px'}
            )))
        ]
    )

    tab_nondomination = dcc.Tab(
        label='Non-Domination',
        children=[
            dbc.Row(dbc.Col(html.H1('4. Non-Domination'))),
            dbc.Row(dbc.Col(html.Button(
                'Non-Dominated Sort',
                id='nondom',
                n_clicks=0
            ))),
            dbc.Row(html.Div(html.Iframe(
                id='nondom-parallel',
                style={'width': '100%', 'height': '1080px'}
            )))
        ]
    )

    tab_export = dcc.Tab(
        label='Export',
        children=[
            dbc.Row(dbc.Col(html.H1('5. Export Plots'))),
            dbc.Row(dbc.Col(html.Button(
                'Export',
                id='export',
                n_clicks=0
            ))),
            dcc.Download(id='download'),
        ]
    )

    # Create app layout
    app.layout = dbc.Container([
        dbc.Row(dbc.Col(html.H1('Multi-Objective Transistor Performance'))),
        dbc.Row(
            dcc.Tabs([
                tab_upload,
                tab_specs,
                tab_robustness,
                tab_nondomination,
                tab_export
            ])
        ),
        dcc.Store(id='initial-store'),
        dcc.Store(id='convert-store'),
        dcc.Store(id='label-store'),
        dcc.Store(id='robust-store'),
        dcc.Store(id='nondom-store')
    ])

    @du.callback(
        output=(
            Output('initial-store', 'data'),
            Output('callback-output', 'children')
        ),
        id='dash-uploader',
    )
    def upload_to_memory(status: du.UploadStatus):
        """Import uploaded files to memory as jsons

        Parameters
        ----------
        status : du.UploadStatus
            Upload status

        Returns
        -------
        dict
            `initial-store` memory

        str
            Message for button
        """
        # Import files
        df_awr_ls = [pd.read_table(i) for i in status.uploaded_files]

        # Convert to json
        json_awr_ls = [i.to_json() for i in df_awr_ls]

        # Store in memory
        data = {'json_awr_ls': json_awr_ls}

        # Message for uploaded files
        msg = html.Ul(
            [html.Li('Uploaded: '+str(x)) for x in status.uploaded_files]
        )

        return data, msg

    @app.callback(
        Output('convert-store', 'data'),
        Output('initial-parallel', 'srcDoc'),
        Output('dec-dropdown', 'options'),
        Output('state-dropdown', 'options'),
        Output('obj-dropdown', 'options'),
        Output('convert_awr', 'children'),
        Input('convert_awr', 'n_clicks'),
        State('initial-store', 'data'),
    )
    def upload_to_memory(n_clicks, data):
        """
        Upload json data and store in memory. These files get processed along
        the way and visualized

        Parameters
        ----------
        n_clicks : int
            Number of clicks
        contents : list
            List of strings of file contents
        filenames : list
            List of strings of filenames

        Returns
        -------
        data : dict
            Dictionary of data to store in memory
        srcdoc : str
            String of html output
        options : list
            Decisions, states, and objecttives
        msg : str
            Message for button
        """
        if n_clicks == 0:
            data = ''
            srcdoc = ''
            options = ['No Files Uploaded']
            msg = 'Convert AWR Format'
        else:
            # Delete files
            shutil.rmtree('uploads')

            # Parse Files
            df_awr_ls = [pd.read_json(i) for i in data['json_awr_ls']]

            # Convert to standard format
            df_ls = [mopa.analysis.awr_to_dataframe(df=i) for i in df_awr_ls]

            # Combine into single device DataFrame
            df_device_states = mopa.analysis.combine_output_single_device(
                df_ls
            )

            # Extract labels
            options = df_device_states.columns.to_list()

            # Render Output
            exp = mopa.viz.parallel(
                df_device_states
            )
            srcdoc = exp.to_html()

            # Store in memory
            data = {
                'df_device_states': df_device_states.to_json(),
                'srcdoc': srcdoc
            }

            # Message
            msg = 'Convert AWR Format: Done'
        return data, srcdoc, options, options, options, msg

    @app.callback(
        Output('label-store', 'data'),
        Output('update-vartypes', 'children'),
        Input('update-vartypes', 'n_clicks'),
        State('dec-dropdown', 'value'),
        State('state-dropdown', 'value'),
        State('obj-dropdown', 'value')
    )
    def update_labels(n_clicks, dec_value, state_value, obj_value):
        """Update stored labels for decisions, states, and objectives

        Parameters
        ----------
        n_clicks : int
            Number of clicks
        dec_value : list
            List of selected decisions
        state_value : list
            List of selected states
        obj_value : list
            List of selected objectives

        Returns
        -------
        data : dict
            Dictionary of data to store in memory
        """
        if n_clicks == 0:
            data = ''
            msg = 'Submit Column Types'
        else:
            data = {
                'obj_labs': obj_value,
                'state_labs': state_value,
                'dec_labs': dec_value,
            }
            msg = 'Submit Column Types: Done'
        return data, msg

    @app.callback(
        Output('robust-store', 'data'),
        Output('robust-parallel', 'srcDoc'),
        Input('robust', 'n_clicks'),
        Input('convert-store', 'data'),
        Input('label-store', 'data'),
    )
    def compute_robustness(n_clicks, initial_data, label_data):
        """
        Compute robustness. Includes adding to memory and visualization

        Parameters
        ----------
        n_clicks : int
            Number of times 'robust' button clicked.
        initial_data : dict
            Uploaded data stored in memory from 'upload_to_memory' tab
        label_data : dict
            Label data stored in memory from 'upload_to_memory' tab

        Returns
        -------
        robust_data : dict
            Dictionary of data to store in memory
        srcdoc : str
            String of html output
        """
        if n_clicks == 0:
            robust_data = ''
            srcdoc = ''
        else:
            # Local vars
            df_device_states = pd.read_json(initial_data['df_device_states'])
            obj_labs = label_data['obj_labs']
            dec_labs = label_data['dec_labs']
            robust_types = ['min', 'max']
            robust_labs = []
            for robust_type in robust_types:
                for obj in obj_labs:
                    robust_labs.append(robust_type + '_' + obj)

            # Compute robustness metrics
            df_device_robust = mopa.analysis.get_native_robust_metrics(
                df=df_device_states,
                dec_labs=dec_labs,
                state_labs=label_data['state_labs'],
                obj_labs=obj_labs,
                robust_types=robust_types
            )
            df_device_robust_states = mopa.analysis.get_states(
                df_device_robust,
                df_device_states,
                dec_labs=dec_labs,
            )

            # Create visualization
            exp = mopa.viz.parallel(
                df_device_robust_states,
                invert_cols=obj_labs+robust_labs
            )
            srcdoc = exp.to_html()

            # Store in memory
            robust_data = {
                'df_device_robust': df_device_robust.to_json(),
                'robust_labs': robust_labs,
                'srcdoc': srcdoc
            }

        return robust_data, srcdoc

    @app.callback(
        Output('nondom-store', 'data'),
        Output('nondom-parallel', 'srcDoc'),
        Input('nondom', 'n_clicks'),
        Input('robust-store', 'data'),
        Input('convert-store', 'data'),
        Input('label-store', 'data')
    )
    def nondom(n_clicks, robust_data, initial_data, label_data):
        """Get Non-dominated solutions

        Parameters
        ----------
        n_clicks : int
            Number of clicks of nondom button
        robust_data : dict
            Dictionary of data to store in memory
        initial_data : dict
            Uploaded data stored in memory from 'upload_to_memory' tab
        label_data : dict
            Label data stored in memory from 'upload_to_memory' tab

        Returns
        -------
        nondom_data : dict
            Dictionary of data to store in memory
        srcdoc : str
            String of html rendering
        """
        if n_clicks == 0:
            nondom_data = ''
            srcdoc = ''
        else:
            # Local Vars
            robust_labs = robust_data['robust_labs']
            dec_labs = label_data['dec_labs']
            obj_labs = label_data['obj_labs']
            df_device_robust = pd.read_json(robust_data['df_device_robust'])
            df_device_states = pd.read_json(initial_data['df_device_states'])

            # Nondominated sorting
            df_nondom = mopa.analysis.get_nondomintated(
                df_device_robust,
                objs=robust_labs,
                max_objs=robust_labs,

            )
            df_nondom_states = mopa.analysis.get_states(
                df_nondom,
                df_device_states,
                dec_labs=dec_labs,
            )

            # Create plot for non-dominated solutions
            exp = mopa.viz.parallel(
                df_nondom_states,
                invert_cols=obj_labs + robust_labs
            )
            srcdoc = exp.to_html()

            # Store in memory
            nondom_data = {
                'df_nondom': df_nondom.to_json(),
                'srcdoc': srcdoc
            }

        return nondom_data, srcdoc

    @app.callback(
        Output('download', 'data'),
        Input('export', 'n_clicks'),
        Input('robust-store', 'data'),
        Input('convert-store', 'data'),
        Input('nondom-store', 'data')
    )
    def download(n_clicks, robust_data, initial_data, nondom_data):
        """Download plots

        Parameters
        ----------
        n_clicks : int
            Number of clicks of export button
        robust_data : dict
            Dictionary of data to store in memory
        initial_data : dict
            Dictionary of data to store in memory
        nondom_data : dict
            Dictionary of data to store in memory
        """
        if n_clicks == 0:
            return 0
        else:
            zip_file_name = "plots.zip"
            with zipfile.ZipFile(zip_file_name, mode="w") as zf:
                zf.writestr('Initial.html', initial_data['srcdoc'])
                zf.writestr('Robust.html', robust_data['srcdoc'])
                zf.writestr('Nondom.html', nondom_data['srcdoc'])
            return dcc.send_file(zip_file_name)

    return app


def main():
    # Create dashboard
    app = create_dashboard()

    # Run dashboard
    app.run_server()


if __name__ == '__main__':
    main()
