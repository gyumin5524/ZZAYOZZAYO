import torch
import numpy as np
from transformers import BertModel, BertTokenizer

from travel.models import CrawledData

# BERT 모델 불러오기 (PDF 예시에 따른 bert-base-uncased)
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
model = BertModel.from_pretrained("bert-base-uncased")

def generate_embedding(text: str) -> np.ndarray:
    """
    BERT 모델을 이용해 텍스트를 임베딩 벡터로 변환하는 함수.
    NaN 값이 발생하면 기본값 (0 벡터)로 대체.
    """
    if not text or text.strip() == "":
        return np.zeros(768, dtype=np.float32)

    inputs = tokenizer(
        text=text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=512
    )

    with torch.no_grad():
        outputs = model(**inputs)

    embeddings = outputs.last_hidden_state[:, 0, :].squeeze().numpy().astype(np.float32)

    if np.isnan(embeddings).any() or np.isinf(embeddings).any():
        print(f"Warning: embedding.py text: {text}")
        embeddings = np.zeros(768, dtype=np.float32)

    return embeddings


def update_embeddings():
    """
    CrawledData 모델에 저장된 레코드 중 아직 임베딩이 없는 데이터에 대해
    BERT 임베딩을 생성한 뒤 저장하는 함수.
    """
    queryset = CrawledData.objects.filter(embedding__isnull=True)
    for data in queryset:
        if not data.content or data.content.isspace():
            continue

        try:
            emb = generate_embedding(data.content)
            data.embedding = emb.tolist()  # NumPy array -> list 변환
            data.save()
        except Exception as e:
            print(f"ID {data.id}의 데이터 임베딩 생성 중 오류 발생: {str(e)}")
            continue
