# 错误日志

## 2025-01-01 初始
- 暂无历史错误

## 2025-01-02 仓库owner错误
- 错误现象：步骤0读取记忆仓库时返回404，创建仓库提示name already exists on this account
- 根因：误将owner写为mcp-memory，实际owner为yynandlp-blip
- 修复方法：先调用get_me获取当前登录用户名，再用该用户名作为owner访问仓库
