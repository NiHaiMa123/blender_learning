# 今汐 Cloth 重建计划（已完成）

## 目标

- 用真正的 Blender Cloth 替代旧的刚体/代理解算。
- 让裙摆在重力下自然运动，并通过身体碰撞体减少穿透。
- 交付可重复打开的 `.blend`、磁盘缓存、测试渲染和参数清单。

## 发现并修正的问题

### 1. Pin 权重语义被写反

旧脚本把 0 当作“完全固定”、1 当作“自由”，实际 Blender Cloth 中恰好相反：

- 权重 `1.0`：完全 Pin。
- 权重 `0.0` 或不属于顶点组：自由参与 Cloth 解算。

旧缓存因此固定了本应自由的顶点，并让顶部点参与下落；旧的 1–120 帧缓存和渲染不能作为有效布料解算证据。

现已修正为：只把每个断开后纱片顶部 5 cm 带的 92 个顶点以权重 `1.0` 加入 `CLOTH_PIN_WAIST`，其余 3,142 个顶点保持自由。

### 2. 磁盘缓存与最终文件名不匹配

Blender 的磁盘点缓存目录取决于烘焙时正在打开的 `.blend` 文件名。旧流程“先烘焙、后另存”为最终文件，会让缓存留在 `blendcache_今汐_cloth_rebuild_v3`，最终文件重开后不能可靠定位。

现已改为：先保存为最终文件，再执行烘焙，最后再次保存。实际缓存位于：

`D:\software\blender\project\blendcache_今汐_cloth_rebuild_final`

### 3. 旧状态说明与验收标准矛盾

旧文档同时写了“内存缓存随 Blend 保存”和“磁盘缓存可读取”，并把交付范围限制到 80 帧。正确 Pin 后 1–120 帧稳定，因此最终文件和验收范围统一为 1–120 帧磁盘缓存。

### 4. 使用了被旧重建污染的备份，原姿势没有可靠继承

旧的 `今汐_before_cloth_rebuild.blend` 已经包含上一轮 `CLOTH_REBUILD_*` 对象，而且原始角色网格已隐藏，不能再视为干净的“重建前”文件。

最终版本改为从 `今汐_夜晚湖畔.blend` 的原始 70,257 顶点骨骼网格重建。源文件第 100 帧保留 76 根非默认姿势骨骼，角色根节点位置为 `(1, -7, 0)`、Z 旋转约 `235°`，即用户原先摆好的回眸姿势。

### 5. 胸衣/腰部被错误拆进 Cloth，造成“身体是空的”

角色是游戏模型，服装覆盖处并没有一套完整、封闭的裸体躯干。旧筛选按材质把胸衣、腰部装饰和裙片一起从可见模型拆进 Cloth；这些上身部件一移动，下面自然会露出空洞。这不是渲染法线问题，而是解算区域选择错误。

最终筛选只允许 `纱内侧`、`纱外侧` 中位于角色后方、向腰部以下延伸且面数足够的 5 个大连通片参与 Cloth。胸衣、腹部、前裙和装饰全部保留在 `CLOTH_REBUILD_BODY_STATIC`，所以解算后身体不再被掏空。

### 6. 碰撞体双层壳把后摆横向弹飞

皮肤碰撞体原来叠加了 `Solidify`，同时 Cloth 距离为 `0.006 m`、身体内外厚度各为 `0.02 m`。后纱在初始姿势与这层厚壳局部相交，求解器会优先把布料向侧面推出，而不是让它在重力下下垂。

最终碰撞体只包含 `皮肤` 材质的 9,145 顶点/15,802 面，不包含头发、饰品和静态服装；移除 `Solidify`，改为外侧 `0.004 m`、内侧 `0.002 m`、Cloth 距离 `0.002 m`。80 帧对照确认后纱由向后斜伸转为沿腿后向下形成分层褶皱。

## 最终实现

- Cloth 对象：`CLOTH_REBUILD_SKIRT`。
- Cloth Modifier：`CLOTH_REBUILD_SKIRT`。
- 网格：3,234 顶点、5,682 面、5 个后侧纱片组件。
- 姿势源：`今汐_夜晚湖畔.blend` 第 100 帧，76 根非默认姿势骨骼。
- Pin：92 个顶部点，权重 `1.0`。
- 自由点：3,142 个。
- 可见身体：`CLOTH_REBUILD_BODY_STATIC`，保持回眸姿势。
- 身体碰撞体：`CLOTH_REBUILD_BODY_COLLIDER`。
- 碰撞体与骨架：烘焙后仅隐藏视口显示，不删除。
- Cloth Quality：`7`。
- Mass：`0.25`。
- Time Scale：`0.5`。
- 空气阻尼：`15.0`。
- 碰撞距离：`0.002`。
- 身体碰撞厚度：外侧 `0.004`、内侧 `0.002`。
- 身体碰撞阻尼：`0.35`。
- 自碰撞：关闭。源网格包含初始重叠的多层薄片，全部开启会引入不稳定。
- 缓存范围：1–120 帧，步长 1，磁盘缓存。

## 验证结果

- 已从磁盘重新打开最终 Blend 验证：`is_baked=True`、`use_disk_cache=True`。
- 磁盘缓存共 120 个文件，约 10.7 MB。
- 1、80、120 帧均无 NaN/Inf。
- 120 帧固定点最大位移：约 `7.1e-7 m`。
- 120 帧自由点平均位移：约 `0.18923 m`，证明回眸姿势下后纱确实参与 Cloth 解算。
- 80–120 帧包围盒稳定并趋于收敛，不再出现旧缓存中最低点掉到地面以下的问题。
- 重开后可见身体存在、碰撞壳与骨架保持隐藏，角色根节点位置和 `235°` 回眸旋转均保持不变。
- 重开验证结果：`passed=true`。

## 交付文件

- 最终 Blend：`D:\software\blender\project\今汐_cloth_rebuild_final.blend`
- 干净姿势源备份：`D:\software\blender\project\今汐_before_cloth_rebuild_posed_source.blend`
- 磁盘缓存：`D:\software\blender\project\blendcache_今汐_cloth_rebuild_final`
- 参数清单：`D:\project\blender_learning\cache\cloth_rebuild_v8\cloth_rebuild_manifest.json`
- 重开验证：`D:\project\blender_learning\validation\cloth_final_reopen_check.json`
- 起始帧渲染：`D:\project\blender_learning\renders\cloth_final_skirt_f001.png`
- 80 帧渲染：`D:\project\blender_learning\renders\cloth_final_skirt_f080.png`
- 120 帧渲染：`D:\project\blender_learning\renders\cloth_final_skirt_f120.png`
- 后侧第 1 帧对照：`D:\project\blender_learning\renders\cloth_rear_v7_f001.png`
- 后侧第 80 帧对照：`D:\project\blender_learning\renders\cloth_rear_v7_f080.png`

## 相关脚本

- `scripts/build_cloth_rebuild_v1.py`：已修正 Pin 权重。
- `scripts/build_cloth_rebuild_pose_v4.py`：从干净第 100 帧回眸姿势重建身体、5 个后纱片和薄皮肤碰撞体。
- `scripts/test_cloth_correct_pin_v4.py`：正确 Pin 的短程/80 帧测试。
- `scripts/bake_cloth_final_v3.py`：已修正 Pin、保存顺序和磁盘缓存流程。
- `scripts/validate_cloth_final.py`：数值、固定点和自由点验证。
- `scripts/reopen_validate_cloth_final.py`：重新打开最终文件后的缓存验证。
- `scripts/finalize_cloth_pose_view.py`：隐藏辅助碰撞壳/骨架并保留可见身体。
- `scripts/render_cloth_final_skirt.py`：1/80/120 帧证据渲染。

## 已知限制

- 自碰撞保持关闭，因此不同重叠裙片之间仍可能有轻微互穿。
- 当前是静态角色姿态上的裙摆重力沉降解算；若以后让骨骼运动，需要让碰撞体随角色动画更新并重新烘焙。
