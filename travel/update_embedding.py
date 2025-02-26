from .models import CrawledData
from .embedding import generate_embedding

def update_embeddings_for_crawled_data():

    queryset = CrawledData.objects.filter(embedding__isnull=True)
    for data in queryset:
        if not data.address or data.address.isspace():
            continue

        try:
            emb = generate_embedding(data.address)
            data.embedding = emb.tolist()
            data.save()
        except Exception as e:
            print(f"ID {data.id} 임베딩 생성 오류: {str(e)}")
            continue