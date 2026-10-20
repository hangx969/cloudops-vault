# Spring AI Alibaba —— 小试牛刀



没有编程基础的同学，直接看 B 站视频学习： https://www.bilibili.com/video/BV1eyWbzEEnw



有编程基础的同学，请看官方文档学习：

1.  https://java2ai.com/ 

2. https://github.com/spring-ai-alibaba/examples/blob/main/spring-ai-alibaba-helloworld/README.md



Spring AI Alibaba 是基于 Spring AI 框架对阿里云百炼大模型服务的集成实现。它让 Java 开发者能够以极简的方式接入大模型，就像写一个普通的 Spring Boot 接口一样简单。



下面通过一个最简单的对话接口，演示如何快速上手。



源码：[ 项目源码（Go、Java、Python）](https://my.feishu.cn/wiki/L1dUw7qKziZeJXk17ojcdoKhn7g) 使用 Spring AI Alibaba 实现一个 AI 对话接口

# 1. 创建项目 & 引入依赖

使用 Maven 创建一个 Spring Boot 项目，在 `pom.xml` 中添加以下关键依赖：

```xml
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>3.4.5</version>
</parent>

<properties>
    <java.version>17</java.version>
    <spring-ai-alibaba.version>1.0.0.2</spring-ai-alibaba.version>
</properties>

<dependencies>
    <!-- Spring Boot Web -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <!-- Spring AI Alibaba DashScope Starter -->
    <dependency>
        <groupId>com.alibaba.cloud.ai</groupId>
        <artifactId>spring-ai-alibaba-starter-dashscope</artifactId>
        <version>${spring-ai-alibaba.version}</version>
    </dependency>
</dependencies>
```

# 2. 配置 API Key 和模型

在 `src/main/resources/application.properties` 中添加配置：

```plaintext
server.port=8080

spring.ai.dashscope.api-key=你的API Key
spring.ai.dashscope.chat.options.model=qwen3-max
```

# 3. 编写启动类

标准的 Spring Boot 启动类，没有任何特殊配置：

```java
package com.example;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class App {
    public static void main(String[] args) {
        SpringApplication.run(App.class, args);
    }
}
```

# 4. 定义请求 & 响应模型

**ChatRequest**—— 接收用户提问：

```java
package com.example.model;

public class ChatRequest {
    private String id;
    private String question;

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    public String getQuestion() { return question; }
    public void setQuestion(String question) { this.question = question; }
}
```

**ChatResponse**—— 封装模型回答：

```java
package com.example.model;

public class ChatResponse {
    private String answer;

    public ChatResponse(String answer) {
        this.answer = answer;
    }

    public String getAnswer() { return answer; }
    public void setAnswer(String answer) { this.answer = answer; }
}
```

**Result**—— 统一响应包装：

```java
package com.example.model;

public class Result<T> {
    private String message;
    private T data;

    public static <T> Result<T> ok(T data) {
        Result<T> r = new Result<>();
        r.message = "OK";
        r.data = data;
        return r;
    }

    public static Result<?> error(String msg) {
        Result<?> r = new Result<>();
        r.message = msg;
        return r;
    }

    public String getMessage() { return message; }
    public T getData() { return data; }
}
```

# 5. 编写对话接口（核心）

这是整个项目最核心的部分，也是 Spring AI Alibaba 真正展现威力的地方—— **只需 3 行代码就能完成一次大模型对话**：

```java
package com.example.controller;

import com.example.model.ChatResponse;
import com.example.model.Result;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")
public class ChatController {

    private final ChatClient chatClient;

    public ChatController(ChatClient.Builder chatClientBuilder) {
        this.chatClient = chatClientBuilder.build();
    }

    @GetMapping("/chat")
    public Result<ChatResponse> chat(@RequestParam String question) {
        String answer = chatClient.prompt(question).call().content();
        return Result.ok(new ChatResponse(answer));
    }
}
```

### 关键代码解析

| 代码                            | 说明                                                                |
| ----------------------------- | ----------------------------------------------------------------- |
| `ChatClient.Builder`          | Spring AI 自动注入的构建器，框架根据 `application.properties` 的配置自动创建对应的大模型客户端 |
| `chatClientBuilder.build()`   | 构建 `ChatClient` 实例，后续所有对话都通过它发起                                   |
| `chatClient.prompt(question)` | 将用户的问题作为 prompt 发送给大模型                                            |
| `.call()`                     | 同步调用大模型，等待返回结果                                                    |
| `.content()`                  | 提取大模型返回的文本内容                                                      |

整个调用链路一气呵成： **构造 prompt → 调用模型 → 提取回答**，一行代码搞定。

# 6. 启动 & 测试

启动应用后，打开浏览器或使用 curl 访问：

```bash
mvn spring-boot:run
curl "http://localhost:8080/api/chat?question=你好，介绍一下你自己"
```

返回结果示例：

```json
{
  "message": "OK",
  "data": {
    "answer": "你好！我是通义千问，一个由阿里云开发的大语言模型..."
  }
}
```
