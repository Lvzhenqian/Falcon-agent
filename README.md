## open-falcon windows客户端源码

基于python 2.7

出现greenlet模块错误：
pip install greenlet flask apscheduler psutil==3.4.2


hook-ctypes.macholib.py 是作用于导入apscheduler模块。

编译命令：
pyinstaller --name agent --onefile \
            --workpath D:/work/build --distpath D:/ \
            --specpath D:/work --upx-dir D:/upx394w \
            --hidden-import greenlet --additional-hooks-dir=. AppMain.py



