# Chapter 45 Coding Agent

Part VI Enterprise Practice —— 企业实践

Version: 2026-08

Last Updated: 2026-08-03

## 本章结论

Coding Agent 的核心不是生成代码，而是在受限 Workspace 内完成“理解—计划—修改—验证—审查”的可回滚闭环。Patch 和测试证据是主要交付物，提交、推送和部署必须受权限与审批控制。

## 学习目标

- 设计 Repository Map、Context Retrieval 和 Change Plan；
- 用 Patch 而不是整文件生成控制变更范围；
- 构建文件、命令、网络和 Secret 沙箱；
- 把测试、静态检查和 Review 作为完成条件；
- 使用任务成功率、回归率和变更规模评估 Coding Agent。

## 45.1 业务背景

“修复折扣计算错误”看似简单，但 Agent 必须知道目标文件、公开 API、现有测试、仓库约束和影响范围。它还可能面对 Prompt Injection 文件、恶意测试、构建脚本和生产密钥。

因此 Workspace 中的所有内容都应视为不可信输入，Agent 的工具权限必须由 Runtime 控制。

## 45.2 生命周期

```text
Issue / Objective
  -> Repository Orientation
  -> Relevant Context Retrieval
  -> Change Plan
  -> Candidate Patch
  -> Patch Validation
  -> Tests / Lint / Typecheck / Security
  -> Diff Review
  -> Human Approval
  -> Commit / PR
```

失败后应回到最近安全状态，而不是连续叠加未经验证的 Patch。每次循环都设置最大轮数、时间和 Token 预算。

## 45.3 Tool 权限分级

| 等级 | 工具 | 默认策略 |
| --- | --- | --- |
| Read | `rg`、读取文件、Git diff | 可自动执行，限制 Workspace |
| Write | Apply Patch、格式化 | 允许候选变更，可回滚 |
| Execute | Test、Build、Package | 沙箱、超时、资源和网络限制 |
| Publish | Commit、Push、PR | 明确授权与审批 |
| Deploy | 发布、迁移、生产操作 | 独立高风险 Workflow |

读权限也可能泄露 Secret，因此 `.env`、密钥目录和凭证文件必须在工具层拒绝。

## 45.4 Context Engineering

不要把整个仓库塞入 Context。推荐按顺序检索：

1. `AGENTS.md`/贡献规范；
2. 目录与语言清单；
3. Symbol/引用关系；
4. 相关实现与测试；
5. 近期 Git 历史；
6. 失败日志的精确片段。

Context 中保留路径、行号和 Hash，修改前验证文件没有被外部并发改变。

## 45.5 最小可运行 MVP

`example.py` 在临时目录创建一个带缺陷的 Python 项目，然后执行：

- AST 解析和函数发现；
- 基线测试；
- 唯一 Anchor 校验；
- 生成 Unified Diff；
- 编译候选源码；
- 用 allowlist 命令和超时运行测试；
- 测试失败自动恢复；
- 成功后停在 `ready_for_review`，不自动提交。

```bash
cd chapters/chapter45
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python example.py
```

示例只修改临时 Workspace，不接触当前仓库。它是完整的最小 Coding Loop，而不是生产级通用代码生成器。

## 45.6 Patch 为什么优于整文件重写

Patch 能保留未修改区域、支持审查、统计变更规模并检测冲突。应用前先执行等价于 `git apply --check` 的检查；Git 官方文档说明 `--check` 只验证补丁是否可应用，不实际修改文件。

生产实现还应限制路径穿越、符号链接、二进制文件、生成文件和超大 Diff。

## 45.7 执行沙箱

至少隔离：文件系统、网络、进程、CPU、内存、时间和 Secret。不要把 `shell=True` 和任意字符串命令暴露给模型。命令应由注册表产生参数数组，并为 `pytest`、`npm test` 等工具配置工作目录、超时和输出上限。

依赖安装默认禁网或使用内部镜像；构建日志进入 Context 前做长度限制和 Secret 脱敏。

## 45.8 验证金字塔

从快到慢执行：语法/格式 → 定向单测 → 静态类型 → 相关模块 → 全量测试 → 安全扫描。失败日志只反馈相关片段，避免反复把数万行日志传给模型。

测试通过不代表 Patch 正确。还要检查需求覆盖、边界条件、API 兼容、无关改动和安全影响。

## 45.9 评测与上线

离线基准使用隔离仓库和可验证测试。指标包括：任务解决率、首次通过率、回归率、平均循环数、Diff 大小、测试选择召回率、越权尝试率和人工接受率。

上线从只读代码问答开始，再开放候选 Patch，最后才允许创建 PR。默认不自动 Merge 和 Deploy。

## 45.10 常见踩坑

- 没读仓库规则就修改；
- 整文件重写造成无关 Diff；
- 测试失败后继续叠加修改；
- 让模型决定任意 Shell 命令；
- 把测试通过当作业务完成；
- 自动 Push、Merge 或部署；
- 忽略仓库文件中的 Prompt Injection。

## 45.11 生产化清单

- Ephemeral Workspace；
- Read/Write/Execute/Publish 分级授权；
- Patch、路径和符号链接校验；
- 命令 allowlist、超时、资源限制；
- 网络和 Secret 隔离；
- 基线与修改后验证；
- Diff 审查和人工批准；
- 全链路 Trace、Artifact 和回滚。

## Summary

Coding Agent 是受治理的软件变更 Runtime。MVP 展示了安全路径、AST、Patch、测试、失败回滚和审批边界；模型只是候选变更生成器，验证和发布权属于确定性工具与人。

## References

[1] Git. git-apply Documentation.
https://git-scm.com/docs/git-apply

[2] OWASP. GenAI Security Project.
https://genai.owasp.org/
