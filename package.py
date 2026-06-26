"""
打包脚本：将插件打包为 PCM 可安装的 ZIP 文件。

用法:
    python package.py              → 生成 production-exporter.zip
    python package.py --install    → 打包并复制到 KiCad PCM 缓存目录

生成的 ZIP 可以直接通过 PCM 的「从文件安装...」进行本地安装。
"""

import os
import sys
import zipfile
import hashlib
from pathlib import Path


def create_zip(source_dir: str, output_zip: str) -> str:
    """创建符合 PCM 规范的 ZIP 包。"""
    source = Path(source_dir)
    output = Path(output_zip)

    files_to_pack = [
        ("metadata.json", source / "metadata.json"),
        ("plugins/__init__.py", source / "plugins" / "__init__.py"),
        ("plugins/production_exporter.py", source / "plugins" / "production_exporter.py"),
        ("plugins/icon.png", source / "plugins" / "icon.png"),
        ("plugins/requirements.txt", source / "plugins" / "requirements.txt"),
        ("resources/icon.png", source / "resources" / "icon.png"),
    ]

    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
        for arcname, filepath in files_to_pack:
            if filepath.exists():
                zf.write(filepath, arcname)
                print(f"  ✓ 添加: {arcname}")
            else:
                print(f"  ⚠ 跳过: {arcname} (文件不存在)")

    # 计算 SHA256
    sha256 = hashlib.sha256(output.read_bytes()).hexdigest()
    size = output.stat().st_size
    print(f"\n打包完成: {output}")
    print(f"  文件大小: {size:,} 字节")
    print(f"  SHA256:   {sha256}")

    return sha256


def update_metadata_with_hash(metadata_path: str, sha256: str, size: int):
    """将 SHA256 和文件大小写入 metadata.json（用于仓库提交）。"""
    import json
    path = Path(metadata_path)
    data = json.loads(path.read_text(encoding="utf-8-sig"))

    for ver in data.get("versions", []):
        ver["download_sha256"] = sha256
        ver["download_size"] = size

    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=4) + "\n",
        encoding="utf-8"
    )
    print(f"  ✓ 已更新 metadata.json 中的 SHA256 和文件大小")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="打包 KiCad PCM 插件")
    parser.add_argument("--install", action="store_true",
                        help="打包后复制到 KiCad PCM 本地缓存目录")
    parser.add_argument("--update-metadata", action="store_true",
                        help="自动更新 metadata.json 中的 SHA256")
    args = parser.parse_args()

    script_dir = Path(__file__).parent.resolve()
    output_zip = script_dir / "production-exporter.zip"

    print("=" * 50)
    print("  KiCad PCM 插件打包工具")
    print("=" * 50)

    sha256 = create_zip(str(script_dir), str(output_zip))

    if args.update_metadata:
        update_metadata_with_hash(
            str(script_dir / "metadata.json"),
            sha256,
            output_zip.stat().st_size
        )

    if args.install:
        # 复制到 KiCad PCM 缓存，方便直接安装
        kicad_versions = ["8.0", "9.0", "10.0", "11.0"]
        home = Path.home()

        for ver in kicad_versions:
            if sys.platform == "win32":
                cache_dir = home / "AppData" / "Local" / "KiCad" / ver / "pcm_cache"
            elif sys.platform == "darwin":
                cache_dir = home / "Library" / "Caches" / "KiCad" / ver / "pcm_cache"
            else:
                cache_dir = home / ".cache" / "kicad" / ver / "pcm_cache"

            if cache_dir.parent.parent.exists():
                cache_dir.mkdir(parents=True, exist_ok=True)
                import shutil
                dest = cache_dir / "production-exporter.zip"
                shutil.copy2(output_zip, dest)
                print(f"  ✓ 已复制到: {dest}")

    print(f"\n★ 在 KiCad 中安装：")
    print(f"   PCM → 从文件安装... → 选择: {output_zip}")


if __name__ == "__main__":
    main()
