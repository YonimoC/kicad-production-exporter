# Production File Exporter - KiCad 生产文件一键导出插件

> 兼容 **KiCad 8.0+**（SWIG Action Plugin）

## 功能

在 KiCad PCB 编辑器中一键导出生产所需的全部文件：

| 导出内容 | 输出位置 |
|----------|----------|
| GERBER 文件 + 钻孔文件 | `XXX_Gerber/` |
| 顶层丝印图 (PDF) | `XXX_丝印与3D图/` |
| 底层丝印图 (PDF) | `XXX_丝印与3D图/` |
| 3D 顶层视图 (PNG) | `XXX_丝印与3D图/` |
| 3D 底层视图 (PNG) | `XXX_丝印与3D图/` |
| 3D STEP 模型 | `XXX_丝印与3D图/` |
| 坐标文件 (Pick & Place CSV) | `XXX_坐标文件/` |
| BOM 物料清单 (XLSX) | `bom-XXX.xlsx` |

> `XXX` 为项目名称（自动从 PCB 文件名提取）

## 安装方法

### 直接放入插件目录（推荐）

将 `production_exporter.py` 和 `icon.png` 复制到 KiCad 插件目录：

- **Windows**: `%USERPROFILE%\Documents\KiCad\8.0\scripts\plugins\`
- **macOS**: `~/Documents/KiCad/8.0/scripts/plugins/`
- **Linux**: `~/.local/share/kicad/8.0/scripts/plugins/`

> 如果是 KiCad 9/10/11，请将路径中的 `8.0` 替换为对应版本号。

安装后，**重启 KiCad** 或通过菜单 **工具 → 外部插件 → 刷新插件** 来加载插件。

### BOM 导出为 XLSX（可选）

插件默认会将 BOM 导出为格式化的 `.xlsx` 文件，需要 `openpyxl` 库：

```bash
# 使用 KiCad 自带的 Python 安装
# Windows:
C:\Program Files\KiCad\8.0\bin\python.exe -m pip install openpyxl

# macOS:
/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3 -m pip install openpyxl
```

如果未安装 `openpyxl`，BOM 将保留为 CSV 格式，不影响其他功能。

## 使用方法

1. 在 KiCad 中打开你的 PCB 项目
2. 点击工具栏上的 **「导出生产文件」** 按钮
3. 选择目标输出文件夹
4. 确认导出内容，点击「是」
5. 等待导出完成

## 文件结构

```
production-exporter/
├── plugins/
│   ├── __init__.py                    # 包初始化
│   ├── production_exporter.py         # 插件主程序
│   ├── icon.png                       # 工具栏图标 (24×24)
│   ├── requirements.txt
│   └── icons/                         # 备用图标
│       ├── icon-light.png
│       └── icon-dark.png
├── resources/
│   └── icon.png                       # PCM 图标 (64×64)
├── metadata.json                      # PCM 包元数据
├── generate_icons.py                  # 图标生成脚本
└── README.md
```

## 原理

插件通过 KiCad 的 SWIG Python 绑定获取当前 PCB 文件路径，然后调用 `kicad-cli` 命令行工具完成各项导出：

| 导出项 | kicad-cli 命令 | 兼容性说明 |
|--------|---------------|------------|
| GERBER | `kicad-cli pcb export gerber` | KiCad 8+ |
| 钻孔 | `kicad-cli pcb export drill` | KiCad 8+ |
| 丝印图 | `kicad-cli pcb plot` | KiCad 8+ |
| 3D 视图 PNG | `kicad-cli pcb render` (优先) → `pcb plot` (回退) | KiCad 9+ 真3D渲染 / K8 复合图层 |
| 坐标文件 | `kicad-cli pcb export pos` | KiCad 8+ |
| BOM | `kicad-cli sch export bom` | KiCad 8+ |
| 3D STEP | `kicad-cli pcb export step` | KiCad 8+ |

## 许可

MIT License
