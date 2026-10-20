package chat

import (
	"SuperBizAgent/api/chat/v1"
	"SuperBizAgent/internal/ai/agent/plan_execute_replan"
	"context"
	"errors"
)

func (c *ControllerV1) AIOps(ctx context.Context, req *v1.AIOpsReq) (res *v1.AIOpsRes, err error) {
	query := `
"1. 你是一个智能的服务告警分析助手,首先调用工具query_prometheus_alerts获取所有活跃的告警。"
"2. 分别根据告警的名称调用工具query_internal_docs，获取告警名对应的处理方案。"
"3. 完全遵循内部文档的内容进行查询和分析,不允许使用文档外的任何信息。"
"4. 涉及到时间的参数都需要先通过工具get_current_time获取当前时间,再结合工具的时间要求进行传参。"
"5. 涉及到日志的查询,需要先通过日志工具获取相关日志信息，参数必须携带地域和日志主题。"
"6. 分别将告警对应查询到的信息进行总结分析,最后生成告警运维分析报告，格式如下：
告警分析报告
---
# 告警处理详情
## 活跃告警清单
## 告警根因分析N(第N个告警)
## 处理方案执行N(第N个告警)
## 结论
`

	resp, detail, err := plan_execute_replan.BuildPlanAgent(ctx, query)
	if err != nil {
		return nil, err
	}
	if resp == "" {
		return nil, errors.New("内部错误")
	}
	res = &v1.AIOpsRes{
		Result: resp,
		Detail: detail,
	}
	return res, nil

}
