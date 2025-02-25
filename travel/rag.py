import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from .models import CrawledData

def search_similar_documents(query_embedding):
    from sklearn.metrics.pairwise import cosine_similarity
    from .models import CrawledData
    import numpy as np

    all_docs = CrawledData.objects.filter(embedding__isnull=False)

    if not all_docs.exists():
        return None

    embeddings = []
    for doc in all_docs:
        embedding = np.array(doc.embedding, dtype=np.float32)

        if np.isnan(embedding).any() or np.isinf(embedding).any():
            embedding = np.zeros(768, dtype=np.float32)

        if len(embedding.shape) == 1:
            embedding = embedding.reshape(1, -1)

        embeddings.append(embedding)

    if not embeddings:
        return None

    embeddings_matrix = np.vstack([emb[0] for emb in embeddings if emb.shape[0] > 0])

    similarities = cosine_similarity(query_embedding, embeddings_matrix)

    most_similar_idx = np.argmax(similarities)

    return all_docs[most_similar_idx]