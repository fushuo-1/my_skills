---
name: easyeda-pcb
description: 从 EasyEDA Pro / 嘉立创EDA专业版的 .epro2 备份里解析 PCB 走线、焊盘和网表，导出顶层/底层/叠加 layout SVG，统计走线长度与最小间距，查某个连接器每个脚接什么。只要用户问到一块真实板子的布局或布线就该用：画或导出 layout 图、看某条网络怎么走、核对连接器脚位、对比两份备份改了什么、评估布线是否满足间距规则、算走线长度。哪怕用户只说「帮我看看这块板子」「这布线行不行」而没提 EasyEDA，只要项目里有 .epro2 备份就适用。Use for EasyEDA Pro board export, layout SVG, routing inspection, netlist tracing, clearance check, layout diff.
compatibility: Python 3.8+，脚本只用标准库；要把 SVG 转 PNG 抽查时需要 Chrome 或 Edge
---

# EasyEDA Pro 板子导出

从 `.epro2` 备份快照里读出走线、焊盘、网表，生成能直接看的 layout 图，或者只查数据不画图。

## 1. 找快照

`<项目>/PCB/<项目>_backup/*.epro2`，取最新的那份。脚本传目录时会自动挑最新。

**完成判据**：`ls -la` 看过所有快照的时间，并且和主工程 `.eprj2` 的修改时间比过。主工程更新得更晚，说明快照不含最新改动 —— 先告诉用户，别直接出一张过期的图让他以为是最新的。

主工程 `.eprj2` 是 SQLite + 加密数据，读不出明文；`.epro2` 是 zip，里面的 `.epru` 是明文 JSON —— 只认后者。用户手上没有 `.epro2` 时，让他在编辑器里「文件 → 导出 → 备份」导一份。

## 2. 跑脚本

```bash
python <本 skill>/scripts/render_layout.py <目录或 .epro2> -o <输出目录> [选项]
```

三个常用分支，按用户要的东西选：

| 用户要什么 | 命令 |
|---|---|
| 看板子 layout | `-o <输出目录>`，出三张 SVG |
| 查某个元件的脚位 | `--pins U4`，打印每个脚的网络 + 对端元件 |
| 查某个网络接了什么 | `--net PB8`，打印这个网络在板上的每个焊盘 |

加上这两个能看更多：

- `--diff 旧备份.epro2`：底层图把"相比旧备份新增的网络"画成绿色，用来回答"这次改了什么"
- `--check`：打印最小铜边间距、每个网络的走线长度、以及绕路最多的 5 条（实际长度 vs 两端点曼哈顿距离）

**完成判据**：SVG 写出（`*_顶层 / _底层 / _叠加.svg`，stdout 会给出画布宽高），或者 `--pins` / `--net` 打印出脚位表。汇报直接用 stdout 里的数字，不要自己重算。

## 3. 抽查图（只在出图时做）

用 `--pins` / `--net` 只查数据时不画图，直接跳到第 4 步，别为了"走完流程"去渲染 PNG —— 那是白花的几分钟和大几万 token。

出图时扫一眼，确认不是空白或错位。stdout 给的宽高直接当 `--window-size`：

```bash
chrome --headless=new --user-data-dir=<临时目录> --hide-scrollbars \
  --run-all-compositor-stages-before-draw --virtual-time-budget=3000 \
  --screenshot=out.png --window-size=<W>,<H> file:///<path>.svg
```

**完成判据**：图里有板框、走线、焊盘和位号，形状和用户在编辑器里看到的一致。少 `--run-all-compositor-stages-before-draw` 会偶发报"written to file"但文件没落地。

## 4. 汇报

给文件路径，加 stdout 的板尺寸、元件数、焊盘数、过孔数、各层走线段数与总长。带 `--diff` 时说清楚哪些网络是这次新增的、各自多长、比最短绕了多少。

## 三个容易踩的坑

1. **文档元数据在 `DOCHEAD` 的后一行**。取前一行会得到一堆空文档，且不报错 —— 改脚本时最容易在这里静默出错。
2. **`PAD_NET` 里 `padNet` 为 null 的是空占位**，不是真焊盘（某板 555 条里 295 条是空占位）。当成真焊盘会算出"555 个焊盘"这种离谱数字。
3. **最小间距报出 USB 差分对（约 0.1mm）属正常**。差分对本来就贴着走，别当违规报给用户。

字段细节、坐标变换、单位换算、旋转验证方法见 [references/epru-format.md](references/epru-format.md)。
