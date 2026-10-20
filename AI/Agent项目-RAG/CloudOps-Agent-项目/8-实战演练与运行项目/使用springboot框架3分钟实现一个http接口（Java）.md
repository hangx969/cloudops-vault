# Spring Boot框架

Spring Boot 是基于 Java 的轻量级、开箱即用的应用开发框架。它极大简化了 Spring 应用的搭建和开发过程，无论是小型服务还是中大型企业级项目，Spring Boot 都是 Java Web 开发的首选。 https://spring.io/projects/spring-boot

源码： [ 项目源码（Go、Java、Python）](https://my.feishu.cn/wiki/L1dUw7qKziZeJXk17ojcdoKhn7g)使用spring boot实现一个http接口

安装环境

1. 安装 Maven（或使用 IDEA 自带的 Maven）



# 快速创建项目

创建 \`pom.xml\`，引入 Spring Boot 父工程和 Web Starter：

```xml
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>3.2.5</version>
</parent>

<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
</dependencies>
```





创建启动类 \`src/main/java/com/example/App.java\`：

```java
@SpringBootApplication
public class App {
    public static void main(String[] args) {
        SpringApplication.run(App.class, args);
    }
}
```



# 新增chat接口

下面我们动手写一个 \`/api/chat\` 接口，体验 Spring Boot 开发的完整流程。



## 1. 创建请求和响应类

在 \`src/main/java/com/example/model/\` 目录下新建两个类：

```typescript
// ChatRequest.java
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



```typescript
// ChatResponse.java
package com.example.model;

public class ChatResponse {
    private String answer;

    public ChatResponse(String answer) { this.answer = answer; }
    public String getAnswer() { return answer; }
    public void setAnswer(String answer) { this.answer = answer; }
}
```



## 2. 创建统一响应包装类



在 \`src/main/java/com/example/model/\` 目录下新建：

```typescript
// Result.java
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



## 3. 编写 Controller

在 \`src/main/java/com/example/controller/\` 目录下新建 \`ChatController.java\`：

```java
package com.example.controller;

import com.example.model.*;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api")
public class ChatController {

    @GetMapping("/chat")
    public Result<ChatResponse> chat(ChatRequest req) {
        return Result.ok(new ChatResponse("chat demo"));
    }
}
```

就这么简单！Spring Boot 通过 \`@RestController\` 和 \`@GetMapping\` 注解，几行代码就完成了接口定义。请求参数会自动绑定到 \`ChatRequest\` 对象上。



# 运行

在项目根目录执行：

```plaintext
mvn spring-boot:run
```

或者直接在 IDEA 中点击 \`App.java\` 的运行按钮。



看到控制台输出类似以下内容就说明启动成功了：

```plaintext
Started App in x.xxx seconds
Tomcat started on port 8080
```



打开浏览器访问：

http://localhost:8080/api/chat?id=1\&question=hello



返回结果：

```plaintext
{
    "message": "OK",
    "data": {
        "answer": "chat demo"
    }
}
```



大功告成，赶快试一试吧～

