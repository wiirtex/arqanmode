from enum import Enum


class TransformerType(str, Enum):
    ALL_MPNET_BASE_V2 = 'all-mpnet-base-v2'
    ALL_DISTILROBERTA_V1 = 'all-distilroberta-v1'
    MULTI_QA_MINILM_L6_COS_V1 = 'multi-qa-MiniLM-L6-cos-v1'
    MULTI_QA_MPNET_BASE_DOT_V1 = 'multi-qa-mpnet-base-dot-v1'
