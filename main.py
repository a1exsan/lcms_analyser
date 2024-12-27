from dash import Dash, Input, State, Output, Patch, callback, ctx
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

import dataViewer as dv
import dataEditor as de
import frontend

data = de.mzdataBuilder()

graph_mz = dv.lcms2Dview(data.get_init_x(),
                       data.get_init_y(),
                       data.get_init_z(),
                       title='mzdata analysis',
                       x_label='Retention time, sec',
                       y_label='Mass / charge')

graph_mass = dv.lcms2Dview(data.get_init_x(),
                           data.get_init_y(),
                           data.get_init_z(),
                           title='Mass Data',
                           x_label='Retention time, sec',
                           y_label='Mass, Da')


frontend_obj = frontend.oligo_lcms_layout(graph_mz, graph_mass, data.db_admin.get_content_tab())

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = frontend_obj.layout

@callback(
    #Output(component_id='textarea_out', component_property='value'),
    Output(component_id='Scatter-mzdata', component_property='figure', allow_duplicate=True),
    Output(component_id='show-retention-time-interval', component_property='children'),
    Output(component_id='show-background-treshold', component_property='children'),
    Output(component_id='show-neighbor-treshold', component_property='children'),
    Output(component_id='show-low-intens-treshold', component_property='children'),
    Output(component_id='show-bkg-polish-repeats', component_property='children'),
    Output(component_id='Scatter-mass-data', component_property='figure', allow_duplicate=True),

    Input(component_id='Scatter-mzdata', component_property='selectedData'),
    Input('retention-time-interval', 'value'),
    Input('background-treshold', 'value'),
    Input('neighbor-treshold', 'value'),
    Input('low-intens-treshold', 'value'),
    Input('bkg-polish-repeats', 'value'),
    Input('polish-button', 'n_clicks'),
    Input('show-init-mzdata-button', 'n_clicks'),
    Input('deconv-fast-button', 'n_clicks'),
    Input('deconvolution-button', 'n_clicks'),
    Input(component_id='Scatter-mass-data', component_property='selectedData'),
    Input('Scatter-mass-data', 'relayoutData'),
    Input('Scatter-mzdata', 'relayoutData'),
    Input(component_id='control-deconv-mode', component_property='value'),
    prevent_initial_call=True
)
def update_output(selectedData,
                  retention_interval,
                  bkg_treshold,
                  neighbor_treshold,
                  low_intens_treshold,
                  bkg_polish_repeats,
                  n_clicks,
                  show_init_data_clicks,
                  fast_deconv_clicks,
                  deconv_clicks,
                  selected_mass_data,
                  relayout_mass_data,
                  relayout_mzdata,
                  deconv_mode):

    triggered_id = ctx.triggered_id

    show_rt_interval = f"rt min: {retention_interval[0]}; rt max: {retention_interval[1]}"
    show_bkg_treshold = f"bkg: {bkg_treshold}"
    show_neighbor_treshold = f"selected: {neighbor_treshold}"
    show_low_intens_treshold = f"selected: {low_intens_treshold}"
    show_bkg_polish_repeats = f"selected: {bkg_polish_repeats}"

    if triggered_id == 'show-init-mzdata-button' and show_init_data_clicks is not None:
        graph_mz.set_data(data.get_init_x(),
                        data.get_init_y(),
                        data.get_init_z())
        return (graph_mz.figure, show_rt_interval, show_bkg_treshold, show_neighbor_treshold,
                show_low_intens_treshold, show_bkg_polish_repeats, graph_mass.figure)

    elif triggered_id == 'polish-button' and n_clicks is not None:
        data.polish(retention_interval, bkg_treshold, neighbor_treshold, bkg_polish_repeats, low_intens_treshold)
        graph_mz.set_data(data.get_x(),
                        data.get_y(),
                        data.get_z())
        return (graph_mz.figure, show_rt_interval, show_bkg_treshold, show_neighbor_treshold,
                show_low_intens_treshold, show_bkg_polish_repeats, graph_mass.figure)

    elif triggered_id == 'deconv-fast-button' and fast_deconv_clicks is not None:
        data.deconv_fast = True
        if len(deconv_mode) > 0:
            deconv_data, deconv_obj = data.deconvolution(is_positive=False)
        else:
            deconv_data, deconv_obj = data.deconvolution(is_positive=True)

        graph_mass.set_data(deconv_data['rt'],
                            deconv_data['mass'],
                            deconv_data['intens'])
        return (graph_mz.figure, show_rt_interval, show_bkg_treshold, show_neighbor_treshold,
                show_low_intens_treshold, show_bkg_polish_repeats, graph_mass.figure)

    elif triggered_id == 'deconvolution-button' and deconv_clicks is not None:
        data.deconv_fast = False
        if len(deconv_mode) > 0:
            deconv_data, deconv_obj = data.deconvolution(is_positive=False)
        else:
            deconv_data, deconv_obj = data.deconvolution(is_positive=True)

        graph_mass.set_data(deconv_data['rt'],
                            deconv_data['mass'],
                            deconv_data['intens'])
        return (graph_mz.figure, show_rt_interval, show_bkg_treshold, show_neighbor_treshold,
                show_low_intens_treshold, show_bkg_polish_repeats, graph_mass.figure)

    elif triggered_id == 'Scatter-mzdata':
        if 'xaxis.range[0]' in list(relayout_mzdata.keys()):
            graph_mz.init_draw(relayout=relayout_mzdata, tags=[])
            return (graph_mz.figure, show_rt_interval, show_bkg_treshold, show_neighbor_treshold,
                    show_low_intens_treshold, show_bkg_polish_repeats, Patch())

        if selectedData:
            if len(selectedData['points']) > 0:
                return (Patch(), show_rt_interval, show_bkg_treshold, show_neighbor_treshold,
                        show_low_intens_treshold, show_bkg_polish_repeats, graph_mass.figure)

    elif triggered_id == 'Scatter-mass-data':

        if 'xaxis.range[0]' in list(relayout_mass_data.keys()):
            graph_mass.current_relayout = relayout_mass_data
            graph_mass.init_draw(relayout=relayout_mass_data, tags=data.mass_tags)
            return (graph_mz.figure, show_rt_interval, show_bkg_treshold, show_neighbor_treshold,
                    show_low_intens_treshold, show_bkg_polish_repeats, graph_mass.figure)
        else:
            graph_mass.current_relayout = {}
            graph_mass.current_relayout['xaxis.range[0]'] = graph_mass.show_data['x'].min()
            graph_mass.current_relayout['xaxis.range[1]'] = graph_mass.show_data['x'].max()
            graph_mass.current_relayout['yaxis.range[0]'] = graph_mass.show_data['y'].min()
            graph_mass.current_relayout['yaxis.range[1]'] = graph_mass.show_data['y'].max()

        if selected_mass_data:
            if len(selected_mass_data['points']) > 0:
                data.selected_mass_points = []
                for point in selected_mass_data['points']:
                    data.selected_mass_points.append({'rt': point['x'], 'mass': point['y'],
                                                      'index': point['pointIndex']
                                                      })
                return (graph_mz.figure, show_rt_interval, show_bkg_treshold, show_neighbor_treshold,
                        show_low_intens_treshold, show_bkg_polish_repeats, Patch())

        if selectedData:
            if len(selectedData['points']) > 0:
                data.selected_mz_points = []
                for point in selectedData['points']:
                    data.selected_mz_points.append({'rt': point['x'], 'mass': point['y'],
                                                      'index': point['pointIndex']
                                                    })
                print(data.selected_mz_points)
                return (Patch(), show_rt_interval, show_bkg_treshold, show_neighbor_treshold,
                        show_low_intens_treshold, show_bkg_polish_repeats, graph_mass.figure)

    raise PreventUpdate


@callback(
    Output(component_id='Scatter-mzdata', component_property='figure'),
    Output(component_id='Scatter-mass-data', component_property='figure'),
    Output(component_id='retention-time-interval', component_property='value'),
    Output('tagging_table', 'data', allow_duplicate=True),
    Output('background-treshold', 'value'),
    Output('neighbor-treshold', 'value'),
    Output('low-intens-treshold', 'value'),
    Output('bkg-polish-repeats', 'value'),

    Input('upload-data', 'filename'),
    Input('upload-data', 'contents'),
    prevent_initial_call=True)

def upload_data_from_file(file_name, file_content):
    triggered_id = ctx.triggered_id
    if triggered_id == 'upload-data':
        if file_content is not None:
            data.load_data(fn=file_name, from_string=file_content)
            if data.new_file:

                graph_mz.set_data(data.get_init_x(),
                                  data.get_init_y(),
                                  data.get_init_z())

                out_rt_interval = data.rt_interval
                out_int_treshold = data.low_intens_treshold
                out_bkg_treshold = data.bkg_treshold
                out_neighbor_treshold = data.neighbor_treshold
                out_bkg_polish_count = data.bkg_polish_count

                if data.db_admin.flags['deconvolution'] > -1:
                    graph_mass.set_data(data.deconv_data['rt'],
                                        data.deconv_data['mass'],
                                        data.deconv_data['intens'])

                    if data.db_admin.flags['tagging'] > -1:
                        tagging_data = frontend_obj.add_tag_to_tab(data.mass_tags)
                    else:
                        tagging_data = frontend_obj.add_tag_to_tab([])
                else:
                    tagging_data = frontend_obj.add_tag_to_tab([])
                    graph_mass.set_data([],
                                        [],
                                        [])

                return (graph_mz.figure, graph_mass.figure, out_rt_interval, tagging_data,
                        out_bkg_treshold, out_neighbor_treshold, out_int_treshold, out_bkg_polish_count)

    raise PreventUpdate

@callback(
    Output('tagging_table', 'data', allow_duplicate=True),
    Output(component_id='Scatter-mass-data', component_property='figure', allow_duplicate=True),
    Output(component_id='oligo-sequence', component_property='value', allow_duplicate=True),

    Input('add-tag-button', 'n_clicks'),
    State('selected-tag', 'value'),
    Input('tagging_table', 'active_cell'),
    Input('del-tag-button', 'n_clicks'),
    Input('del-points-button', 'n_clicks'),
    Input('show-tags-button', 'n_clicks'),
    Input('sequence-tag', 'value'),
    Input('control-text-view', 'value'),
    prevent_initial_call=True
)
def update_tags_tab(add_tag_click, tag_name, active_cell, del_tag_click, del_points_click, show_tags_click,
                    seq_of_tag, view_text):
    triggered_id = ctx.triggered_id
    if triggered_id == 'add-tag-button' and add_tag_click is not None:
        data.add_mass_tag(tag_name, sequence=seq_of_tag)
        taging_data = frontend_obj.add_tag_to_tab(data.mass_tags)
        return taging_data, Patch(), seq_of_tag

    elif triggered_id == 'tagging_table' and active_cell is not None:
        data.selected_tag_row = active_cell['row']
        #graph_mass.draw_select_tag(data.mass_tags[data.selected_tag_row])
        graph_mass.init_draw(relayout=graph_mass.current_relayout, tags=[data.mass_tags[data.selected_tag_row]])
        return Patch(), graph_mass.figure, data.get_active_seq()

    elif triggered_id == 'del-tag-button' and del_tag_click is not None:
        data.delete_tag()
        taging_data = frontend_obj.add_tag_to_tab(data.mass_tags)
        patched_figure = Patch()
        return taging_data, patched_figure, Patch()

    elif triggered_id == 'del-points-button' and del_points_click is not None:
        data.drop_points_from_mass_data()
        patched_tag = Patch()
        graph_mass.set_data(data.deconv_data['rt'],
                            data.deconv_data['mass'],
                            data.deconv_data['intens'])
        return patched_tag, graph_mass.figure, Patch()

    elif triggered_id == 'show-tags-button' and show_tags_click is not None:
        graph_mass.init_draw(relayout=graph_mass.current_relayout, tags=data.mass_tags)
        return Patch(), graph_mass.figure, ''

    raise PreventUpdate

@callback(
    Output(component_id='Scatter-mass-data', component_property='figure', allow_duplicate=True),
    Input('control-text-view', 'value'),
    Input('control-ellipse-color', 'value'),
    prevent_initial_call=True
)
def update_text_label_view(ctr_text_view, ctr_ellipse_color):
    triggered_id = ctx.triggered_id
    if triggered_id == 'control-text-view':
        graph_mass.control_text_label_view = not ctr_text_view != []
        graph_mass.init_draw(relayout=graph_mass.current_relayout, tags=data.mass_tags)
        return graph_mass.figure

    elif triggered_id == 'control-ellipse-color':
        graph_mass.set_ellipse_color(is_red=ctr_ellipse_color != [])
        graph_mass.init_draw(relayout=graph_mass.current_relayout, tags=data.mass_tags)
        return graph_mass.figure

    raise PreventUpdate


@callback(
    Output(component_id='oligo-mass', component_property='children'),
    Output(component_id='oligo-extinction', component_property='children'),

    Input(component_id='oligo-sequence', component_property='value'),
    Input(component_id='calculate-oligo-prop-button', component_property='n_clicks')
)
def update_oligo_sequence_props(sequence, button_click):
    triggered_id = ctx.triggered_id
    if triggered_id == 'calculate-oligo-prop-button' and button_click is not None:
        if sequence != '':
            props = de.oligo_properties(sequence)()
            return (f"Mol Mass, Da: {props['Mol Mass, Da:']}",
                    f"Extinction, OE/mol: {props['Extinction, OE/mol:']}")
    raise PreventUpdate

@callback(

    Output(component_id='Scatter-mass-data', component_property='figure', allow_duplicate=True),
    Output('tagging_table', 'data', allow_duplicate=True),
    Output('db-content-table', 'data', allow_duplicate=True),

    Input('db-content-table', 'active_cell'),
    Input('load-db-data-button', 'n_clicks'),
    Input('update-db-data-button', 'n_clicks'),
    prevent_initial_call=True
)
def db_content_update(active_cell, load_button_click, update_button_click):
    triggered_id = ctx.triggered_id

    if triggered_id == 'db-content-table' and active_cell is not None:
        data.selected_db_tab_row = active_cell['row']

    if triggered_id == 'load-db-data-button' and load_button_click is not None:
        data.load_data(fn='', from_string='', description='', row_index=data.selected_db_tab_row)
        if data.db_admin.flags['deconvolution'] > -1:
            graph_mass.set_data(data.deconv_data['rt'],
                                data.deconv_data['mass'],
                                data.deconv_data['intens'])
        if data.db_admin.flags['tagging'] > -1:
            taging_data = frontend_obj.add_tag_to_tab(data.mass_tags)
        else:
            taging_data = None

        return graph_mass.figure, taging_data, Patch()

    if triggered_id == 'update-db-data-button' and update_button_click is not None:
        return graph_mass.figure, Patch(), data.db_admin.get_content_tab().to_dict('records')

    raise PreventUpdate

@callback(

    Output(component_id='fragment_table', component_property='data', allow_duplicate=True),

    Input('fragment-type-list', 'value'),
    Input('generate-frag-button', 'n_clicks'),
    Input('find-frag-button', 'n_clicks'),
    Input('clear-frag-button', 'n_clicks'),
    Input('init-find-sequence', 'value'),
    prevent_initial_call=True
)
def fragment_generator(type_list, gen_click, find_click, clear_click, sequence):
    triggered_id = ctx.triggered_id

    if triggered_id == 'generate-frag-button' and gen_click is not None:
        if sequence is not None:
            data.create_fragments_generator(sequence, type_list)
            return data.get_fragments_tab()

    raise PreventUpdate

@callback(

    Output(component_id='mz_identify_table', component_property='data', allow_duplicate=True),
    Output(component_id='Scatter-mzdata', component_property='figure', allow_duplicate=True),
    Output(component_id='tagging_mz_table', component_property='data', allow_duplicate=True),

    Input(component_id='calculate-mz-button', component_property='n_clicks'),
    Input(component_id='oligo-seq-mz', component_property='value'),
    Input(component_id='Scatter-mzdata', component_property='selectedData'),
    Input(component_id='mz-tag-window', component_property='value'),
    Input(component_id='mz-find-window', component_property='value'),
    Input(component_id='add-tag-mz-button', component_property='n_clicks'),
    Input(component_id='add-area-mz-button', component_property='n_clicks'),
    Input(component_id='oligo-mz-tag-name', component_property='value'),
    prevent_initial_call=True
)
def mz_tab_update(mz_tab_btn, oligo_seq, mz_points, mz_window, mz_find_wind, add_tag_click, add_area_click, tag_name):
    triggered_id = ctx.triggered_id

    if triggered_id == 'calculate-mz-button' and mz_tab_btn is not None:
        if oligo_seq is not None:
            if mz_points is not None:
                mz_tab, rect, local_mz_list = data.get_mz_tab(oligo_seq, mz_points['points'], mz_find_wind)
                graph_mz.mz_leder = mz_tab
                graph_mz.local_mz_list = local_mz_list
                graph_mz.leder_rect = rect
                graph_mz.window = mz_window
                graph_mz.init_draw()
            else:
                mz_tab, rect = data.get_mz_tab(oligo_seq, {})
            return mz_tab, graph_mz.figure, Patch()

    elif triggered_id == 'add-tag-mz-button' and add_tag_click is not None:
        if oligo_seq is not None:
            if graph_mz.mz_leder != [] and graph_mz.leder_rect != {}:
                mz_tags = data.add_mz_tag(tag_name, oligo_seq, graph_mz.leder_rect, graph_mz.window, graph_mz.mz_leder)
                return graph_mz.mz_leder, graph_mz.figure, mz_tags

    elif triggered_id == 'add-area-mz-button' and add_area_click is not None:
        if mz_points['points'] is not None:
            mz_tags = data.add_mz_area(tag_name, oligo_seq, mz_points['points'])
            return Patch(), graph_mz.figure, mz_tags

    raise PreventUpdate

@callback(

    Output(component_id='Scatter-mzdata', component_property='figure', allow_duplicate=True),
    Output(component_id='conc-pts', component_property='children', allow_duplicate=True),

    Input(component_id='mz-low-intens-treshhold', component_property='value'),
    Input(component_id='Scatter-mzdata', component_property='selectedData'),
    Input(component_id='show-selected-pts-button', component_property='n_clicks'),
    Input(component_id='show-all-pts-button', component_property='n_clicks'),
    Input(component_id='save-sel-pts-button', component_property='n_clicks'),
    Input(component_id='conc-pts-button', component_property='n_clicks'),
    Input(component_id='Scatter-mzdata', component_property='relayoutData'),
    prevent_initial_call=True
)
def mz_deconvolution_update(low_intens_treshold, sel_points, selected_click, all_click, save_click, conc_click,
                            sel_box_property):

    triggered_id = ctx.triggered_id

    if triggered_id == 'show-selected-pts-button' and selected_click is not None:
        selected_data = data.select_mz_intens_data(float(low_intens_treshold), sel_points['points'])
        graph_mz.set_data(
            selected_data['rt'],
            selected_data['mz'],
            selected_data['intens']
        )
        graph_mz.init_draw()
        return graph_mz.figure, data.get_points_concentration(sel_box_property)
    elif triggered_id == 'show-all-pts-button' and selected_click is not None:
        graph_mz.set_data(
            data.get_x(),
            data.get_y(),
            data.get_z()
        )
        graph_mz.init_draw()
        return graph_mz.figure, 0

    elif  triggered_id == 'save-sel-pts-button' and save_click is not None:
        data.selected_mz_df.to_csv('selected_points.csv', sep='\t', index=False)

    elif triggered_id == 'conc-pts-button' and conc_click is not None:
        concentration = data.get_points_concentration(sel_box_property)
        return Patch(), concentration

    raise PreventUpdate


if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0", port=8550, use_reloader=False)
    
