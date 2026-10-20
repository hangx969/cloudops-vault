# Eino

**Eino\[‘aino]**(近似音: i know，希望框架能达到 “i know” 的愿景) 旨在提供基于 Go 语言的终极大模型应用开发框架。 它从开源社区中的诸多优秀 LLM 应用开发框架，如 LangChain 和 LlamaIndex 等获取灵感，同时借鉴前沿研究成果与实际应用，提供了一个强调简洁性、可扩展性、可靠性与有效性，且更符合 Go 语言编程惯例的 LLM 应用开发框架。



# 实现一个简单的LLM对话

## 构造Message

```go
func createMessages(ctx context.Context) []*schema.Message {
    // 创建模板，使用 FString 格式
    template := prompt.FromMessages(schema.FString,
       // 系统消息模板。这里本质就是创建 system prompt
       schema.SystemMessage("你是一个{role}。你需要用{style}的语气回答问题。你的目标是帮助程序员保持积极乐观的心态，提供技术建议的同时也要关注他们的心理健康。"),
       // 插入需要的对话历史（新对话的话这里不填）
       schema.MessagesPlaceholder("chat_history", true),
       // 用户消息模板。这里本质就是创建 user prompt
       schema.UserMessage("问题: {question}"),
    )
    // 下面的template.Format就是用一个map，把对应的key填充到对应的{key}的位置里
    messages, _ := template.Format(ctx, map[string]any{
       "role":     "程序员鼓励师",
       "style":    "积极、温暖且专业",
       "question": "我的代码一直报错，感觉好沮丧，该怎么办？",
       // 对话历史（这个例子里模拟两轮对话历史）
       "chat_history": []*schema.Message{
          schema.UserMessage("你好"),
          schema.AssistantMessage("嘿！我是你的程序员鼓励师！记住，每个优秀的程序员都是从 Debug 中成长起来的。有什么我可以帮你的吗？", nil),
          schema.UserMessage("我觉得自己写的代码太烂了"),
          schema.AssistantMessage("每个程序员都经历过这个阶段！重要的是你在不断学习和进步。让我们一起看看代码，我相信通过重构和优化，它会变得更好。记住，Rome wasn't built in a day，代码质量是通过持续改进来提升的。", nil),
       },
    })
    return messages
}
```



## 创建大模型的入口

记得将这里的 API key 换成你自己的。

```go
func openAIForDeepSeekV3Quick(ctx context.Context) (cm model.ToolCallingChatModel, err error) {
    config := &openai.ChatModelConfig{
       APIKey:  "",
       Model:   "deepseek-v3-1-terminus",
       BaseURL: "https://ark.cn-beijing.volces.com/api/v3",
    }
    cm, err = openai.NewChatModel(ctx, config)
    if err != nil {
       return nil, err
    }
    return cm, nil
}
```



## 与LLM交互

```go
func main() {
    ctx := context.Background()
    // 使用模版创建messages
    log.Printf("===create messages===\n")
    messages := createMessages(ctx)
    log.Printf("messages: %+v\n\n", messages)
    // 创建llm
    log.Printf("===create llm===\n")
    cm, err := openAIForDeepSeekV3Quick(ctx)
    if err != nil {
       panic(err)
    }
    log.Printf("create llm success\n\n")

    log.Printf("===llm generate===\n")
    result, err := cm.Generate(ctx, messages)
    if err != nil {
       panic(err)
    }
    log.Printf("result: %+v\n\n", result.Content)
}
```

![](https://raw.githubusercontent.com/hangx969/upload-images-md/main/20260501135045082.png)

