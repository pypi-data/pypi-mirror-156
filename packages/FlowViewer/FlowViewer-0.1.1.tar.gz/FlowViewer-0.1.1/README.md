# ✨️简介

FlowViewer 是一个基于 python 的 Chrome 浏览器数据包监测器。

它可以异步监听浏览器收发数据，实时返回结果供同步程序使用。

**使用文档：** 📒[点击打开](http://g1879.gitee.io/flowviewer)

**联系邮箱：**  g1879@qq.com

**QQ群：** 897838127

# 📕背景

许多网页的数据来自接口，在网站使用过程中动态加载，如使用 JS 加载内容的翻页列表。

这些数据通常以 json 形式发送，浏览器接收后，对其进行解析，再加载到 DOM 相应位置。

做数据采集的时候，我们往往从 DOM 中去获取解析后数据的，可能存在 数据不全、加载响应不及时、难以判断加载完成等问题。

使用本库，可把自动化与数据包检测结合起来，通过网络数据状况配合操作动作，使开发更便利，程序可靠性更高。

# 🍀 特性

- 轻便，使用简单

- 无侵入式检测，手动、自动程序都可使用

- 可设置检测目标、数量、时间

- 可同步使用检测到的数据

- 可自动搜索 Chrome 进程，便于监听 selenium 打开的未知端口浏览器

# 🎇简单示例

这个示例简单介绍一下监听器的工作方式，具体用法看后面的章节。

```python
from FlowViewer import Listener

listener =Listener(9222)  # 创建监听器，监听9222端口的浏览器
listener.set_targets('JobSearchResult.aspx')  # 设置需要监听的url

listener.listen(count=10)  # 开始监听，接收到10条目标url的请求后停止

for i in listener.steps():
    print(i[0].body)  # 打印实时打印监听到的内容

listener.stop()  #停止监听
```

# 🛠使用方法

[点击跳转到使用手册](http://g1879.gitee.io/flowviewer)

# 🖐🏻 免责声明

请勿将 FlowViewer 应用到任何可能会违反法律规定和道德约束的工作中,请友善使用 FlowViewer，遵守蜘蛛协议，不要将 FlowViewer 用于任何非法用途。如您选择使用 FlowViewer 即代表您遵守此协议，作者不承担任何由于您违反此协议带来任何的法律风险和损失，一切后果由您承担。

# ☕ 请我喝咖啡

如果本项目对您有所帮助，不妨请作者我喝杯咖啡 ：）

![](https://gitee.com/g1879/DrissionPage-demos/raw/master/pics/code.jpg)
