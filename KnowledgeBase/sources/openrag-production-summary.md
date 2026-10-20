---
title: OpenRAG 生产级知识库架构实战
tags:
  - knowledgebase/source
  - AI/RAG
  - enterprise
  - architecture
date: 2026-06-07
sources:
  - "[[OpenRAG生产级知识库架构实战]]"
aliases:
  - OpenRAG摘要
---

# OpenRAG 生产级知识库架构实战

## 元信息
- **原始文档**：[[OpenRAG生产级知识库架构实战]]
- **领域**：AI / RAG / 企业级架构
- **摄入日期**：2026-06-07

## 摘要
以 OpenRAG（Docling + OpenSearch + Langflow + Backend）为底座，系统讲解企业级 RAG 平台的完整架构设计。从四面分离架构（控制面/数据面/检索面/生成面）出发，覆盖文档异步导入链路、Chunk 知识单元建模、OpenSearch 混合检索、Reranker 精排、权限模型（检索前过滤+生成前复核）、问答链路服务拓扑、K8s 高并发资源池拆分、缓存分层、可观测性 SLI/SLO、0 到 100 万文档演进路线、Agentic RAG 引入策略、MCP 接入和生产排坑清单。21 章全覆盖，含代码骨架和上线前 Checklist。

## 关键知识点
1. **四面分离架构**：控制面（治理：租户/权限/配额）、数据面（持续接入：异步导入+幂等+可恢复）、检索面（召回质量：多路召回+Reranker）、生成面（可约束可追责：Answer Guard）
2. **文档导入链路**：命令请求+异步流水线（而非同步上传即解析），导入任务数据模型含 7 个状态（pending→downloading→parsing→chunking→indexing→completed/failed），Worker 处理阶段职责拆分
3. **Chunk 知识单元建模**：不是切字符串，而是做知识单元建模。推荐元数据模型含 chunk_id/doc_id/section_path/chunk_type/tokens/embedding/acl_tags 等字段
4. **OpenSearch 双索引**：文档索引与 Chunk 索引分离，Chunk 索引 Mapping 含 dense_vector + text + keyword + nested 类型
5. **混合检索三路召回**：BM25 文本召回 + 向量语义召回 + 结构化过滤，通过 RRF（Reciprocal Rank Fusion）融合排序
6. **Reranker 精排**：cross-encoder 模型（bge-reranker-v2-m3），是把 Top-K 变成可用答案的关键一跳。高并发下需做请求合并（micro-batching）+ GPU 资源池隔离
7. **权限模型**：检索前 ACL 过滤（OpenSearch filter query）+ 生成前复核（Answer Guard 二次校验 chunk 权限），双重保障防止权限穿透
8. **K8s 高并发部署**：拆成 API 池、Embedding 池、Retrieval 池、Reranker 池、LLM 池，各自独立 HPA，扩缩容看业务指标（p99 latency/queue depth）而非 CPU
9. **缓存分层**：Embedding 缓存（Redis，TTL 24h）+ 检索结果缓存（短 TTL）+ 文档元数据缓存（长 TTL），缓存的是链路中的稳定中间结果而非最终答案
10. **可观测性 SLI/SLO**：检索 P99 < 500ms、生成 P99 < 5s、召回准确率 > 85%、权限穿透率 = 0%
11. **演进路线**：验证期（单实例+同步导入+BM25）→ 生产初期（异步导入+混合检索+Reranker+权限）→ 平台化（多租户+MCP+Agentic RAG+缓存+可观测性）
12. **上线前 Checklist**：架构侧/数据侧/检索侧/工程侧/治理侧 五个维度共 20+ 检查项

## 涉及的概念与实体
- [[KnowledgeBase/entities/Kubernetes]]
- [[KnowledgeBase/entities/MCP]]

## 值得注意
- 与知识库已有的 RAG-Agent 项目（Spring Boot + ES 8.10 混合检索）互补：RAG-Agent 侧重代码实现，本文侧重**架构设计和生产治理**
- 四面分离架构思想可泛化到其他 AI 平台设计中
- 权限模型的"检索前过滤+生成前复核"双重设计是企业级 RAG 的生死线
- 生产排坑清单（第十九章）包含 4 个高频问题的具体解决方案
