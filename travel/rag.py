from sklearn.metrics.pairwise import cosine_similarity
from .models import CrawledData
import numpy as np

def search_similar_documents(query_embedding):
    # CrawledData에서 embedding이 있는 문서만 가져오기
    all_docs = CrawledData.objects.filter(embedding__isnull=False)

    if not all_docs.exists():
        return None  # 문서가 없으면 None 반환

    embeddings = []
    for doc in all_docs:
        embedding = np.array(doc.embedding, dtype=np.float32)

        # NaN 또는 Inf 값이 있을 경우, 해당 벡터를 zero vector로 변경
        if np.isnan(embedding).any() or np.isinf(embedding).any():
            print(f"Warning: Invalid embedding for document ID {doc.id}, replacing with zero vector.")
            embedding = np.zeros(768, dtype=np.float32)

        if embedding.ndim == 1:
            embedding = embedding.reshape(1, -1)  # 1차원 배열을 2차원 배열로 변환

        embeddings.append(embedding)

    if not embeddings:
        return None  # 임베딩이 없으면 None 반환

    # 임베딩 배열을 합쳐서 하나의 matrix로 만듬
    embeddings_matrix = np.vstack([emb[0] for emb in embeddings if emb.shape[0] > 0])

    # query_embedding이 2차원 배열인지 확인하고, 그렇지 않으면 reshape
    if query_embedding.ndim == 1:
        query_embedding = query_embedding.reshape(1, -1)

    if query_embedding.shape[1] != embeddings_matrix.shape[1]:
        print("Error: query_embedding and embeddings_matrix dimensions do not match.")
        return None

    # cosine similarity 계산
    similarities = cosine_similarity(query_embedding, embeddings_matrix)

    # 가장 유사한 문서의 인덱스 찾기
    most_similar_idx = np.argmax(similarities.flatten())
    most_similar_idx = int(most_similar_idx)

    # 유사도가 낮으면 None을 반환하도록 설정
    if similarities.flatten()[most_similar_idx] < 0.7:  # 0.7을 임계값으로 설정 
        print("No sufficiently similar documents found.")
        return None

    # 가장 유사한 문서를 반환
    return all_docs[most_similar_idx]