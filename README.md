# 蜘蛛源仓库（自动检测版）

手机 APP 的接口从本地 `file://` 改成从这里拉取，检测在云端自动跑。

## 结构

```
├── PY/                  # 把你的 .py 源全部丢进来
├── base/spider.py        # 检测用的基类桩（不用动）
├── check.py              # 检测+生成脚本（不用动）
├── api.json              # 生成的接口（自动更新，不用手动改）
├── check_report.txt      # 每次检测报告（自动更新）
└── .github/workflows/check.yml  # 每12小时自动跑（不用动）
```

## 配置步骤（只做一次）

1. **建仓库**：GitHub 新建仓库（建议私有），把本目录所有文件传上去
2. **放源**：把 PY/ 里的 `.gitkeep` 删掉，把你的 164 个 `.py` 源传到 `PY/` 目录
3. **放非py线路**：如果你原来的 `宜优精选.json` 里有 jar 等非 py 线路，把它的 `sites` 里非 `.py` 的条目复制出来，第一次手动创建一个 `api.json` 传上去（格式跟原来一样），之后脚本会自动保留它们只更新 py 部分；如果没有非 py 线路，跳过这步（脚本会自动建）
4. **开 Actions**：仓库 Settings → Actions → General → 允许 workflow 读写（Workflow permissions 选 Read and write）
5. **手动跑一次**：Actions 标签页 → Check Spiders → Run workflow，看日志确认通过
6. **改 APP 接口**：OK影视里把接口地址改成
   `https://raw.githubusercontent.com/你的用户名/仓库名/main/api.json`
   私有仓库的话 raw 地址需要 token，嫌麻烦就用公开仓库（源文件不含隐私信息）


## 日常使用

- 加新源：把 `.py` 丢进 `PY/`，git push，Actions 自动跑（或手动点 Run workflow）
- 删源：从 `PY/` 删掉文件，push 即可
- 想立刻触发：Actions → Run workflow，不用等 12 小时
