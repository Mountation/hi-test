# CaseAI

CaseAI 是一个基于 Django 的 AI 评测系统，允许用户通过上传 Excel 文件创建评测集（EvaluationSet），存储语料（Corpus），并对模型进行评测与结果导出。该项目包含前端 UI（Bootstrap）、文件上传与解析、批量数据写入、评测执行与结果管理。

## 主要功能

- 创建/删除评测集（EvaluationSet）
- 从 Excel 文件导入语料（支持 `.xlsx` / `.xls`）
- 批量插入语料以提高导入性能
- 网页端上传进度显示（上传过程中显示进度条）
- 分页显示评测集内的语料（每页最多 10 条）
- 批量删除评测集及其语料（在数据库层做 QuerySet 删除以提高性能）
- 执行评测并显示/导出评测结果（评测执行逻辑位于 `myapp/views/evaluation.py`）

## 代码结构（关键文件）

- `manage.py` - Django 管理脚本
- `CaseAI/` - Django 项目配置
  - `settings.py` - 项目配置
  - `urls.py` - URL 路由
- `myapp/` - 应用代码
  - `models.py` - 数据模型：`EvaluationSet`, `Corpus`, `EvaluationRun`, `CorpusResult`
  - `views/dataset.py` - 上传/创建/查看/删除评测集逻辑
  - `templates/dataset/` - 前端模板（创建、列表、查看、运行页面）
  - `AIEval.py`, `AIClient.py` - 与 AI 模型交互与评估的逻辑
  - `views/evaluation.py` - 评测执行流程

## 已做的重要优化

1. 导入性能
   - 使用 `openpyxl` 的 `read_only=True` 模式按行流式解析 Excel，避免一次性加载整个文件到内存。
   - 使用 Django 的 `bulk_create`（按批次，例如 1000 条/批）批量写入 `Corpus`，大幅减少数据库插入次数与延迟。
   - 批量插入包裹在 `transaction.atomic()` 中以保证一致性。

2. 上传体验
   - 前端 `create.html` 使用 `XMLHttpRequest` 的 `xhr.upload.onprogress` 事件实现上传进度条，用户可见上传进度（注意：该进度仅包含网络上传进度，不包含服务器端解析/入库时间）。

3. 删除性能
   - `delete_dataset` 先以 QuerySet (`Corpus.objects.filter(evaluation_set=...)`) 在数据库层执行批量删除，然后删除 `EvaluationSet`，避免 ORM 对每条记录逐一 delete 触发的大量开销。

4. 页面显示
   - `view_dataset` 使用 Django `Paginator` 实现分页，每页显示 10 条语料，降低页面渲染压力并提升 UX。

## 环境与依赖

推荐在虚拟环境中运行（venv / conda）。项目主要依赖：

- Python 3.8+（项目环境中为 3.13）
- Django 版本（请查看 `CaseAI/settings.py` 中 `INSTALLED_APPS`）
- openpyxl

你可以使用 pip 安装必要依赖（如果需要我可以生成 `requirements.txt`）：

```powershell
pip install django openpyxl
```

## 配置说明

- 在 `CaseAI/settings.py` 中配置数据库（当前项目使用 SQLite `db.sqlite3`，可切换为 PostgreSQL/MySQL 以获得更好性能和并发支持）。
- 若部署到生产环境，请确保静态文件与媒体文件的正确配置，并使用生产级 WSGI 服务器（例如 Gunicorn + Nginx 或 Windows 下的适配方案）。

## 启动说明（本地开发）

1. 克隆代码并进入项目目录：

```powershell
cd d:\JHKdoc\CaseAI
```

2. 创建并激活虚拟环境（可选）：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. 安装依赖：

```powershell
pip install -r requirements.txt  # 如果你有 requirements.txt
# 或者
pip install django openpyxl
```

4. 运行数据库迁移（如果需要）：

```powershell
python manage.py migrate
```

5. 启动开发服务器：

```powershell
python manage.py runserver
```

6. 在浏览器中访问：

- 管理页面 / 主要功能（例如 `http://127.0.0.1:8000/`）
- 创建评测集页面：`/datasets/create/`
- 查看评测集页面：`/datasets/view/<id>/`

## 使用说明（快速示例）

- 创建评测集：在“创建评测集”页面填写名称、描述并上传 Excel 文件（.xlsx/.xls）。上传时浏览器将显示上传进度。
- 查看语料：在“查看评测集”页面以分页方式查看语料记录（每页 10 条）。
- 删除评测集：在“评测集列表”页执行删除操作，后端在数据库层批量删除关联语料以提高性能。

## 测试与性能评估

- 当前没有自动生成的性能基准脚本。我可以为你添加一个管理命令，用于生成大量测试语料并测量导入/删除耗时，以便量化优化效果。

## 已知限制与后续改进建议

- 上传进度仅反映客户端上传到服务器的网络传输进度，不包括服务器端解析和数据库写入。若需完整的导入进度反馈，请将导入任务异步化（例如 Celery + Redis），后端在执行时持久化进度并提供进度查询接口。
- 对于非常大的数据量（百万级），建议使用更强的数据库（Postgres）、分批删除策略、或直接在数据库上做批量 SQL 操作以控制事务日志大小。
- 可以完善前端分页为 AJAX 翻页以获得更流畅的用户体验。

## 联系/维护

如需我继续：
- 添加性能基准脚本并运行测试，或
- 将导入/删除迁移到后台任务队列并实现实时进度，或
- 生成 `requirements.txt` 与更完整的部署说明

请告诉我你希望我接着做哪件事，我会继续推进并更新 todo 列表。

## 部署说明（生产环境建议）

以下为将本项目部署到生产环境的推荐步骤与注意事项，示例以 Linux（Ubuntu）为主，Windows 下部署要点会在最后说明。

1. 使用生产数据库
   - 推荐使用 PostgreSQL 替代 SQLite：性能和并发更好，支持更复杂的事务和备份。
   - 在 `CaseAI/settings.py` 中配置 `DATABASES`，或通过环境变量注入数据库 URL（例如 `DATABASE_URL`）。

2. 虚拟环境与依赖
   - 在服务器上创建虚拟环境并安装依赖：

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. 配置环境变量
   - 在生产中请设置：
     - `DJANGO_SETTINGS_MODULE=CaseAI.settings`
     - `SECRET_KEY`（强随机值，切勿硬编码在仓库中）
     - `DEBUG=False`
     - `DATABASE_URL` 或直接在 `settings.py` 中配置数据库连接

4. 静态文件收集（collectstatic）
   - 使用 `whitenoise` 或由 Nginx 提供静态文件：

```bash
python manage.py collectstatic --noinput
```

5. 运行数据库迁移并创建超级用户

```bash
python manage.py migrate
python manage.py createsuperuser
```

6. 使用 Gunicorn（Linux）启动应用

```bash
gunicorn CaseAI.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

7. 使用 Nginx 反向代理（推荐）
   - 配置 Nginx 将静态文件指向 collectstatic 目录，动态请求代理到 Gunicorn 的 127.0.0.1:8000。

8. 安全与性能建议
   - 使用 HTTPS（Let’s Encrypt）
   - 设置合理的 Gunicorn worker 数（一般为 CPU 核心数 * 2 + 1）
   - 配置数据库连接池（Postgres）与监控

9. 后台任务与扩展
   - 若需要将导入/评测迁移为异步任务，请引入 Celery + Redis 并把耗时操作（解析/插入/评测）放到任务队列中，以便前端通过任务 ID 查询进度。

10. Windows 部署提示
    - Windows 下可以使用 IIS、Waitress、或直接通过 `python manage.py runserver`（仅用于开发）。
    - 若在 Windows 上部署生产服务，建议使用 `Waitress`（生产 WSGI）或容器化（Docker）将应用封装到 Linux 容器中以获得一致性和更好的性能。

示例 Nginx + Gunicorn、Postgres、Whitenoise 的流程可以根据你的服务器环境定制，需要的话我可以为你写出具体的 Nginx 配置与 Systemd service 文件。
