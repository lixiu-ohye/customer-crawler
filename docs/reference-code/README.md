# customer-crawler 参考代码索引

| 目录 | 内容 | 状态 |
|------|------|------|
| `gateway/` | Go Gin API 网关（19 Handler 占位 + 鉴权/审计中间件） | 参考实现 |
| `service-intent/` | 意向评分服务（关键词预筛省 90% LLM 成本 → 过滤 → LLM 评分） | 参考实现 |
| `service-trigger/` | 触达频控服务（5 道频控关卡 + 账号池 ZSET 选号 + 延迟队列） | 参考实现 |
| `pain-point-system/` | 行业痛点解决方案管理系统（12 行业词库 + 8 大模块） | 参考实现 |
| `promotion-split/` | 小程序分账系统（仅一级推广 + 7天冻结自动分账 + 第三方托管） | 参考实现 |
| `deploy/` | docker-compose + kafka_init + redis_init 部署脚本 | 参考实现 |
