def find_most_collaborative_author(graph, update_results):
    """6. İster: En çok işbirliği yapan yazar (ID'ye göre)."""
    try:
        if not graph or len(graph.nodes) == 0:
            update_results("Graf henüz yüklenmedi veya düğüm bulunamadı.")
            return

        # Yazarlar ve işbirliği yaptığı kişi sayıları (derece hesaplaması)
        collaborations = {}

        for node in graph.nodes:
            # Yazarın işbirliği yaptığı kişi sayısını hesapla
            collaborations[node] = len(graph[node])

        # En fazla işbirliği yapan yazarı bul
        most_collaborative_id = max(collaborations, key=collaborations.get)
        max_collaborations = collaborations[most_collaborative_id]

        # Komşuları dosyaya yazdır (debug için)
        with open("most_collaborative_neighbors_debug.txt", "w", encoding="utf-8") as file:
            file.write(f"Yazar ORCID ID: {most_collaborative_id}\n")
            file.write(f"Komşular ({max_collaborations}):\n")
            for neighbor in graph.neighbors(most_collaborative_id):
                file.write(f"  - Komşu ORCID ID: {neighbor}\n")

        # En fazla işbirliği yapan yazarın bilgilerini kullanıcıya sun
        update_results(
            f"6. İster: En fazla işbirliği yapan yazar (ORCID ID): {most_collaborative_id} "
            f"({max_collaborations} kişiyle işbirliği yaptı)."
        )

    except Exception as e:
        update_results(f"Hata oluştu: {str(e)}")
