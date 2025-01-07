from PyQt5.QtWidgets import QInputDialog, QLineEdit
def calculate_collaboration_count(graph, orcid_to_name, update_results, parent):
    """5. İster: İşbirliği yapılan kişi sayısını hesapla."""
    try:
        # Kullanıcıdan ORCID ID alın
        orcid_id, ok = QInputDialog.getText(
            parent, "Yazar ORCID", "Lütfen bir yazarın ORCID ID'sini girin:", QLineEdit.Normal
        )
        if not ok or not orcid_id.strip():
            update_results("Geçerli bir ORCID ID'si girilmedi.")
            return

        orcid_id = orcid_id.strip()

        # Grafikte ORCID ID'nin olup olmadığını kontrol et
        if orcid_id not in graph:
            update_results(f"ORCID ID '{orcid_id}' grafikte bulunamadı.")
            return

        # Komşuların sayısını hesapla
        collaboration_count = len(list(graph.neighbors(orcid_id)))

        # Sonuçları QLabel'de göster
        update_results(
            f"5. İster: ORCID ID  '{orcid_id}' ile işbirliği yapan toplam kişi sayısı: {collaboration_count}"
        )

    except Exception as e:
        # Hata mesajını göster
        update_results(f"Hata oluştu: {str(e)}")
