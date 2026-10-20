package sse

import (
	"context"
	"fmt"
	"time"

	"github.com/gogf/gf/v2/container/gmap"
	"github.com/gogf/gf/v2/net/ghttp"
	"github.com/gogf/gf/v2/util/guid"
)

// Client 表示SSE客户端连接
type Client struct {
	Id          string
	Request     *ghttp.Request
	messageChan chan string
}

// Service SSE服务
type Service struct {
	clients *gmap.StrAnyMap // 存储所有客户端连接
}

// New 创建SSE服务实例
func New() *Service {
	return &Service{
		clients: gmap.NewStrAnyMap(true),
	}
}

// Create 创建SSE连接
func (s *Service) Create(ctx context.Context, r *ghttp.Request) (*Client, error) {
	// 设置SSE必要的HTTP头
	r.Response.Header().Set("Content-Type", "text/event-stream")
	r.Response.Header().Set("Cache-Control", "no-cache")
	r.Response.Header().Set("Connection", "keep-alive")
	r.Response.Header().Set("Access-Control-Allow-Origin", "*")
	// 创建新客户端
	clientId := r.Get("client_id", guid.S()).String()
	client := &Client{
		Id:          clientId,
		Request:     r,
		messageChan: make(chan string, 100),
	}
	// 发送连接成功消息
	r.Response.Writefln("id: %s", clientId)
	r.Response.Writefln("event: connected")
	r.Response.Writefln("data: {\"status\": \"connected\", \"client_id\": \"%s\"}\n", clientId)
	r.Response.Flush()
	return client, nil
}

// SendToClient 向指定客户端发送消息
func (c *Client) SendToClient(eventType, data string) bool {
	msg := fmt.Sprintf(
		"id: %d\nevent: %s\ndata: %s\n\n",
		time.Now().UnixNano(), eventType, data,
	)
	// 尝试发送消息，如果缓冲区满则跳过
	c.Request.Response.Writefln(msg)
	c.Request.Response.Flush()
	return true
}
