from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QInputDialog, QLineEdit
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import networkx as nx

def find_shortest_path(graph, orcid_to_name, update_results_callback, parent):
    """
    İki yazar arasında en kısa yolu bulur ve grafiksel olarak gösterir.
    """
    # Kullanıcıdan iki yazarın ORCID ID'si istenir
    source_orcid, ok1 = QInputDialog.getText(parent, "Kaynak ORCID", "Kaynak yazar ORCID ID'sini girin:", QLineEdit.Normal)
    if not ok1 or not source_orcid.strip():
        update_results_callback("Geçerli bir ORCID ID'si girilmedi.")
        return

    target_orcid, ok2 = QInputDialog.getText(parent, "Hedef ORCID", "Hedef yazar ORCID ID'sini girin:", QLineEdit.Normal)
    if not ok2 or not target_orcid.strip():
        update_results_callback("Geçerli bir ORCID ID'si girilmedi.")
        return

    # ORCID ID'lerin grafikte olup olmadığını kontrol et
    if source_orcid.strip() not in graph or target_orcid.strip() not in graph:
        update_results_callback("Kaynak veya hedef düğüm bulunamadı.")
        return

    try:
        # En kısa yolu hesapla
        path = nx.shortest_path(graph, source=source_orcid.strip(), target=target_orcid.strip(), weight="weight")
        update_results_callback(f"1. İster: En kısa yol: {' -> '.join(path)}")

        # Grafikte en kısa yolu göster
        show_shortest_path_on_graph(graph, path, orcid_to_name, parent)

        return path  # En kısa yol verisini döndür

    except nx.NodeNotFound:
        update_results_callback("Kaynak veya hedef düğüm bulunamadı.")
    except nx.NetworkXNoPath:
        update_results_callback("Kaynak ve hedef arasında bir yol yok.")


def show_shortest_path_on_graph(graph, path, orcid_to_name, parent):
    """
    Grafikte sadece en kısa yolu çizmek için gereken düğümleri ve kenarları kullanır.
    """
    class ShortestPathWindow(QMainWindow):
        def __init__(self, graph, path, orcid_to_name):
            super().__init__()
            self.setWindowTitle("1. İster: En Kısa Yol")
            self.resize(800, 600)
            self.init_ui(graph, path, orcid_to_name)

        def init_ui(self, graph, path, orcid_to_name):
            # Yeni bir alt grafik oluştur (sadece yol içeren)
            subgraph = graph.subgraph(path)

            # Düğüm pozisyonlarını hesapla (Spring düzeni kullanarak)
            pos = nx.spring_layout(subgraph, seed=42)

            # Matplotlib figürünü oluştur
            fig, ax = plt.subplots(figsize=(10, 8))

            # Düğüm etiketlerini ORCID ID yerine isimle göster
            labels = {node: orcid_to_name.get(node, node) for node in subgraph.nodes}

            # Grafiği çiz (düğümler ve kenarlar)
            nx.draw(subgraph, pos, ax=ax, with_labels=True, labels=labels, node_color='skyblue', node_size=2000, font_size=10, font_weight='bold', edge_color='gray')

            # En kısa yolu kırmızı ile vurgula
            path_edges = list(zip(path[:-1], path[1:]))
            nx.draw_networkx_edges(subgraph, pos, edgelist=path_edges, edge_color='red', width=2, ax=ax)

            # Kuyruk bilgilerini yan tarafta göster
            queue_info = "Adım Adım Kuyruk:\n"
            for i in range(len(path)):
                queue_info += f"Adım {i + 1}: {' -> '.join(path[:i + 1])}\n"

            ax.text(-0.1, 0.5, queue_info, fontsize=10, transform=ax.transAxes, verticalalignment='center', bbox=dict(facecolor='white', alpha=0.7))
            # PyQt5 düzeni için canvas oluşturuluyor
            canvas = FigureCanvas(fig)

            # Pencere düzenini ayarla
            layout = QVBoxLayout()
            layout.addWidget(canvas)

            central_widget = QWidget()
            central_widget.setLayout(layout)
            self.setCentralWidget(central_widget)

    # Pencereyi açık tutabilmek için bir referans saklayın
    if not hasattr(parent, "child_windows"):
        parent.child_windows = []

    window = ShortestPathWindow(graph, path, orcid_to_name)
    parent.child_windows.append(window)  # Referansı saklayın
    window.show()
