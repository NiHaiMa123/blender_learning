# 从参考图反推通用 Blender 建模数据：Inverse Graphics 工作流

> 本报告定义的不是“树怎么照着图建”，而是一条对 **人物、服装、武器、车辆、家具、建筑、植物、场景道具** 都适用的通用流程：
>
> **image → evidence → scene/object representation → parameter hypotheses → Blender → render → validation → refine**
>
> 目标不是从单张图“恢复唯一真实 3D”，而是生成一份 **可解释、可执行、可验证** 的 3D 规格，使 Agent 能明确知道：哪些数据来自图像、哪些来自模型估计、哪些来自类别先验、哪些只是设计自由度。

---

# 0. 核心定义：这不是“看图建模”，而是通用 inverse graphics

单张 RGB 图像通常无法唯一确定：

- 绝对尺度
- 真实焦距与主体距离的唯一组合
- 被遮挡面
- 背面形状
- 精确深度
- 材质与光照的唯一分解
- 对称对象不可见侧的真实细节

所以目标必须改写为：

> **寻找一组 3D 场景参数，使其渲染结果最大程度解释参考图中的可观测证据，同时让不可观测部分满足合理的结构/类别/物理先验。**

对于只要求一个英雄镜头的资产，优先级是：

**目标视角一致性 > 关键结构一致性 > 3D 合理性 > 非目标视角完整性。**

对于需要多角度、动画或复用的资产，则提高 3D 合理性和隐藏面完整性的权重。

---

# 1. 第一原则：所有参数必须标记“证据来源”

统一使用四类标签：

| 标签 | 含义 | 示例 | 约束强度 |
|---|---|---|---|
| **O — Observed** | 从像素直接观测 | 轮廓、关键点、可见边界、遮挡顺序、消失线 | 强 |
| **E — Estimated** | 算法/模型估计 | 焦距、相对深度、法线、反照率、人体姿态 | 中，必须带置信度 |
| **P — Prior** | 类别/结构/物理先验 | 对称、刚性、人体骨骼、车辆轮轴共线、树枝连续 | 正则化 |
| **D — Designed** | 不可观测部分的人为选择 | 背面造型、隐藏厚度、不可见内部结构 | 弱，自由度 |

每个参数至少记录：

```yaml
value: ...
source: O | E | P | D
confidence: 0.0-1.0
range: [min, max]   # 若无法确定单值
locked: true/false  # 是否允许优化器/Agent 修改
```

**禁止把 E/P/D 写成“从图中测出来的真实数据”。**

---

# 2. 通用场景表示：把图像拆成六层变量

无论参考图里是什么对象，都先拆成下面六层，而不是直接跳到 mesh。

## 2.1 Global Camera

- focal length / FOV
- principal direction
- roll / pitch / yaw
- camera position（通常与尺度存在耦合）
- lens distortion（若存在）

## 2.2 Scene Layout

- ground plane
- dominant planes
- horizon / gravity
- foreground / midground / background
- object-to-object spatial relations

## 2.3 Object / Part Graph

把“一个图里看到的东西”变成结构图：

```text
scene
├── character
│   ├── body
│   ├── hair
│   ├── coat
│   └── sword
├── tree
│   ├── trunk
│   └── canopy
└── shrine
    ├── roof
    ├── pillars
    └── stairs
```

每个节点可有：

- parent / child
- rigid / articulated / deformable
- visible / partially visible / hidden
- symmetry relation
- attachment relation
- repeated-instance relation

## 2.4 Geometry

对象的 3D 形状，但**不强制统一表示方式**。

不同对象应选择最适合它的参数化表示，而不是全部强行变成自由 mesh。

## 2.5 Appearance

- base color / albedo
- roughness
- metallic
- normal / bump
- transmission / subsurface
- opacity
- texture scale/orientation

## 2.6 Lighting / Atmosphere

- key light direction
- light size / softness
- environment illumination
- fog / volume
- bounce / fill

这六层必须尽量解耦，否则 Agent 很容易用错误变量补偿另一个变量，例如“相机错了却改模型”“光照错了却改材质颜色”。

---

# 3. 通用 Pipeline 总览

```text
Reference Image(s)
        ↓
[0] Task profile / reconstruction target
        ↓
[1] Semantic + geometric evidence extraction
        ↓
[2] Camera and global layout hypotheses
        ↓
[3] Scene graph / part graph
        ↓
[4] Object-specific geometry parameterization
        ↓
[5] Depth / hidden-shape hypotheses
        ↓
[6] Blender proxy generation
        ↓
[7] Render-based validation
        ↓
[8] Constrained optimization / Agent refinement
        ↓
[9] Material + lighting inverse matching
        ↓
Final asset + evidence/spec/validation report
```

最重要的是：

> **先得到一个可参数化 proxy，再优化参数；不要一上来让 Agent 对最终 mesh 做无限自由编辑。**

---

# 4. Step 0：先定义任务类型，因为“正确 3D”取决于用途

分析前记录：

```yaml
task:
  target: hero_shot | reusable_asset | animation_asset | scene_reconstruction
  reference_count: 1
  target_views: [main]
  required_hidden_geometry: low | medium | high
  required_physical_validity: low | medium | high
```

四种任务区别：

### Hero shot

只需要目标镜头成立；允许较大的 D 类自由度。

### Reusable asset

需要多个角度合理；必须提高对称、体积、背面等先验权重。

### Animation asset

除了静态形状，还要求关节、衣服厚度、拓扑、碰撞等可变形结构正确。

### Scene reconstruction

更重视相机、地面、多个对象之间的尺度和空间布局。

---

# 5. Step 1：从图像抽取“证据层”，不是直接预测 Blender 参数

视觉模型（DEVIT / VLM / segmentation / depth / normal model）主要负责这一层。

建议统一抽取以下数据。

## 5.1 Masks / visible regions

每个对象和关键部件：

```yaml
objects:
  sword:
    mask: masks/sword.png
  coat:
    mask: masks/coat.png
```

mask 用于：

- silhouette
- bounding box
- visible area
- region IoU

## 5.2 Landmarks

适用于几乎所有类别。

例：

- 人：眼、肩、肘、腕、髋、膝、踝
- 车：轮心、灯角、窗角、车身特征线端点
- 武器：握把中心、护手端点、刀尖
- 建筑：屋檐角点、柱脚、门框角点
- 树：分叉、主枝端点

全部使用归一化屏幕坐标：

```text
u = x / image_width
v = y / image_height
```

## 5.3 Curves / centerlines

适用于：

- 肢体轴线
- 武器长轴
- 电缆/管道
- 树枝
- 衣服边缘
- 车辆 character line
- 建筑轮廓线

曲线比自由 mesh 更容易约束。

## 5.4 Edge / contour constraints

记录：

- silhouette
- crease
- seam
- hard-surface edge
- material boundary
- projected straight line

## 5.5 Occlusion graph

这是单图中最可靠的深度证据之一：

```text
A occludes B → 在该局部 A 比 B 靠近相机
```

例如：

```yaml
occlusion_edges:
  - [left_hand, sword_handle]
  - [coat_front, torso]
  - [front_wheel, wheel_arch_inner]
```

遮挡关系通常只给**顺序**，不给精确距离。

## 5.6 Symmetry / repetition / parallelism

这是通用流程中价值非常高的一类约束。

可检测：

- bilateral symmetry
- rotational symmetry
- repeated windows / spokes / bolts
- parallel edges
- equal-radius circles
- aligned wheel centers
- repeated floor tiles

这些约束可以把欠约束单图问题大幅收缩。

## 5.7 Material regions

先分“材质区域”，不要立刻估 PBR 数值。

```yaml
material_regions:
  - id: metal_01
  - id: fabric_01
  - id: skin_01
  - id: painted_plastic_01
```

## 5.8 Confidence

每个视觉观测都必须带置信度。

模型看不清、被遮挡、强反光、雾、运动模糊、AI 生成图的异常透视，都应降低 confidence。

---

# 6. Step 2：相机与全局布局先于精细几何

相机和模型几何高度耦合。

错误示例：

- 焦距太长 → Agent 用拉宽模型来补偿
- pitch 错 → Agent 用弯曲/倾斜物体补偿
- camera height 错 → Agent 修改角色腿长或建筑比例

因此顺序必须是：

**camera → layout → object pose/scale → local shape**

## 6.1 相机证据

优先级：

1. 多组可靠消失线
2. 已知矩形/圆/平行结构
3. 地平线 / gravity
4. 学习式 camera estimator
5. 常见焦段先验

相机不要输出假精确值：

```yaml
camera:
  focal_mm:
    value: 32
    range: [26, 40]
    source: E
    confidence: 0.62
```

## 6.2 不要过早建立统一 px/m

透视投影近似满足：

```text
screen_size ∝ focal_length × world_size / depth
```

不同深度不存在统一 `px/m`。

绝对尺度只能由：

- 已知尺寸对象
- 人体高度等弱先验
- 多视图
- 外部信息

进行锚定。

否则全部使用无量纲比例。

---

# 7. Step 3：Scene Graph / Part Graph 先于 mesh

通用建模 Agent 应首先建立对象拓扑关系，而不是立刻创建几何。

示例：角色 + 武器：

```yaml
parts:
  body:
    type: articulated
  coat:
    type: deformable_shell
    attached_to: body
  sword:
    type: rigid
    attached_to: right_hand
```

示例：车辆：

```yaml
parts:
  body_shell:
    type: rigid_surface
  wheel_FL:
    type: rigid_repeated
    symmetry_partner: wheel_FR
  wheel_RL:
    instance_of: wheel_FL
```

如果 part graph 错了，后面即使局部 mesh 很精细，也会不断返工。

---

# 8. Step 4：Geometry Adapter——通用主流程里唯一需要按类别切换的部分

不要寻找“一种表示适用于所有对象”。

主框架统一，但几何参数化根据对象选择 adapter。

## 8.1 Rigid / manufactured object

适合：

- 武器
- 家具
- 车辆
- 机械件
- 产品

优先参数：

- primitive decomposition
- planes
- cylinders
- profiles
- symmetry
- repeated parts
- bevel radius
- section curves

例如刀剑优先描述为：

```text
center axis + blade profile + cross-section + thickness + guard primitives
```

而不是让 Agent 自由雕整块 mesh。

## 8.2 Architecture / environment

优先：

- planes
- vanishing directions
- floor/wall intersections
- repeated modules
- facade grid
- profile extrusion

先恢复大平面和结构节奏，再细化装饰。

## 8.3 Articulated body / creature

优先：

- skeleton
- joint landmarks
- bone-length ratios
- joint rotations
- body volume sections
- symmetry

先求 pose，再求局部体型；禁止用网格变形补错误骨骼姿态。

## 8.4 Clothing / soft object

优先：

- attachment boundaries
- seam / hem curves
- panel topology
- silhouette
- folds as secondary detail
- thickness

可见褶皱属于局部表面证据，但衣服隐藏体积和背面 drape 通常是 P/D。

## 8.5 Organic static object

适合：

- 岩石
- 树根
- 肌肉形物体

优先：

- macro axis
- cross sections
- major bulges
- silhouette
- SDF / smooth volume

## 8.6 Vegetation

这是一个 adapter，不是主流程。

优先：

- branching graph
- branch centerlines
- radius profiles
- canopy volumes
- density field

## 8.7 Unknown / highly irregular object

可先使用：

- monocular 3D reconstruction
- image-to-3D
- SDF / point cloud / Gaussian / mesh proposal

但这些结果只作为 **shape hypothesis / initialization**。

后续仍应重新投影到目标图，用统一 evidence 层进行约束和验证。

---

# 9. Step 5：深度和隐藏面必须维护“候选假设”，不要伪装成真值

单图最主要的不确定性来自深度。

学习式 depth / normal 模型可以帮助初始化，但不能视为 ground truth。

对每个对象维护少量 hypotheses：

```yaml
hypotheses:
  depth_A:
    description: sword slightly toward camera
    score_prior: 0.45
  depth_B:
    description: sword approximately parallel to image plane
    score_prior: 0.35
  depth_C:
    description: sword away from camera
    score_prior: 0.20
```

然后让 Blender 重投影结果决定哪个候选更能解释图像。

## 9.1 对曲线类结构

已知：

```text
C_img(s) = [u(s), v(s)]
```

不要自由优化 XYZ，而只优化少量 depth knots：

```text
z(s) → 2~5 个控制参数
```

## 9.2 对平面/硬表面

优先求：

- plane orientation
- distance
- profile dimensions

利用平行、对称、矩形、圆等约束补深度。

## 9.3 对人体

2D joints 锁定投影；3D joint depth 由人体骨长、关节活动范围和遮挡关系约束。

## 9.4 对服装

边界和接触位置作为强约束；离开身体后的厚度/鼓起量作为弱参数。

---

# 10. Step 6：先生成 Proxy，不要直接做最终资产

Proxy 的目标不是漂亮，而是验证：

- camera 是否正确
- scene layout 是否正确
- object proportions 是否正确
- part topology 是否正确
- pose / depth 是否正确

Proxy 应满足：

- 低面数
- 参数化
- 可脚本重建
- 无复杂材质
- 快速渲染

例如：

- 人体：骨架 + capsule/简单 body volumes
- 车辆：box + wheel cylinders + profile surfaces
- 建筑：planes/boxes
- 衣服：粗 shell
- 树：curve skeleton + canopy ellipsoids

只有 proxy 通过几何验收，才进入细节阶段。

---

# 11. Step 7：统一 Render-based Validation

任何类别最终都回到同一个验证逻辑：

> **3D 参数 → Blender 渲染 → 与参考图比较。**

但不能只看一个总 IoU。

## 11.1 通用误差项

```text
L =
  w_landmark   * L_landmark
+ w_silhouette * L_silhouette
+ w_edge       * L_edge
+ w_part       * L_part
+ w_occlusion  * L_occlusion
+ w_depth      * L_depth_hint
+ w_prior      * L_structural_prior
```

### Landmark error

关键点重投影距离。

### Silhouette error

IoU / Dice / boundary distance。

### Edge error

关键结构线与渲染边缘的距离。

### Part error

部件区域位置、比例和可见面积。

### Occlusion error

前后关系是否满足参考图。

### Depth hint error

只在 confidence 足够高时使用单目 depth 等弱约束。

### Structural prior

例如：

- 对称误差
- 刚性误差
- 骨长变化
- 轮轴不共线
- 建筑不垂直
- 树枝不连续

## 11.2 非目标视角 sanity check

即使是 hero asset，也建议增加少量检查视角：

```text
main
main + yaw 20°
main - yaw 20°
slight top / side diagnostic
```

它们不是要求与参考一致，而是防止出现：

- 纸片模型
- 极端压扁
- 交叉穿模
- 错误背面

---

# 12. Step 8：优化时按变量层级逐级解锁

不要让 Agent 一次修改所有东西。

推荐 staged optimization：

## Stage A — Camera

锁模型，只调 camera hypothesis。

## Stage B — Global transform

调对象整体：

- position
- scale
- orientation

## Stage C — Primary structure

调：

- skeleton
- part proportions
- major profile
- major planes

## Stage D — Hidden/depth variables

调不可观测方向。

## Stage E — Secondary shape

调局部曲面、褶皱、bevel、枝节等。

## Stage F — Material / lighting

几何稳定后再做外观。

这样可避免不同变量互相补偿。

---

# 13. Geometry 与 Material/Lighting 必须分开反演

图像像素近似是：

```text
Image = Render(Geometry, Material, Lighting, Camera)
```

一个暗区域可能来自：

- 深色 albedo
- 阴影
- AO
- 表面背光
- 雾衰减

因此不要把 RGB 颜色直接当材质颜色。

建议顺序：

1. geometry proxy
2. neutral material diagnostic render
3. lighting direction / softness
4. material region matching
5. roughness / metallic / transmission
6. texture detail
7. atmosphere

对需要高质量材质匹配的对象，可使用 inverse rendering / procedural material parameter optimization；但这仍是 geometry 稳定后的第二阶段。

---

# 14. Agent 的职责边界

## Vision / DEVIT / VLM 负责

- detect / segment
- part decomposition
- landmark
- curve trace
- edge / line
- symmetry/repetition cues
- occlusion relations
- material-region semantics
- uncertainty assessment

## Geometry solver / scripts 负责

- camera solve
- coordinate transforms
- constrained triangulation / lifting
- parameter fitting
- symmetry enforcement
- optimization
- render loss

## Blender Agent 负责

- 根据 spec 创建 proxy
- 调用类别 adapter
- 修改允许解锁的参数
- 渲染 diagnostic passes
- 写回结果和误差

## Human 负责

- 目标审美
- 多个欠约束解之间的设计选择
- 判断“符合参考”与“更好看”的优先级
- 决定何时停止优化

**不应该让任何单个 VLM 同时承担视觉测量、3D 推断、建模和验收全部职责。**

---

# 15. 推荐的通用数据结构

```text
analysis/<shot_name>/
├── input/
│   └── reference.png
├── evidence/
│   ├── masks/
│   ├── landmarks.json
│   ├── curves.json
│   ├── edges.json
│   ├── occlusion_graph.json
│   ├── symmetry.json
│   ├── material_regions.json
│   ├── depth_hint.exr
│   └── normal_hint.exr
├── scene/
│   ├── camera_candidates.yaml
│   ├── layout.yaml
│   └── scene_graph.yaml
├── objects/
│   ├── object_001.yaml
│   ├── object_002.yaml
│   └── ...
├── hypotheses/
│   └── hypothesis_set.yaml
└── validation/
    ├── metrics.json
    ├── overlays/
    └── diagnostics/
```

单个对象 spec 示例：

```yaml
id: sword_01
class: rigid_manufactured
adapter: profile_extrusion

observations:
  mask: evidence/masks/sword.png
  landmarks: [guard_L, guard_R, tip, grip_center]
  centerline: sword_axis

constraints:
  symmetry: bilateral
  straight_axis: true

parameters:
  length:
    value: 1.0
    source: O
    units: normalized
    locked: true

  thickness:
    value: 0.035
    range: [0.02, 0.06]
    source: P
    confidence: 0.45

  depth_angle:
    value: -8
    range: [-20, 10]
    source: E
    confidence: 0.40
```

---

# 16. 类别 Adapter 表

| 类别 | 首选参数化 | 主要强约束 | 主要隐藏自由度 |
|---|---|---|---|
| 人体/角色 | skeleton + volumes | joints, silhouette | joint depth, back volume |
| 衣服 | shell/panels + attachment curves | hem, seam, silhouette | backside drape, thickness |
| 武器/机械 | primitives + profiles + symmetry | straight edges, symmetry | thickness, backside details |
| 车辆 | profile + planes + repeated wheels | wheel centers, windows, silhouette | cabin depth, hidden side |
| 建筑 | planes + extrusion + module grid | vanishing lines, verticals | room depth, hidden facade |
| 家具/产品 | primitives + symmetry | corners, circles, repeated parts | backside geometry |
| 岩石/有机物 | SDF/sections | silhouette, major bulges | backside volume |
| 植物 | branching graph + volumes | branch projection, canopy silhouette | depth spread, hidden branches |
| 场景 | scene graph + planes + proxies | horizon, overlap, scale relations | absolute depth/scale |

这个表只影响 Step 4 的 geometry representation；其他步骤不变。

---

# 17. 自动化优先级

最值得先实现的不是“自动生成最终 mesh”，而是以下中间件：

1. `extract_evidence.py`
   - masks
   - landmarks
   - curves
   - lines
   - occlusion relations

2. `solve_camera.py`
   - camera candidate set

3. `build_scene_graph.py`
   - object / part topology

4. `build_proxy.py`
   - 根据 adapter + spec 生成 Blender proxy

5. `render_diagnostics.py`
   - silhouette
   - ID masks
   - depth
   - normal
   - wireframe

6. `compare_reference.py`
   - landmark error
   - silhouette boundary
   - edge distance
   - part overlap
   - occlusion violations

7. `optimize_parameters.py`
   - 只优化 unlocked 参数
   - 每次记录 loss 变化

---

# 18. 对当前 blender_learning / Maple 的定位

Maple 不应继续成为报告的主体，它只是第一个测试 case。

其已有数据可以映射到通用 schema：

```text
trunk/branch mask        → evidence/masks
branch centerlines       → evidence/curves
fork points              → landmarks
front/back branches      → occlusion_graph
camera guesses           → camera_candidates
branch depth profile     → hypotheses
canopy distribution      → vegetation adapter parameters
```

因此 Maple 的价值是验证通用管线，而不是让主框架变成“树木专用系统”。

下一个验证对象最好故意换类别，例如：

- 一把武器 / 机械物：验证 hard-surface + symmetry adapter
- 一个角色姿势：验证 articulated adapter
- 一件衣服：验证 deformable-shell adapter
- 一个建筑/室内截图：验证 plane/layout adapter

如果同一 evidence → proxy → render-validation 主流程无需改，只替换 adapter，才说明这个框架真正通用。

---

# 19. 最终原则

整个系统应该遵循以下原则：

1. **图像先变成证据，不直接变成 Blender 数值。**
2. **Observed / Estimated / Prior / Designed 永远分开。**
3. **Camera、Geometry、Material、Lighting 不互相偷补误差。**
4. **先 scene graph / part graph，再 mesh。**
5. **先 proxy，再最终资产。**
6. **不同类别换 geometry adapter，不换主 pipeline。**
7. **单目 depth 是弱观测，不是真实 3D。**
8. **不可观测变量维护候选/区间，不制造假精度。**
9. **所有建模结果必须回到参考相机做 render-based validation。**
10. **Agent 只能修改当前阶段允许解锁的变量。**

最终我们要构建的不是一个“会照图建树的 Agent”，而是一个：

> **把任意参考图转换成结构化 3D 假设，再通过 Blender 渲染闭环逐步收敛的通用 inverse-graphics 建模系统。**
