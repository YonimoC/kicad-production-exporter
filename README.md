# Production File Exporter - KiCad 生产文件一键导出插件

> 版本 **1.1.7** · 兼容 **KiCad 8.0 ~ 11**（SWIG Action Plugin）

## 功能

在 KiCad PCB 编辑器中一键导出生产所需的全部文件：

| 导出项 | 输出文件 | 说明 |
|--------|----------|------|
| GERBER 文件 | `XXX_Gerber/` | 全部铜层（含内层）+ F/B.Paste、F/B.Silkscreen、F/B.Mask、Edge.Cuts |
| 钻孔文件 | `XXX_Gerber/` | Excellon 格式，PTH / NPTH 分离 |
| 丝印图 (PDF) | `XXX_丝印与3D图/XXX_丝印.pdf` | 顶层+底层合并为**单个多页 PDF**（含 Paste/Silkscreen/Mask/Edge.Cuts，底层自动镜像） |
| 坐标文件 (CSV) | `XXX_坐标文件/XXX_坐标.csv` | Pick & Place，单位 mm |
| BOM 物料清单 (XLSX) | `bom-XXX.xlsx` | 由原理图导出并格式化为 XLSX，DNP 项排在后面 |
| 3D STEP 文件 | `XXX_丝印与3D图/XXX_3D.step` | KiCad 8+ |
| 3D 视图 (PNG) | `XXX_丝印与3D图/XXX_3D_顶层.png`、`XXX_3D_底层.png` | **仅 KiCad 9+**（走 `pcb render` 真 3D 渲染） |

> `XXX` 为项目名称（自动从 PCB 文件名提取）

## 安装

### 方式一：PCM 安装（推荐）

从 [Releases](https://github.com/YonimoC/kicad-production-exporter/releases) 下载 `production-exporter.zip`，然后：

KiCad → **插件和内容管理器 (PCM)** → **从文件安装...** → 选择该 zip

### 方式二：手动安装

将整个 `plugins/` 目录（**必须包含 `plugins/lib/`**）复制到 KiCad 用户插件目录：

- **Windows**: `%USERPROFILE%\Documents\KiCad\<版本>\scripts\plugins\`
- **macOS**: `~/Documents/KiCad/<版本>/scripts/plugins/`
- **Linux**: `~/.local/share/kicad/<版本>/scripts/plugins/`

安装后**重启 KiCad**，或通过 **工具 → 外部插件 → 刷新插件** 加载。

## 依赖说明（已内嵌，无需安装）

| 依赖 | 用途 |
|------|------|
| `openpyxl` + `et_xmlfile` | 将 BOM 由 CSV 转换为格式化 XLSX |
| `pypdf` | 将顶层/底层丝印 PDF 合并为多页 PDF |

这些库已内嵌在 `plugins/lib/` 下并由插件自动加载，**不需要** `pip install`。
若内嵌加载失败，BOM 会自动保留为 CSV，不影响其他功能。

## 使用方法

1. 在 KiCad 中打开你的 PCB 工程
2. 点击工具栏上的 **「导出生产文件」** 按钮
3. 在弹出的窗口里勾选要导出的项目（按组排列：**制造文件** / **3D 模型** / **3D 图片**，窗口标题显示插件版本号）
4. 选择目标输出文件夹
5. 确认后等待进度条完成，结束时弹窗给出每一项的成功/失败汇总

## 文件结构

```
production-exporter/
├── plugins/
│   ├── __init__.py
│   ├── production_exporter.py         # 插件主程序
│   ├── icon.png                       # 工具栏图标
│   ├── requirements.txt
│   ├── icons/                         # 主题图标
│   │   ├── icon-light.png
│   │   └── icon-dark.png
│   └── lib/                           # 内嵌依赖（随包发布，无需安装）
│       ├── openpyxl/
│       ├── et_xmlfile/
│       └── pypdf/
├── resources/
│   └── icon.png                       # PCM 图标
├── metadata.json                      # PCM 包元数据
├── package.py                         # 打包脚本
├── generate_icons.py                  # 图标生成脚本
└── README.md
```

## 输出结构示例

```
<你选择的输出目录>/
├── XXX_Gerber/              # GERBER + 钻孔文件
├── XXX_丝印与3D图/           # 丝印 PDF、3D 视图 PNG、3D STEP
├── XXX_坐标文件/             # 坐标 CSV
└── bom-XXX.xlsx             # BOM 物料清单
```

## 原理

插件通过 KiCad 的 SWIG Python 绑定获取当前 PCB 路径，再调用 `kicad-cli` 完成导出：

| 导出项 | kicad-cli 命令 | 兼容性 |
|--------|---------------|--------|
| GERBER | `kicad-cli pcb export gerbers -l <动态层列表>` | KiCad 8+ |
| 钻孔 | `kicad-cli pcb export drill --excellon-separate-th` | KiCad 8+ |
| 丝印图 | `kicad-cli pcb export pdf`（F/B 各导一份后合并） | KiCad 8+ |
| 坐标文件 | `kicad-cli pcb export pos --format csv --units mm` | KiCad 8+ |
| BOM | `kicad-cli sch export bom` | KiCad 8+（需原理图） |
| 3D 视图 PNG | `kicad-cli pcb render --side top\|bottom`（回退 `pcb export pdf`） | KiCad 9+ |
| 3D STEP | `kicad-cli pcb export step --force --subst-models` | KiCad 8+ |

### 3D STEP 的模型路径处理

KiCad 9+ 的 3D 模型库**只提供 `.step`，不再提供 `.wrl`**，而旧工程里的模型引用多为
`${KICADn_3DMODEL_DIR}/xxx.wrl`。插件导出 STEP 时会：

1. **解析模型路径中的 `${VAR}`**：依次尝试进程环境变量 → KiCad 配置（Configure Paths）
   → 当前 KiCad 自带模型库（兼容 `KICAD8_3DMODEL_DIR` 这类旧版本变量名）
   → 依据板内绝对路径推断自定义变量（如 `${KICAD_3RD_PARTY}`）
2. **将找不到的 `.wrl` 引用改写为同名 `.step`**（写临时板文件导出，**不改动你的原工程**）
3. 以 `-D VAR=VALUE` 把变量传给 kicad-cli，并附带 `--subst-models` 兜底

这样旧工程在新版 KiCad 下导出的 STEP 也能包含完整模型，不再出现部分封装丢失。

## 常见问题

**Q：导出汇总里出现 `An error occurred attempting to load the global footprint library table`？**

这是本机 KiCad 全局库表（`fp-lib-table`）的配置问题，与导出产物无关。插件已将其视为
非致命提示：只要 STEP 文件正常生成即判为成功。

**Q：3D 视图 PNG 无法导出？**

该功能需要 **KiCad 9+**（依赖 `kicad-cli pcb render`）。KiCad 8 下该选项不会出现在选择窗口中。

**Q：BOM 没有生成 XLSX？**

请确认 `plugins/lib/` 随插件一起安装。若内嵌依赖加载失败，BOM 会保留为 CSV 兜底。

## 版本历史

- **1.1.7** — STEP 模型路径修复（环境变量解析 + `.wrl` → `.step` 改写）；主窗口显示版本号；导出项分组；窗口按内容自适应尺寸
- **1.1.6** — 更换插件图标
- **1.1.5** — BOM 按 Description 分组、位号范围展开（`D2-D5` → `D2,D3,D4,D5`）；内嵌 openpyxl
- **1.1.4** — 丝印 PDF 顶层+底层合并；内嵌 pypdf
- **1.1.3** — 修复四层板 GERBER 内层丢失；铜层检测；DNP 支持；导出项目选择
- **1.1.2** — 修复 KiCad 8 BOM 数量；钻孔 PTH/NPTH 分离
- **1.1.1** — 修复底层铜层丢失；新增板层识别；UI 优化
- **1.1.0** — 导出进度条
- **1.0.0** — 首个版本

## 许可

MIT License
