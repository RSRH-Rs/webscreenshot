# HoshinoBot 网页截图插件

这是一个基于 HoshinoBot 的网页截图插件，相比于[隔壁的截图插件](https://github.com/kcn3388/pagecut)，这个插件进行截图的过程中并不会造成堵塞。

## 使用方法

1.clone 本插件：
在 HoshinoBot\hoshino\modules 目录下使用以下命令拉取本项目

```
git clone https://github.com/RSRH-Rs/webscreenshot.git
```

2.依赖：

```
pip install aiohttp~=3.8.4
pip install playwright~=1.32.1
playwright install
```

3.启用模块

在 hoshino\config\_\_bot\_\_.py 文件的 MODULES_ON 加入 'webscreenshot'

然后重启 HoshinoBot

触发关键词：`网页截图`,`网页预览`

当有以 http/https 开头的链接会自动发送网页截图

4.配置文件
在 config.py 里面设置是否开启绿标检测
如果不开，群友发什么网站都会截图(包括色情暴力)

```
qq_certification_status: bool = True  # 是否开启QQ绿标检测
```

## 其他

Linux 和 Windows 都已测过，完美运行~
Linux 安装 playwright 的话看具体提示(貌似是`apt install playwright-dev`，我也忘了，具体看调用 playwright 报错信息)

**渣代码,欢迎提出改进建议~**
