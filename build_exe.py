"""
1688商品采集工具 - 修正版打包脚本
运行: python build_exe.py
"""

import os
import shutil
import subprocess

def clean_build():
    """清理旧的构建文件"""
    folders = ['build', 'dist', '__pycache__']
    for folder in folders:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"✓ 已清理: {folder}")

    # 清理 spec 文件（使用 '.' 表示当前目录）
    for file in os.listdir('.'):
        if file.endswith('.spec'):
            os.remove(file)
            print(f"✓ 已清理: {file}")

def check_files():
    """检查必要文件是否存在"""
    required = ['app.py', 'scraper.py', 'update.py']
    missing = [f for f in required if not os.path.exists(f)]
    if missing:
        print(f"❌ 缺少文件: {', '.join(missing)}")
        return False
    print("✓ 必要文件检查通过")
    return True

def build_with_pyinstaller():
    """使用 PyInstaller 打包"""
    # 基础命令（注意 --add-data 格式：源文件;目标目录）
    cmd = [
        'pyinstaller',
        '--onefile',               # 单文件
        '--windowed',              # 无控制台窗口
        '--name=1688商品采集工具',  # exe文件名
        '--add-data=scraper.py;.',   # 将 scraper.py 打包到 exe 根目录
        '--add-data=update.py;.',    # 将 update.py 打包到 exe 根目录
        '--hidden-import=requests',
        '--hidden-import=jsonpath',
        '--hidden-import=csv',
        '--hidden-import=threading',
        '--hidden-import=webbrowser',
        '--hidden-import=hashlib',
        '--hidden-import=random',
        '--hidden-import=json',
        '--hidden-import=github-content-downloader',
        '--noconfirm',
        'app.py'
    ]

    # 添加图标（如果有）
    if os.path.exists('th.ico'):
        cmd.insert(4, '--icon=th.ico')
        print("✓ 找到图标文件 th.ico")

    print("\n开始打包...")
    print("执行命令:", ' '.join(cmd))
    print("=" * 60)

    result = subprocess.run(cmd, capture_output=False)

    if result.returncode == 0:
        print("\n✅ 打包成功！")
        exe_path = os.path.join('dist', '1688商品采集工具.exe')
        if os.path.exists(exe_path):
            size = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"📁 输出位置: {os.path.abspath(exe_path)}")
            print(f"📊 文件大小: {size:.2f} MB")
            return True
        else:
            print("❌ 未找到生成的 exe 文件")
            return False
    else:
        print("\n❌ 打包失败！")
        return False

def main():
    print("=" * 60)
    print("1688商品采集工具 - 打包程序")
    print("=" * 60)
    if not check_files():
        return
    print("\n清理旧文件...")
    clean_build()
    if build_with_pyinstaller():
        print("\n🎉 打包完成！")
        print("📁 输出位置: dist/1688商品采集工具.exe")
        print("💡 双击即可运行，无需安装 Python")
    else:
        print("\n打包失败，请检查：")
        print("1. 是否安装 PyInstaller: pip install pyinstaller")
        print("2. 所有依赖是否已安装: pip install requests jsonpath github_downloader")
        print("3. github_downloader 模块是否存在（update.py 中使用了它）")

if __name__ == '__main__':
    main()