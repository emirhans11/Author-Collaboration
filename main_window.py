# main_window.py
from PyQt5.QtWidgets import QWidget
from design import Ui_Form  # Design.py, PyQt tarafından üretilen UI sınıfı
from functions import Functions  # İster fonksiyonlarını içerir

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        # Fonksiyon sınıfını yükle
        self.functions = Functions(self.ui,self)
        
        # Butonlar ve isterler arasında bağlantı
        self.ui.btn_ister1.clicked.connect(self.functions.find_shortest_path)
        self.ui.btn_ister2.clicked.connect(self.functions.create_priority_queue)
        self.ui.btn_ister3.clicked.connect(self.functions.create_bst_with_removal)
        self.ui.btn_ister4.clicked.connect(self.functions.calculate_collaboration_paths)
        self.ui.btn_ister5.clicked.connect(self.functions.calculate_collaboration_count)
        self.ui.btn_ister6.clicked.connect(self.functions.find_most_collaborative_author)
        self.ui.btn_ister7.clicked.connect(self.functions.find_longest_path)
