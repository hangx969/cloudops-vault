package tools

import (
	"SuperBizAgent/internal/ai/retriever"
	"context"
	"encoding/json"
	"log"

	"github.com/cloudwego/eino/components/tool"
	"github.com/cloudwego/eino/components/tool/utils"
)

type QueryInternalDocsInput struct {
	Query string `json:"query" jsonschema:"description=The query string to search in internal documentation for relevant information and processing steps"`
}

func NewQueryInternalDocsTool() tool.InvokableTool {
	t, err := utils.InferOptionableTool(
		"query_internal_docs",
		"Use this tool to search internal documentation and knowledge base for relevant information. It performs RAG (Retrieval-Augmented Generation) to find similar documents and extract processing steps. This is useful when you need to understand internal procedures, best practices, or step-by-step guides stored in the company's documentation.",
		func(ctx context.Context, input *QueryInternalDocsInput, opts ...tool.Option) (output string, err error) {
			rr, err := retriever.NewMilvusRetriever(ctx)
			if err != nil {
				log.Fatal(err)
			}
			resp, err := rr.Retrieve(ctx, input.Query)
			if err != nil {
				log.Fatal(err)
			}
			respBytes, _ := json.Marshal(resp)
			output = string(respBytes)
			return output, nil
		})
	if err != nil {
		log.Fatal(err)
	}
	return t
}
