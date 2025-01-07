from PyQt5.QtWidgets import QApplication, QInputDialog, QLineEdit, QProgressBar, QVBoxLayout, QWidget, QLabel, QListWidget, QMessageBox
import heapq
import time

def create_priority_queue(graph, orcid_to_name, update_results_callback, parent):
    """
    2. İster: Yazarın işbirlikçi düğümleri ağırlıklarına göre sıralanması ve kuyruk işlemleri.
    
    Args:
        graph (nx.Graph): NetworkX grafiği.
        orcid_to_name (dict): ORCID ile yazar isimlerini eşleyen sözlük.
        update_results_callback (function): Sonuçları güncelleme fonksiyonu.
        parent (QWidget): PyQt5'te üst widget (genellikle ana pencere).
    """
    # Kullanıcıdan ORCID ID alın
    orcid_id, ok = QInputDialog.getText(parent, "Yazar ORCID", "Lütfen bir yazarın ORCID ID'sini girin:", QLineEdit.Normal)
    if not ok or not orcid_id.strip():
        update_results_callback("Geçerli bir ORCID ID'si girilmedi.")
        return

    # ORCID ID'den yazar adını bul
    author = orcid_to_name.get(orcid_id.strip())
    if not author:
        update_results_callback(f"ORCID ID '{orcid_id}' ile eşleşen bir yazar bulunamadı.")
        return

    # Yazarın grafikte olup olmadığını kontrol et
    if author not in graph:
        update_results_callback(f"{author} grafikte bulunamadı.")
        return

    # Komşular ve ağırlıkları alın
    neighbors = [(neighbor, graph[author][neighbor]['weight']) for neighbor in graph.neighbors(author)]

    # Kuyruk oluşturulacak: Bu kısımda priority queue kullanılır
    priority_queue = []
    for neighbor, weight in neighbors:
        heapq.heappush(priority_queue, (-weight, neighbor))  # Negatif ağırlık, çünkü heapq küçükten büyüğe çalışır

    # Kuyruğun işlenme sürecini gösterecek yeni bir pencere açalım
    queue_window = QWidget()
    queue_layout = QVBoxLayout(queue_window)

    queue_label = QLabel("Kuyruk oluşturuluyor...\n", queue_window)
    queue_layout.addWidget(queue_label)
    
    progress_bar = QProgressBar(queue_window)
    queue_layout.addWidget(progress_bar)
    progress_bar.setRange(0, len(neighbors))
    
    queue_window.setWindowTitle(f"{author} İşbirlikçileri Kuyruğu")
    queue_window.setGeometry(500, 500, 400, 200)
    queue_window.show()

    # Kuyruğun görsel gösterimi için QListWidget kullanacağız
    list_widget = QListWidget(queue_window)
    queue_layout.addWidget(list_widget)

    # Kuyruğun görselleştirilmesi: Kuyruğa öğe ekleme ve çıkarma
    result = f"2. İster: {author} yazarı ve işbirlikçi ağırlıkları (ağırlıklara göre sıralanmış):\n"
    
    # Kuyruğa öğe ekle
    index = 0
    while priority_queue:
        weight, neighbor = heapq.heappop(priority_queue)
        result += f"{neighbor}: {-weight}\n"
        index += 1

        # Canlı olarak öğe ekle
        list_widget.addItem(f"{neighbor}: {-weight}")
        queue_label.setText(f"Eklenen: {neighbor} ({-weight})")

        # Görsel animasyon: Her öğe eklendikçe ilerleme çubuğunu güncelle
        progress_bar.setValue(index)

        # Anlık güncellemeler için kısa bir süre bekle
        QApplication.processEvents()
        time.sleep(0.5)  # 0.5 saniye bekle

    # Kuyruktan öğe çıkarma animasyonu
    for i in range(len(neighbors)):
        item = list_widget.takeItem(0)  # Kuyruğun başındaki öğeyi çıkar
        queue_label.setText(f"Çıkarılan: {item.text()}")
        list_widget.addItem(f"{item.text()} (Çıkarıldı)")  # Çıkarılan öğe için farklı bir etiket ekleyebiliriz

        # Görsel animasyon: Kuyruk çıktıkça güncellenmiş gösterim
        QApplication.processEvents()
        time.sleep(1)  # Kuyruk öğeleri çıkarılırken bir bekleme süresi

    # Sonuçları tamamla ve kullanıcıya göster
    update_results_callback(result)
    queue_window.close()

    # Ayrıca kullanıcıya işlem hakkında bilgilendirme yapılabilir
    QMessageBox.information(parent, "Kuyruk Sonuçları", "Yazar ve işbirlikçileri başarıyla sıralandı ve kuyruktan çıkarıldı.")
