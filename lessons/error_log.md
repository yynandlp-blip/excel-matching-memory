# 错误日志

## 2025-01-01 初始
- 暂无历史错误

## 2025-01-02 仓库owner错误
- 错误现象：步骤0读取记忆仓库时返回404，创建仓库提示name already exists on this account
- 根因：误将owner写为mcp-memory，实际owner为yynandlp-blip
- 修复方法：先调用get_me获取当前登录用户名，再用该用户名作为owner访问仓库

## 2025-08-25 clean_name缺失html.unescape导致HTML实体残留
- 错误现象：匹配输出goods_name中出现`&amp;`等HTML实体（如"无线智能色度计&amp;浊度计"）
- 根因：match_latest.py中clean_name函数漏写了html.unescape步骤，且输出goods_name时也未对原始供货名称做反转义
- 修复方法：在clean_name中加入html.unescape（位于strip之后、normalize之前），输出goods_name时也调用html.unescape处理原始供货名称
