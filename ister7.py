from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QInputDialog, QLineEdit
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import networkx as nx


class LongestPathWindow(QMainWindow):
    def __init__(self, subgraph, longest_path, author, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"7. İster: {author} için En Uzun Yol")
        self.subgraph = subgraph  # Sadece en uzun yolun alt grafiği
        self.longest_path = longest_path
        self.author = author
        self.init_ui()

    def init_ui(self):
        # Pencere arayüzü oluşturma
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        # Matplotlib için Figure ve Canvas oluşturma
        figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(figure)
        layout.addWidget(self.canvas)

        # Matplotlib grafiği için eksen oluşturma
        self.ax = figure.add_subplot(111)
        self.draw_graph()

    def draw_graph(self):
        """Grafikte sadece en uzun yolu çizer."""
        self.ax.clear()

        # Düğümlerin düzenli bir yerleşimi için pozisyon hesapla
        pos = nx.spring_layout(self.subgraph, seed=42)

        # Sadece alt grafiği çiz
        nx.draw(
            self.subgraph, pos, ax=self.ax,
            with_labels=True,
            node_color="skyblue",
            edge_color="red",
            node_size=500,
            font_size=10
        )

        # Başlık ekle ve çizimi tamamla
        self.ax.set_title(f"{self.author} için En Uzun Yol", fontsize=14)
        self.canvas.draw()


def find_longest_path(graph, orcid_to_name, update_results, parent):
    """7. İster: Kullanıcıdan alınan yazar ID’sinden gidebileceği en uzun yolu bul ve sadece yolu göster."""
    try:
        # Kullanıcıdan ORCID ID'si alma
        orcid_id, ok = QInputDialog.getText(parent, "Yazar ORCID", "Lütfen bir yazarın ORCID ID'sini girin:", QLineEdit.Normal)
        if not ok or not orcid_id.strip():
            update_results("Geçerli bir ORCID ID'si girilmedi.")
            return

        # ORCID ID'sinden yazar adını bulma
        author = orcid_to_name.get(orcid_id.strip())
        if not author:
            update_results(f"ORCID ID '{orcid_id}' ile eşleşen bir yazar bulunamadı.")
            return

        # Grafikte yazarın varlığını kontrol etme
        if author not in graph:
            update_results(f"{author} grafikte bulunamadı.")
            return

        # En uzun yolu bulma
        longest_path = []
        for target in graph.nodes:
            if author != target:
                try:
                    # Kısa yolları hesapla ve en uzunu belirle
                    path = nx.shortest_path(graph, source=author, target=target)
                    if len(path) > len(longest_path):
                        longest_path = path
                except nx.NetworkXNoPath:
                    continue

        # Alt grafiği oluşturma
        if longest_path:
            edges = list(zip(longest_path, longest_path[1:]))
            subgraph = graph.edge_subgraph(edges).copy()  # Sadece en uzun yolun kenarlarını içeren alt grafik

            # Sonuçları göster ve pencereyi başlat
            result = f"7. İster: {author} yazarı için en uzun yol:\n\n{' -> '.join(longest_path)}"
            update_results(result)
            longest_path_window = LongestPathWindow(subgraph, longest_path, author, parent)
            longest_path_window.show()
        else:
            update_results(f"7. İster: {author} yazarı için bir yol bulunamadı.")
    except Exception as e:
        update_results(f"Hata oluştu: {str(e)}")
