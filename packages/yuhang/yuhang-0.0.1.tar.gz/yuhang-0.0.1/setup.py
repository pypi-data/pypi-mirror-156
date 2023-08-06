import setuptools
import yuhang


setuptools.setup(
    # 项目的名称(宇航)
    name="yuhang",
    #项目的版本
    version=yuhang.__version__,
    entry_points={
        'console_scripts': [
            'yuhang=yuhang.cli.calc:add',
            'yuhang-poc=yuhang.cli.calc:sub',
        ],
    },
    # python版本描述
    python_requires='>=3.6.0',
    # 项目的作者
    author="查米刘",
    # 作者的邮箱
    author_email="liucm421@163.com",
    # 项目描述
    description="简单的加减运算上传测试",
    # 关键词？
    keywords=['laipvt'],
    # 项目的长描述
    long_description="简单的加减运算上传测试",
    # 以哪种文本格式显示长描述
    long_description_content_type="text/markdown",
    # 所需要的依赖
    install_requires=[],  # 比如["flask>=0.10"]
    # 项目主页
    url="https://www.yuhang.com",
    # 项目中包含的子包，find_packages() 是自动发现根目录中的所有的子包。
    packages=setuptools.find_packages(),
    # 其他信息，这里写了使用 Python3，MIT License许可证，不依赖操作系统。
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)