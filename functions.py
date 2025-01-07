import pandas as pd
import networkx as nx
import subprocess
from PyQt5.QtWidgets import QVBoxLayout
from ister1 import find_shortest_path
from ister2 import create_priority_queue
from ister3 import create_bst_with_removal
from ister4 import calculate_collaboration_paths
from ister5 import calculate_collaboration_count
from ister6 import find_most_collaborative_author  # 6. İster fonksiyonu
from ister7 import find_longest_path
from newgraph import run_collaboration_graph
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
import ast

class Functions:
    def __init__(self, ui, parent=None):
        self.ui = ui
        self.parent = parent
        self.graph = nx.Graph()
        self.authors_to_papers = {}
        self.orcid_to_name = {}
        self.shortest_path = None  # En kısa yol burada saklanacak
        self.load_graph_data()
        self.setup_graph_display()
        
    def load_graph_data(self):
        """Excel'den verileri oku ve graf oluştur."""
        file_path = "C:\\Users\\emirh\\OneDrive\\Masaüstü\\prolab\\PROLAB 3 - DATASET.xlsx"
        data = pd.read_excel(file_path)

        # Beklenen sütunları kontrol et
        expected_columns = ['coauthors', 'author_name', 'paper_title', 'orcid']
        if not all(col in data.columns for col in expected_columns):
            raise KeyError(f"Excel dosyasındaki eksik sütunlar: {', '.join([col for col in expected_columns if col not in data.columns])}")

        # Coauthors sütununu listeye çevir ve eşleme yap
        data['coauthors_list'] = data['coauthors'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
        self.orcid_to_name = dict(zip(data['orcid'], data['author_name']))

        for _, row in data.iterrows():
            main_author_id = row['orcid']  # ORCID ID kullanımı
            coauthors = row['coauthors_list']
            paper_title = row.get('paper_title', "Bilinmeyen Makale")

            self.authors_to_papers.setdefault(main_author_id, []).append(paper_title)

            for coauthor_id in coauthors:
                if coauthor_id == main_author_id:
                    continue

                if self.graph.has_edge(main_author_id, coauthor_id):
                    self.graph[main_author_id][coauthor_id]['weight'] += 1
                else:
                    self.graph.add_edge(main_author_id, coauthor_id, weight=1)

        nx.set_node_attributes(self.graph, {author_id: {"papers": papers} for author_id, papers in self.authors_to_papers.items()})


    def setup_graph_display(self):
        """lbl_graph içine Dash tabanlı grafiği yerleştir."""
        file_path = "C:\\Users\\emirh\\OneDrive\\Masaüstü\\proje3veriçekme\\PROLAB 3 - DATASET.xlsx"
        port = 8050

        # Dash uygulamasını ayrı bir subprocess olarak çalıştır
        self.dash_process = subprocess.Popen(
            ["python", "newgraph.py", file_path, str(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW  # Dash'i sessizce çalıştırır
        )

        # Dash uygulamasını QWebEngineView'de görüntüle
        dash_url = f"http://127.0.0.1:{port}"
        web_view = QWebEngineView()
        web_view.setUrl(QUrl(dash_url))

        if not self.ui.lbl_graph.layout():
            layout = QVBoxLayout()
            self.ui.lbl_graph.setLayout(layout)

        self.ui.lbl_graph.layout().addWidget(web_view)

    def update_results(self, text):
        """Sonuçları QLabel'de göster."""
        self.ui.result_scr.setText(text)

    # İster çağrıları
    def find_shortest_path(self):
        """1. İster: En kısa yolu bul."""
        path = find_shortest_path(self.graph, self.orcid_to_name, self.update_results, self.parent)
        if path:
            self.shortest_path = path  # En kısa yolu sakla

    def create_priority_queue(self):
        """2. İster: Öncelik kuyruğu oluştur."""
        create_priority_queue(self.graph, self.orcid_to_name, self.update_results, self.parent)

    def create_bst_with_removal(self):
        """3. İster: BST oluştur."""
        if not self.shortest_path:
            self.update_results("Önce 1. İsteri çalıştırarak geçerli bir yol hesaplayın.")
            return
        create_bst_with_removal(self.shortest_path,self.orcid_to_name,self.update_results, self.parent)

    def calculate_collaboration_paths(self):
        """4. İster: İşbirlikçi yolları hesapla."""
        calculate_collaboration_paths(self.graph, self.orcid_to_name, self.update_results, self.parent)

    def calculate_collaboration_count(self):
        """5. İster: İşbirlikçi sayısını hesapla."""
        calculate_collaboration_count(self.graph, self.orcid_to_name, self.update_results, self.parent)

    def find_most_collaborative_author(self):
        """6. İster: En çok işbirliği yapan yazarı bul."""
        find_most_collaborative_author(self.graph, self.update_results)

    def find_longest_path(self):
        """7. İster: En uzun yolu bul."""
        find_longest_path(self.graph, self.orcid_to_name, self.update_results, self.parent)
