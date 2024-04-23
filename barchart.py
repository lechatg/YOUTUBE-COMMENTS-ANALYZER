import plotly.graph_objects as go
import numpy as np

# Generate a bar chart with 10 topics that are most frequent in comments
def make_top10_bar(topics_info, len_docs):
    
    # Take df from row #1 because I don't need "Undistibuted" comments on this barchart
    y_count = []
    for y in topics_info["Count"][1:]:
        y_new = (y/len_docs) * 100
        y_count.append(y_new)

    x = topics_info["Name_for_barchart"][1:]
    
    fig = go.Figure(go.Bar(
        x=y_count,
        y=x,
        marker=dict(
            color = y_count,
            colorscale = [(0,"rgb(137, 205, 205)"), (1,"rgb(146, 71, 173)")],
            line=dict(
                color='AliceBlue',
                width=1),
        ),
        name = 'Percentage of all comments for this video',
        orientation='h',
        showlegend=True,
    ))

    fig.update_layout(
        # title = dict(
        #     text = '<b>Top 10 topics discussed in comments</b>',
        #     x = 0.5, 
        #     font=dict(size=18, color = 'white')
        # ),
        yaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=True,
            domain=[0, 1],

        ),
        xaxis=dict(
            griddash = "dot",
            zeroline=True,
            showline=False,
            showticklabels=True,
            showgrid=True,
            domain=[0, 1],
        ),
        legend=dict(x=-0.1, y=-0.12, font_size=14, font_color = 'white'),
        margin=dict(l=100, r=20, t=40, b=70),
        paper_bgcolor = 'rgb(12, 67, 98)',
        plot_bgcolor='rgb(12, 67, 98)'
    )

    annotations = []

    y_s = np.round(y_count, decimals=1)

    # Adding labels
    for yd, xd in zip(y_s, x):

        annotations.append(dict(xref='x1', yref='y1',
                                y=xd, x=yd + 0.7,
                                text=str(yd) + '%',
                                font=dict(family='Arial', size=14,
                                        color='white'),
                                showarrow=False))

    fig.update_layout(annotations=annotations)

    # Sort plot from highest to lowest
    fig.update_layout(barmode='stack', yaxis={'categoryorder':'total ascending'})
    
    # Move labels from Y-axis a little bit and add % to values on X-axis
    fig.update_yaxes(ticksuffix = "   ", tickfont=dict(color = 'white', family = 'Arial', size=18))
    fig.update_xaxes(ticksuffix = "%", tickfont=dict(color = 'white'))

    fig.update_layout(width = 1000, height = 620)
    # fig.show()

    return fig
