# Chapter 2 软件架构为什么不断演进？

Part I Foundations —— 为什么需要 AI Agent

Version: 2026-07

Last Updated: 2026-07-31

## Core Question

为什么软件架构会从 MVC、SOA、Microservice、Cloud Native 一路演进到 AI Agent？

## Chapter Conclusion

软件架构的每一次演进，都不是为了追逐新概念，而是为了把上一代系统无法承受的复杂度重新组织起来。

MVC 解决职责耦合，SOA 解决系统集成，Microservice 解决大型单体与团队协作，Cloud Native 解决弹性和运维复杂度。

AI Agent 要解决的是另一类复杂度：

软件如何处理无法提前写死流程、需要理解目标并动态决策的任务。

因此，Agent 可以被理解为现代软件技术栈中的 Intelligence Layer。

## Learning Objectives

完成本章后，你应该能够理解：

- 软件架构演进背后的共同逻辑
- MVC、SOA、Microservice、Cloud Native 分别解决了什么问题
- 为什么 AI Agent 不是微服务或云原生的替代品
- 为什么 Agent 更适合作为 Intelligence Layer
- 企业软件技术栈如何因为 Agent 增加新的层次

## 2.1 架构演进不是线性替代

很多技术讨论容易把架构演进理解成一种线性替代：

```text
MVC 被 SOA 替代
SOA 被 Microservice 替代
Microservice 被 Cloud Native 替代
Cloud Native 被 AI Agent 替代
```

这种理解是不准确的。

真实的软件架构演进，更像是在已有系统之上增加新的组织层次。

MVC 没有消失。今天的 Web 应用、移动应用、后台管理系统中，仍然大量使用分层思想。

SOA 没有消失。企业系统集成、服务治理、跨系统流程仍然离不开服务化思想。

Microservice 没有消失。大型互联网系统和复杂企业系统仍然需要独立部署、弹性扩展和团队边界。

Cloud Native 也没有消失。容器、Kubernetes、服务网格、可观测性和自动化运维，仍然是现代软件基础设施的重要组成。

AI Agent 也不是来替代这些架构的。

它是在这些架构之上，增加一层新的能力：

理解目标，并组织执行。

## 2.2 MVC：解决职责耦合

早期应用程序经常把界面、业务逻辑和数据访问混在一起。

当系统规模很小时，这种方式可以快速开发。

但当应用变大后，问题会迅速出现：

- 界面变化会影响业务逻辑
- 业务规则变化会影响数据访问
- 数据结构变化会影响用户界面
- 代码难以测试
- 多人协作时容易互相踩踏

MVC 的价值在于把系统拆成三个相对清晰的职责：

```text
View
  ↓
Controller
  ↓
Model
```

View 负责展示。

Controller 负责接收请求和组织交互。

Model 负责业务数据和核心状态。

MVC 的本质不是一个 UI 框架模式，而是一种复杂度隔离方式。

它告诉开发者：不要把所有逻辑都堆在一起，而要按照职责分离系统。

## 2.3 SOA：解决企业系统集成

当企业软件从单个应用走向多个系统之后，新的问题出现了。

CRM、ERP、财务系统、供应链系统、人力资源系统、数据仓库，都会产生自己的数据和业务能力。

这些系统如果互相直接调用，很快会变成复杂的点对点网络：

```text
System A ↔ System B
System A ↔ System C
System B ↔ System D
System C ↔ System E
```

系统越多，连接越复杂。

SOA 的核心思想是把业务能力抽象成服务，让系统通过服务接口协作。

它解决的问题不是单个应用内部的代码组织，而是企业级系统之间的集成和复用。

SOA 让软件架构从“应用内部结构”扩展到“企业能力网络”。

## 2.4 Microservice：解决大型单体与团队协作

随着业务持续增长，单体应用会遇到新的瓶颈：

- 代码库越来越大
- 发布周期越来越慢
- 一个模块出问题可能影响整个系统
- 团队之间协作成本变高
- 不同业务模块扩展需求不同

Microservice 的核心思想是把大型系统拆分成多个围绕业务能力组织的小服务。

每个服务可以独立开发、独立测试、独立部署、独立扩展。

```text
Order Service
Payment Service
Inventory Service
User Service
Notification Service
```

Microservice 解决的不是“如何写一个函数”，而是“如何让大型组织持续交付大型软件系统”。

因此，Microservice 本质上也是一种复杂度管理方式。

它把技术边界、业务边界和团队边界尽量对齐。

## 2.5 Cloud Native：解决运行与运维复杂度

当系统变成大量服务之后，新的复杂度又出现了：

- 服务如何部署
- 如何扩缩容
- 如何发现服务
- 如何做健康检查
- 如何发布和回滚
- 如何监控日志、指标和链路
- 如何在故障时自动恢复

Cloud Native 的出现，是为了让大规模分布式系统能够更稳定、更自动化地运行。

容器解决环境一致性。

Kubernetes 解决编排和调度。

服务网格解决服务通信治理。

可观测性解决系统运行状态理解。

CI/CD 解决持续交付。

Cloud Native 的核心，不只是“上云”，而是把软件运行环境也工程化。

## 2.6 AI Agent：解决开放性任务复杂度

到 Cloud Native 为止，软件工程已经很好地处理了很多复杂度：

- 代码复杂度
- 系统集成复杂度
- 团队协作复杂度
- 部署运维复杂度

但还有一种复杂度没有被真正解决：

任务本身的开放性复杂度。

传统架构默认执行路径可以提前定义。

而开放性任务的执行路径，往往需要在运行中根据目标、上下文和中间结果动态决定。

例如：

```text
用户目标：找出本季度利润下降的主要原因
  ↓
Agent 理解目标
  ↓
选择财务、销售、库存、供应链等数据工具
  ↓
根据查询结果调整分析路径
  ↓
形成解释和建议
```

这不是 MVC、SOA、Microservice 或 Cloud Native 能单独解决的问题。

它需要一层新的软件能力：

Intelligence Layer。

## 2.7 Agent 是 Intelligence Layer

可以把现代企业软件技术栈理解为：

```text
User / Business Goal
  ↓
Intelligence Layer
  ↓
Application Layer
  ↓
Service Layer
  ↓
Data Layer
  ↓
Infrastructure Layer
```

AI Agent 位于 Intelligence Layer。

它不直接替代业务应用、微服务、数据库或基础设施。

它负责把用户目标转换成执行过程，并协调下层系统完成任务。

在这个位置上，Agent 的职责包括：

- 理解自然语言目标
- 选择合适工具
- 管理任务状态
- 调用应用、服务和数据系统
- 根据反馈调整下一步
- 判断任务是否完成

如果说 Cloud Native 让软件“更容易运行”，那么 AI Agent 让软件“更容易理解目标并行动”。

这是两类不同的问题。

## Summary

软件架构的每一次演进，都是为了管理新的复杂度。

MVC 解决应用内部职责耦合。SOA 解决企业系统集成。Microservice 解决大型单体和团队协作。Cloud Native 解决大规模系统运行与运维复杂度。

AI Agent 不是这些架构的替代品，而是在现代软件技术栈之上增加的一层 Intelligence Layer。

它解决的是开放性任务复杂度：当任务无法提前写死流程时，软件如何理解目标、选择工具、动态执行并持续反馈。

本章结论：

Agent 是现代软件技术栈中的 Intelligence Layer。

## Notes

本章中的架构演进顺序是为了建立理解框架，不表示所有企业都会严格按这个顺序演进。

Agent 与 Cloud Native、Microservice、SOA、MVC 是不同层次的问题。后续章节讨论 Agent 时，会默认它运行在已有应用、服务、数据和基础设施之上。

## References

[1] Martin Fowler, James Lewis.  
Microservices.  
https://martinfowler.com/articles/microservices.html

[2] Cloud Native Computing Foundation.  
CNCF Cloud Native Definition.  
https://github.com/cncf/toc/blob/main/DEFINITION.md

[3] OpenAI.  
A Practical Guide to Building Agents.  
https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/

[4] Anthropic.  
Building Effective Agents.  
https://www.anthropic.com/engineering/building-effective-agents

以上 URL 已在 2026-07-31 验证可访问。
