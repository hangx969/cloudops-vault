package main

import (
	retriever2 "SuperBizAgent/internal/ai/retriever"
	"context"
	"fmt"
)

func main() {
	ctx := context.Background()
	r, err := retriever2.NewMilvusRetriever(ctx)
	if err != nil {
		panic(err)
	}
	query := "服务下线是什么原因"
	docs, err := r.Retrieve(ctx, query)
	if err != nil {
		panic(err)
	}
	fmt.Println("Q：", query)
	for _, doc := range docs {
		fmt.Println("A：", doc.Content)
	}
	fmt.Println("Done", len(docs))
}
