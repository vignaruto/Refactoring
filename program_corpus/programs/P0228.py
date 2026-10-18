def compute_pairwise_embedding_similarity(embeddings: list[list[float]]) -> list[list[float]]:
    n = len(embeddings)
    sim_matrix = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            sim_matrix[i][j] = sum(embeddings[i][k] * embeddings[j][k] for k in range(len(embeddings[i]))) / (((sum(x**2 for x in embeddings[i])**0.5) * (sum(y**2 for y in embeddings[j])**0.5)) + 1e-9)
    return sim_matrix

if __name__ == "__main__":
    vecs = [[1.0, 0.0], [0.0, 1.0]]
    res = compute_pairwise_embedding_similarity(vecs)
    assert res[0][0] > 0.99
