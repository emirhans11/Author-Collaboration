import dash
from dash import dcc, html
import plotly.graph_objects as go
import pandas as pd
import networkx as nx
import sys
import socket

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

    if is_port_in_use(port):
        print(f"Port {port} is already in use. Please use a different port.")
        sys.exit(1)

def run_collaboration_graph(file_path, port=8050):
    # Excel'den verileri oku
    data = pd.read_excel(file_path)

    # Veri işleme - coauthors sütununu doğru formatta işleme
    data["coauthors_list"] = data["coauthors"].apply(lambda x: eval(x) if isinstance(x, str) else [])

    # Graph oluştur ve kenarları ekle
    G = nx.Graph()  # Yönsüz graf
    author_names = {}  # Author ID'lerini ve isimlerini eşleştirmek için bir dictionary
    author_papers = {}  # Author ID'lerini ve yer aldığı makaleleri eşleştirmek için bir dictionary

    # Bağlantı ekleme işlemi
    for _, row in data.iterrows():
        author_id = row["orcid"]  # Yazarın ID'sini al
        author_name = row["author_name"]  # Yazarın ismini al
        coauthors_ids = row["coauthors_list"]  # Yazar arkadaşlarının ID'leri
        paper_title = row["paper_title"]  # Makale başlığını al
        author_names[author_id] = author_name  # Author ID'sini isme eşleştir

        # Makale bilgilerini yazar ID'sine göre kaydet
        if author_id not in author_papers:
            author_papers[author_id] = []
        author_papers[author_id].append(paper_title)

        # Yazarın kendisiyle olan bağlantıları ve tekrarlayanları engelleme
        for coauthor_id in set(coauthors_ids):
            if coauthor_id != author_id and (author_id, coauthor_id) not in G.edges:
                G.add_edge(author_id, coauthor_id, paper_title=paper_title)

    # Derece hesaplama
    degrees = {node: len(G[node]) for node in G.nodes()}

    # Node pozisyonlarını belirle
    pos = nx.spring_layout(G, seed=42)

    # Edge trace oluştur
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=0.7, color="rgba(255, 255, 255, 0.5)"),
        hoverinfo="none",
        mode="lines"
    )

    # Node trace oluştur
    node_x, node_y, node_degree = [], [], []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_degree.append(len(G[node]))  # Node'un derecesi

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers",
        hoverinfo="text",
        marker=dict(
            showscale=True,
            colorscale="YlGnBu",
            size=[degree + 8 for degree in node_degree],
            color=node_degree,
            colorbar=dict(
                thickness=20,
                title="Node Degree",
                xanchor="left",
                titleside="right",
                outlinewidth=0
            ),
            line=dict(width=1, color="black")
        )
    )

    # Node etiketleri ekle (İsim ve ID'ler)
    node_text = []
    for idx, node in enumerate(G.nodes()):
        node_name = author_names.get(node, str(node))
        node_text.append(f"<b>{node_name}</b><br>Degree: {node_degree[idx]}")
    node_trace.text = node_text

    # Dash uygulamasını oluştur
    app = dash.Dash(__name__)

    @app.callback(
        dash.dependencies.Output('author-details', 'children'),
        [dash.dependencies.Input('graph', 'clickData')]
    )
    def update_author_details(click_data):
        if click_data is None:
            return "Yazar bilgilerini görmek için bir düğüme tıklayın."

        # Tıklanan noktanın indeksini kullanarak node ID'yi alalım
        point_index = click_data['points'][0]['pointIndex']
        node_id = list(G.nodes())[point_index]  # Grafikteki sırasına göre node ID'sini alın

        # Yazar ismi ve makale bilgilerini alın
        author_name = author_names.get(node_id, None)
        if author_name is None:
            return html.Div([html.H5(f"Yazar adı bulunamadı (ID: {node_id})")])

        papers = author_papers.get(node_id, ["Makale yok"])

        papers_list = "\n".join([f"- {paper}" for paper in papers])

        return html.Div([ 
            html.H5(f"Yazar: {author_name}"),
            html.P(f"Yazarın Yer Aldığı Makaleler:"),
            html.Pre(papers_list)
        ])

    # Dashboard düzeni
    app.layout = html.Div([ 
        html.Div([ 
            dcc.Graph( 
                id='graph',
                figure=go.Figure( 
                    data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title=dict(text="Yazarlar Arası Bağlantı Grafiği", x=0.5, font=dict(size=24)),
                        showlegend=False,
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        paper_bgcolor="black",
                        plot_bgcolor="rgba(0,0,0,0)",
                        height=800
                    )
                ),
                config={'scrollZoom': True}
            ),
        ], style={"width": "80%", "display": "inline-block"}),

        html.Div(id='author-details', style={"marginTop": "30px"})  # Çıktılar alt altta olacak şekilde
    ])

    # Dash uygulamasını çalıştır
    app.run_server(debug=True, port=port)

if __name__ == "__main__":

    file_path = sys.argv[1]
    port = int(sys.argv[2])

    # Port kontrolü
    try:
        run_collaboration_graph(file_path, port)
    except Exception as e:
        print(f"Dash server failed to start on port {port}: {e}")
