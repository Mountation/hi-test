# 架构说明

本文档总结了 CaseAI 的架构与技术选型（中文）。

![Architecture diagram](assets/architecture.svg)

## 概述

CaseAI 是一个基于 Django 的评测平台，允许用户通过上传 Excel 文件创建评测集（EvaluationSet），批量写入语料（Corpus），并对 AI 模型执行评测与结果管理。核心功能包括：Excel 导入、批量数据存储、评测执行与结果查看/导出。

## 组件与技术栈

- 语言：Python 3.8+
- Web 框架：Django（路由、视图、模板、ORM）
- Excel 解析：openpyxl（使用 read_only 流式解析以处理大文件）
- 数据库：
  - 开发/本地：SQLite（便于快速启动）
  - 生产建议：PostgreSQL（更好的并发、事务与持久性）
- 前端：
  - Bootstrap（布局与样式）
  - 原生 JS（XHR / fetch）用于上传进度与部分 AJAX 操作
- 后台任务（可选）：Celery + Redis（将耗时导入/评测任务异步化）
- 部署：
  - WSGI：Gunicorn（Linux）或 Waitress（Windows）
  - 反向代理与静态：Nginx + Whitenoise
- 可观测性：
  - 日志：Python logging（按日轮转，保留 7 天）
  - 指标（可选）：Prometheus / StatsD / Datadog；日志收集到 ELK/EFK

## 数据流

1. 用户在前端上传 Excel 文件。
2. 服务端使用 openpyxl 的流式解析逐行读取并产生记录。
3. 将记录按批次写入数据库（Django 的 bulk_create），并在 transaction.atomic 中保证一致性。
4. 可发起评测任务，评测可同步执行或交给后台 worker（如 Celery）。

## 建议

- 数据量增大时请在生产环境使用 PostgreSQL。
- 将导入与评测任务异步化（Celery + Redis）可显著提升前端响应性与可观测性。
- 将重要性能指标（导入总耗时、rows/sec、batch 耗时）导出到监控平台，以便建立仪表盘。

## 资源

- `docs/assets/architecture.svg`：文档用的简单架构示意图。

---

如果需要我可以将文档转换为更丰富的图（PlantUML/Mermaid）或进一步配置 MkDocs 发布。