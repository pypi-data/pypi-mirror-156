from setuptools import setup,find_packages


setup(
    name="UI_dep_test",                                     # 包的分发名称，使用字母、数字、_、-
    version="0.0.1",                                        # 版本号, 版本号规范：https://www.python.org/dev/peps/pep-0440/
    author="MYZY",                                       # 作者名字
    author_email="elton.tian@myzygroup.com",                      # 作者邮箱
    description="",                            # 包的简介描述
    packages=find_packages(),# 如果项目由多个文件组成，我们可以使用find_packages()自动发现所有包和子包，而不是手动列出每个包，在这种情况下，包列表将是example_pkg
    url="https://github.com/",
    classifiers=[                                           # 关于包的其他元数据(metadata)
        "Programming Language :: Python :: 3",              # 该软件包仅与Python3兼容
        "License :: OSI Approved :: MIT License",           # 根据MIT许可证开源z
        "Operating System :: OS Independent",               # 与操作系统无关
    ],
    install_requires=[],  # 依赖的包
    package_data={  # Optional
            "dbr":['CommonServiceLocator.dll', 'ErrorHandler.dll','GalaSoft.MvvmLight.dll','GalaSoft.MvvmLight.Extras.dll','GalaSoft.MvvmLight.Platform.dll',
                   'Hsc.dll','imo.ico','log4net.dll','logo.png','Newtonsoft.Json.dll','PresentationFramework.Aero2.dll','StationNetCore.dll',
                   'System.Windows.Interactivity.dll','version.txt','WPFMessageBox.dll','Xceed.Wpf.DataGrid.dll','Xceed.Wpf.Toolkit.dll']
        },
    python_requires='>=3'
)
