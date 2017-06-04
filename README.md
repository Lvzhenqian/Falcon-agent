## open-falcon windows客户端源码

基于python 3.5.2 

用pyinstaller 3.3 dev编译

安装：pip install https://github.com/pyinstaller/pyinstaller/tarball/develop

hook-ctypes.macholib.py 是作用于导入apscheduler模块。

编译命令：
pyinstaller --onefile \
            --name agent --paths .\api;.\AutoUpdate;.\Client;.\Metric;.\PluginManage;.\util  \
            --workpath D:\work\build --distpath D:\ --specpath D:\work --upx-dir D:\upx394w \
            --hidden-import greenlet \
            --additional-hooks-dir .\ AppMain.py


出现greenlet模块错误：
pip install greenlet

出现Syntax error: 'yield' inside async function (Python 3.5.1)：
pip install jinja2==2.8.1