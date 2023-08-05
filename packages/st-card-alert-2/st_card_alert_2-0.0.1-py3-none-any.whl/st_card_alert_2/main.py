from typing import Container
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from vega_datasets import data
import hydralit_components as hc

from matplotlib import cm
from matplotlib.patches import Circle, Wedge, Rectangle
import matplotlib.pyplot as plt
import datetime
from collections import Counter

import os
import streamlit.components.v1 as components

st.set_option('deprecation.showPyplotGlobalUse', False)

st.set_page_config(
     page_title="ATLAS Energy AI",
     page_icon="🧊",
     layout="wide",
     initial_sidebar_state="expanded",
     menu_items={
         'Get Help': 'https://www.extremelycoolapp.com/help',
         'Report a bug': "https://www.extremelycoolapp.com/bug",
         'About': "# This is a header. This is an *extremely* cool app!"
     }
 )

 


st.header('CrossnoKaye ATLAS Energy AI Platform')

option = st.selectbox(
     'Select Facility',
     ('Facility#1', 'Facility#2', 'Facility#3', 'Facility#4'))


# Header
with st.container():
    col_bar, col_card_1, col_card_2, col_card_3 = st.columns([4,1,1,1])
    with col_bar:
        st.subheader("Energy Savings Breakdown・Per Equipment")
    
    with col_card_1:
        st.subheader("Alert Activity")


# Top Panel
with st.container():

    col_bar, col_card_1, col_card_2, col_card_3 = st.columns([4,1,1,1])

    with col_bar:  
        data_mock_stacked_bar = pd.DataFrame(columns=['Saving','Type','Year','Instrument'])
        data_mock_stacked_bar['Saving'] = [0.55,0.25,0.10,0.06,0.04]
        data_mock_stacked_bar['Type'] = 'Energy Saving'
        data_mock_stacked_bar['Instrument'] = ['Compressors','Evaporators',
                                            'Condensers','Lighting','Other']

        # Stacked Bar Plot
        source = data_mock_stacked_bar

        bars = alt.Chart(source).mark_bar().encode(
            x=alt.X('sum(Saving):Q', stack='zero',axis=alt.Axis(format='%')),
            y=alt.Y('Type:N'),
            color=alt.Color('Instrument'),
            order=alt.Order(
            # Sort the segments of the bars by this field
            'Instrument',
            sort='ascending'
            )
        )

        text = alt.Chart(source).mark_text(dx=-10, dy=-40, color='white').encode(
            x=alt.X('sum(Saving):Q', stack='zero'),
            y=alt.Y('Type:N'),
            detail='Instrument:N',
            text=alt.Text('sum(Saving):Q', format=""),
            # text=alt.Text('Type:N', format=""),
            order=alt.Order(
            # Sort the segments of the bars by this field
            'Instrument',
            sort='ascending'
            )
        )

        # bars + text
        st.altair_chart(bars + text, use_container_width=True)



    # Top Right Panel

    #can apply customisation to almost all the properties of the card, including the progress bar
    theme_bad = {'bgcolor': '#FFF0F0','title_color': 'red','content_color': 'red','icon_color': 'red', 'icon': 'fa fa-times-circle'}
    theme_neutral = {'bgcolor': '#f9f9f9','title_color': 'orange','content_color': 'orange','icon_color': 'orange', 'icon': 'fa fa-question-circle'}
    theme_good = {'bgcolor': '#EFF8F7','title_color': 'green','content_color': 'green','icon_color': 'green', 'icon': 'fa fa-check-circle'}
    theme_caution = {'bgcolor': '#2e2e2e','title_color': 'white','content_color': 'gray','icon_color': 'yellow', 'icon': 'fa fa-exclamation-triangle'}
    theme_warning = {'bgcolor': '#2e2e2e','title_color': 'white','content_color': 'gray','icon_color': 'orange', 'icon': 'fa fa-exclamation-triangle'}
    theme_critical = {'bgcolor': '#2e2e2e','title_color': 'white','content_color': 'gray','icon_color': 'red', 'icon': 'fa fa-bell'}
    with col_card_1:
        hc.info_card(title='771', content='Q1 2021 Caution Alerts',bar_value=20,theme_override=theme_caution)
        hc.info_card(title='605', content='Q1 2022 Caution Alerts',bar_value=20,theme_override=theme_caution)

    with col_card_2:
        hc.info_card(title='175', content='Q1 2021 Warning Alerts',bar_value=20,theme_override=theme_warning)
        hc.info_card(title='141', content='Q1 2022 Warning Alerts',bar_value=20,theme_override=theme_warning)

    with col_card_3:
        hc.info_card(title='78', content='Q1 2021 Critical Alerts',bar_value=20,theme_override=theme_critical)
        hc.info_card(title='71', content='Q1 2022 Critical Alerts',bar_value=20,theme_override=theme_critical)




# Middle Panel

# Define gauge
def degree_range(n):
    start = np.linspace(0, 180, n + 1, endpoint=True)[0:-1]
    end = np.linspace(0, 180, n + 1, endpoint=True)[1::]
    mid_points = start + ((end - start) / 2.)
    return np.c_[start, end], mid_points


def rot_text(ang):
    rotation = np.degrees(np.radians(ang) * np.pi / np.pi - np.radians(90))
    return rotation


def gauge(avg_value,
          labels=['LOW', 'MEDIUM', 'HIGH', 'VERY HIGH', 'EXTREME'],
          quarter = '(Q1) 2022',
          colors='jet_r', arrow=1, title='', fname=False):


    N = len(labels)

    if arrow > N:
        raise Exception("\n\nThe category ({}) is greated than \
        the length\nof the labels ({})".format(arrow, N))


    if isinstance(colors, str):
        cmap = cm.get_cmap(colors, N)
        cmap = cmap(np.arange(N))
        colors = cmap[::-1, :].tolist()
    if isinstance(colors, list):
        if len(colors) == N:
            colors = colors[::-1]
        else:
            raise Exception("\n\nnumber of colors {} not equal \
            to number of categories{}\n".format(len(colors), N))


    fig, ax = plt.subplots()
    fig.patch.set_facecolor('#0f1116')
    

    ang_range, mid_points = degree_range(N)

    labels = labels[::-1]

    patches = []
    for ang, c in zip(ang_range, colors):
        # sectors
        patches.append(Wedge((0.,0.), .4, *ang, facecolor='#0f1116', lw=2))
        # arcs
        patches.append(Wedge((0., 0.), .4, *ang, width=0.10, facecolor=c, lw=2, alpha=1))

    foo = [ax.add_patch(p) for p in patches]


    for mid, lab in zip(mid_points, labels):
        ax.text(0.35 * np.cos(np.radians(mid)), 0.35 * np.sin(np.radians(mid)), lab, \
                horizontalalignment='center', verticalalignment='center', fontsize=14, \
                fontweight='bold', rotation=rot_text(mid))

    r = Rectangle((-0.4, -0.1), 0.8, 0.1, facecolor='#0f1116', lw=2)
    ax.add_patch(r)

    ax.text(0, -0.05, title, horizontalalignment='center', \
            verticalalignment='center', fontsize=22, fontweight='bold',color='w')
    ax.text(0, -0.1, 'Avg. for '+ quarter, horizontalalignment='center', \
            verticalalignment='center', fontsize=12, fontweight='bold',color='gray',alpha=0.9)
    ax.text(-0.05, -0.18, avg_value, horizontalalignment='center', \
            verticalalignment='center', fontsize=36, fontweight='bold',color='w')
    if title in ['Compressor Efficiency','Evaporator Efficiency','Condenser Efficiency']:
        ax.text(0.06, -0.185, "COP", horizontalalignment='center', \
                verticalalignment='center', fontsize=18, fontweight='bold',color='gray')
    elif title == "Ammonia Level":
        ax.text(0.08, -0.185, "LBS", horizontalalignment='center', \
                verticalalignment='center', fontsize=18, fontweight='bold',color='gray')
    elif title == "Overall Health Facility":
        ax.text(0.18, -0.185, "Above Avg.", horizontalalignment='center', \
                verticalalignment='center', fontsize=18, fontweight='bold',color='gray')


    pos = mid_points[abs(arrow - N)]

    ax.arrow(0, 0, 0.225 * np.cos(np.radians(pos)), 0.225 * np.sin(np.radians(pos)), \
             width=0.04, head_width=0.09, head_length=0.1, fc='w', ec='w')

    ax.add_patch(Circle((0, 0), radius=0.02, facecolor='white'))
    ax.add_patch(Circle((0, 0), radius=0.01, facecolor='k', zorder=11))
    plt.title("Equipment Health", fontsize = 20)
    ax.set_frame_on(False)
    ax.axes.set_xticks([])
    ax.axes.set_yticks([])
    ax.axis('equal')
    plt.tight_layout()
    if fname:
        fig.savefig(fname, dpi=200)

with st.container():
    st.header("Equipment Health")

    col_1, col_2, col_3, col_4, col_5 = st.columns(5)

    with col_1:
        gauge(avg_value = 1.5,
              labels=['VERY LOW', 'LOW', 'MEDIUM', 'HIGH'],
              quarter = '(Q1) 2022',
              colors=["#ff0d38", "orange", '#ffc600', '#05cb04'], arrow=4, title="Compressor Efficiency")
        st.pyplot()
    with col_2:
        gauge(avg_value = "1.5",
              labels=['VERY LOW', 'LOW', 'MEDIUM', 'HIGH'],
              quarter = '(Q1) 2022',
              colors=["#ff0d38", "orange", '#ffc600', '#05cb04'], arrow=4, title="Evaporator Efficiency")
        st.pyplot()
    with col_3:
        gauge(avg_value = "1.5",
              labels=['VERY LOW', 'LOW', 'MEDIUM', 'HIGH'],
              quarter = '(Q1) 2022',
              colors=["#ff0d38", "orange", '#ffc600', '#05cb04'], arrow=4, title="Condenser Efficiency")
        st.pyplot()
    with col_4:
        gauge(avg_value = "15K",
              labels=['VERY LOW', 'LOW', 'MEDIUM', 'HIGH'],
              quarter = '(Q1) 2022',
              colors=["#ff0d38", "orange", '#ffc600', '#05cb04'], arrow=1, title="Ammonia Level")
        st.pyplot()
    with col_5:
        gauge(avg_value = "+0.5",
              labels=['VERY LOW', 'LOW', 'MEDIUM', 'HIGH'],
              quarter = '(Q1) 2022',
              colors=["#ff0d38", "orange", '#ffc600', '#05cb04'], arrow=2, title="Overall Health Facility")
        st.pyplot()

# Bottom Panel

with st.container():
    st.write('Bottom')
    col_1, col_2 = st.columns([3,1])

    with col_1:
        data_line = pd.DataFrame(np.random.randn(50, 1),columns=['2021'])
        data_line['2021'] = data_line['2021'].values*200+400
        data_line = data_line.reset_index()
        line_chart_2021 = alt.Chart(data_line).mark_line().encode(
            x=alt.X('index',title=''),
            y=alt.Y('2021',title='(kW)'),
        #     color='Instrument',
        #     strokeDash='Instrument',
            color=alt.value("#86df05")
        )

        st.altair_chart(line_chart_2021, use_container_width=True)

    with col_2:
        # Altair Line Chart
        df1 = data.stocks().copy()
        df1 = df1[df1['symbol'].isin(['AAPL','AMZN','IBM'])]
        df1['price'] = df1.iloc[::-1]['price'].values

        df2 = pd.DataFrame()
        for i in ['AAPL','AMZN','IBM']:
            temp = df1[df1['symbol']==i].copy()
            temp['date'] = pd.to_datetime(pd.date_range(start='2021-01-01', end='2021-12-31',
                                                        periods=len(temp)))
            df2 = pd.concat([df2,temp], axis=0)


        df2.columns=['Year','Month','Energy']
        df2['Year'] = df2['Year'].replace({'AAPL':'2021','AMZN':'2022','IBM':'2023'})

        dom = ['2021','2022','2023']
        rng = ['#96ff00','#00e100','#009300']

        line_chart_yoy = alt.Chart(df2).mark_line().encode(
            x=alt.X('Month', axis=alt.Axis(format='%b')),
            y='Energy',
            # color='Year',
            color=alt.Color('Year', scale=alt.Scale(domain=dom, range=rng)),
            # strokeDash='Year',
            
        )
        
        st.altair_chart(line_chart_yoy, use_container_width=True)




# Test Component
_RELEASE = False

# Declare a Streamlit component. `declare_component` returns a function
# that is used to create instances of the component. We're naming this
# function "_component_func", with an underscore prefix, because we don't want
# to expose it directly to users. Instead, we will create a custom wrapper
# function, below, that will serve as our component's public API.

# It's worth noting that this call to `declare_component` is the
# *only thing* you need to do to create the binding between Streamlit and
# your component frontend. Everything else we do in this file is simply a
# best practice.

if not _RELEASE:
    _component_func = components.declare_component(
        # We give the component a simple, descriptive name ("st_card_component"
        # does not fit this bill, so please choose something better for your
        # own component :)
        "st_card_component",
        # Pass `url` here to tell Streamlit that the component will be served
        # by the local dev server that you run via `npm run start`.
        # (This is useful while your component is in development.)
        url="http://localhost:3001",
    )
else:
    # When we're distributing a production version of the component, we'll
    # replace the `url` param with `path`, and point it to to the component's
    # build directory:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("st_card_component", path=build_dir)


# Create a wrapper function for the component. This is an optional
# best practice - we could simply expose the component function returned by
# `declare_component` and call it done. The wrapper allows us to customize
# our component's API: we can pre-process its input args, post-process its
# output value, and add a docstring for users.
def st_card_component(title, subtitle, body, type):
    """Create a new instance of "card_component".
    """
    # the below initializes the react component (in CardComponent.tsx)
    _ = _component_func(
        title=title,
        subtitle=subtitle,
        body=body,
        type=type
    )


# Add some test code to play with the component while it's in development.
# During development, we can run this just as we would any other Streamlit
# app: `$ streamlit run st_card_component/__init__.py`
if not _RELEASE:
    import streamlit as st

    st.subheader("Component test")

    st.markdown("---")

    # Header
    with st.container():
        col_bar, col_card_1, col_card_2, col_card_3 = st.columns([4,1,1,1])
        with col_bar:
            st.subheader("Energy Savings Breakdown・Per Equipment")
        
        with col_card_1:
            st.subheader("Alert Activity")


    # Top Panel
    with st.container():

        col_bar, col_card_1, col_card_2, col_card_3 = st.columns([4,1,1,1])

        with col_bar:  
            data_mock_stacked_bar = pd.DataFrame(columns=['Saving','Type','Year','Instrument'])
            data_mock_stacked_bar['Saving'] = [0.55,0.25,0.10,0.06,0.04]
            data_mock_stacked_bar['Type'] = 'Energy Saving'
            data_mock_stacked_bar['Instrument'] = ['Compressors','Evaporators',
                                                'Condensers','Lighting','Other']

            # Stacked Bar Plot
            source = data_mock_stacked_bar

            bars = alt.Chart(source).mark_bar().encode(
                x=alt.X('sum(Saving):Q', stack='zero',axis=alt.Axis(format='%')),
                y=alt.Y('Type:N'),
                color=alt.Color('Instrument'),
                order=alt.Order(
                # Sort the segments of the bars by this field
                'Instrument',
                sort='ascending'
                )
            )

            text = alt.Chart(source).mark_text(dx=-10, dy=-40, color='white').encode(
                x=alt.X('sum(Saving):Q', stack='zero'),
                y=alt.Y('Type:N'),
                detail='Instrument:N',
                text=alt.Text('sum(Saving):Q', format=""),
                # text=alt.Text('Type:N', format=""),
                order=alt.Order(
                # Sort the segments of the bars by this field
                'Instrument',
                sort='ascending'
                )
            )

            # bars + text
            st.altair_chart(bars + text, use_container_width=True)



        # Top Right Panel

        with col_card_1:
            st_card_component(title="771",
                          subtitle = "TOTAL",
                          body = 'Q1 2021 Caution Alerts',
                          type='Caution')
            st_card_component(title="605",
                          subtitle = "TOTAL",
                          body = 'Q1 2022 Caution Alerts',
                          type='Caution')

        with col_card_2:
            st_card_component(title="175",
                          subtitle = "TOTAL",
                          body = 'Q1 2021 Warning Alerts',
                          type='Warning')
            st_card_component(title="141",
                          subtitle = "TOTAL",
                          body = 'Q1 2022 Warning Alerts',
                          type='Warning')

        with col_card_3:
            st_card_component(title="78",
                          subtitle = "TOTAL",
                          body = 'Q1 2021 Critical Alerts',
                          type='Critical')
            st_card_component(title="71",
                          subtitle = "TOTAL",
                          body = 'Q1 2022 Critical Alerts',
                          type='Critical')