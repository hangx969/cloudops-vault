package tools

import (
	"context"

	e_mcp "github.com/cloudwego/eino-ext/components/tool/mcp"
	"github.com/cloudwego/eino/components/tool"
	"github.com/gogf/gf/v2/frame/g"
	"github.com/mark3labs/mcp-go/client"
	"github.com/mark3labs/mcp-go/mcp"
)

/*
	GetLogMcpTool

https://cloud.tencent.com/developer/mcp/server/11710
https://cloud.tencent.com/document/product/614/118699#90415b66-8edb-43a9-ad5a-c2b0a97f5eaf

https://www.cloudwego.io/zh/docs/eino/ecosystem_integration/tool/tool_mcp/
https://mcp-go.dev/clients
*/
func GetLogMcpTool() ([]tool.BaseTool, error) {
	// https://mcp-api.tencent-cloud.com/sse/XXXX
	mcpUrl, err := g.Cfg().Get(context.Background(), "mcp_url")
	if err != nil {
		return nil, err
	}
	ctx := context.Background()
	cli, err := client.NewSSEMCPClient(mcpUrl.String())
	if err != nil {
		return []tool.BaseTool{}, err
	}
	err = cli.Start(ctx)
	if err != nil {
		return []tool.BaseTool{}, err
	}
	initRequest := mcp.InitializeRequest{}
	initRequest.Params.ProtocolVersion = mcp.LATEST_PROTOCOL_VERSION
	initRequest.Params.ClientInfo = mcp.Implementation{
		Name:    "example-client",
		Version: "1.0.0",
	}
	if _, err = cli.Initialize(ctx, initRequest); err != nil {
		return []tool.BaseTool{}, err
	}
	mcpTools, err := e_mcp.GetTools(ctx, &e_mcp.Config{Cli: cli})
	if err != nil {
		return []tool.BaseTool{}, err
	}
	return mcpTools, nil
}
