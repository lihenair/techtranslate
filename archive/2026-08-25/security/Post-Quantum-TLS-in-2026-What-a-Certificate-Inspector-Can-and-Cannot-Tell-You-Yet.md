---
title: "2026 年后量子 TLS：证书检查器目前能告诉你什么、还不能告诉你什么"
title_en: "Post-Quantum TLS in 2026: What a Certificate Inspector Can and Cannot Tell You Yet"
source_url: https://capytoolkit.com/blog/security-privacy/post-quantum-tls-certificate-inspector-can-and-cannot-tell-you/
author: Capy
published_at: 2026-08-23
translated_at: 2026-08-25
tech_domain: security
tags: [post-quantum, tls, certificates, ml-kem, cryptography]
cover_image: https://cdn.capytoolkit.com/img/2026/08/post-quantum-tls-certificate-inspector-can-and-cannot-tell-you.jpg
---

# 2026 年后量子 TLS：证书检查器目前能告诉你什么、还不能告诉你什么

原文链接：<https://capytoolkit.com/blog/security-privacy/post-quantum-tls-certificate-inspector-can-and-cannot-tell-you/>

原文作者：Capy

![文章头图](https://cdn.capytoolkit.com/img/2026/08/post-quantum-tls-certificate-inspector-can-and-cannot-tell-you.jpg)

作者：[Capy](https://capytoolkit.com/about/)（[@CapyToolkit](https://x.com/CapyToolkit)）

发布于 2026 年 8 月 23 日。

**半个互联网已经在握后量子握手，证书却仍是经典算法。本地五分钟审计，看清你的域名站在哪一层。**

头条说半个网站已经量子就绪。然后你点自己站点的小锁，导出证书，把每个字段瞪一遍，却找不到任何提到量子的东西。与此同时，有厂商这个月已经催了你两封邮件，推销一套后量子迁移套餐，报价像救火。两边对不上，糊涂在两个方向都贵：要么慌着买一份现在根本卖不给你的迁移，要么把整件事当噪音，而对手已经在安静地录你的流量、留待日后解密。

诚实的图景是这样的。TLS 有一层几年前就悄悄做完了后量子升级，很大概率你上次打开页面时，服务器已经协商过它。另一层完全没动。证书仍带着经典签名，没有任何工具能改这一点。本文把这两层拆开，说明在 2026 年一张证书究竟能透露多少「就绪」信息，并给你一套五分钟审计，先对自己的域名跑一遍，再谈要不要为迁移建议掏钱。

## [为什么小锁看起来没变，底下却全换了](#why-your-padlock-looks-the-same-while-everything-underneath-changed)

2026 年 6 月一项覆盖 32,011 个域名的测量发现：49.3% 的站点用基于 `ML-KEM-768` 与 `X25519` 的混合后量子密钥交换完成了 TLS 握手；而公开信任的叶子证书里，携带后量子签名的基本为零。<sup>1</sup> 两个数字都对。它们描述的是同一批站点、同一时刻；多数仪表盘却把它们压成一个误导词：就绪。

加密这一半先动，是因为有一个有名字的威胁：现在收割、以后解密（harvest-now-decrypt-later）。对手今天录下你的加密流量，廉价存着，等密码学意义上相关的量子计算机到来再解密。<sup>2</sup> 于是会话机密性带着过期日。伪造证书签名是另一回事：那次攻击要等机器真的存在才成立，所以身份认证可以按兵不动，等标准和签发策略追上。

把两层分开，最近被追问的量子就绪问题，大半就有答案了。这也为本文的实操半边铺路：CapyToolkit 的[证书检查器在浏览器里解析任意 PEM 或 DER 链](https://capytoolkit.com/tools/security/cert-inspector/)，精确告诉你站点哪一层已经动过、哪一层还没有。

## [两层东西都被叫做「后量子 TLS」](#two-different-layers-get-called-post-quantum-tls)

混淆有一半来自用词。一次 TLS 连接干两件事：证明你在跟对的服务器说话，以及建出一个窃听者推不出来的秘密。这两份活跑在不同的密码学上，走不同的供应链，迁移日程也完全不同。把「后量子 TLS」当成一个开关，团队最后就会握着一把承诺过量的小锁。

### [密钥交换 vs. 证书](#key-exchange-vs-certificates)

密钥交换回答机密性问题。自 2024 年起，双方都支持混合方案的浏览器与服务器，一直在把经典椭圆曲线交换 `X25519`，和 NIST 于 2024 年 8 月标准化为 [`FIPS 203`](https://csrc.nist.gov/pubs/fips/203/final) 的格基方案 `ML-KEM-768` 合在一起用。<sup>3</sup> 攻击者要恢复会话密钥，必须两边都破。<sup>4</sup> 协商发生在握手里，从不碰证书字段——所以你在证书里检查不到它。

证书回答身份问题。服务器出示一串 `X.509` 证书；证书机构给叶子签名，浏览器用 RSA、ECDSA 这类经典算法验签。要换成 ML-DSA，签发方得提供密钥，根程序得信任它们，CA/Browser Forum 还得定下允许它们的基线。截至 2026 年 8 月，这些在公网都还没落地。<sup>1</sup>

拆开就是：

* 混合密钥交换保护的是**现在的机密性**：对付今天录流量、等量子硬件成熟后再解密的对手。
* 后量子证书签名保护的是**以后的真实性**：对付需要真有量子计算机才能做成的伪造。

### [为什么密钥交换先动](#why-key-exchange-moved-first)

重活是 Chrome 干的。124 版在 2024 年 4 月默认启用了基于 Kyber 的混合组；<sup>5</sup> 131 版切到了标准化的 `X25519MLKEM768` 组，由 [`RFC 10024` 为 TLS 1.3 规定](https://www.rfc-editor.org/rfc/rfc10024)。<sup>6</sup> Firefox 132 启用了同一组，所有 Chromium 系浏览器自动继承了这套行为。<sup>7</sup> 客户端会说这种话之后，服务器端打开它就塌成 CDN 控制台里的一个开关；大运营商翻得很快。到 2025 年 10 月末，Cloudflare 报告：多数由人发起的 Web 流量，已经受后量子密钥协商保护。<sup>2</sup>

证书这一侧没有对等的快车道。要向公网签发一张 ML-DSA 签名的叶子，需要可信根链，而主流根程序里还没有。CA/Browser Forum 服务器证书工作组截至 2026 年 7 月仍把 Allow ML-DSA 提案列在草案、没有更新，因此公开信任证书里允许 ML-DSA 的基线尚未合并；连涵盖 TLS 中 ML-DSA 的 IETF 草案，到 2026 年中仍是活跃工作组文档。<sup>8</sup> 内部 PKI 更快，因为根在你手里——这解释了企业为何先在内部试点后量子证书，而公网还在等。基线不变之前，公开证书层结构性卡住，没有任何工具能催它。

## [眼前这张证书实际能告诉你什么](#what-the-certificate-in-front-of-you-actually-shows)

把完整链贴进检查器，每张证书各自成一张卡：主体、签发者、有效期、SAN、序列号、`SHA-256` 指纹，再加上这场讨论真正转着的两个字段：公钥算法与签名算法。把这两个字段读对，就是全部技巧。多数量子就绪的糊涂，会在你能分清两者、并知道哪一个会先动的那一刻死掉。

### [密钥算法字段](#the-key-algorithm-field)

2026 年 8 月的典型生产站点上，叶子卡会写 `RSA 2048` 或 `ECDSA P-256`，签名是 `SHA-256`，整条链里看不到任何古怪东西。即便同一站点每次连接都协商 `X25519MLKEM768`，这也是预期状态。对经典攻击者来说，这些密钥余量很大；NIST [`SP 800-57` 把 `RSA 2048` 大约评为 112 bit 安全强度，ECDSA P-256 约 128](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-57pt1r5.pdf)，撑过它们会服务的每一个有效期窗口都够。<sup>9</sup> 想把取舍摊开对比，检查器的 [RSA 与 ECDSA 对照写了证书体积、握手性能与强度等价](https://capytoolkit.com/tools/security/cert-inspector/reference/#rsa-vs-ecdsa-certificate)。

工具对真正过时的密码学喊得很响：弱于 `2048-bit RSA` 的密钥、以及任何 `SHA-1` 签名，都会在卡上直接挂彩色徽章。一张干净、没有徽章的卡，仍然对会话的密钥交换只字不提。干净不等于量子就绪。这两件事住在不同层，而这文件里只出现其中一层。

### [签名算法 vs. 公钥类型](#signature-algorithm-vs-public-key-type)

`SubjectPublicKeyInfo`——检查器呈现为公钥的那一块——描述主体拥有并用来证明持有权的是什么密钥。签名算法字段描述签发者如何给这张证书本身签名。今天两者都是经典的。两者最终都要迁，而且从叶子到根的每张卡都能看见它们，所以你可以核对整条链，而不是假定任何事。

按卡可见听起来平淡，直到你想到迁移日。CA 一旦开始提供 ML-DSA 选项，那些已经知道哪些证书跑 `RSA 2048`、哪些跑 `ECDSA P-256`、哪张中间证签什么的团队，一个下午就能换完。其他人那天要从重新摸清自己的基础设施开始。CapyToolkit 的工具页说得很直白：知道每张证书当前的算法，正是跟踪哪些要换的方法。先盘点。采购以后再说，如果还需要的话。

## [用证书检查器做的五分钟审计](#a-five-minute-audit-routine-with-the-certificate-inspector)

该落地了。收集你运营域名的证书链，本地检查，按链上每个位置记四件事。流程跑在浏览器标签页里粘贴的文本上，符合 [CapyToolkit 那套「全在本地处理」的浏览器工具风格](https://capytoolkit.com/)；唯一值得知道的例外是可选的域名查询：它只把主机名发给取证服务，返回的链仍在本地渲染。你的证书文件本身哪儿也不去。

### [从上到下读链](#reading-the-chain-top-to-bottom)

1. 从它住的地方导出完整链：nginx 的 `fullchain.pem`、cert-manager secret，或 `keytool` 输出。
2. 把 PEM 文本贴进检查器，或把文件拖进投放区；`.pem`、`.crt`、`.cer`、`.der` 都能解析。
3. 从叶子开始读卡。叶子默认展开；中间证和根默认折叠。
4. 每张卡上先记公钥算法与长度，再记下面的签名算法。
5. 终点应是一张标成自签名的 ROOT CERTIFICATE。若最后一张读成 INTERMEDIATE CERTIFICATE，链就不完整，客户端一直在悄悄补洞。

第 2 步的摩擦多半来自格式怪癖。PEM 不过是包在头尾行之间、Base64 包起来的 DER 字节，所以一个文件可以开心装整条链；DER 是原始二进制，通常只装一张证。Windows 导出给你 `.der`，设备吐出无头的 Base64；[PEM 与 DER 编码指南说明怎么分辨并互相转换](https://capytoolkit.com/tools/security/cert-inspector/pem-vs-der-certificate-format/)。完整性另有规则；[证书链验证指南走了一遍 `RFC 5280` 的路径检查（含排序），健全的链要满足这些](https://capytoolkit.com/tools/security/cert-inspector/certificate-chain-validation/)。

2026 年 8 月所谓「干净」，无聊得令人安心：没有过期或即将过期徽章，没有 WEAK KEY 或 SHA-1 SIGNATURE 警告，完整链收在自签名根上，每张卡都是经典算法。按现行每一条要求，这条链都完全健康，同时一点也不量子就绪。预期就是这个结果。别去「修」它。

### [把发现记下来](#recording-what-you-find)

把结果写成一份朴素清单：链上每个位置一行，列是域名、密钥算法、签名算法、过期日。今天这张表看起来琐碎；等你的 CA 提供后量子选项那天，它就会变成迁移清单，因为该换的行会自己排出来。没有它的团队，那个未来日要从零审计自己的舰队开始。

顺便再加一列：每张卡上的 `SHA-256` 指纹，用检查器的复制按钮直接拷。指纹免费给你变更检测。重签的证书会产出新摘要，其他字段可以不变，所以以后指纹一变，就精确证明哪一环被动过；从业者靠同一性质做 pinning 与审计轨迹，见 [SHA-256 指纹参考](https://capytoolkit.com/tools/security/cert-inspector/reference/#sha256-fingerprint)。

## [真正决定迁移时间表的是什么](#what-actually-determines-your-migration-timeline)

瓶颈不在你的证书。CA/Browser Forum 于 2025 年通过的提案 `SC-081v3`，把证书最长寿命从 398 天压到 2029 年 3 月的 47 天；ACME 自动化已经在无人干预下续签大多数舰队。<sup>10</sup> 不论量子怎么走，证书周转都会加速，所以你现在搭的续签管道，也会变成过渡最终要求的那次替换的投递机制。在 [47 天下限到来之前把过期告警就位](https://capytoolkit.com/tools/security/cert-inspector/tls-certificate-expiry-monitoring/)，付两次账：一次防中断，一次防迁移手忙脚乱。

实践里，密钥交换状态由服务器栈和厂商决定，不由任何路线图幻灯片决定。边缘是否说 `X25519MLKEM768`，取决于 CDN 或负载均衡上的开关，以及底下的 OpenSSL、Go 或 nginx 版本；OpenSSL 在 2025 年 4 月发布的 3.5 版原生支持了 ML-KEM 与 ML-DSA，更老的栈需要 provider 插件。<sup>11</sup> 内部系统跟自己的钟表走；企业路线图常把内部 mTLS 与代码签名排在公网 TLS 前好年，因为私有根让你不必等论坛投票就能部署。噪声剥掉，只剩三件事：

* 今天有人向你推销公网站点的后量子证书替换，直接拒。没有 CA 能签发公开信任的 PQ 叶子，所以这套话术是演戏。
* 确认混合密钥交换已在边缘生效——看 CDN 控制台，或一条 `openssl s_client`。保护「现在被录的流量」的，是这个开关。
* 自动化续签不断周转时，保持按链的算法清单最新；PQ 签发落地那天，你执行的是清单，而不是另开一个发现项目。

## [下一轮续签之前，你站在哪](#where-this-leaves-you-before-the-next-renewal-cycle)

所以，诚实总结。在证书层，你的站点没有任何量子化，因为公开 PKI 没动。在握手层，大约一半被测站点已经挡住了流量录制，查你自己的只要几分钟。两件事都不需要相信任何人的营销页，包括我的。

盯两个里程碑。第一是 CA/Browser Forum 基线允许在公开信任证书里用 ML-DSA；第二是某家大 CA 真的签发一张。任一落地，你的清单会告诉你哪些行要改；在那之前，续签继续自动化，问题就停在今天这个位置。

还有一点值得欣赏。每一步都跑在你贴进浏览器标签页的文本上，所以你检查过的链、查过的域名、建过的清单，从未碰过服务器。没有人把你对后量子就绪的兴趣，跟你的证书数据关联起来——因为没什么可关联。基础设施侦察仍是你的，这类审计就该这样。

## [来源](#sources)

1. Vanishka Mohan Dubey and Gaurav Varshney, “Measurement Study of Post-Quantum Readiness of Internet: 2026,” arXiv, June 2026. <https://arxiv.org/abs/2606.16473>
2. Cloudflare, “State of the post-quantum Internet in 2025,” blog.cloudflare.com, October 2025. <https://blog.cloudflare.com/pq-2025/>
3. Wikipedia contributors, “ML-KEM,” en.wikipedia.org, accessed August 2026. <https://en.wikipedia.org/wiki/ML-KEM>
4. D. Stebila, S. Fluhrer, and S. Gueron, “Hybrid key exchange in TLS 1.3,” draft-ietf-tls-hybrid-design-07, IETF, August 2023. <https://www.ietf.org/archive/id/draft-ietf-tls-hybrid-design-07.txt>
5. Google Chrome Team, “Chrome 124 release notes,” developer.chrome.com, April 2024. <https://developer.chrome.com/release-notes/124>
6. K. Kwiatkowski, P. Kampanakis, B. E. Westerbaan, and D. Stebila, “Post-Quantum Traditional (PQ/T) Hybrid Key Agreement Mechanisms for TLS 1.3,” RFC 10024, IETF, 2026. <https://www.rfc-editor.org/info/rfc10024>
7. Mozilla, “Firefox 132 release notes for developers,” developer.mozilla.org, October 2024. <https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/132>
8. CA/Browser Forum, “Minutes of the Server Certificate Working Group, 2 July 2026,” cabforum.org, July 2026. <https://cabforum.org/2026/07/02/2026-07-02-minutes-of-the-server-certificate-working-group/>
9. Wikipedia contributors, “Key size,” en.wikipedia.org, accessed August 2026. <https://en.wikipedia.org/wiki/Key_size>
10. CA/Browser Forum, “Ballot SC081v3: Introduce Schedule of Reducing Validity and Data Reuse Periods,” cabforum.org, April 2025. <https://cabforum.org/2025/04/11/ballot-sc081v3-introduce-schedule-of-reducing-validity-and-data-reuse-periods/>
11. OpenSSL Project, “Release OpenSSL 3.5.0,” github.com, April 2025. <https://github.com/openssl/openssl/releases/tag/openssl-3.5.0>
