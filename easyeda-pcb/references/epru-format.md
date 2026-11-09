# .epru 文件格式与字段

`.epro2` 解开是 zip，里面 `<工程名>.epru`（几 MB 明文）。这份文档只讲脚本之外还要知道的细节。

## 结构

对象之间用 `|` 分隔，行尾是 `|\n`。切分后逐个 `json.loads`。

```
{"type":"DOCHEAD","ticket":...}|
{文档元数据 docType / uuid / title ...}|
{"type":"LAYER"...}|
{LAYER 的属性补丁}|
```

- 文档元数据**在 DOCHEAD 的下一行**
- 有 `type` 的是实体头；紧跟其后没有 `type` 的对象是属性补丁，要顺序 `update` 进当前实体，不合并就只剩 ticket/id

## 认文档

- PCB 板文档没有可用的 `docType` 特征，**用"含 PAD_NET 实体的那个 section"来认**，全文件只有一个
- 元件封装是另外的 section，`meta.uuid` 形如 `<板doc>_<componentId>`；元件的 `ATTR(key=Footprint).value` 就等于这个 uuid，直接对表
- 少数元件引用的封装写成 16 位 hex（库封装），此时拿不到焊盘几何 —— 图上会缺这几个焊盘，汇报时说一声

## 字段（坐标单位全是 mil，× 0.0254 = mm）

| 实体 | 关键字段 |
|---|---|
| `LINE` 走线 | `netName` `layerId`(1=Top, 2=Bottom) `startX/startY/endX/endY` `width` |
| `VIA` 过孔 | `netName` `centerX/centerY` `viaDiameter` `holeDiameter` |
| `PAD_NET` 焊盘-网络绑定 | `id` = `["PAD_NET",<componentId>,<padNum>,<elementId>]`，网络名在 **`padNet`** 字段 |
| `COMPONENT` 元件 | `x` `y` `angle` |
| `PAD` 封装内焊盘 | `num` `centerX/centerY`（封装局部坐标）`hole{width}` `defaultPad{padType,width,height}` `layerId` |
| `POUR` 铺铜 | `layerId` `netName`，`path` 是扁平数组 `[x,y,"L",x,y,...]` |
| `POLY` 图形 | `polyType == "BOARD_OUTLINE"` 的是板框，`path = ["R", x, y, w, h, angle, 圆角]`，坐标是板的**右上角**（y 最大处） |
| `ATTR` 属性 | `key` 为 `Designator` / `Footprint` 时有用，`x/y` 是位号丝印位置 |

板内坐标范围：`x ∈ [板框 x, 板框 x+宽]`，`y ∈ [板框 y−高, 板框 y]`，y 轴向上。

## 元件旋转

封装焊盘是局部坐标，要按元件 `angle` 变换成板坐标：

```python
def rotate(c, px, py):
    cx, cy, ang = c['x'], c['y'], c['angle'] % 360
    if ang == 90:  return cx + py, cy - px
    if ang == 180: return cx - px, cy - py
    if ang == 270: return cx - py, cy + px
    return cx + px, cy + py
```

验证：算出的焊盘中心应落在某条走线的端点上（±0.3mm）。命中率 70% 上下是正常的 —— 剩下的走线从焊盘边缘引出，不是变换错。

## 能拿到 / 拿不到

- **能**：全部走线（网络名、层、线宽）、过孔、每个焊盘的网络（等价完整网表）、元件位置和位号、板框、铺铜范围、位号丝印文字位置
- **不能**：铺铜实际填充（`pourFill` 常为空，要打开工程重新铺铜）、丝印线条和元件外形（脚本用焊盘包围盒代替）、叠层与板厚（在工程设置里，不在备份文件里）

## 渲染坐标

SVG 里 `y_svg = 板顶y − y_mm`，比例取 10 px/mm 左右（135×121mm 的板 → 1530×1437 画布刚好）。线宽按实际 `width × scale` 画，最小 1.5px，否则细线看不见。
