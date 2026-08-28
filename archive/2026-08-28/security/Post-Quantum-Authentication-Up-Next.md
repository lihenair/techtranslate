---
title: "后量子认证：接下来该做什么"
title_en: "Post-Quantum Authentication: Up Next"
source_url: https://www.ietf.org/blog/iab-pq-workshop-cfp/
published_at: 2026-08-28
translated_at: 2026-08-28
tech_domain: security
tags: [security, post-quantum, cryptography, ietf, tls]
---

# 后量子认证：接下来该做什么

原文链接：<https://www.ietf.org/blog/iab-pq-workshop-cfp/>

发布于 2026 年 8 月 28 日。

**密钥协商已在部署，认证还远；IAB 10 月布拉格研讨会要收生产侧证据。**

后量子密钥协商（key establishment）已从标准走向部署。后量子认证（post-quantum authentication）还远得多，而规格工作也不再是唯一瓶颈。IAB 将于 2026 年 10 月 11–12 日在布拉格举办研讨会，把部署经验与相关协议、标准的人聚在一起。

[研讨会聚焦加速后量子认证的部署](https://www.iab.org/announcements/call-for-papers-iab-workshop-on-accelerating-the-deployment-of-post-quantum-authentication-pqws/)。我们要的是证据：生产系统里到底是什么在拖部署。立场论文（position paper）应写什么、怎么交，见下文；截止 **2026 年 9 月 4 日**。

后量子认证部署很复杂。协议标准在推进，但生产系统里碰到的约束，还需要更多研究。

规格工作并不缺。NIST 已标准化 [FIPS 204 的 ML-DSA](https://csrc.nist.gov/pubs/fips/204/final) 与 [FIPS 205 的 SLH-DSA](https://csrc.nist.gov/pubs/fips/205/final)。IETF 已发布在 X.509 里使用它们的约定：[RFC 9881](https://www.rfc-editor.org/rfc/rfc9881.html) 与 [RFC 9909](https://www.rfc-editor.org/rfc/rfc9909.html)。还有 [复合签名](https://datatracker.ietf.org/doc/draft-ietf-lamps-pq-composite-sigs/)、[Merkle 树证书](https://datatracker.ietf.org/doc/draft-ietf-plants-merkle-tree-certs/) 与 [基于 KEM 的认证](https://datatracker.ietf.org/doc/draft-celi-wiggers-tls-authkem/) 等活跃提案。

我们大体上还缺的，是这些方案撞上生产系统时会发生什么。密钥与签名的尺寸我们知道，单项操作也能做基准测试；对证书链、握手上限、密码模块、固件预算、离线验证、信任库时间线的影响，知道得少得多。

我们想听试过、量过、买过、规划过或运营过这场迁移任何一环的人怎么说。

## [「没那么急」不等于「可以晚点」](#why-less-urgent-does-not-mean-later)

后量子认证常被说成不如后量子密钥协商急。威胁模型上说得通：密钥协商防的是「先收集、后解密」（harvest-now-decrypt-later）——今天截获的密文，等足够强的量子计算机出现可能被解开。认证防的是主动攻击者用这类机器伪造签名或凭证——今天还没有这样的机器。

问题在于：这比较的是威胁何时到来，却没有比较迁移要花多久。

Cloudflare 2019 年开始准备后量子迁移，2022 年为所有网站与 API 启用后量子加密；[2026 年 4 月报告](https://blog.cloudflare.com/post-quantum-roadmap/)称其网络上超过 65% 的人类流量已是后量子加密。数字只代表一家大网，不是全网，但时间表有参考价值：全面在服务端启用数年后，仍有相当大比例流量还没完成迁移。

密钥协商还有利部署形态：客户端与服务端可独立加支持，两边就绪就协商新机制。Web TLS 推广里，密钥协商组件不需要新证书链、新信任锚或升级长期签名密钥。

认证参与者与依赖更多——验证方必须事先知道接受什么。部署要证书机构、依赖方（relying party）、信任库、密码模块与应用做兼容改动。有些凭证用在实时握手里，另一些嵌在固件、软件包、身份令牌或归档文档里，可能多年后离线验证。路径各不相同，许多组件比寻常软件动得慢。

威胁可能更远，迁移却也更长。若这项工作吃掉大部分剩余预警期，把认证当第二优先级，就不能等密钥协商做完再动。

## [成本不是抽象的](#the-costs-are-not-abstract)

新对象不是「大一点」，是另一个量级。

NIST 安全级别 3 下，ML-DSA-65 公钥 1,952 字节，签名 3,309 字节。Ed25519 公钥 32 字节，签名 64 字节。只看传输的叶子+中间证书链里两个公钥与两个证书签名：ML-DSA-65 这四项共 10,522 字节；Ed25519 共 192 字节——差近 **55 倍**。这还是下限，不含名称、扩展、ASN.1 编码、透明度信息与协议 framing。

[SLH-DSA](https://www.rfc-editor.org/rfc/rfc9909.html) 换另一种权衡：公钥小，但标准签名从 7,856 到 49,856 字节（视参数集而定）。

尺寸不是唯一成本，签名性能也差很多。ML-DSA 可能比常见椭圆曲线签名耗 CPU 显著更多；部分 SLH-DSA 参数集签名贵几个数量级。规模上来，会影响证书签发、TLS 终结、身份令牌签名、软件与固件签名、验证容量。

尺寸后果取决于外围协议。[QUIC](https://www.rfc-editor.org/rfc/rfc9000.html) 里，客户端 Initial 数据报至少 1,200 字节；服务端尚未验证客户端地址时，发送量不得超过收到字节数的三倍。收到一个最小 Initial 后，服务端发送预算 3,600 字节。一个 ML-DSA-65 公钥加签名共 5,261 字节——还没算证书其余部分。

这不等于 QUIC 里做不了后量子认证：客户端可发更多数据、服务端可验证地址、协议还有别的缓解。但证书尺寸不再能轻松落在椭圆曲线时代无害的假设里。

别的系统约束不同。[RFC 9191](https://www.rfc-editor.org/rfc/rfc9191.html) 记录 EAP 认证器在 40–50 次往返后放弃会话，并结论：证书链大于约 60 KB 时，许多现有 EAP-TLS 部署无法成功——这问题在后量子标准之前就有。更大的密钥与签名让它更紧要。

这些例子说明尺寸与算力成本都重要，却不告诉运营者：对包数、重试、p50/p99 延迟、认证失败、内存、签名容量、存储或带宽具体改了什么。那需要生产系统的测量。

## [哪些约束才真正绑死？](#which-constraints-are-actually-binding)

几种不同的部署问题被当成一个问题在聊。要比较提案，至少得区分这些约束：

* **尺寸与协议行为**。证书链、握手 flight、令牌、包或固件镜像能长到多大，才会撞上传输上限、分片阈值、解析器假设、设备预算或计费阈值？QUIC 与 EAP 展示尺寸如何以两种非常不同的方式变成运营问题。
* **硬件与密钥托管**。密钥能否生成、导入、为高可用复制、在策略允许时备份、轮换，并通过现有 HSM、TPM、安全元件、智能卡或 PKCS #11 使用？支持是否要新固件、换硬件或新的 [FIPS 140-3](https://csrc.nist.gov/pubs/fips/140-3/final) 验证？路线图日期看不出绑死的是硅片、API、认证流程还是产品优先级。
* **长寿命与离线验证**。验证方是在线且定期更新，还是焊在改不了的设备里？能否拿到新信任锚、吊销信息、Merkle checkpoint、时间戳或算法策略？适合浏览器的设计，对 boot ROM、归档签名对象或建成多年后验证的包可能无关。
* **签名架构与容量**。密钥要产多少签名、多快、从多少站点？维持该速率要多少 CPU 或硬件容量？崩溃、故障转移、备份恢复与灾备能否保住签名状态？NIST 在 [SP 800-208](https://csrc.nist.gov/pubs/sp/800/208/final) 里允许受控应用使用有状态 LMS/XMSS，但安全依赖谨慎的状态管理。
* **运营成本**。对延迟、吞吐、CPU、内存、带宽、存储、签发容量、监控与失败率有什么影响？设计可能符合协议却仍太贵或太脆，运营不了。
* **生态协调**。CA、信任库、客户端、硬件厂商与运营者需要什么顺序，才能实现并测试兼容机制？哪一方必须先动，下一方才能测任何东西？

研讨会应指出：在哪些系统里哪些约束绑死，证据足够让运营者与协议设计者按系统差异做不同选择。

## [每种方案都在挪成本](#each-approach-moves-the-cost)

不止「把经典签名密钥换成后量子签名密钥」——多种提案各有额外权衡。

[复合 ML-DSA 签名](https://datatracker.ietf.org/doc/draft-ietf-lamps-pq-composite-sigs/)把 ML-DSA 与传统签名算法组合，两个分量签名都要验过才算有效。好处是双重保险（hedge）：只要有一个分量仍安全，复合就不可伪造；代价是额外的线路上开销、计算、密钥管理、实现与验证预算。保留传统分量是硬需求时很合适；尺寸、CPU 或模块支持已是问题时就不合适。

[Merkle 树证书](https://datatracker.ietf.org/doc/draft-ietf-plants-merkle-tree-certs/)把重复签名成本挪到共享 log 基础设施、包含证明与更新通道。当前草案一例：约 2,500 张证书的独立子树，包含证明 384 字节，外加依赖方（relying party）需要的签名。landmark-relative 形式对约 440 万张证书的子树可产生 736 字节证明、无需签名，但仅当依赖方有足够新的 log 信息。这条路用基础设施与验证方「新鲜度」预算，换线路与签名预算。

[基于 KEM 的认证](https://datatracker.ietf.org/doc/draft-celi-wiggers-tls-authkem/)通过交互式密钥交换证明长期 KEM 私钥的持有，而不是对 TLS 握手 transcript 签名。在线握手里可能有用的尺寸/性能权衡，但会改协议与凭证模型。按构造，它不能认证必须独立、离线验证的固件镜像、软件包或归档文档。它花协议改动与交互预算，降低在线认证成本。

还有几乎不需要新密码学的运营杠杆：减少中间证书数量、在不需要长期公开可验证处避免签名、改凭证寿命、压缩重复证书结构。有些系统里这些可能比新构造买得更多——公开测量还不够，我们不知道在哪。

没有单一「高效」方案。每种都在约束之间挪成本；有用的问题是：特定部署能负担花哪种资源。

## [谁该给我们发材料？](#who-should-send-us-something)

研讨会特别需要负责系统里协议设计者通常看不见的部分的人写报告。

HSM 团队有用的论文可能是：对比测过的设备/固件版本上 ML-DSA 密钥生成、导入、签名、复制与故障转移。CA 可报告拟议链与透明度材料的精确尺寸、签发流水线要改什么、哪些客户端版本能验过。QUIC、EAP 或 VPN 运营者可报告链变长后的包数、尾延迟与认证失败率。

固件团队可报告验证方可用 flash/RAM、允许的启动延迟、设备预期寿命、哪些候选能满足这些限制。信任库运营者可报告新算法的接受时间线、已有验证支持、根计划对申请者的要求、今天多少客户端人口能验过。

以上是研讨会想要的证据类型，不是说这些测试已经失败。一张表加五段说明，可能比精修过的研究论文更有用。

## [交什么、怎么交](#what-to-send-us)

PDF 一至两页，发至 [pq-workshop-pc@iab.org](mailto:pq-workshop-pc@iab.org)，截止 **2026 年 9 月 4 日**。简短意向说明也可以，不必计划到场。[征文说明](https://www.iab.org/announcements/call-for-papers-iab-workshop-on-accelerating-the-deployment-of-post-quantum-authentication-pqws/)涵盖其余：写什么、如何公开、研讨会如何进行。
