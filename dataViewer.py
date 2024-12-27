import plotly.graph_objs as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd

class lcms2Dview():

    def __init__(self, data_x, data_y, data_z, x_label='', y_label='', title=''):

        self.data = pd.DataFrame()
        self.data['x'] = data_x
        self.data['y'] = data_y
        self.data['z'] = data_z

        self.x_label = x_label
        self.y_label = y_label
        self.title = title
        self.reduce_data_treshold = 76000
        self.figure_width = 1000
        self.figure_height = 700
        self.control_text_label_view = True
        self.ellipse_color = 'Blue'
        self.mz_leder = []
        self.leder_rect = {}
        self.window = 2
        self.local_mz_list = []

        self.figure = go.Figure()
        self.reduce_data()
        self.proj_x_data = self.get_x_proj_data()
        self.proj_y_data = self.get_y_proj_data()
        self.init_draw()

        self.current_relayout = {}


    def get_max_intens_on_x(self, relayout={}):
        if 'xaxis.range[0]' in list(relayout.keys()):
            conditions = ((self.proj_x_data['x'] >= relayout['xaxis.range[0]'])&
                          (self.proj_x_data['x'] <= relayout['xaxis.range[1]']))
            df = self.proj_x_data[conditions]
            return df['intens'].max()
        else:
            return self.proj_x_data['intens'].max()

    def get_max_intens_on_y(self, relayout={}):
        if 'xaxis.range[0]' in list(relayout.keys()):
            conditions = ((self.proj_y_data['y'] >= relayout['yaxis.range[0]']) &
                          (self.proj_y_data['y'] <= relayout['yaxis.range[1]']))
            df = self.proj_y_data[conditions]
            return df['intens'].max()
        else:
            return self.proj_y_data['intens'].max()

    def get_x_proj_data(self):
        x_uniq = list(self.show_data['x'].unique())
        out = {'x': [], 'intens': []}
        for x in x_uniq:
            intens = self.show_data[self.show_data['x'] == x]['z'].sum()
            out['x'].append(x)
            out['intens'].append(intens)
        df = pd.DataFrame(out)
        df.sort_values(by='x', ascending=True, inplace=True)
        return df

    def get_y_proj_data(self):
        self.show_data['round_y'] = round(self.show_data['y'], 1)
        y_uniq = list(self.show_data['round_y'].unique())
            #y_uniq = list(y_uniq.unique())
        out = {'y': [], 'intens': []}
        for y in y_uniq:
            intens = self.show_data[self.show_data['round_y'] == y]['z'].sum()
            out['y'].append(y)
            out['intens'].append(intens)
        df = pd.DataFrame(out)
        df.sort_values(by='y', ascending=True, inplace=True)
        return df

    def set_data(self, data_x, data_y, data_z):
        self.data = pd.DataFrame()
        self.data['x'] = data_x
        self.data['y'] = data_y
        self.data['z'] = data_z

        self.reduce_data()
        self.proj_x_data = self.get_x_proj_data()
        self.proj_y_data = self.get_y_proj_data()
        self.init_draw()

    def reduce_data(self):
        if self.data.shape[0] > self.reduce_data_treshold:
            shift = int(round(self.data.shape[0] / self.reduce_data_treshold, 0))
        else:
            self.show_data = self.data.copy()
            return None
        reduced = {'x': [], 'y': [], 'z': []}
        rt_list = sorted(list(self.data['x'].unique()))
        index = 0
        while True:
            if index > len(rt_list) - 1:
                break
            df = self.data[self.data['x'] == rt_list[index]]
            reduced['y'].extend(df['y'])
            reduced['z'].extend(df['z'])
            reduced['x'].extend(np.zeros(df['y'].shape[0]) + rt_list[index])
            index += shift

        self.show_data = pd.DataFrame(reduced)

    def set_ellipse_color(self, is_red=True):
        if is_red:
            self.ellipse_color = 'Red'
        else:
            self.ellipse_color = 'Blue'

    def init_draw(self, relayout={}, tags=[]):

        self.figure.data = []
        self.figure.layout = {}

        self.figure = make_subplots(rows=2, cols=2, row_heights=[3, 1], column_widths=[4, 1])

        self.scatter = go.Scattergl(x=self.show_data['x'], y=self.show_data['y'],
                                    mode='markers',
                                    marker=dict(size=3, color='green', line=dict(width=0)))

        self.show_data.sort_values(by='x', ascending=True, inplace=True)
        self.x_proj = go.Scattergl(x=self.proj_x_data['x'], y=self.proj_x_data['intens'], mode='lines')

        self.show_data.sort_values(by='y', ascending=True, inplace=True)
        self.y_proj = go.Scattergl(x=self.proj_y_data['intens'], y=self.proj_y_data['y'], mode='lines')

        self.figure.add_trace(self.scatter, row=1, col=1)
        self.figure.add_trace(self.x_proj, row=2, col=1)
        self.figure.add_trace(self.y_proj, row=1, col=2)

        if self.leder_rect != {}:
            for row in self.mz_leder:
                self.figure.add_shape(
                    type="circle",
                    xref="x", yref="y",
                    x0=self.leder_rect['rt_min'], y0=row['mz'] - self.window,
                    x1=self.leder_rect['rt_max'], y1=row['mz'] + self.window,
                    opacity=0.4,
                    fillcolor='red',
                    line_color='red',
                    )

        if self.local_mz_list != []:
            x_left = self.leder_rect['rt_min']
            x_right = self.leder_rect['rt_max']
            for row in self.local_mz_list:

                exp_mz, t_mz = row['exp mz'], row['teor mz']
                if abs(exp_mz - t_mz) <= 1 and exp_mz != -1:
                    color = 'blue'
                else:
                    color = 'red'

                self.figure.add_trace(go.Scatter(
                    x=[x_left],
                    y=[exp_mz],
                    marker=dict(size=10, symbol="arrow-right", color=color, line=dict(width=0)),
                ))
                self.figure.add_trace(go.Scatter(
                    x=[x_right],
                    y=[exp_mz],
                    marker=dict(size=10, symbol="arrow-left", color=color, line=dict(width=0)),
                ))
                """
                self.figure.add_shape(
                    type="rect",
                    xref="x", yref="y",
                    x0=self.leder_rect['rt_min'] + 10, y0=mz - 5,
                    x1=self.leder_rect['rt_max'] - 10, y1=mz + 5,
                    opacity=0.4,
                    fillcolor='black',
                    line_color='black',
                )
                """

        for tag in tags:
            self.figure.add_shape(
                type="circle",
                xref="x", yref="y",
                x0=tag['rt min'], y0=tag['min mass'],
                x1=tag['rt max'], y1=tag['max mass'],
                opacity=0.4,
                fillcolor=self.ellipse_color,
                line_color=self.ellipse_color,
            )

            if self.control_text_label_view:
                tag_area = round(tag['area%'], 1)
                self.figure.add_annotation(x=tag['rt max'], y=tag['avg mass'],
                                           text=f"<b>{tag['tag name']}</b>",
                                           showarrow=False,
                                           yshift=20,
                                           xshift=-abs(tag['rt max'] - tag['rt min'])-5,
                                           #arrowhead=1,
                                           # align="center",
                                           ax=0,
                                           ay=0,
                                           font=dict(
                                               family="Courier New, monospace",
                                               size=14,
                                               color="#000000"
                                           ),
                                           )

                """
                self.figure.add_annotation(x=tag['rt max'], y=tag['avg mass'],
                                            text=f"<b>({tag_area}%)</b>",
                                            showarrow=False,
                                            yshift=-15,
                                       #arrowhead=1,
                                       # align="center",
                                            ax=0,
                                            ay=0,
                                            font=dict(
                                                family="Courier New, monospace",
                                                size=14,
                                                color="#ff0000"
                                                ),
                                            )
                """

        self.figure.update_traces()

        if 'xaxis.range[0]' in list(relayout.keys()):
            self.figure.update_layout(
            title=self.title,
            width=self.figure_width,
            height=self.figure_height,
            yaxis_title=self.y_label,
            xaxis3=dict(title=self.x_label),
            showlegend=False,
            xaxis_range=[relayout['xaxis.range[0]'], relayout['xaxis.range[1]']],
            yaxis_range=[relayout['yaxis.range[0]'], relayout['yaxis.range[1]']],
            xaxis3_range=[relayout['xaxis.range[0]'], relayout['xaxis.range[1]']],
            yaxis3_range=[0, self.get_max_intens_on_x(relayout)],
            yaxis2_range=[relayout['yaxis.range[0]'], relayout['yaxis.range[1]']],
            xaxis2_range=[0, self.get_max_intens_on_y(relayout)]
        )
        else:
            self.figure.update_layout(
                title=self.title,
                width=self.figure_width,
                height=self.figure_height,
                yaxis_title=self.y_label,
                xaxis3=dict(title=self.x_label),
                showlegend=False
            )

    def draw_select_tag(self, tag):
        self.figure.data = []
        self.figure.layout = {}

        self.scatter = go.Scattergl(x=self.show_data['x'], y=self.show_data['y'],
                                    mode='markers',
                                    marker=dict(size=3, color='green', line=dict(width=0)))

        self.figure.add_trace(self.scatter)
        self.figure.add_shape(
            type="circle",
            xref="x", yref="y",
            x0=tag['rt min'], y0=tag['min mass'],
            x1=tag['rt max'], y1=tag['max mass'],
            opacity=0.4,
            fillcolor=self.ellipse_color,
            line_color=self.ellipse_color,
        )

        self.figure.add_annotation(x=tag['rt max'], y=tag['avg mass'],
                            text=f"<b>{tag['tag name']} ({tag['area%']}%)</b>",
                            showarrow=True,
                            arrowhead=1,
                            align="center",
                            ax=30,
                            ay=0,
                            font=dict(
                                        family="Courier New, monospace",
                                        size=14,
                                        color="#ff0000",

                                   ),
                                   )

        self.figure.update_traces()
        self.figure.update_layout(
            title=self.title,
            width=self.figure_width,
            height=self.figure_height,
            xaxis_title=self.x_label,
            yaxis_title=self.y_label,
            showlegend=False)

    def draw_all_tags(self, tags):
            self.figure.data = []
            self.figure.layout = {}

            self.scatter = go.Scattergl(x=self.show_data['x'], y=self.show_data['y'],
                                        mode='markers',
                                        marker=dict(size=3, color='green', line=dict(width=0)))

            self.figure.add_trace(self.scatter)

            for tag in tags:
                self.figure.add_shape(
                type="circle",
                xref="x", yref="y",
                x0=tag['rt min'], y0=tag['min mass'],
                x1=tag['rt max'], y1=tag['max mass'],
                opacity=0.4,
                fillcolor="blue",
                line_color="blue",
            )

                self.figure.add_annotation(x=tag['rt max'], y=tag['avg mass'],
                                            text=f"<b>{tag['tag name']} ({tag['area%']}%)</b>",
                                            showarrow=True,
                                            arrowhead=1,
                                            #align="center",
                                            ax=30,
                                            ay=0,
                                            font=dict(
                                                family="Courier New, monospace",
                                                size=14,
                                                color="#ff0000"
                                           ),
                                           #bordercolor="#c7c7c7",
                                           #borderwidth=2,
                                           #borderpad=4,
                                           #bgcolor="#ff7f0e",
                                           #opacity=0.8
                                           )

            self.figure.update_traces()
            self.figure.update_layout(
                title=self.title,
                width=self.figure_width,
                height=self.figure_height,
                xaxis_title=self.x_label,
                yaxis_title=self.y_label,
                showlegend=False)