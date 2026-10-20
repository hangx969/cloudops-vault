package tools

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"time"

	"github.com/cloudwego/eino/components/tool"
	"github.com/cloudwego/eino/components/tool/utils"
)

// PrometheusAlert 告警信息结构
type PrometheusAlert struct {
	Labels      map[string]string `json:"labels"`
	Annotations map[string]string `json:"annotations"`
	State       string            `json:"state"`
	ActiveAt    string            `json:"activeAt"`
	Value       string            `json:"value"`
}

// PrometheusAlertsResult 告警查询结果
type PrometheusAlertsResult struct {
	Status string `json:"status"`
	Data   struct {
		Alerts []PrometheusAlert `json:"alerts"`
	} `json:"data"`
	Error     string `json:"error,omitempty"`
	ErrorType string `json:"errorType,omitempty"`
}

// SimplifiedAlert 简化的告警信息
type SimplifiedAlert struct {
	AlertName   string `json:"alert_name" jsonschema:"description=告警名称，从 Prometheus 告警的 labels.alertname 字段提取"`
	Description string `json:"description" jsonschema:"description=告警描述信息，从 Prometheus 告警的 annotations.description 字段提取"`
	State       string `json:"state" jsonschema:"description=告警状态，通常为 'firing'（触发中）或 'pending'（待触发）"`
	ActiveAt    string `json:"active_at" jsonschema:"description=告警激活时间，RFC3339 格式的时间戳，例如 '2025-10-29T08:48:42.496134755Z'"`
	Duration    string `json:"duration" jsonschema:"description=告警持续时间，从激活时间到当前时间的时长，格式如 '2h30m15s'、'30m15s' 或 '15s'"`
}

// PrometheusAlertsOutput 告警查询输出
type PrometheusAlertsOutput struct {
	Success bool              `json:"success" jsonschema:"description=查询是否成功"`
	Alerts  []SimplifiedAlert `json:"alerts,omitempty" jsonschema:"description=活动告警列表，每个告警包含名称、描述、状态、激活时间和持续时间。相同 alertname 的告警只保留第一个"`
	Message string            `json:"message,omitempty" jsonschema:"description=操作结果的状态消息"`
	Error   string            `json:"error,omitempty" jsonschema:"description=如果查询失败，包含错误信息"`
}

// queryPrometheusAlerts 查询Prometheus告警
func queryPrometheusAlerts() (PrometheusAlertsResult, error) {
	return PrometheusAlertsResult{}, nil
	baseURL := "http://127.0.0.1:9090"
	apiURL := fmt.Sprintf("%s/api/v1/alerts", baseURL)

	log.Printf("Querying Prometheus alerts: %s", apiURL)

	// 创建HTTP客户端
	client := &http.Client{
		Timeout: 10 * time.Second,
	}
	var result PrometheusAlertsResult

	// 发送请求
	resp, err := client.Get(apiURL)
	if err != nil {
		return result, fmt.Errorf("failed to query Prometheus alerts: %v", err)
	}
	defer resp.Body.Close()

	// 读取响应
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return result, fmt.Errorf("failed to read response: %v", err)
	}

	// 解析JSON响应
	if err = json.Unmarshal(body, &result); err != nil {
		return result, fmt.Errorf("failed to parse response: %v", err)
	}

	return result, nil
}

// calculateDuration 计算从 activeAt 到现在的持续时间
func calculateDuration(activeAtStr string) string {
	// 解析 RFC3339 格式的时间
	activeAt, err := time.Parse(time.RFC3339Nano, activeAtStr)
	if err != nil {
		return "unknown"
	}

	// 计算持续时间
	duration := time.Since(activeAt)

	// 格式化持续时间
	hours := int(duration.Hours())
	minutes := int(duration.Minutes()) % 60
	seconds := int(duration.Seconds()) % 60

	if hours > 0 {
		return fmt.Sprintf("%dh%dm%ds", hours, minutes, seconds)
	} else if minutes > 0 {
		return fmt.Sprintf("%dm%ds", minutes, seconds)
	} else {
		return fmt.Sprintf("%ds", seconds)
	}
}

// NewPrometheusAlertsQueryTool 创建Prometheus告警查询工具
func NewPrometheusAlertsQueryTool() tool.InvokableTool {
	t, err := utils.InferOptionableTool(
		"query_prometheus_alerts",
		"Query active alerts from Prometheus alerting system. This tool retrieves all currently active/firing alerts including their labels, annotations, state, and values. Use this tool when you need to check what alerts are currently firing, investigate alert conditions, or monitor alert status.",
		func(ctx context.Context, input *struct{}, opts ...tool.Option) (output string, err error) {
			log.Printf("Querying Prometheus active alerts")

			// 调用Prometheus Alerts API
			result, err := queryPrometheusAlerts()
			if err != nil {
				alertsOut := PrometheusAlertsOutput{
					Success: false,
					Error:   err.Error(),
					Message: "Failed to query Prometheus alerts",
				}
				jsonBytes, _ := json.MarshalIndent(alertsOut, "", "  ")
				return string(jsonBytes), err
			}

			// 转换为简化格式，对于相同的 alertname，只保留第一个
			seenAlertNames := make(map[string]bool)
			simplifiedAlerts := make([]SimplifiedAlert, 0)
			for _, alert := range result.Data.Alerts {
				alertName := alert.Labels["alertname"]

				// 如果这个 alertname 已经存在，跳过
				if seenAlertNames[alertName] {
					continue
				}

				// 标记为已见过
				seenAlertNames[alertName] = true

				simplified := SimplifiedAlert{
					AlertName:   alertName,
					Description: alert.Annotations["description"],
					State:       alert.State,
					ActiveAt:    alert.ActiveAt,
					Duration:    calculateDuration(alert.ActiveAt),
				}
				simplifiedAlerts = append(simplifiedAlerts, simplified)
			}

			// 构建成功响应
			alertsOut := PrometheusAlertsOutput{
				Success: true,
				Alerts:  simplifiedAlerts,
				Message: fmt.Sprintf("Successfully retrieved %d active alerts", len(simplifiedAlerts)),
			}

			// 转换为JSON
			jsonBytes, err := json.MarshalIndent(alertsOut, "", "  ")
			if err != nil {
				log.Printf("Error marshaling alerts result to JSON: %v", err)
				return "", err
			}

			log.Printf("Prometheus alerts query completed: %d alerts found", len(simplifiedAlerts))
			return string(jsonBytes), nil
		})
	if err != nil {
		log.Fatal(err)
	}
	return t
}
