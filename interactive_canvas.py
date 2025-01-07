import networkx as nx
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class InteractiveCanvas(FigureCanvas):
    def __init__(self, graph, authors_to_papers, update_results_callback):
        self.graph = graph
        self.authors_to_papers = authors_to_papers
        self.update_results_callback = update_results_callback
        self.figure = Figure(figsize=(8, 6))
        self.ax = self.figure.add_subplot(111)
        super().__init__(self.figure)

        self.pos = nx.spring_layout(self.graph, seed=42)
        self.highlighted_node = None  # Fareyle üzerine gelinen düğüm
        self.clicked_node = None  # Tıklanan düğüm

        self.mpl_connect("motion_notify_event", self.on_hover)
        self.mpl_connect("button_press_event", self.on_click)
        self.mpl_connect("scroll_event", self.on_scroll)

        self.scale = 1.0  # Zoom ölçeği
        self.draw_graph()

    def draw_graph(self):
        """Grafiği çiz."""
        self.ax.clear()
        nx.draw(
            self.graph, self.pos, ax=self.ax,
            with_labels=False, node_color="skyblue",
            edge_color="gray", node_size=300, font_size=8
        )

        # Fareyle üzerine gelinen düğümü vurgula
        if self.highlighted_node:
            nx.draw_networkx_labels(
                self.graph, self.pos, ax=self.ax,
                labels={self.highlighted_node: self.highlighted_node},
                font_color="red", font_size=10
            )

        self.ax.set_title("İnteraktif Grafik", fontsize=14)
        self.figure.tight_layout()
        self.draw()

    def on_hover(self, event):
        """Fare hareketiyle düğüm üstüne gelindiğinde çalışır."""
        if event.inaxes == self.ax:
            for node, (x, y) in self.pos.items():
                if abs(event.xdata - x) < 0.03 and abs(event.ydata - y) < 0.03:  # Yakınlık kontrolü
                    self.highlighted_node = node
                    self.draw_graph()
                    return
        self.highlighted_node = None
        self.draw_graph()

    def on_click(self, event):
        """Fare tıklamasıyla düğüme tıklanıldığında çalışır."""
        if event.inaxes == self.ax:
            for node, (x, y) in self.pos.items():
                if abs(event.xdata - x) < 0.03 and abs(event.ydata - y) < 0.03:
                    self.clicked_node = node
                    papers = self.authors_to_papers.get(node, [])
                    papers_info = "\n".join([f"{paper['title']} ({paper['year']})" for paper in papers])
                    self.update_results_callback(f"Yazar: {node}\nMakaleler:\n{papers_info}")
                    return

    def on_scroll(self, event):
        """Fare kaydırmasıyla zoom işlemi."""
        zoom_factor = 1.1 if event.button == "up" else 1 / 1.1
        self.scale *= zoom_factor
        self.ax.set_xlim([x * self.scale for x in self.ax.get_xlim()])
        self.ax.set_ylim([y * self.scale for y in self.ax.get_ylim()])
        self.draw_graph()