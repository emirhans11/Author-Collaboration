from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QInputDialog, QLineEdit
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
def find_node(bst, target):
    """BST'de belirtilen düğümü bulur."""
    if bst is None or bst["root"] is None:
        return None
    if bst["root"] == target:
        return bst
    if target < bst["root"]:
        return find_node(bst["left"], target)
    else:
        return find_node(bst["right"], target)
def create_bst_with_removal(path, orcid_to_name, update_results, parent=None):
    """
    1. İsterde oluşturulan en kısa yol verisini kullanarak bir BST oluşturur.
    Kullanıcıdan bir yazar ID'si istenerek bu yazar ağacın yapısından çıkarılır ve güncel ağaç görselleştirilir.
    """
    if not path:
        update_results("En kısa yol verisi bulunamadı. Lütfen önce 1. İsteri çalıştırın.")
        return

    # Düğümlerden BST oluşturma
    def build_bst(nodes):
        if not nodes:
            return None
        nodes.sort()  # Sıralama garantisi
        mid = len(nodes) // 2
        root = nodes[mid]
        left = build_bst(nodes[:mid])
        right = build_bst(nodes[mid + 1:])
        return {"root": root, "left": left, "right": right}


    # Kullanıcıdan bir yazar ID'si iste
    removed_id, ok = QInputDialog.getText(parent, "Yazar ORCID", "Lütfen çıkarılacak bir yazarın ORCID ID'sini girin:", QLineEdit.Normal)
    if not ok or not removed_id.strip():
        update_results("Geçerli bir ORCID ID'si girilmedi.")
        return

    removed_id = removed_id.strip()
    if removed_id not in path:
        update_results(f"ORCID ID '{removed_id}' en kısa yol kuyrukta bulunamadı.")
        return

    # Yazar ID'sini kuyruktan çıkar
    updated_path = [node for node in path if node != removed_id]

    # Yeni BST'yi oluştur
    bst = build_bst(updated_path)

    # BST'yi görselleştirme
    dialog = BSTDialog(bst, updated_path, orcid_to_name, parent)
    dialog.show()

    # Sonuçları QLabel üzerinde göster
    update_results(f"3. İster: En kısa yoldan oluşturulan BST'den {removed_id} çıkarıldı ve son durumu görselleştirildi.")


class BSTCanvas(FigureCanvas):
    """BST'yi çizmek için özel bir Matplotlib Canvas."""
    def __init__(self, bst, orcid_to_name):
        self.figure = Figure(figsize=(12, 10))
        super().__init__(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.bst = bst
        self.orcid_to_name = orcid_to_name
        self.draw_bst()

    def draw_bst(self):
        """BST'yi çiz."""
        self.ax.clear()
        positions, labels = self.get_positions_and_labels(self.bst)
        self.ax.set_title("3. İster: BST Görselleştirme", fontsize=14)
        self.ax.axis("off")

        # Düğümleri çiz
        for node, (x, y) in positions.items():
            label = self.orcid_to_name.get(node, str(node))  # Yazar isimlerini göster
            self.ax.scatter(x, y, s=700, c="skyblue", edgecolor="black")
            self.ax.text(x, y, label, fontsize=8, ha='center', va='center')

        # Kenarları çiz
        for node, (x, y) in positions.items():
            bst_node = find_node(self.bst, node)
            if bst_node is None:
                continue
            if bst_node["left"] is not None:
                left_node = bst_node["left"]["root"]
                self.ax.plot([x, positions[left_node][0]], [y, positions[left_node][1]], color="black", linewidth=2)
            if bst_node["right"] is not None:
                right_node = bst_node["right"]["root"]
                self.ax.plot([x, positions[right_node][0]], [y, positions[right_node][1]], color="black", linewidth=2)
        self.draw()

    def get_positions_and_labels(self, bst_node, x=0, y=0, x_offset=20, y_offset=20, positions=None, labels=None):
        """BST düğüm pozisyonlarını ve etiketlerini çıkar."""
        if bst_node is None:
            return positions, labels
        if positions is None:
            positions = {}
        if labels is None:
            labels = {}
        positions[bst_node["root"]] = (x, y)
        labels[bst_node["root"]] = self.orcid_to_name.get(bst_node["root"], str(bst_node["root"]))
        if bst_node["left"] is not None:
            self.get_positions_and_labels(bst_node["left"], x - x_offset, y - y_offset, x_offset * 0.7, y_offset, positions, labels)
        if bst_node["right"] is not None:
            self.get_positions_and_labels(bst_node["right"], x + x_offset, y - y_offset, x_offset * 0.7, y_offset, positions, labels)
        return positions, labels


class BSTDialog(QMainWindow):
    """BST Görselleştirme için ayrı bir pencere."""
    def __init__(self, bst, path, orcid_to_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle("3. İster: BST Görselleştirme")
        self.resize(1000, 800)
        layout = QVBoxLayout()
        self.canvas = BSTCanvas(bst, orcid_to_name)
        layout.addWidget(self.canvas)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
