# goframe框架

`GoFrame` 是一款模块化、高性能的 `Go` 语言开发框架。 如果您想使用 `Golang` 开发一个业务型项目，无论是小型还是中大型项目， `GoFrame` 是您的不二之选。如果您想开发一个 `Golang` 组件库， `GoFrame` 提供开箱即用、丰富强大的基础组件库也能助您的工作事半功倍。 https://goframe.org/



# 安装框架

https://goframe.org/quick/scaffold-index

使用脚手架快速启动一个http服务

```bash
gf init demo -u
cd demo && gf run main.go
```

[配置Goland ](https://goframe.org/docs/cli/gen-ctrl#%E8%87%AA%E5%8A%A8%E6%A8%A1%E5%BC%8F%E6%8E%A8%E8%8D%90)，使得能自动生成代码



# 新增chat接口

1. 首先，我们在api目录下依葫芦画瓢创建chat/v1目录，并编写Chat接口

![](https://raw.githubusercontent.com/hangx969/upload-images-md/main/20260501134532346.png)



```go
type ChatReq struct {
    g.Meta   `path:"/chat" method:"get" summary:"对话"`
    Id       string
    Question string
}

type ChatRes struct {
    Answer string `json:"answer"`
}
```

2. Ctrl+S保存，此时框架会自动帮我们生成internal/controller/chat控制层的代码。我们返回一个chat demo字符串回去

![](https://raw.githubusercontent.com/hangx969/upload-images-md/main/20260501134535293.png)



```bash
func (c *ControllerV1) Chat(ctx context.Context, req *v1.ChatReq) (res *v1.ChatRes, err error) {
    return &v1.ChatRes{Answer: "chat demo"}, nil
}
```

3. 将我们刚才写的chat控制器绑定上去

![](https://raw.githubusercontent.com/hangx969/upload-images-md/main/20260501134538336.png)

4. 最后，我们需要将collector层的返回值返回出去

![](https://raw.githubusercontent.com/hangx969/upload-images-md/main/20260501134541274.png)



```go
func main() {
    s := g.Server()
    s.Group("/api", func(group *ghttp.RouterGroup) {
       group.Middleware(ResponseMiddleware)
       group.Bind(chat.NewV1())
    })
    s.SetPort(6872)
    s.Run()
}

func ResponseMiddleware(r *ghttp.Request) {
    r.Middleware.Next()
    var (
       msg string
       res = r.GetHandlerResponse()
       err = r.GetError()
    )
    if err != nil {
       msg = err.Error()
    } else {
       msg = "OK"
    }
    r.Response.WriteJson(Response{
       Message: msg,
       Data:    res,
    })
}

type Response struct {
    Message string      `json:"message" dc:"消息提示"`
    Data    interface{} `json:"data"    dc:"执行结果"`
}
```



# 运行

`go run main.go` 看到route里面有刚才写的接口就说明成功了，赶快试一试吧～

![](https://raw.githubusercontent.com/hangx969/upload-images-md/main/20260501135155973.png)

![](https://raw.githubusercontent.com/hangx969/upload-images-md/main/20260501134543949.png)

