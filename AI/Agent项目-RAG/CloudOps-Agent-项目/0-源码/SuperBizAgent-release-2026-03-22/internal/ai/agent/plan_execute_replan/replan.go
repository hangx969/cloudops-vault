package plan_execute_replan

import (
	"SuperBizAgent/internal/ai/models"
	"context"

	"github.com/cloudwego/eino/adk"
	"github.com/cloudwego/eino/adk/prebuilt/planexecute"
)

func NewRePlanAgent(ctx context.Context) (adk.Agent, error) {
	model, err := models.OpenAIForDeepSeekV31Think(ctx)
	if err != nil {
		return nil, err
	}
	return planexecute.NewReplanner(ctx, &planexecute.ReplannerConfig{
		ChatModel: model,
	})
}
