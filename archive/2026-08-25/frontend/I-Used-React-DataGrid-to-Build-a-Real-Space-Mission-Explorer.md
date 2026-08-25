---
title: "我用 React DataGrid 做了一个真实的太空任务浏览器"
title_en: "I Used React DataGrid to Build a Real Space Mission Explorer"
source_url: https://dev.to/hadil/i-used-react-datagrid-to-build-a-real-space-mission-explorer-4g8b
author: Hadil Ben Abdallah
translated_at: 2026-08-25
tech_domain: frontend
tags: [frontend, react, datagrid, typescript, ui]
cover_image: https://media2.dev.to/dynamic/image/width=1200,height=627,fit=cover,gravity=auto,format=auto/https%3A%2F%2Fdev-to-uploads.s3.us-east-2.amazonaws.com%2Fuploads%2Farticles%2Fo2cju3bl5dyv99bq0tyx.png
---

# 我用 React DataGrid 做了一个真实的太空任务浏览器

原文链接：<https://dev.to/hadil/i-used-react-datagrid-to-build-a-real-space-mission-explorer-4g8b>

原文作者：Hadil Ben Abdallah

![文章头图](https://media2.dev.to/dynamic/image/width=1200,height=627,fit=cover,gravity=auto,format=auto/https%3A%2F%2Fdev-to-uploads.s3.us-east-2.amazonaws.com%2Fuploads%2Farticles%2Fo2cju3bl5dyv99bq0tyx.png)

作者：[Hadil Ben Abdallah](https://dev.to/hadil)

**我此前通读了 React DataGrid 的文档和特性列表，还写过一篇[《React DataGrid：免费开源、带企业版的 React 数据表格（AG Grid 的替代品）》](https://dev.to/hadil/react-datagrid-a-free-open-source-react-data-grid-with-an-enterprise-edition-an-ag-grid-5beg)。这次我想像在真实项目里用其他数据表格那样用它：从真实数据集出发，围绕它做有用的交互，用大量记录把表格顶满，看看哪里会出问题。**

于是我做了一个**太空任务与卫星浏览器（Space Mission & Satellite Explorer）**——一个小型的、飞行动力学风格的 Web 应用，可以按机构、目的地、任务类型、年代浏览各种太空任务。

项目背后是一个 **10 万条任务的在线档案库**，交互分析则由 **1200 行的客户端工作集**驱动。这让我有机会测试远不止基础排序和分页的东西：过滤、分面搜索（faceted search）、分组、透视（pivoting）、行固定、自定义单元格渲染、虚拟滚动，以及服务端无限滚动。

围绕同一份数据我还做了另外两个页面：一个做聚合与可视化的**任务分析（Mission Analytics）**页，以及一个用树形数据（Tree Data）呈现单个任务时间线的**任务详情（Mission Details）**页。

这篇文章记录的就是构建过程中发生的事——从装好 React DataGrid、配第一批列，到跑 10 万条记录，再到最后判断下一个数据密集型 React 项目还会不会选它。

* * *

## [TL;DR](#tldr)

我用 [React DataGrid](https://reactdatagrid.dev/) 做了一个太空任务浏览器，看它在真实应用里表现如何。

项目用 **1200 行客户端数据集**做交互分析，另有 **10 万行在线档案**通过服务端无限滚动加载。

过程中用到的特性包括：

*   多列排序
*   快速搜索
*   分面过滤
*   行分组
*   行固定
*   透视表（Pivot Table）构建器
*   自定义单元格渲染
*   虚拟滚动
*   CSV/Excel 导出
*   用 Tree Data 做任务时间线

集成比我预想的顺利。API 一上手就觉得眼熟；大多数特性照文档示例稍作调整就能用，在小工作集和完整档案之间切换也一直保持流畅。

当然也有几处要多花功夫，后面会讲。但总体上，亲手做完这个项目，我对 React DataGrid 的印象比只读特性列表要好得多。

* * *

## [我做了什么：一个太空任务浏览器](#what-i-built-a-space-mission-explorer)

我把这个项目叫 **Orbital Index / 任务数据终端**。

想法很简单：拿一大批虚构的太空任务记录，把它变成开发者能想象自己真会用的东西——一个可搜索、可过滤的界面，按机构、目的地、状态、任务类型、发射日期、时长、成本和年代浏览任务。

我刻意没有再做一个千篇一律的 CRUD 仪表盘，因为这份数据集天然会制造出「需要数据表格才好解决」的那类问题。

一条任务记录有足够多的结构化字段，让过滤和排序有意义。任务可以按机构或目的地分组，成本和时长可以聚合。而且任务本身有天然的层级：

**发射 → 地球轨道 → 地月转移 → 月球轨道 → 下降与着陆 → 表面作业 → 返回地球**

最后这一点也给了我一个测试 Tree Data 的正当理由，而不是为了凑特性清单硬加。

应用最终有三个主页面：

*   **任务浏览器（Mission Explorer）：** 主数据表格界面，负责搜索、过滤、分组、透视、编辑和浏览任务档案。
*   **任务分析（Mission Analytics）：** 以图表为主的视图，把同一份任务数据变成成功率、机构对比、目的地分布、时长统计和成本分析。
*   **任务详情（Mission Details）：** 单个任务视图，包含元数据、乘组与设备信息、相关档案，以及层级式的任务时间线。

React DataGrid 的测试大多发生在浏览器页。分析页复用同一份 1200 行工作集和聚合逻辑来出图，详情页则给了我一个完全不同的场景来试表格的层级数据能力。

技术栈是 **React**、**TypeScript**、**Tailwind CSS**、**React DataGrid**、任务数据集，外加一个图表库做分析视图。

进入正题前先交代一句：项目初始搭建有一小部分是我 vibe-coding 出来的，免得把大块时间耗在和这次实验无关的样板代码上。

这里的目标不是证明我能从零手写一个完整的太空任务网站，而是把时间花在真实项目里实际使用 React DataGrid，看它怎么应对数据、交互和规模。

项目刻意控制在「从头到尾能看懂」的大小，但又足够复杂，复杂到一个朴素的 `<table>` 会开始吃力。

你可以自己打开项目玩玩：

[在线 Demo 👀](https://orbitalindex.vercel.app/)

[GitHub 仓库 ⭐](https://github.com/Hadil-Ben-Abdallah/space-mission-explorer)

* * *

## [装好 React DataGrid](#setting-up-react-datagrid)

项目结构就位后，我想先让表格跑起来，再去管界面的其他部分。我从开源包开始，第一版渲染刻意保持简单。

安装很直接：

```
npm install react-open-source-grid
```

然后引入库的样式表：

```
import 'react-open-source-grid/dist/lib/index.css';
```

第一次测试只放了几个任务字段：

```
const columns: Column[] = [
  { field: 'mission', headerName: 'Mission', width: 200 },
  { field: 'agency', headerName: 'Agency', width: 120 },
  { field: 'status', headerName: 'Status', width: 140 },
  { field: 'launchDate', headerName: 'Launch Date', width: 130 },
  { field: 'destination', headerName: 'Destination', width: 150 },
];
```

接着我为**任务**、**机构**、**状态**、**发射日期**、**目的地**、**任务类型**和**时长**定义了带类型的列，把数据集映射上去。

到这一步，API 已经很眼熟了，不需要花时间学一套完全陌生的表格模型。

写的过程中我一直开着 React DataGrid 的 [GitHub 仓库](https://github.com/bhushanpoojary/react-open-source-datagrid)和[文档](https://reactdatagrid.dev/)，毕竟这是一次上手实测。

* * *

## [搭建任务浏览器](#building-the-mission-explorer)

我不想只塞几行数据、然后宣称「我用过数据表格了」。我要足够多的数据和交互，才能看出这个组件能不能扛住真实应用里的复杂度。

最终我用了两种数据集模式：**1200 行的客户端工作集**，用于交互分析和虚拟滚动；以及 **10 万行的在线档案**，通过服务端无限滚动按需加载。

这两种模式的差别很有用：同一份任务数据有了两种不同的用法，而不是为了跑分硬造一个巨型数据集。

![任务浏览器页面](https://media2.dev.to/dynamic/image/width=800%2Cheight=%2Cfit=scale-down%2Cgravity=auto%2Cformat=auto/https%3A%2F%2Fdev-to-uploads.s3.us-east-2.amazonaws.com%2Fuploads%2Farticles%2F9phwvx6bo6dp3c904cju.png)

任务浏览器页面

### [排序、过滤和搜索](#sorting-filtering-and-search)

我先从任何数据表格都该有的交互开始。列头支持排序，包括多列排序，所以「先按机构、再按发射日期排任务」这种事不用自己写排序逻辑。

过滤方面有全局搜索框和单列过滤器两套。全局搜索适合快速找到某个任务、机构或目的地；列头下方的过滤器则在需要收窄某个字段时给我更多控制。

对这份数据集来说，侧边栏过滤器更好用。**分面搜索（faceted search）**面板可以按机构、状态、目的地、任务类型和年代过滤，不用什么都往搜索框里敲。每个分面还带实时计数，比如 **NASA (265)**、**Successful (839)**，一眼就能看出每个过滤条件对应多少数据。

如果我想只看「1990 年代 NASA 成功的火星任务」，就可以从几个维度同时收窄数据集，而不用自己在表格外面搭一套复杂的过滤 UI。

我还测了列宽调整和列拖拽排序，把浏览器适配到不同屏幕和工作流时，两者都很顺手。

![用 React DataGrid 做排序、过滤和搜索](https://media2.dev.to/dynamic/image/width=800%2Cheight=%2Cfit=scale-down%2Cgravity=auto%2Cformat=auto/https%3A%2F%2Fdev-to-uploads.s3.us-east-2.amazonaws.com%2Fuploads%2Farticles%2F6kmk7aucsyk97b9ele54.png)

排序、过滤和搜索

### [分组与固定](#grouping-and-pinning)

过滤跑通后，我想看看表格怎么处理更偏分析的交互。

React DataGrid 支持把列拖进表格上方的分组区。也就是说，我可以先按「机构」给任务分组，再按另一个字段进一步组织，而不是把每条任务都当成孤立的一行。

![用 React DataGrid 做分组与固定](https://media2.dev.to/dynamic/image/width=800%2Cheight=%2Cfit=scale-down%2Cgravity=auto%2Cformat=auto/https%3A%2F%2Fdev-to-uploads.s3.us-east-2.amazonaws.com%2Fuploads%2Farticles%2Fg43z1fjrq3sxbj2g7m2b.png)

分组与固定

我还把四条参考任务固定在表格顶部。这功能不大，但在大数据集里非常实用：重要记录一直可见，我可以放心滚动浏览档案的其余部分。

### [透视表](#pivot-table)

浏览器页最有意思的部分是内置的**透视表（Pivot Table）**构建器。

我不用为每种分析手写聚合逻辑，只要选好**行分组字段**、**透视列**、**值列**和**聚合方式**，直接在界面上应用配置即可，还能开关小计行和总计列。

比如，把任务按机构分组、按目的地透视，再对时长或成本做聚合。这样表格就从「翻记录的地方」变成了「探索数据集的工具」。

![用 React DataGrid 做透视表](https://media2.dev.to/dynamic/image/width=800%2Cheight=%2Cfit=scale-down%2Cgravity=auto%2Cformat=auto/https%3A%2F%2Fdev-to-uploads.s3.us-east-2.amazonaws.com%2Fuploads%2Farticles%2Fbrhej5db5npk6rc3f3b1.png)

透视表

### [自定义单元格、合计与导出](#custom-cells-totals-and-export)

我还用自定义单元格渲染让表格更好扫读。任务状态不是纯文本，而是彩色徽章：**Successful**、**Planned**、**Partial Success**、**Failed**、**Cancelled**、**in progress** 各有颜色。工作集还带一个合计页脚，聚合时长、成本等数值。

表格周边我加上了生产环境数据表该有的控件：列选择器、CSV 和 Excel 导出、布局重置，以及从 **Ultra Compact** 到 **Comfortable** 的四档密度。

![用 React DataGrid 做自定义单元格与合计](https://media2.dev.to/dynamic/image/width=800%2Cheight=%2Cfit=scale-down%2Cgravity=auto%2Cformat=auto/https%3A%2F%2Fdev-to-uploads.s3.us-east-2.amazonaws.com%2Fuploads%2Farticles%2Fqnirffh7mq1gsgfkiavu.png)

自定义单元格与合计

![用 React DataGrid 做 CSV 和 Excel 导出](https://media2.dev.to/dynamic/image/width=800%2Cheight=%2Cfit=scale-down%2Cgravity=auto%2Cformat=auto/https%3A%2F%2Fdev-to-uploads.s3.us-east-2.amazonaws.com%2Fuploads%2Farticles%2F8pw1jhxwkhskxy1t1b25.png)

CSV 和 Excel 导出

最让我满意的是：分面过滤、分组、透视、固定行、自定义渲染和导出能在同一个界面里组合使用，页面不会散成一堆互不相干的控件。

* * *

## [搭建任务分析页](#building-mission-analytics)

任务浏览器跑通后，我想让这份数据集干点浏览记录之外的事。这就是第二个页面：**任务分析（Mission Analytics）**。

这个页面刻意以图表为先。我没有再摆一张表，而是用浏览器页里同一份任务数据和聚合逻辑，做出一组可视化，回答关于任务历史、机构、目的地和成本的更高层的问题。

页面顶部是四张摘要卡片：

*   **1200** 个任务在范围内
*   **79.6%** 的平均成功率
*   **6691.2 亿美元**的项目总成本
*   **1543 天**的平均任务时长

卡片下面是五个可视化：按年代的发射节奏、机构可靠性、目的地分布、按任务类型的成功率画像，以及成本与任务时长的关系。

![任务分析页面](https://media2.dev.to/dynamic/image/width=800%2Cheight=%2Cfit=scale-down%2Cgravity=auto%2Cformat=auto/https%3A%2F%2Fdev-to-uploads.s3.us-east-2.amazonaws.com%2Fuploads%2Farticles%2Fgzieofm88rb8ts9js6lo.png)

任务分析页面

### [发射节奏与机构可靠性](#launch-cadence-and-agency-reliability)

第一张图看**按年代的发射节奏**：数据集中任务总数和成功任务数在各年代如何变化。

这给档案加了一个历史维度——盯着浏览器里的单条记录是看不出来的。我不再问「哪些任务发射了」，而是开始问「任务活动随时间怎么变」。

接着，**机构可靠性**图对比了 NASA、SpaceX、Roscosmos、ESA、CNSA、ISRO、JAXA、Blue Origin 等机构的发射量和平均成功率。

这里聚合能力就派上用场了。图表并不基于专为仪表盘另造的数据集，而是直接从我在浏览器页里过滤、分组、分析的同一批任务记录推导出来的。

![发射节奏与机构可靠性](https://media2.dev.to/dynamic/image/width=800%2Cheight=%2Cfit=scale-down%2Cgravity=auto%2Cformat=auto/https%3A%2F%2Fdev-to-uploads.s3.us-east-2.amazonaws.com%2Fuploads%2Farticles%2Fv52pk30xm5u0njqyml64.png)

发射节奏与机构可靠性

### [目的地、任务类型与成本](#destination-mission-type-and-cost)

剩下三个可视化看的是同一份数据的不同维度。

**目的地分布**图展示档案里的任务都去了哪：地球轨道、月球、火星、小行星带、深空、木星。

**按任务类型的成功率画像**换了个角度，对比巡视器、轨道器、飞掠、无人着陆器、太空望远镜、采样返回等任务类型的成功率。

最后，**成本 vs 任务时长**散点图让我检查「贵的任务是不是也更久」。每个点代表一个任务，特别烧钱或特别长寿的项目一眼就能挑出来。

有意思的是，这个页面不需要再放一张表格，React DataGrid 依然有用：底层数据集和聚合逻辑还在干活，我只是把结果换成了更容易直观理解的形式。

![目的地、任务类型与成本](https://media2.dev.to/dynamic/image/width=800%2Cheight=%2Cfit=scale-down%2Cgravity=auto%2Cformat=auto/https%3A%2F%2Fdev-to-uploads.s3.us-east-2.amazonaws.com%2Fuploads%2Farticles%2Fr7fhm0vpotbmqzshpmjf.png)

目的地、任务类型与成本

* * *

## [搭建任务详情页](#building-the-mission-details-page)

在完整档案里泡了一阵之后，我想让第三个页面做相反的事：从 **10 万个任务钻到某一个任务**。

示例用的是 **MX-000006，Apollo VIII**。页面把任务的主要信息汇总在一起——发射日期、时长、项目成本、乘组——而不是把一切又塞进一张大表。

![任务详情页面](https://media2.dev.to/dynamic/image/width=800%2Cheight=%2Cfit=scale-down%2Cgravity=auto%2Cformat=auto/https%3A%2F%2Fdev-to-uploads.s3.us-east-2.amazonaws.com%2Fuploads%2Farticles%2Fjrxijo39vzuhwypf582c.png)

任务详情页面

不过这个页面最有意思的部分是**任务时间线**。

### [用 Tree Data 做真实的任务时间线](#using-tree-data-for-a-real-mission-timeline)

任务不是一堆互不相干的字段，它天然有先后结构：先发射，再入轨，然后才是主要作业，依此类推。

所以时间线正适合用**树形数据（Tree Data）**。

我把 Apollo VIII 分成 5 个阶段：

```
Apollo VIII
├── Launch
├── Orbit Insertion
├── Payload Commissioning
├── Operations
└── Deorbit
```

每个阶段有自己的 **COMPLETE** 状态徽章和 `T+` 天数偏移，时间线同时给出任务的层级和时间脉络。

![用 Tree Data 做真实的任务时间线](https://media2.dev.to/dynamic/image/width=800%2Cheight=%2Cfit=scale-down%2Cgravity=auto%2Cformat=auto/https%3A%2F%2Fdev-to-uploads.s3.us-east-2.amazonaws.com%2Fuploads%2Farticles%2Fie1ym6l1uj7wgne1xqez.png)

用 Tree Data 呈现真实任务

这是那种「有了真实应用才显出意义」的特性。我本可以为时间线手写一个嵌套组件，但 Tree Data 天然就映射这种结构化信息。

页面其余部分是**乘组名单**、**载荷与设备**和**相关档案**三个区块，让附加的任务信息随手可查，又不至于把页面变成另一个密密麻麻的数据管理界面。

![乘组名单、载荷与设备、相关档案](https://media2.dev.to/dynamic/image/width=800%2Cheight=%2Cfit=scale-down%2Cgravity=auto%2Cformat=auto/https%3A%2F%2Fdev-to-uploads.s3.us-east-2.amazonaws.com%2Fuploads%2Farticles%2Fe2hxccopw84l3yt4d5sa.png)

乘组名单、载荷与设备、相关档案

到这一步，应用的三个部分已经协同工作：

*   **任务浏览器**负责搜索和操作档案
*   **任务分析**负责从更高层理解数据
*   **任务详情**负责钻进单个任务

比起一张小演示表，这给了我一个好得多的评估环境：真实的过滤、分组、透视、层级数据、自定义渲染和大数据集，全都跑在同一个项目里。

* * *

## [主题与 UI 定制](#theming-amp-ui-customization)

功能跑通之后，我花了些时间让表格真正「长在」应用里。默认外观不是不能用，只是和我想要的深色、青色点缀的**飞行动力学终端**风格不搭。

我用主题变量调整了表格外观，并用自定义单元格渲染做了任务状态徽章。Successful、Planned、Partial Success、Failed、Cancelled、in progress 各用不同颜色，扫读浏览器页轻松了很多。

我还用了四档密度——**Ultra Compact、Compact、Normal、Comfortable**——每行显示的信息量可以调整，不用重排表格布局。

让我欣赏的一点是：做定制不需要跟组件的默认样式搏斗。大部分工作是让 React DataGrid 融入项目的视觉语言，而不是绕开表格本身的限制。

* * *

## [开发体验：哪些容易，哪些费劲](#developer-experience-what-was-easy-and-what-took-more-work)

整体开发体验是这个项目最大的加分项之一。安装到第一个能用的表格上屏，比我预期的快，API 也眼熟。

基础表格跑起来之后，加排序、过滤、分组和透视表构建器都很顺，和文档示例对得上。任务详情页的 Tree Data 实现也一样。我没有一直陷在「怎么让这个库干它不擅长的事」里。

可访问性（accessibility）也是我在使用中留意的方面。我测了键盘导航，也关注了表格的 ARIA 行为。对于我用到的那些冷门特性，文档的示例也够用。

话说回来，不是每个环节都同样省心。越专门的特性越要花时间理解——比排序、过滤这类日常操作费劲。透视表构建器和 Tree Data 配置是我查示例最多、反复琢磨数据该怎么组织的两块。

* * *

## [React DataGrid vs 朴素 HTML 表格：我会怎么选](#react-datagrid-vs-a-basic-html-table-what-i-would-choose)

如果只是展示五行十行的静态数据，我不会上 React DataGrid。朴素的 HTML 表格或轻量 React 表格更简单，也完全够用。

但这个项目是另一回事。

一旦需要 **10 万条任务**、分面搜索、多列排序、分组、透视、Tree Data、自定义单元格渲染和服务端无限滚动，朴素表格意味着这些功能大部分得我自己造。

这正是 React DataGrid 划算的地方：与其把时间耗在搭建和维护表格基础设施上，不如专注应用本身——任务该怎么组织、用户能探索什么、分析该怎么做。

* * *

## [React DataGrid 值得用吗？](#is-react-datagrid-worth-using)

做完这个项目，我认为 React DataGrid 适合那些「数据本身就是用户体验重头戏」的应用。

我会特别考虑用它的场景：

*   数据密集型仪表盘
*   分析类应用
*   管理后台
*   金融类应用
*   企业内部工具
*   大数据集应用
*   过滤或分组逻辑复杂的项目
*   有层级数据的应用
*   需要服务端数据加载的 React 应用

太空任务浏览器是个好测试，因为它同时命中了其中好几条：1200 行客户端工作集做交互分析，10 万条在线档案走服务端无限滚动。

* * *

## [写在最后](#final-thoughts)

做这个太空任务浏览器，让我对 React DataGrid 的认识比光看特性清单深得多。

我拿到一份真实数据集，把它变成 10 万行任务档案的交互式浏览器，围绕它搭了分析页，还用 Tree Data 做了任务时间线——全程不用自己造表格基础设施。

对数据密集型 React 应用来说，这才是最重要的：

**表格应当扛住数据的复杂度，让你专注于构建它之上的产品。**

* * *

感谢阅读！本文作者 [Hadil Ben Abdallah](https://dev.to/hadil)（[LinkedIn](https://www.linkedin.com/in/hadil-ben-abdallah/) / [GitHub](https://github.com/Hadil-Ben-Abdallah) / [X](https://x.com/hadilbnabdallah)）。
