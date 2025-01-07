import plotly.graph_objects as go
import networkx as nx

def create_plotly_graph(G, orcid_to_name):
    """NetworkX grafiğini Plotly grafiğine dönüştürür."""
    pos = nx.spring_layout(G)

    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=0.5, color="rgba(200,200,255,0.5)"),
        hoverinfo="none",
        mode="lines"
    )

    node_x, node_y, node_degree = [], [], []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_degree.append(len(G[node]))

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers",
        hoverinfo="text",
        marker=dict(
            showscale=True,
            colorscale="Viridis",
            size=[degree + 7 for degree in node_degree],
            color=node_degree,
            colorbar=dict(
                thickness=20,
                title="Node Degree",
                xanchor="left",
                titleside="right",
                outlinewidth=0
            )
        )
    )

    node_text = []
    for node, degree in zip(G.nodes(), node_degree):
        node_name = orcid_to_name.get(node, str(node))
        node_text.append(f"<b>{node_name}</b><br>Degree: {degree}")
    node_trace.text = node_text

    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title=dict(text="<b>Collaboration Graph</b>", x=0.5, font=dict(size=22, color="white")),
            showlegend=False,
            hovermode="closest",
            margin=dict(b=0, l=0, r=0, t=50),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            paper_bgcolor="black",
            plot_bgcolor="rgba(0,0,0,0)"
        )
    )
    return fig
