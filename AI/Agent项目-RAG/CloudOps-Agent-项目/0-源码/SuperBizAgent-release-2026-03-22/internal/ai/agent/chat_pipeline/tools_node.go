package chat_pipeline

import (
	"context"

	"github.com/cloudwego/eino-ext/components/tool/duckduckgo/v2"
	"github.com/cloudwego/eino/components/tool"
)

func newSearchTool(ctx context.Context) (bt tool.BaseTool, err error) {
	config := &duckduckgo.Config{}
	bt, err = duckduckgo.NewTextSearchTool(ctx, config)
	if err != nil {
		return nil, err
	}
	return bt, nil
}
