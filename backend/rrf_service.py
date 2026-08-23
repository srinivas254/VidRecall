from config import (
    RRF_K
)


def reciprocal_rank_fusion(chunk_ranks: dict) -> list[int]:

    rrf_scores = {}

    for chunk_index, ranks in chunk_ranks.items():

        score = 0.0

        # Dense contribution
        if ranks["dense_rank"] is not None:
            score += 1 / (RRF_K + ranks["dense_rank"])

        # Sparse contribution
        if ranks["sparse_rank"] is not None:
            score += 1 / (RRF_K + ranks["sparse_rank"])

        rrf_scores[chunk_index] = score

    # Highest RRF score first
    ranked_chunks = sorted(
        rrf_scores,
        key=rrf_scores.get,
        reverse=True
    )

    return ranked_chunks