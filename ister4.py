from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QInputDialog, QLineEdit, QTableWidget, QTableWidgetItem
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import networkx as nx
import matplotlib.cm as cm


class CollaborationPathsThread(QThread):
    paths_calculated = pyqtSignal(dict)  # İşbirlikçi yollar hesaplandığında sinyal gönder

    def __init__(self, graph, author, parent=None):
        super().__init__(parent)
        self.graph = graph
        self.author = author

    def run(self):
        # İşbirliği yollarını hesapla
        paths = nx.single_source_dijkstra_path(self.graph, source=self.author)
        self.paths_calculated.emit(paths)


class CollaborationPathsWindow(QMainWindow):
    def __init__(self, graph, paths, author, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"4. İster: {author} İşbirlikçi Yolları")
        self.graph = graph
        self.paths = paths
        self.author = author
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        # Matplotlib figure and canvas
        figure = Figure(figsize=(12, 10))
        self.canvas = FigureCanvas(figure)
        layout.addWidget(self.canvas)

        # Tablo widget'ı
        self.table_widget = QTableWidget(self)
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(["Hedef Düğüm", "Yol"])
        layout.addWidget(self.table_widget)

        self.ax = figure.add_subplot(111)
        self.canvas.mpl_connect('scroll_event', self.on_scroll)  # Zoom özelliği
        self.draw_graph()
        self.populate_table()

    def draw_graph(self):
        """Grafikte yolları çizer."""
        self.ax.clear()

        # Daha düzenli bir layout kullanımı
        pos = nx.spring_layout(self.graph, seed=42)  # Daha düzenli düğüm yerleşimi

        # Düğümleri ve kenarları çiz
        nx.draw(
            self.graph, pos, ax=self.ax,
            with_labels=True, node_size=1000, font_size=10,
            node_color="skyblue", edge_color="lightgray", width=1,
            font_weight='bold', font_color="black"
        )

        # Yolları kırmızıyla vurgula
        for target, path in self.paths.items():
            if len(path) > 1:
                edges = list(zip(path, path[1:]))
                nx.draw_networkx_edges(self.graph, pos, edgelist=edges, ax=self.ax, edge_color="red", width=2)

        # Yazar adlarını vurgulama: Burada aktif olan yazarı vurgulamak için daha belirgin yapabiliriz
        self.ax.annotate(self.author, (pos[self.author][0], pos[self.author][1]), textcoords="offset points", xytext=(0,10), ha='center', color="green", fontsize=12)

        self.ax.set_title(f"{self.author} için İşbirlikçi Yollar", fontsize=16)
        self.canvas.draw()

    def on_scroll(self, event):
        """Zoom in/out işlemi.""" 
        scale_factor = 1.2 if event.button == 'up' else 1 / 1.2
        xlim, ylim = self.ax.get_xlim(), self.ax.get_ylim()
        self.ax.set_xlim([x * scale_factor for x in xlim])
        self.ax.set_ylim([y * scale_factor for y in ylim])
        self.canvas.draw()

    def populate_table(self):
        """Tabloyu yollarla doldurur."""
        self.table_widget.setRowCount(len(self.paths))
        for row, (target, path) in enumerate(self.paths.items()):
            self.table_widget.setItem(row, 0, QTableWidgetItem(target))
            self.table_widget.setItem(row, 1, QTableWidgetItem(" -> ".join(path)))

    def resizeEvent(self, event):
        """Pencere boyutları değiştiğinde otomatik olarak çizimi güncelle."""
        self.draw_graph()


def calculate_collaboration_paths(graph, orcid_to_name, update_results, parent):
    """4. İster: İşbirlikçi yolları hesapla ve grafikte göster."""
    try:
        # Kullanıcıdan yazar ORCID'sini alma
        orcid_id, ok = QInputDialog.getText(parent, "Yazar ORCID", "Lütfen bir yazarın ORCID ID'sini girin:", QLineEdit.Normal)
        if not ok or not orcid_id.strip():
            update_results("Geçerli bir ORCID ID'si girilmedi.")
            return

        # ORCID'den yazar adını al
        author = orcid_to_name.get(orcid_id.strip())
        if not author:
            update_results(f"ORCID ID '{orcid_id}' ile eşleşen bir yazar bulunamadı.")
            return

        # Grafikte yazarın olup olmadığını kontrol et
        if author not in graph:
            update_results(f"{author} grafikte bulunamadı.")
            return

        # İşbirliği yollarını hesaplama işlemi için thread başlat
        thread = CollaborationPathsThread(graph, author, parent)

        def on_paths_calculated(paths):
            # Sonuçları QLabel üzerinde göster
            result = f"4. İster: {author} yazarı için işbirlikçi yolları:\n\n"
            result += "\n".join([f"{target}: {' -> '.join(path)}" for target, path in paths.items()])
            update_results(result)

            # İşbirlikçi yolları için pencereyi başlat
            collaboration_window = CollaborationPathsWindow(graph, paths, author, parent)
            collaboration_window.show()

        # Thread tamamlandığında sinyal ile sonuçları işleyin
        thread.paths_calculated.connect(on_paths_calculated)

        # Thread tamamlandıktan sonra kendisini durdur ve temizle
        thread.finished.connect(thread.deleteLater)

        # Parent üzerinde referans tut (thread kaybolmasın)
        parent.thread = thread

        # Thread başlat
        thread.start()

    except Exception as e:
        update_results(f"Hata oluştu: {str(e)}")
