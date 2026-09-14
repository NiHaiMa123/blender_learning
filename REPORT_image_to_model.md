# 从参考图反推 Blender 建模数据：可观测性、反演与验证方法

> 本报告不是“看图后凭经验怎么建模”的教程，而是定义一条可重复的 **image → evidence → parameters → Blender → validation** 管线。
>
> 目标：让 Agent 在开始建模前，先把参考图转换成一份带 **来源、置信度、自由度和验证条件** 的建模规格书；之后每一轮修改都应能回答：**改的是哪个参数、为什么改、由哪条图像证据支持、误差有没有下降。**
>
> Maple 项目背景：此前已经进行了大量 Blender 迭代，`renders/maple/` 中保存了多个阶段结果。问题并不是“不会继续调”，而是前期没有把参考图约束转换成足够完整、可执行的参数空间，导致 Agent 只能在 Blender 中边看边猜。

---

## 0. 最重要的结论

从单张 RGB 图像反推 3D 模型，本质上是 **欠约束的 inverse graphics 问题**。

一张图真正提供的不是“完整 3D 数据”，而是三类东西：

1. **直接观测量（Observed）**：像素位置、轮廓、可见边缘、颜色、遮挡关系、消失线索。
2. **模型估计量（Estimated）**：焦距、重力方向、相对深度、表面法线、反照率等，由算法和训练先验估计，有误差。
3. **不可观测自由度（Assumed / Designed）**：背面形状、被遮挡几何、绝对尺度、很多出屏方向、隐藏分叉等，必须靠先验或人为设计。

**禁止把 2、3 类写成“从图里测出来的数据”。**

因此正确目标不是“恢复唯一真实模型”，而是：

> 找到一组 3D 参数，使它在目标相机下最大程度解释参考图，同时在不可观测方向上满足合理的结构先验。

对当前 Maple 项目而言，最终评价优先级应是：

**目标相机重投影一致性 > 关键结构一致性 > 3D 合理性 > 非目标视角美观度。**

这是英雄镜头资产，不应为了不存在的“唯一真实 3D”牺牲目标画面。

---

# 1. 建模前先做“可观测性分解”

每一个准备写进 Blender 的参数必须标记证据类型。

| 标签 | 含义 | 例子 | 是否可直接作为硬约束 |
|---|---|---|---|
| **O (Observed)** | 图像中直接测得 | 分叉像素坐标、剪影宽度、枝条投影角度 | 是 |
| **E (Estimated)** | 模型/几何算法估计 | 焦距、相对深度、法线 | 否，应带置信度 |
| **P (Prior)** | 领域先验 | 树枝连续、半径总体递减、枫树枝序习惯 | 仅作正则化 |
| **D (Designed)** | 为目标镜头人为设计 | 隐藏枝的出屏方向、背面树冠厚度 | 否 |

推荐进一步给每个参数增加 `confidence ∈ [0,1]`。

示例：

```yaml
limb_R:
  fork_uv: [0.52, 0.29]        # O, confidence 0.95
  projected_angle_deg: 12      # O, confidence 0.90
  projected_length_H: 0.45     # O, confidence 0.85
  depth_direction: away_camera # E/P, confidence 0.35
  hidden_curvature: 0.18       # D, confidence 0.15
```

这样 Agent 就知道：

- `fork_uv` 不应随便动；
- `depth_direction` 可以试多个候选；
- `hidden_curvature` 本来就是设计自由度，不要花十轮去“猜真实值”。

---

# 2. 不要先反推“模型”，先反推“相机 + 2D 约束”

模型和相机是耦合的。

如果相机错了，Agent 会错误地用模型形变补偿透视：

- 焦距太长 → 会把树冠横向拉开；
- 相机太高 → 会错误压低主枝；
- pitch 错误 → 会用树干弯曲补偿；
- camera distance / scale 错误 → 会把所有尺寸判断带偏。

所以顺序必须是：

**Camera first → screen-space structure → depth hypotheses → geometry.**

---

# 3. Step A：建立统一坐标系

不要直接记录“x=550 px”。所有分析都使用归一化画面坐标：

```text
u = x / image_width
v = y / image_height
```

约定：

- 左上 `(0,0)`
- 右下 `(1,1)`
- 主体基准高度 `H` 采用参考图中可见树干/主体高度
- 世界尺度暂不赋米

同时定义三套空间：

1. **Image space**：`(u,v)`
2. **Camera space**：`(Xc,Yc,Zc)`，其中 `Zc` 为视深
3. **Blender world space**：最终构建坐标

任何规格表都必须明确数值属于哪套空间。

---

# 4. Step B：先建立“屏幕空间结构图”，而不是只做一个二值 mask

现报告最大的问题之一，是把主体分割后直接跳到树干中心线。

仅有 silhouette 不足以描述建模结构。至少需要 5 类 2D 数据。

## B1. 主体 mask

用于确定：

- 总包围框
- 投影面积
- 外轮廓
- 左/右/顶部极值
- 局部宽度

现有：

- `renders/maple/ref_branches_silhouette.png`
- `renders/maple/ref_branches_color.png`

阈值法可以保留，但应视为 **项目专用 segmentation heuristic**，不能写成通用方法。

如果参考图条件改变，可替换为 SAM/人工 mask。

## B2. 结构中心线 skeleton

必须明确区分：

- trunk centerline
- primary limb centerline
- secondary limb centerline

中心线不应简单由“每行 mask 左右边界中点”得到，因为叶片、交叉枝和分叉会污染结果。

更可靠做法：

1. mask 只提供候选区域；
2. 关键主干区人工/半自动标注若干控制点；
3. 用 spline 拟合；
4. 在垂直于局部中心线方向上测半径。

输出：

```yaml
trunk_centerline_2d:
  - [u0, v0]
  - [u1, v1]
  ...
```

## B3. Landmark / junction 关键点

必须单独记录：

- 根部中心
- 最大左凸点
- 收腰位置
- 主分叉点
- signature limb 出枝点
- co-leader 转折点
- 每个一级枝端点

这些关键点比全局 IoU 更重要。

建议目标：关键点重投影误差 < **画面短边的 0.5–1.0%**。

## B4. Width profile 局部宽度曲线

对每条主结构沿中心线采样：

```text
s = 沿中心线的归一化弧长
r_screen(s) = 屏幕空间半径
```

这比“基径 55 px → 末端 21 px”更完整。

最后用 5–10 个采样点表达即可，不需要逐像素。

## B5. Occlusion graph 遮挡图

这是旧报告严重缺失的部分。

单张图虽然不能给绝对深度，却能可靠给出一部分 **前后顺序**：

```text
A occludes B  =>  A 在该交叉位置位于 B 前方
```

例如：

```yaml
occlusion_edges:
  - [trunk, limb_back]
  - [limb_R, crown_cluster_03]
```

它不能告诉你相差 0.3m 还是 3m，但可以直接约束拓扑排序。

对树这种大量自遮挡对象，这类信息比一张单目 depth map 更可靠。

---

# 5. Step C：相机反演必须单独作为一个求解问题

## C1. 可求什么

若场景中存在可靠的：

- 建筑平行线
- 地面方向
- 垂直线
- 地平线

可以估计：

- focal length / FoV
- roll
- pitch / gravity direction
- principal orientation

工具可以包括：

- fSpy：人工指定消失方向，适合有建筑结构的画面
- GeoCalib：单图估计相机内参/重力方向的学习式方法

当前 Maple 参考图左侧建筑/屋顶可以作为辅助，但要注意：**场景中的日式屋顶并不保证每条边都是真正平行的正交建筑线。**

所以相机输出必须是一个区间，而不是一个假精确值。

例如：

```yaml
camera:
  focal_mm:
    value: 30
    range: [26, 35]
    evidence: E
    confidence: 0.65
  roll_deg:
    value: 0.4
    range: [-0.5, 1.0]
    confidence: 0.8
  pitch_deg:
    value: 6
    range: [4, 9]
    confidence: 0.6
```

## C2. 不要直接求 `px/m`

旧报告提出“像素坐标 ↔ px/m”，这是容易误导的。

透视相机中：

```text
screen size ∝ focal_length × world_size / depth
```

同一个对象在不同深度没有统一 `px/m`。

只有当：

- 深度已知，或
- 假设所有测量都位于同一近似平面

才可以得到局部换算关系。

因此在 3D 深度尚未建立前，应始终保持 **无量纲 screen-space ratio**。

---

# 6. Step D：单目深度、法线等 AI 输出只能作为“弱观测”

可使用：

- Depth Anything V2：单目相对深度 / 特定模型下的 metric depth
- Marigold：单目 depth；同系列也支持 surface normals / intrinsic decomposition

但必须明确：

> 单图深度本身是 ill-posed；模型输出依赖训练先验。对 AI 图、游戏 CG、雾景、细树枝、透明/半透明叶片，其误差可能具有结构性。

所以正确用途是：

### 可以做

- 判断大的前景 / 中景 / 背景层级
- 判断某根明显枝条总体向镜头还是远离镜头
- 给隐藏自由度生成初始假设
- 为背景山、建筑、地面提供粗层次

### 不应该做

- 把 depth 灰度直接当米
- 用它精确决定每根枝的 3D 控制点
- 用树叶区域深度恢复叶团真实厚度
- 把 depth estimator 与参考图冲突时自动认定 estimator 正确

### 建议融合规则

```text
直接遮挡证据 O > 多条透视几何 O/E > 稳定的 depth 大结构 E > 植物先验 P > 随机设计 D
```

---

# 7. Step E：从 2D branch trace 反推 3D 曲线，不是直接“抬成三维”

这是本项目真正的核心。

对一根树枝，2D 图像已经确定了它的投影曲线：

```text
C_img(s) = [u(s), v(s)]
```

3D 仍缺一个函数：

```text
z_depth(s)
```

因此不要让 Agent 同时自由修改 XYZ。

应该把问题写成：

> **UV 投影尽量锁死，仅优化 depth profile。**

即先构造一条在相机平面上完全对齐参考的曲线，再只给它少量深度控制参数：

```yaml
depth_profile:
  start: 0.0
  mid: -0.35
  end: -0.10
```

或使用 2–4 个 depth knots。

这样一个原本几十个自由度的问题，会变成 2–4 个自由度。

## 为什么这比“看图手摆 3D 枝条”有效

因为目标图已经告诉你：

- 它在画面哪里开始
- 经过哪里
- 在哪里结束
- 投影弯曲方向

Agent 不应再次猜这些已经观测到的信息。

真正需要猜的只有“它向屏幕里/外多少”。

---

# 8. Step F：树干不是一条中心线，必须拆成 3 个层级

旧报告把主干描述成：

```text
centerline + radius
```

这只适合圆管。

参考中的老树干视觉形态至少应拆成：

## F1. Macro axis

控制整个树干的大弯曲。

```yaml
axis_points: [...]
```

## F2. Section envelope

每个高度截面不是仅一个 `radius`，而应至少允许：

```yaml
section:
  width_camera_x
  depth_camera_z
  rotation
  asymmetry
```

目标镜头看不到 `depth_camera_z`，因此它属于 D/P 自由度。

## F3. Local form features

单独记录：

- buttress/root flare
- elbow/bulge
- waist
- fork swelling
- longitudinal ridge

这些不应靠 Noise texture 或统一 displacement 生成。

**先建立低频形体，再做树皮。**

当前 Maple 规格里已经观察到的“左凸、腰部内收、分叉膨大”可以保留，但应标为 **screen-space envelope observation**，而不是完整 3D 截面测量。

---

# 9. Step G：树枝拓扑必须显式建图

最终不要只给 Blender 一堆 curves。

定义结构图：

```yaml
branches:
  trunk:
    parent: null
  limb_R:
    parent: trunk
    attach_s: 0.68
  coLeader:
    parent: trunk
    attach_s: 0.82
  limb_back:
    parent: trunk
    attach_s: 0.80
```

每根枝至少需要：

```yaml
id
parent_id
attach_parameter
centerline_uv[]
depth_knots[]
radius_profile[]
visibility
occlusion_relations[]
confidence
```

这才是可以直接生成 Blender curve 的数据。

---

# 10. 植物学规律应该是正则项，不是反演结果

旧报告中植物形态规则占比过高，容易把“先验”误当“测量”。

可以使用：

- 分枝连续性
- 半径总体向末端递减
- 分叉处截面积关系的近似原则
- 物种典型分枝习惯
- 重力导致的大枝下垂趋势
- 向光性造成的枝冠偏置

但它们的作用应是：

> 当图像没有约束某个自由度时，用来选一个合理解。

而不是：

> 图上看不到，所以按公式算出“真实解”。

尤其不要在当前资产里把所谓“黄金角”“达芬奇规则指数”当硬参数。

对英雄镜头资产，视觉证据与画面设计优先。

---

# 11. 树冠不能只反推一个 silhouette，需要“体积占据 + 密度场”

叶片阶段如果继续只做外轮廓，仍然会出现：

- 外轮廓差不多，但内部太密
- 树干被完全堵死
- 叶团像均匀球
- 没有前后层次

建议把树冠拆成三层数据。

## H1. 2D canopy envelope

按画面区域建立多个叶团，而不是一个总 mask：

```yaml
clusters:
  crown_L_top:
  crown_center:
  crown_R_limb:
  crown_back:
```

每个 cluster 记录：

- 2D bbox
- centroid
- projected area
- boundary roughness
- overlap with trunk

## H2. Density map

把叶冠区域划成粗网格，如 `16×8`：

```text
density(u,v) ∈ [0,1]
```

它直接控制 Geometry Nodes 的实例化密度。

## H3. 3D thickness prior

叶团厚度通常不可从单图恢复。

因此只需要少量设计参数：

```yaml
cluster_depth:
  front_extent
  back_extent
  depth_bias
```

再用遮挡图限制前后顺序。

这比让 Agent 随机把叶片撒进一个 3D 球体可靠得多。

---

# 12. 材质反演也要区分“颜色”与“光照”

直接从参考图采到的 RGB 不是 Base Color。

它包含：

```text
observed color = material × lighting × visibility × atmosphere × tone mapping
```

因此：

- 参考图阴影中的深棕不能直接设为 bark Base Color
- 逆光叶片的橙红不能直接设为 leaf Base Color
- 雾中的低对比颜色不能作为材质固有色

Marigold 等方法的 intrinsic decomposition 可以提供辅助，但仍应视为 E 数据。

对项目更实用的做法是：

1. 从多个明暗区域取色，得到 **appearance palette**；
2. 先在中性光下调 Base Color / Roughness；
3. 再通过主光、透射、雾和 AgX 逼近参考的最终 appearance。

所以规格书需要分别记录：

```yaml
material_prior
appearance_target
```

而不是只有一个“颜色值”。

---

# 13. 光照反推应使用“方向约束”，不要假装能恢复唯一灯光

单张图能可靠推断的通常是：

- 主光来自哪一侧
- 是硬光还是软光
- 逆光/侧逆光/顺光关系
- 阴影大致方向
- 天空/环境填充冷暖关系

难以唯一反推：

- Sun strength 精确值
- 世界强度
- 色温精确值
- 是否还有画外补光

因此写成区间：

```yaml
key_light:
  azimuth_deg: [110, 135]
  elevation_deg: [8, 18]
  character: warm_backlight
```

然后把强度作为渲染优化变量。

---

# 14. 验证：不能只用 IoU

旧方案：

```text
render silhouette → XOR / IoU
```

这可以保留，但只能作为一项指标。

因为两个不同 3D 模型可以产生几乎相同的英雄视角 silhouette。

完整验证至少分 5 类。

## V1. Landmark reprojection error

所有关键点：

```text
E_landmark = mean(||p_render - p_ref||)
```

推荐用画面短边百分比表示。

这是最优先指标。

## V2. Centerline distance

对主干和一级枝中心线计算 Chamfer / 最近点距离。

比 IoU 更能定位“枝条方向错了但粗细盖住误差”的情况。

## V3. Width profile error

比较若干采样截面的局部宽度。

可以直接判断：

- 根部过粗
- 腰部不够收
- 分叉膨大不足
- 末端 taper 太快

## V4. Silhouette IoU

继续保留。

但应分区：

```text
trunk
signature limb
upper fork
whole tree
```

不要只看 whole-object IoU。

## V5. Occlusion consistency

检查：

```text
reference: A in front of B
render:    A in front of B ?
```

这是恢复 depth hypothesis 最重要的验证之一。

---

# 15. 增加一个“非英雄视角正则检查”，但不要用它压过目标镜头

目标是英雄视角资产，所以不能要求每个方向都匹配不存在的参考。

但需要防止 Agent 用极端作弊几何：

- 所有枝压在同一平面
- 树干深度只有 5 cm
- 叶冠成为一张卡片

因此每次关键阶段额外渲：

- target view
- yaw +30°
- yaw -30°

非目标视角只做 **sanity check**：

- 没有明显纸片化
- 没有严重自穿插
- 主干截面合理
- 枝条连接连续

不要求它们与参考图匹配。

---

# 16. 正确的优化顺序：一次只开放一组自由度

过去 10+ 轮容易打转，本质上是同时调整太多变量。

推荐阶段锁参：

## Stage 1 — Camera lock

只调：

- focal length
- camera pose
- object global transform

树用非常粗的 proxy。

验收：地平线/构图/主体 bbox 基本一致。

## Stage 2 — 2D skeleton lock

只调：

- trunk UV curve
- primary branch UV curve
- fork landmarks

所有 depth = 0。

验收：landmark + centerline。

## Stage 3 — Depth solve

UV 尽量锁定，只调：

- depth knots
- cross-section depth
- occlusion ordering

验收：目标镜头仍保持 2D 对齐；±30° 合理。

## Stage 4 — Radius / macro form

调：

- width profile
- root flare
- elbow
- waist
- fork swelling

验收：width error + silhouette。

## Stage 5 — Secondary structure

补足图像中真正参与阅读的二级枝。

不要为了“植物学复杂”生成大量无关枝条。

## Stage 6 — Canopy volumes

先叶团 proxy，再 leaf instances。

验收：cluster bbox / density / trunk visibility。

## Stage 7 — Material / light / atmosphere

几何不再大改。

---

# 17. Maple 项目：现有测量如何重新解释

现有 `MAPLE_TREE_SPEC.md` 中的数据不是全部作废，而是要重新标注证据等级。

例如现有主干表：

| z/H | x offset | screen radius | 解释 |
|---|---:|---:|---|
| 0.00 | 0.00 | 0.115 | O：参考视图根部包络 |
| 0.35 | -0.10 | 0.088 | O：投影中心线/宽度 |
| 0.52 | -0.145 | 0.082 | O：左侧 elbow 特征 |
| 0.72 | -0.07 | 0.060 | O：waist 特征 |
| 0.82 | -0.02 | 0.072 | O：fork 局部投影膨大 |
| 1.00 | -0.12 | 0.045 | O：顶部投影趋势 |

注意：这些值应命名为 **screen-space radius / projected envelope**，而不是 3D `r/H` 真值。

如果相机近似正视且树干局部深度变化小，可以拿它作为 Blender 初始半径；但它仍然是模型假设，不是严格三维测量。

现有 signature right limb 的“整体先下行、末端再上挑”也是有效 O 数据；真正缺失的是它的 `depth_profile`。

因此下一轮不应该继续改它的 2D 走势，而应该测试少量 3D depth hypotheses，例如：

```text
H0: 基本位于主干平面
H1: 中段向镜头 0.3H，再回到平面
H2: 中段远离镜头 0.3H，再回到平面
```

分别渲染 target / ±30°，按遮挡和体积阅读选择。

---

# 18. 建模规格书 V2：Agent 真正需要的输出

建议后续不要再写自然语言规格，而生成 YAML / JSON。

```yaml
reference:
  resolution: [1536, 687]
  target_view: hero

camera:
  focal_mm:
    value: 30
    range: [26, 35]
    source: E
    confidence: 0.65
  pitch_deg:
    value: 6
    range: [4, 9]
    source: E

anchors:
  tree_base:
    uv: [0.31, 0.88]
    source: O
    confidence: 0.98
  main_fork:
    uv: [0.36, 0.34]
    source: O
    confidence: 0.90

branches:
  trunk:
    parent: null
    centerline_uv: [...]
    screen_radius: [...]
    depth_knots:
      values: [0.0, 0.05, -0.05]
      source: D
      confidence: 0.2

  limb_R:
    parent: trunk
    attach_s: 0.68
    centerline_uv: [...]
    screen_radius: [...]
    depth_knots:
      values: [0.0, -0.25, -0.10]
      source: E_P
      confidence: 0.35

occlusion_graph:
  - front: trunk
    back: limb_back
    confidence: 0.85

canopy_clusters:
  - id: crown_R
    bbox_uv: [...]
    centroid_uv: [...]
    density_target: 0.72
    depth_extent_H: [0.20, 0.35]
    depth_source: D

validation:
  landmark_error_shortside_pct: 1.0
  centerline_error_shortside_pct: 1.2
  trunk_iou: 0.85
  whole_silhouette_iou: 0.80
  require_occlusion_consistency: true
  sanity_views_deg: [-30, 30]
```

数字只是 schema 示例；实际值必须由参考分析脚本输出，不能从本模板直接抄。

---

# 19. 建议增加的自动分析产物

当前项目已经有 silhouette 图。下一步比继续手调 Blender 更值得做的是补齐这些中间件：

```text
analysis/maple/
├── reference_mask.png
├── landmarks.json
├── trunk_centerline.json
├── branch_centerlines.json
├── width_profiles.json
├── occlusion_graph.json
├── camera_candidates.json
├── depth_hint.exr/png
├── canopy_density.png
└── model_spec.yaml
```

并生成一张可视化 overlay：

- 红点：landmarks
- 蓝线：centerlines
- 绿短线：width samples
- 数字：branch ID
- 实线/虚线：前景/后景假设

**如果人看 overlay 都不能确认“数据表达的是参考图”，就不允许进入 Blender 阶段。**

---

# 20. 推荐的 Agent 执行协议

每一轮 Blender 修改必须输出：

```text
Hypothesis
  哪个参数当前是错的？

Evidence
  由哪条 O / E / P 数据判断？

Change
  只修改哪些变量？

Expected image-space effect
  预计画面中的哪个 landmark / centerline / width 会向哪里移动？

Render
  target + 必要的 sanity view

Measurement
  修改前后误差

Decision
  keep / revert / next hypothesis
```

禁止：

> “感觉主枝还不太像，所以再调一下位置。”

允许：

> “`limb_R` 中段中心线比参考低 14 px，而 fork 与 tip 已对齐，因此仅减小中段 curve handle 的 V 偏差；depth knots 保持不变。”

这才会结束无方向迭代。

---

# 21. 工具定位

| 工具 | 在本流程中的正确角色 |
|---|---|
| SAM / 手工 mask | 获得 O：主体/局部分割 |
| fSpy | 几何相机候选 E |
| GeoCalib | 学习式相机/重力候选 E |
| Depth Anything V2 | 大尺度相对深度提示 E |
| Marigold | depth / normal / intrinsic 辅助 E |
| Blender Python | 参数化生成 + 批量渲染 |
| OpenCV / NumPy | landmark、centerline、IoU、overlay、误差测量 |

参考：

- GeoCalib: https://github.com/cvg/GeoCalib
- Depth Anything V2: https://github.com/DepthAnything/Depth-Anything-V2
- Marigold: https://github.com/prs-eth/Marigold

---

# 22. 对当前 Maple 项目的结论

旧报告的方向“先测量、再建模”是对的，但实现上仍停留在 **silhouette-driven modeling**，还没有形成真正的 **inverse-modeling parameterization**。

当前最应该做的不是继续增加树木生成公式，而是补齐四项：

1. **Camera candidates**：把相机先锁到一个合理区间。
2. **2D structural annotation**：landmarks + 每根一级枝 centerline + width profile。
3. **Occlusion graph + depth hypotheses**：明确哪些是图像证据，哪些是 3D 猜测。
4. **Blender 参数与图像误差一一映射**：每轮只开放一组自由度，自动量化 before/after。

`p27` 一类后期结果如果已经在目标镜头上接近参考，不能由此推出“单图信息已榨干”。更准确的说法是：

> **当前的 2D silhouette 信息已经利用较多，但相机、遮挡关系、depth profile、局部宽度和树冠体积还没有被显式建模为独立变量，因此仍有大量可利用信息，只是旧流程没有把它们结构化。**

下一步推荐先停止继续手调最终树，做一个 `analysis → model_spec.yaml → Blender proxy` 的最小闭环。只要这个 proxy 的相机、主干和一级枝能通过 landmark / centerline / width / occlusion 四类验收，再恢复细节、树皮和叶冠。
