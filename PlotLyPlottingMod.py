# coding: utf-8
from plotly import __version__
from plotly.offline import download_plotlyjs, init_notebook_mode, iplot
from plotly.offline import plot
from plotly.graph_objs import Scatter

import plotly as py
import pandas as pd
from plotly import session, tools, utils
import uuid
import json
from plotly import tools
import plotly.graph_objs as go

init_notebook_mode() 

import LHCclass
import madxmodule
import pandas as pd
import numpy as np
import matplotlib
from matplotlib import pyplot as plt
import csv
import glob
import datetime
import collections
import time
import subprocess
import os
from scipy import optimize as opt
from scipy import constants as const
from StringIO import StringIO
from matplotlib import rc,rcParams
from matplotlib.patches import Rectangle
import itertools

# simdata
from pandas.tools.plotting import autocorrelation_plot
from pandas.tools.plotting import lag_plot
from pandas.tools.plotting import scatter_matrix

# function definitions
# ********************

# -----------------------------------------------------------------------------------------------------
# plotly javascript 
# loading of the javascript 
# -----------------------------------------------------------------------------------------------------
def get_plotlyjs():
    path = os.path.join('plotly.min.js')
    plotlyjs = resource_string('plotly', path).decode('utf-8')
    return plotlyjs

# -----------------------------------------------------------------------------------------------------
# plotly offline plotting function 
# allows to generate offline plots wiht plotly
# -----------------------------------------------------------------------------------------------------
def new_iplot(figure_or_data, show_link=True, link_text='Export to plot.ly',validate=True):

    figure = tools.return_figure_from_figure_or_data(figure_or_data, validate)

    width  = figure.get('layout', {}).get('width', '100%')
    height = figure.get('layout', {}).get('height', 525)
    
    try:
        float(width)
    except (ValueError, TypeError):
        pass
    else:
        width = str(width) + 'px'

    try:
        float(width)
    except (ValueError, TypeError):
        pass
    else:
        width = str(width) + 'px'

    plotdivid = uuid.uuid4()
    jdata     = json.dumps(figure.get('data', []), cls=utils.PlotlyJSONEncoder)
    jlayout   = json.dumps(figure.get('layout', {}), cls=utils.PlotlyJSONEncoder)

    config = {}
    config['showLink'] = show_link
    config['linkText'] = link_text
    jconfig            = json.dumps(config)

    plotly_platform_url = session.get_session_config().get('plotly_domain',
                                                           'https://plot.ly')
    if (plotly_platform_url != 'https://plot.ly' and
            link_text == 'Export to plot.ly'):

        link_domain = plotly_platform_url            .replace('https://', '')            .replace('http://', '')
        link_text = link_text.replace('plot.ly', link_domain)


    script = '\n'.join([
        'Plotly.plot("{id}", {data}, {layout}, {config}).then(function() {{',
        '    $(".{id}.loading").remove();',
        '}})'
    ]).format(id=plotdivid,
              data=jdata,
              layout=jlayout,
              config=jconfig)

    html="""<div class="{id} loading" style="color: rgb(50,50,50);">
                 </div>
                 <div id="{id}" style="height: {height}; width: {width};" 
                 class="plotly-graph-div">
                 </div>
                 <script type="text/javascript">
                 {script}
                 </script>
                 """.format(id=plotdivid, script=script,
                           height=height, width=width)

    return html

# -----------------------------------------------------------------------------------------------------
# plotly layout template
# defines a layout template to use with plotly plotting
# returs basically a dictionary but can be a nested dictionary
# -----------------------------------------------------------------------------------------------------
def layouttemplate(
    titlein     = '',
    titlefontin =  dict(
                        family = 'Arial, sans-serif',
                        size = 16,
                        color = 'black'
                    ),
    widthin     = 0,
    heightin    = 0,
    xaxisdc     = dict(
                    title         = '',
                    titlefont     = dict(
                                        family = 'Arial, sans-serif',
                                        size = 16,
                                        color = 'black'
                                         ),
                    range          = [-1600,1600],
                    linewidth      = 4,
                    gridwidth      = 2,
#                   gridcolor      = 'rgb(140,140,140)',
                    autotick       = False,
                    ticks          = 'outside',
                    tick0          = 0,   # location of first tick
                    dtick          = 100, # distance between ticks
                    ticklen        = 10,  # length of the tick line
                    tickwidth      = 0.5, # width of the tick line
                    tickcolor      = '#000',
                    tickangle      = 0,
                    showticklabels = True,
                    tickfont       = dict(
                                        family = 'Arial, sans-serif',
                                        size = 12,
                                        color = 'black'
                                        ),
                    zeroline       = True,
                    zerolinewidth  = 2
#                     showgrid=True
                ),
    yaxisdc   = dict(
                    title         = '',
                    titlefont     = dict(
                                        family = 'Arial, sans-serif',
                                        size = 16,
                                        color = 'black'
                                         ),
                    range          = [-1600,1600],
                    linewidth      = 4,
                    gridwidth      = 2,
#                   gridcolor      = 'rgb(140,140,140)',
                    autotick       = False,
                    ticks          = 'outside',
                    tick0          = 0,   # location of first tick
                    dtick          = 100, # distance between ticks
                    ticklen        = 10,  # length of the tick line
                    tickwidth      = 0.5, # width of the tick line
                    tickcolor      = '#000',
                    tickangle      = 0,
                    showticklabels = True,
                    tickfont       = dict(
                                        family = 'Arial, sans-serif',
                                        size = 12,
                                        color = 'black'
                                        ),
                    zeroline       = True,
                    zerolinewidth  = 2
#                     showgrid=True
                ),
    shapeslst = []
                 ):
    
    try:
        float(widthin)
    except (ValueError, TypeError):
        pas

    try:
        float(heightin)
    except (ValueError, TypeError):
        pass
    if ((widthin > 0) & (heightin > 0)):
        layout = go.Layout(
                title     = titlein,
                titlefont = titlefontin,
                autosize  = False,
                width = widthin,
                height= heightin,
                xaxis= xaxisdc,
                yaxis= yaxisdc,
                shapes = shapeslst
                )
    else:
         layout = go.Layout(
                title     = titlein,
                titlefont = titlefontin,
                autosize  = True,
                xaxis= xaxisdc,
                yaxis= yaxisdc,
                shapes = shapeslst
                )
    return layout

# -----------------------------------------------------------------------------------------------------
# transforming data to be plotted with plotly
# basically returns a list of traces from the input data that can be plotted using plotly plot or iplot
# and the above defined new_iplot
# -----------------------------------------------------------------------------------------------------
def tracelist(xlist,ylist,legendname=None,hovertext=None,setmode='scatter',hover=True):
    trace = {
        'x'         : xlist,
        'y'         : ylist,
        'mode'      : setmode,
        'name'      : legendname,
        'text'      : hovertext,
        'hoverinfo' : hover
        }
    return trace

# -----------------------------------------------------------------------------------------------------
# reading twiss outfile *.tfs
# function that removes the headers from the tfs file and returns a dataframe containing only the data
# -----------------------------------------------------------------------------------------------------
def readtfs(tfsfile):
    df = pd.read_csv(tfsfile,skiprows=range(45),nrows=2,delim_whitespace=True)
    df = df[df['NAME']!='%s']
    colsdf = list(df.columns[1:])
    df = pd.read_csv(tfsfile,skiprows=range(47),delim_whitespace=True,names=colsdf,index_col=False)
    return df

# -----------------------------------------------------------------------------------------------------
# plotly shapes 
# definition of beamlinegraphic element rectangle for MB and MQ
# -----------------------------------------------------------------------------------------------------
def rectangledict(x0,y0,x1,y1,rgbcolorlinestr='rgb(10,10,10)',width=1,rgbfillcolor='rgb(100,250,250)'):
    out = {
        'type' : 'rect',
        'xref' : 'x',
        'yref' : 'y',
        'x0'   : x0,
        'y0'   : y0,
        'x1'   : x1,
        'y1'   : y1,
        'line' : {
            'color' : rgbcolorlinestr,
            'width' : width,
        },
        'fillcolor' : rgbfillcolor,
        'opacity' :0.9
    }
    return out

# -----------------------------------------------------------------------------------------------------
# plotly shapes 
# definition of beamlinegraphic element hoverinfo 
# ---------------------------------------------------------------------------------------------------
def shapeannotations(xin,yin,textin):
    out = go.Scatter(
        x = [xin],
        y = [yin],
        text = textin,
        mode = 'markers',
        opacity = 0,
        hoverinfo = 'text',
        showlegend=False
    )
    return out
