# Scripts

`scripts/` 保存仓库级、可重复执行的开发与发布自动化。业务逻辑属于 Python 包，临时实验属于 Notebook，只有跨目录维护任务才进入这里。

## 适用脚本

- 文档链接、章节结构和引用检查；
- Dataset 下载、Checksum 和脱敏验证；
- Evaluation/Benchmark 批量运行与报告生成；
- 示例环境初始化和 Smoke Check；
- 版本、Tag、Release Notes 和发布前检查。

## 脚本契约

每个脚本应支持 `--help`，返回可靠退出码，并在 README 或模块 Docstring 中说明输入、输出、副作用和回滚方法。默认只操作仓库内文件；删除、覆盖、上传和发布必须显式确认。

推荐 Python 作为跨平台入口：

```text
scripts/
├── check_docs.py
├── run_evaluation.py
└── release.py
```

## 安全与可复现性

- 不在命令行参数或日志打印 Secret；
- 外部下载固定来源并校验 Hash；
- 支持 Dry Run 的写操作应默认 Dry Run；
- 路径相对仓库根解析，不依赖开发者个人目录；
- CI 使用的脚本必须能在无交互环境运行。

当前目录尚无脚本实现。只有当相同维护步骤需要第二次人工执行时再加入脚本，并同时更新根目录运行说明。
