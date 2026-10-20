"""文档相关数据模型"""

from typing import Optional

from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    """文档分片模型"""

    content: str = Field(..., description="分片内容")
    start_index: int = Field(..., description="分片在原文档中的起始位置")
    end_index: int = Field(..., description="分片在原文档中的结束位置")
    chunk_index: int = Field(..., description="分片索引（从0开始）")
    title: Optional[str] = Field(None, description="分片所属章节标题")

    class Config:
        """Pydantic 配置"""
        json_schema_extra = {
            "example": {
                "content": "这是一段文档内容...",
                "start_index": 0,
                "end_index": 100,
                "chunk_index": 0,
                "title": "第一章",
            }
        }
