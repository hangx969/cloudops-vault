package chat_pipeline

import (
	"SuperBizAgent/internal/ai/embedder"
	"context"

	"github.com/cloudwego/eino/components/embedding"
)

func newEmbedding(ctx context.Context) (eb embedding.Embedder, err error) {
	return embedder.DoubaoEmbedding(ctx)
}
