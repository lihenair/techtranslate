---
title: "框架还重要吗？"
title_en: "Do Frameworks Matter Anymore?"
source_url: https://brookslybrand.com/posts/do-frameworks-matter-anymore/
author: Brooks Lybrand
published_at: 2026-09-16
translated_at: 2026-09-24
tech_domain: frontend
tags: [frontend, react, frameworks, agents, remix]
---

# 框架还重要吗？

原文链接：<https://brookslybrand.com/posts/do-frameworks-matter-anymore/>

原文作者：Brooks Lybrand

作者：[Brooks Lybrand](https://brookslybrand.com/)（[@BrooksLybrand](https://x.com/BrooksLybrand)）

发布于 2026 年 9 月 16 日。

**不是抬杠。我真想想清楚：2026 年，在 vibe coding、agentic programming 的时代，你用哪个 web framework 还重要吗？更要紧的是——我们还该不该做新框架？**

不是抬杠。我真想想清楚：2026 年，在 vibe coding、agentic programming、loop 或 graph 或随便哪种当下最火的图示隐喻工程的时代，你用哪个 web framework，还重要吗？更重要的是（对我和我的兴趣而言），冒着[自己给自己套上 Betteridge 定律](https://en.wikipedia.org/wiki/Betteridge%27s_law_of_headlines)的风险：我们还该不该做新框架？

React 赢了，所以我们还要不要试新东西？

是不是只剩下更多 niche 空间？没人在乎实现细节。没人在乎 `.tsx` 里装了什么。这是打开了试新东西的门，还是「既然无所谓，全行业就永远用最稳的那套」？

大动荡里，我们有机会重思最佳实践（或者像 Remix 那样，再重思一遍），把[一切重新摊上桌面](https://youtu.be/2n41YjR5QfU?t=993)。

[嵌入内容（原站 YouTube）](https://www.youtube.com/watch?v=2n41YjR5QfU)

![嵌入内容（原站 YouTube）](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Do-Frameworks-Matter-Anymore/yt-2n41YjR5QfU.jpg)

不等于一切都会留在桌上——只是留下好的、丢掉坏的、改掉丑的。这篇文章的问题不需要被「驳倒」，值得认真想。

我全职做开源框架三年了，对这个问题很感兴趣。我不是想护自己/护手艺，而是想把活干得更好、也有个像样的职业。我在考虑，也在试图预测（并制造）未来。记住「我可能错」很谦卑；记住别人多半也会错，则挺鼓舞人。

我想把问题和它的含义拆成更基本的零件，再搭出一个值得追求、值得去建的现实版本。为此，先想想「web framework 是什么」会有帮助。这很难——词太虚、太泛，最后你会拿 Flask 比 jQuery 比 React 比 Next.js。不如问：框架提供什么价值。我觉得这句话够用：

**框架为你建网站提供抽象、结构与约束。**

## [想象](#imagine)

> Imagine there's no React  
>  It's easy if you try  
>  No Svelte below us  
>  Above us, only bi(nary)  
>  Imagine all the people  
>  Prompting for today

（抱歉，Svelte，把你换成了「hell」那个韵脚。不是觉得你像地狱，只是好听。）

回到论点，再摊开一点。我现在听到的主流说法是：

> 模型从大概 2025–2026 冬开始够强，能做 agentic programming 之后，我越来越不在乎代码（你也应该）。前端尤其如此——大半是表现层。所以，好看就是好。
>
> 鉴于模型现状，再鉴于 React 已是最主导的 UI 框架，加上很火的 meta-framework Next.js（还有 React Router、TanStack Start 等不错的选择），真没什么必要、也没什么价值去试别的。而且野外 React 代码多得多，模型训得更重，因此对 React 更熟（至少更眼熟）。React 奇点已经发生了，接受吧。

显然（我希望）我这会儿有点在开玩笑。但论点仍值得想——主要因为我看到有人把这意见和 React 一起[cargo cult](https://x.com/BrooksLybrand/status/2091968967887692042)进 vibe-coded 应用。也有更认真的人，比如 Cursor 团队，似乎真信：在 agentic programming 时代，[用 React 是优势](https://x.com/poteto/status/2089227731305464150)。

我很想逐条拆：

* 前端代码不用操心
* 模型对 React 最好，因为训练数据
* 新框架缺训练数据，模型会不行

但我不确定值不值得，尤其为 React 吵架。我对逻辑有更大意见，根子还是原问题：**框架还重要吗？**

我不懂的是：为什么是 React？为什么还要任何框架或 UI 库？

若 LLM 前端已经这么强，人们又越来越不在乎 HTML / JavaScript / CSS 细节、只在乎看起来和用起来对——那为什么还要在 LLM 和网站之间再塞一层抽象？若有什么时候该拥抱 Web Components，难道不是现在？

React 不必再当人设。免责声明：我 YouTube 频道就叫「React Tips with Brooks Lybrand」。再说，我们已经有 AI 实验室来当新人设了，没事的。

换个说法：

> 模型从大概 2025–2026 冬开始够强，能做 agentic programming 之后，做漂亮、可交互的网站比以往容易，不必再操心以前叫 DX（Developer Experience）的那些。我的 agent 不在乎基于文件的路由，我干嘛还拿「正确设置 `useEffect`」去烦它？
>
> 再说，模型在 JavaScript、HTML、CSS（某种程度上）上训得够好了，再叠复杂度既没必要也没价值。

这语气里有跳跃和错处，但不比第一种更被广泛接受的说法更多。

二选一：

* 框架不重要——那你没理由用 React。
* 用 React 多半仍有优势——那框架就重要。

## [web framework 的价值是什么？](#what-is-the-value-of-a-web-framework)

啊，web framework。从哪起、到哪止？目的是什么？还要不要？说到底，jQuery 到底哪里不好？有人论证过「既然训练数据里多，就该让 agent 用 jQuery」吗？没有的话，该有人提。Agent 不在乎意大利面代码，对吧？

我还记得 2010 年代的「框架大战」。当时给公司选型，在 React、Angular、Vue 里挑。那就是我们口中的「框架」。Gatsby 有，但不够通用（只做静态站）。Next.js 挺酷，也很受限（没有像样的 mutation 故事）。React 生态里，多半用 create-react-app（CRA），_或许_会有人 [eject](https://create-react-app.dev/docs/available-scripts/#npm-run-eject)——若团队里有人觉得 SSR 有价值、想自己搭。

我最终选了 React，很多人也是。但为什么？React 作为框架，到底哪里迷人？

若问 React 团队为什么赢、为什么好，他们多半会说「composition」。很难精确概括 React 的特别之处，但我觉得这是一大块。职业生涯和用 React 的早期，我并不真懂「composition」是什么。我只知道：

* React 很容易塞进已有站点
* React 能把逻辑和标记漂亮地封进组件，还可复用
* React 有不断长大的生态：路由、样式、head/meta……补齐我需要的零件

后来才明白：React 从一开始就带服务端渲染（SSR），有点像 PHP 那种「脚本里写 HTML」的手感。搭起来更费事，尤其对我这种偏前端的人。于是催生了「backend-for-frontend 工程师」，以及 Next.js、Remix（旧版的那个，[抱歉](https://remix.run/remix-history)）这类 meta-framework。

React 解决了一堆问题。不管 [Rauch 先生怎么想](https://x.com/rauchg/status/2088757738037989755)（通常他挺准），React 并不是因为「自带一套包着好样式系统和可拥有、可改造的底层无障碍组件的组件库」才「赢」的。`shadcn/ui` 很棒，别误会。但即便在组件库 / 设计系统这条线上，它也只是长串继任者里最新的一环：Radix、Reach UI、Material UI、Bootstrap，以及更多我跳过、忘了或不认识的。`shadcn/ui` 能叠在一堆流行前任之上，恰恰证明 React 的厉害，而不是反过来。

这段「React 为何赢」的长而短的岔路，远不够写全历史，也几乎没碰其他 web framework 的有趣之处。尽管 React 主导，仍有许多框架和 meta-framework 周下载数百万、被开发者热爱。它也完全没提 Laravel、Ruby on Rails 这类非 JavaScript 框架的流行。

若不回头看我的初恋 React 对我意味着什么，我不知怎样更好评估框架价值。React 让我能做动态网站而不必沦为意大利面；意大利面贵，因为长期难改、难养。React 抬高了我、解放我去解决不想自己解的问题，并打开一扇门：其他开发者在改进它、在上面造更有用的工具。

如文首所说，我认为框架的增值很简单：**框架为你建网站提供抽象、结构与约束。**

这甚至不是框架独有——库、模块、类、函数皆然。代码是一串抽象，向计算机以及任何会操纵或学习它的东西表达意义与意图。以前那意味着人，我们叫「读代码」，于是很在乎变量名。如今我们在乎的细节层级在挪、在落定。也许我们在某条无限曲线上，会越来越不在乎树木，直到连森林也不在乎。我个人怀疑，但也可能完全错了。

不管怎样，我仍想要框架。我想要测得好、安全、好推理、能把 agent 推进它该进的槽里、产出我喜欢的结果的代码。

## [人人都在用框架](#everyone-uses-a-framework)

好了，西洋镜掀开：问「框架还重要吗？」时，我_有点_在开玩笑。

记得 [React Conf 2024 Core Team Q&A](https://www.youtube.com/watch?v=lyqMfofOpu8) 里，[Ricky Hanlon](https://x.com/rickyfm) 说过：

[嵌入内容（原站 YouTube）](https://www.youtube.com/watch?v=lyqMfofOpu8)

![嵌入内容（原站 YouTube）](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Do-Frameworks-Matter-Anymore/yt-lyqMfofOpu8.jpg)

> 你要么在用框架，要么在造框架；造框架真的很难。

这不是我第一次听到。之前在一家[德州杂货店](https://www.heb.com/)的 web 平台团队，我们也撞过同一件事。我们在 React 外包了自家 meta-framework：首请求走服务端渲染，之后整文档 hydrate，客户端用 React Router（v5？）接手路由。

这小框架有个可爱名字（`exo`，好像是；没人说得清为什么叫这），但多数工程师不把它当框架。我主要怪功能少、也没营销（内部框架何必宣传？）。可我们确实用了自家框架，维护成本高、负担重，真正懂它怎么工作的人很少——相当大的负债。

长话短说：他们开始迁离这套土制 meta-framework，换到 Next.js。我没看到迁完——差不多这时我去 Shopify 跟 Remix 团队共事（当然我们会「开玩笑」说，正是这决定把我气走的）。

这则轶事的时间线，明确落在 agentic programming「变强」之前。假设你现在开 greenfield 项目，且不是演示或一次性展示站，我觉得 Ricky 的话既比以往更真，也有一点点错。

先说错的：「造框架真的很难。」现在其实没那么难。当然看你要什么。要好、稳、少 bug、安全、全栈的框架，绝不是两三个 prompt 就能长出来。开始用之后，你可能发现 LLM 没法让它覆盖你要的一切，于是悄悄在框架旁打补丁；而取决于你怎么「造」这框架，补丁又会变成框架的一部分。避免硬焊黑客式 workaround、定下好、稳、可扩展的抽象，即便有前沿模型，仍要一点工作与迭代——以我的经验。

但造一个框架——甚至不必是烂的，只是凑合的——并不真难。我知道，因为你若不用框架、直接让 LLM 建站，它会替你造一个。这 LLM 未必有功能广度，也绝没有营销预算或野心来推销它的框架，但它仍在造。它会造框架，就像会造函数、类，以及我们「手写」时惯用的抽象。你看得少，不代表 agent 不做我们在做的同一件事。我甚至不想叫它 slop——那是只加功能不清理的渐进堆砌，我最早的项目都是这么堆的。没什么新鲜，最大变化是速度。

Agent 现在建站更快。查资料、找点子更快。造烂摊子也更快。这些以前我们也能做，这不是「人 > AI 写代码」的论调。我的意思只是：你要么用显式框架，要么在生成隐式框架。若你觉得完全无所谓，那[回到前面](#imagine)：干嘛还用 React？你可能不懂那套定制框架，但你的 agent 懂——它写的、它大概喜欢。你问 LLM 它的框架，它知道的比你对 React 内部知道的还多；这只是「[LLM 直接交二进制](https://x.com/elonmusk/status/2084304083851034949)而不交人类可读代码」那条路上再往前一步。若你信那条路，至少诚实点，把 React 扔掉——它多半只在拖慢你。

若你出于某种理由，仍觉得 LLM 用 React 或 Next.js 这类 meta-framework 更好，我猜是因为你更希望它用战过、抽得好、文档全的东西。你大概也喜欢它给 agent 装护栏，不必在现有轮子够用时再造轮子。你可能还喜欢：有整个团队、许多依赖这框架的公司在想安全问题，不只是你和（但愿）你的 agent。你或许还有别的理由；下面是我的：

## [我要（和不要）框架里有什么](#what-i-want-and-dont-want-in-a-framework)

如今我更关心代码的「形状」——抽象和结构帮大忙。我也关心约束 agent（测试、lint、Skills、可复制的可扩展模式）。以前亲手敲字时重要的许多东西，笼统叫 Developer Experience（DX）。有些对我仍有用；有些对我不太有用（但对 agent 有用）；有些对我们俩似乎都没用。看几个轶事例子。

**比如 Hot Module Replacement。**

HMR 让我改站后立刻在浏览器看到更新，不必整页刷新。可靠时极有用，尤其在调设计、又牵涉用户流程时（表单错误提示、默认折叠的手风琴、装饰元素的绝对定位）。不是生死功能，但我发现即便（或许尤其）跟 agent 协作时，若在啃复杂交互、想把设计拧到位，HMR 仍然很有帮助。

**比如 TypeScript。**

TypeScript 以前对我超有价值，因为它制造约束。JavaScript 得有类型了（听说 C# 开发者欢呼）。而且更容易发现对象上有哪些字段和方法——悬停或 `command+.` 就行。TypeScript 是内建文档的重要部分，帮我在代码里保持高效。如今我几乎不在乎去发现某个对象上的具体方法，类型约束也不再直接帮我。

但[很多人](https://x.com/matteocollina/status/2098080734317547756/quotes)和我仍觉得：对复杂应用（不是做完就扔的 1-shot vibe），类型约束能明显拧紧 LLM 迭代、减少一不小心全盘搞砸。而且就我所见，有 LSP 时，遇到不熟的函数、对象、模块（遗留代码或上一个 agent 生成的），它也更好做发现。

**比如 `useEffect`。**

我知道它几乎是骂 React 的代言人，也知道 React 团队[提供了新 API](https://react.dev/reference/react/useEffectEvent)来补短板。可问题是：我亲手甩 React 时，自认是 `useEffect` 巫师（至少自我感觉如此）。我不那么讨厌它，信得过自己。它可靠、古怪、很强，我用得顺手——主要因为我自信知道_什么时候别用_。跟 LLM 一起时，我觉得 `useEffect` 比古怪更糟：模型再聪明，我也不放心让它们挥这把抽象。事实上，Grok Bot 的开发显然[直接禁了 `useEffect`](https://x.com/poteto/status/2089227731305464150)。

回想框架增值。我要的框架 ~~有短裙和长外套~~**为建网站提供抽象、结构与约束**。

我发现：若**抽象**不存在，LLM 会造一个。有时无所谓，只是一次性抽象。有时要紧——抽象围着真实的 web 原语转（客户端导航用 Navigation API）；有时抽象跟其他抽象合拍（路由里用 [`fetch`](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API) 与 [Request](https://developer.mozilla.org/en-US/docs/Web/API/Request)/[Response](https://developer.mozilla.org/en-US/docs/Web/API/Response) 模型）；有时抽象封装了很难一次做对、做稳、无 bug 的行为（你喜欢的话是 React Server Components；不喜欢的话是 Remix 的 [Frame](https://guides.remix.run/streaming-ui-with-frames/)）。

结构我已经说过：我仍想看到代码的形状。也许 [Musk 先生](https://x.com/elonmusk/status/2094242307511853196)是对的，我们正加速到超人级写码，我试图理解代码最终是拖累。眼下，我跟 agent 一起干、先给它搭好核心架构、发现它写出难跟（甚至不是对我，是对 agent；我看得出它们何时发懵）的代码时再精炼架构，效果最好。

最后是**约束**。我要「怎样正确做事」极其清楚。逃生舱要可能，但通常不必，一旦用了，对我和机器都要一眼可见。我要测试与工具内建在框架里，检查 agent 的活。我要文档立刻可得，最好就在 `node_modules`，别让 agent 老去网上刮、还可能带回馊主意。

## [所以，框架还重要吗？](#so-do-frameworks-matter-anymore)

这篇博客我已经写了[三个星期](https://x.com/BrooksLybrand/status/2092273347060969474)。过去三年职业生涯都在开源 web 框架上。我喜欢这活，也希望可预见的未来继续干。回答「框架还重要吗？」对我极其重要——因为比起爱做框架，我更恨做无关紧要的事。

写这篇、以及跟业内同伴多次对话之后，我对几件事比较有把握：

* AI 绝对在重塑软件怎么做——个人层面与规模层面。
* 在被证伪之前，不同人、不同做法，即便用同一模型 / harness，质量仍差很多。因此[我会把 LLM 当可以练好的工具](https://x.com/BrooksLybrand/status/2099544341693767704)。
* 没人真正知道 AI 对软件开发——遑论世界——的长期影响。
* AI 是眼下行业的主焦点。

我认为约 2013–2019 的 **Framework Wars**，以及续集 **Framework Wars: The Rise of the Meta-Frameworks**（约 2020–2024），已经结束。把终年写成 2024，说明我觉得结束有一阵子了。人们可以不再为 JavaScript 疲劳；谢天谢地，因为我们都知道[我们已经在为 AI 炒作 / 末日循环疲劳](https://www.youtube.com/watch?v=iPUn1Fnfn0k)。

[嵌入内容（原站 YouTube）](https://www.youtube.com/watch?v=iPUn1Fnfn0k)

![嵌入内容（原站 YouTube）](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Do-Frameworks-Matter-Anymore/yt-iPUn1Fnfn0k.jpg)

我已接受，或正在接受：人们不再像从前那样渴求框架——许多方面这大概是好事。那段时间有点疯，我当然也深度买入。

但一样东西不必是炒作中心，才重要或有用。以前很少有人谈 `git` 性能或 GitHub 替代，直到成群的 OpenClaws 和其他乱跑的 agent 把整套系统压测出新瓶颈。[现在这里又火了](https://cursor.com/blog/git-at-any-scale)。

技术发展是动态的；新工具、想法、模式、库会再催生更多。与其坐着唉叹人们不再在 Xwitter 上为 Next.js vs Remix 互撕，我宁可真正参与建造：我认为我和别人能受益的东西。

再问一次：**框架还重要吗？** 让我把「是」说清楚，总结到目前为止：

* 行业似乎这么想——不然干嘛用 React？
* 你不用框架，agent 会造一个——所以你反正在用。
* 框架提供抽象、结构与约束。跟 agent 塑软件时这些是好事。用想清楚的、开源的、战过的、文档好的，多半比模型自制的土制更有益。

写到这里的总结时，我意识到这可能像在打稻草人。「当然人们觉得框架重要、能帮 agent，React 和 Next.js（或任何够好的现成框架）已经解决了。」

也行。那问题变成：**新框架还重要吗？**

若我们以为所有问题都解决了，那人类与技术发展未免太悲哀。那种颓废不适合我。对我来说：一样东西若好，大概还能更好。也许现有景观「够好」——对你够好就行，对我不够。

我要一个真正全栈的 JavaScript 框架。也许永远到不了——先前尝试没起飞（👋 Meteor，我们都爱过你）。只要我（或我的 agent）还得拼一堆包，才能从数据库拼到路由、样式、动画和无障碍组件，就有改进空间。

我要它建在 web 标准与 API 上，说 web 的语言，而不是 Node.js 或某一家 JavaScript 运行时的语言。我要它感觉通用，像它服务的平台的自然延伸，而不是某个博士生的冷僻研究项目。

我也要 AI 好用、产出我能推理的代码的框架。不要最终变成一堆我看不懂的乱。我不是在造车，但该死的，我要掀开引擎盖时知道自己在看什么。我还没见过真正「为 agent」建语言 / 框架的好 empirically 方法。目前，我的品味（只意味着我主观、有偏差的模型协作经验）对我_远比_任何基准、或做 TODO app 花了多少 token 的分析重要。不是说不该试——而是：很难造出「哪个框架对 agent 最好」的决定性客观度量，这本身就证明还有改进空间。

新框架还重要吗？只有一个办法真正知道。咱们造几个。

---

_感谢 [Alex Anderson](https://bsky.app/profile/ralexanderson.com)、[Moishi Netzer](https://x.com/moishinetzer)、[Elijah F. Hopp](https://x.com/elijahfhopp)、[Braydon Coyer](https://x.com/BraydonCoyer) 阅读早稿并给出宝贵反馈。也感谢同事 [Matt Brophy](https://x.com/brophdawg11)、[Mark Dalgleish](https://x.com/markdalgleish)、[Michael Jackson](https://x.com/mjackson) 无尽的辩论与分享。_ 🙏

---

由 Markdown 用[一小段 Node.js 脚本](https://github.com/brookslybrand/brookslybrand.com/blob/main/scripts/build.js)构建。
