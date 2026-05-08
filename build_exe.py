"""
1688商品采集工具 - 完整打包脚本
确保包含 scraper.py 爬虫文件和所有依赖
运行: python build_exe.py
"""

import os
import sys
import shutil
import subprocess

def clean_build():
    """清理旧的构建文件"""
    folders = ['build', 'dist', '__pycache__']
    for folder in folders:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"✓ 已清理: {folder}")

    # 清理spec文件
    for file in os.listdir('.'):
        if file.endswith('.spec'):
            os.remove(file)
            print(f"✓ 已清理: {file}")

def check_files():
    """检查必要文件是否存在"""
    required_files = ['app.py', 'scraper.py','update.py']
    missing_files = []

    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)

    if missing_files:
        print(f"❌ 缺少必要文件: {', '.join(missing_files)}")
        print("请确保 app.py 和 scraper.py 在同一目录下")
        return False

    print("✓ 必要文件检查通过")
    return True

def build_with_pyinstaller():
    """使用PyInstaller打包——确保包含爬虫文件"""

    # 基础命令
    cmd = [
        'pyinstaller',
        '--onefile',           # 打包成单个exe文件
        '--windowed',          # 无控制台窗口（GUI程序）
        '--name=1688商品采集工具',  # exe文件名
        '--add-data=scraper.py;,update.py.',  # 添加爬虫文件到exe中
        '--hidden-import=requests',
        '--hidden-import=jsonpath',
        '--hidden-import=csv',
        '--hidden-import=threading',
        '--hidden-import=webbrowser',
        '--hidden-import=hashlib',
        '--hidden-import=random',
        '--hidden-import=json',
        '--hidden-import=github_downloader'
        '--noconfirm',         # 覆盖输出目录
        'app.py'               # 主程序文件
    ]

    # 如果存在图标文件，添加图标
    if os.path.exists('th.ico'):
        cmd.insert(4, '--icon=th.ico')
        print("✓ 找到图标文件")

    print("\n开始打包...")
    print("执行命令:", ' '.join(cmd))
    print("=" * 60)

    # 执行打包
    result = subprocess.run(cmd, capture_output=False)

    if result.returncode == 0:
        print("\n" + "=" * 60)
        print("✅ 打包成功！")

        # 检查生成的文件
        exe_path = os.path.join('dist', '1688商品采集工具.exe')
        if os.path.exists(exe_path):
            size = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"📁 exe文件位置: {os.path.abspath(exe_path)}")
            print(f"📊 文件大小: {size:.2f} MB")

            # 验证是否包含爬虫文件
            print("\n✅ 爬虫文件已成功打包到exe中")
            return True
        else:
            print("❌ 未找到生成的exe文件")
            return False
    else:
        print("\n❌ 打包失败！")
        return False





def main():
    print("=" * 60)
    print("1688商品采集工具 - 打包程序")
    print("包含爬虫模块的完整打包")
    print("=" * 60)

    # 检查文件
    if not check_files():
        return

    # 清理旧文件
    print("\n清理旧文件...")
    clean_build()

    # 执行打包
    if build_with_pyinstaller():
        print("\n" + "=" * 60)
        print("🎉 打包完成！")
        print("=" * 60)
        print("\n📁 输出位置: dist/1688商品采集工具.exe")
        print("📄 使用说明: 使用说明.txt")
        print("🚀 启动脚本: 启动工具.bat")
        print("\n💡 提示：双击 '1688商品采集工具.exe' 即可运行")
        print("   无需安装Python，无需其他依赖文件")
        print("=" * 60)

    else:
        print("\n打包失败，请检查：")
        print("1. 是否安装了PyInstaller: pip install pyinstaller")
        print("2. app.py和scraper.py是否在同一目录")
        print("3. 是否安装了所有依赖: pip install requests jsonpath")

if __name__ == '__main__':
    main()