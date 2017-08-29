# open-falcon windows客户端源码
## 基于python 2.7编写
### 需导入的模块
`pip install greenlet flask apscheduler psutil==3.4.2`

### Pyinstaller 编译命令：
`pyinstaller --name agent --onefile --workpath D:/work/build --distpath D:/ --specpath D:/work --upx-dir D:/upx394w --hidden-import greenlet --additional-hooks-dir=. AppMain.py`

### 源码文件说明：
```
AppMain.py                  主程序入口，一般编译时指向的就是这个文件。
AutoInstall.py              自动下载更新，安装插件，主要作用是对比MD5.txt文件并下载安装客户端
BaseMetric                  自动获取系统基础数据，拼凑好后提交
Config.py                   配置文件读取模块，用于读取cfg.json等文件，以便于程序使用
Crond.py                    一个crontab 程序，用于管理定时作业，在到达某个时间内执行某个任务
Hook-ctypes.macholib.py     编译时 Apscheduler 模块时添加的文件，主要编译时pyinstaller要使用。
HttpAPI.py                  一个使用Flask 框架来提供API接口
Manage.py                   扩展程序管理模块，用来读取plugin目录里的 .py 文件，执行并获取其metric
Repo.py                     HBS 固定数据上传使用。
JsonClient.py               提供用于传送数据的JSON客户端。
diskIOmertic.py             调用WMI客户端来获取磁盘IO信息，并加入到BaseMetric里提交。
```


