package mem

import (
	"sync"

	"github.com/cloudwego/eino/schema"
)

var SimpleMemoryMap = make(map[string]*SimpleMemory)
var mu sync.Mutex

func GetSimpleMemory(id string) *SimpleMemory {
	mu.Lock()
	defer mu.Unlock()
	// 如果存在就返回，不存在就创建
	if mem, ok := SimpleMemoryMap[id]; ok {
		return mem
	} else {
		newMem := &SimpleMemory{
			ID:            id,
			Messages:      []*schema.Message{},
			MaxWindowSize: 6,
		}
		SimpleMemoryMap[id] = newMem
		return newMem
	}
}

type SimpleMemory struct {
	ID            string            `json:"id"`
	Messages      []*schema.Message `json:"messages"`
	MaxWindowSize int
	mu            sync.Mutex
}

func (c *SimpleMemory) SetMessages(msg *schema.Message) {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.Messages = append(c.Messages, msg)
	if len(c.Messages) > c.MaxWindowSize {
		// 确保成对丢弃消息，保持对话配对关系
		// 计算需要丢弃的消息数量（必须是偶数）
		excess := len(c.Messages) - c.MaxWindowSize
		if excess%2 != 0 {
			excess++ // 确保丢弃偶数条消息
		}
		// 丢弃前面的消息，保持对话配对
		c.Messages = c.Messages[excess:]
	}
}
func (c *SimpleMemory) GetMessages() []*schema.Message {
	c.mu.Lock()
	defer c.mu.Unlock()

	return c.Messages
}
