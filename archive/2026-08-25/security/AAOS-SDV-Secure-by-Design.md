---
title: "AAOS SDV：默认安全设计"
title_en: "AAOS SDV - Secure by Design"
source_url: https://android-developers.googleblog.com/2026/08/aaos-sdv-secure-by-design.html
author: Markus Vill, Sean Keys, Istvan Nador
translated_at: 2026-08-25
tech_domain: security
tags: [aaos, automotive, secure-by-design, rust, dice]
cover_image: https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEh5wMRO7HwquRHIzH0qLwRDKkYVq-nIB4DwG5R2mLK3R3p1lo9nAVblduqSjSFc7rC3xo0bFBXB9iiTv662Bs4y7Ex_35labdsyXi9rM6FNWECqz19Nl7UrI5pO28Un6GBeInO2-yEJeNx0v3thcG5QWWTrCFQvvAIaYB60GEumMmHulA3mmYTtDL68isQ/s2048/Android-1-Meta.jpg
---

# AAOS SDV：默认安全设计

原文链接：<https://android-developers.googleblog.com/2026/08/aaos-sdv-secure-by-design.html>

原文作者：Markus Vill、Sean Keys、Istvan Nador

![文章头图](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEh5wMRO7HwquRHIzH0qLwRDKkYVq-nIB4DwG5R2mLK3R3p1lo9nAVblduqSjSFc7rC3xo0bFBXB9iiTv662Bs4y7Ex_35labdsyXi9rM6FNWECqz19Nl7UrI5pO28Un6GBeInO2-yEJeNx0v3thcG5QWWTrCFQvvAIaYB60GEumMmHulA3mmYTtDL68isQ/s2048/Android-1-Meta.jpg)

作者：Markus Vill（Software Engineer）、Sean Keys（Security Engineer）、Istvan Nador（Software Engineer），Android Auto

**软件定义车辆上的 Android Automotive OS，如何把域隔离、APEX 完整性、Rust 与 DICE 认证做成默认安全。**

在 Google，我们相信产品应默认安全设计（secure by design）。因此面向软件定义车辆（Software Defined Vehicle, SDV）的 Android Automotive Operating System（AAOS SDV），建在既有、[市场已验证的平台](https://source.android.com/docs/automotive/sdv/workstreams/hardware/sdv-on-qnx)之上，并借助 [Cuttlefish](https://source.android.com/docs/devices/cuttlefish) 这类虚拟化技术。[发布公告](https://blog.google/products-and-platforms/platforms/android/android-automotive-os/)侧重功能；本文摊开其中一部分安全概念。

![AAOS SDV 安全设计概览示意](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgKJVr7S37jvQ8V8UUzRD7mv7llfrTAKcLx7MnEZGB-jUOdhHqLl1-82xTmhFQzVE6XEyUCMWZb2KM9tjthzS1NQMzAMaiXtaK7SYfXTmghcttgCoDcJMLFTcZx6BiE7fWevJZdde_jENeuhz6LLciWSqzhruVCllLP-7pU4yBjj8fzdOXMEUl-D1lok9Q/s1600/Android-1-Blog.jpg)

## [基础：域隔离](#foundation-domain-isolation)

### [用虚拟化隔离同芯上的实例](#virtualization-to-isolate-co-hosted-instances)

把电子控制单元（ECU）收进单颗芯片，是当前趋势；多个域并排运行，隔离会变弱。

AAOS SDV 实例内部虽有隔离机制，但逻辑域常常更适合独立跑。例如仪表盘与信息娱乐系统要求不同。我们用虚拟机并行跑多个实例，让共享必须显式声明，隔离才是默认行为。

### [继承的 Android 安全能力](#inherited-android-security)

AAOS SDV 从 [Microdroid](https://source.android.com/docs/core/virtualization/microdroid) 演化而来——面向隐私虚拟机（pVM）优化的精简 Android。这条血缘让 Android 平台工程师能直接用上他们已经熟悉的安全特性。

### [进程隔离与默认拒绝](#process-isolation--deny-by-default)

AAOS SDV 沿用 Android 基于用户 ID（UID）的隔离模型，为每个应用建沙箱。每个服务跑在专用进程里，有唯一 UID，用来管访问权、数据目录和其他限制。我们用可移植操作系统接口（POSIX）能力严格收紧可执行操作，再配上 Security-Enhanced Linux（SELinux），落实「默认拒绝」（deny-by-default）。每个服务只拿最低必要权限：缺配置就挡访问，而不是弄成过度宽松的系统。同一策略也用在我们的[通信权限系统](https://docs.google.com/document/d/1_q-l1FyhNgYZWMYg5BlCbp165oCzs1_wPRdQaO-9DGE/edit?resourcekey=0-1ed5JHEP0tz16QD0v0xUBQ&tab=t.0#heading=h.a39ozyiarfpb)上，后文会讲。

### [成熟的漏洞管理](#proven-vulnerability-management)

AAOS SDV 接入 Android 成熟的安全响应与漏洞管理基础设施，覆盖发现、分级、修复与披露。生命周期包含持续自动扫描、年度深度渗透测试，以及经 [Android 安全漏洞报告流程](https://source.android.com/docs/security/overview/updates-resources) 汇入的合作伙伴情报。安全团队对发现的漏洞分级、按风险定严重度，并跟踪到修复完成。披露与发布策略经每月 [Android Security Bulletins](https://source.android.com/docs/security/bulletin) 协调，再辅以严格的定期安全审计与全面架构评审，保证平台长期韧性。

## [完整性：安全的软件交付](#integrity-secure-software-delivery)

除了进程隔离，安全平台还必须在执行前保证代码完整性。我们用下面几条路护住软件交付：

### [经认证的软件交付](#authenticated-software-delivery)

AAOS SDV 提供两种安装方式。第一，软件直接装到只读的 system、product 或 vendor 分区，每次启动都验签。这护住基础系统组件。

第二，服务走 Android Pony EXpress（[APEX](https://source.android.com/docs/core/ota/apex)）包。每个 APEX 封装软件及其依赖，把包当成分区，强制验签。在 AAOS SDV 里，APEX 把代码签名当成持续、由硬件强制的契约。APEX 靠四根柱子压住恶意代码执行：

#### [1. 不可变存储](#1-immutable-storage)

* **机制：** Android 内核用**只读 loopback** 把 `apex_payload.img` 直接当成原始存储设备挂上，并带严格的 `MS_RDONLY` 标志。
* **为何更安全：** OS 看不到写路径，因为文件不会解包到车机存储上。即便攻击者拿到 `root`，也改不了正在跑的 APEX 代码——文件系统层拒绝一切写命令。

#### [2. 密码学完整性](#2-cryptographic-integrity)

* **机制：** 密码学签名校验的是整份文件系统镜像的 [Merkle Tree](https://en.wikipedia.org/wiki/Merkle_tree)。
* **为何更安全：** 内核用按块的 `dm-verity`，对每个 4KB 数据块即时验签。攻击者若改闪存上的原始块，内核发现哈希对不上，立刻停执行。

#### [3. 严格隔离](#3-strict-isolation)

* **机制：** 套用[进程隔离一节](https://docs.google.com/document/d/1_q-l1FyhNgYZWMYg5BlCbp165oCzs1_wPRdQaO-9DGE/edit?resourcekey=0-1ed5JHEP0tz16QD0v0xUBQ&tab=t.0#heading=h.yy1a1k1zo4rf)里的规则做沙箱，APEX 作为专用分区挂在 `/apex` 下。
* **为何更安全：** 每个服务有自己的用户与数据目录，未显式共享就不能碰。专用分区让 Android 建出专用链接器命名空间，非特权系统守护进程只能碰显式暴露的库，攻击面更小。

#### [4. 原子恢复](#4-atomic-recovery)

* **机制：** APEX 用「Active/Backup」设计做**双缓冲回滚**。出厂刷入的 APEX 留在不可变的 `/system` 分区，更新落在可变的 `/data` 分区。
* **为何更安全：** 更新失败或看起来可疑时，`apexd` 守护进程在早期启动阶段标成「失败」。系统立刻把符号链接切回 `/system`。原子恢复有助于避免系统卡在半残状态。

## [韧性：内存安全的开发](#resilience-memory-safe-development)

验载保护系统不被外部篡改，平台韧性还取决于底层代码怎么写。AAOS SDV 的新组件，我们优先选内存安全。

### [Rust 作为主语言](#rust-as-the-primary-language)

AAOS SDV 瞄准小系统、要快可用；撑不起完整 Android 栈，于是范围收在 native framework。为分布式系统搭所需基础设施，我们在既有设施之外又写了多个组件，并采用 Rust 作为主语言。服务的业务逻辑也用 Rust 写，帮合作伙伴写出更安全的软件。设计上，[Rust 用内存安全特性帮忙挡住常见的一类内存安全漏洞，同时支持团队在写 native 代码时的吞吐](https://blog.google/security/rust-in-android-move-fast-fix-things/)。

## [分布式信任：网络与访问控制](#distributed-trust-network--access-control)

软件定义车辆需要隔离域之间的安全交互。AAOS SDV 的 mesh 供给架构用密码学方式核对每个通信端点的版本与作者，来应对这份复杂度。

### [设备与 Mesh 供给](#device-and-mesh-provisioning)

AAOS SDV Mesh 通过[把每个组件的网络身份，数学绑定到其实际二进制执行状态](https://source.android.com/docs/automotive/sdv/workstreams/core/vm-attestation/dice-profile)，完成认证。这套模型用硬件扎根的校验，换掉隐式的软件信任。

Mesh 认证设计成持续且密码学的。例如，避免出现「车载网关只因为信息娱乐 VM 有正确 IP，就信任一台已被攻陷的 VM」这类场景。

硬件强制隔离与自动隔离协议护住平台。SDV mesh 内的对等设备用基于 DICE 的认证与证明（下一节细讲），帮忙识别并遏制未授权代码执行或配置篡改。

### [基于 DICE 的 TLS，护住 VM 到 VM 通信](#dice-based-tls-to-secure-vm-to-vm-communication)

#### [把宿主身份钉在现实上](#grounding-the-host-identity-in-reality)

**DICE（Device Identifier Composition Engine）的黄金法则：** 固件里哪怕改一行代码（小更新或恶意利用），推导出的复合设备标识符（Compound Device Identifier, CDI）也会整段变掉，生成完全不同的 Alias Key。

**DICE** 与 **TLS（传输层安全）** 合在一起，解决零信任架构的根本难题：认证一台机器的同时，核验其软件完整性。

硬件背书的 DICE 标识，加上 TLS 加密握手，让接收方既能核对调用方身份，又能核对精确的软件状态。

传统证书只证明持有某个秘密；发现不了固件被篡改。DICE 用测量启动分层解决：

* **唯一设备密钥（Unique Device Secret, UDS）：** 制造时生成的随机密码学秘密。只有第一级引导加载程序能碰 UDS；其他软件与外部接口都碰不到。
* **分层测量（复合设备标识符）：** 硬件 ROM 用 UDS 与下一层固件的精确代码及配置做哈希，启动这条链。得到 CDI，再随后续每一层启动顺序往下链式传递。

AAOS SDV mesh 内的服务交互由严格访问控制管辖。与所有 AAOS SDV 软件一样，这些访问控制本身经认证，完整性在设备级、以及 mesh 内跨设备，都靠基于 DICE 的认证护住。

### [分层访问控制](#layered-access-control)

AAOS SDV 用纵深防御，好在不牺牲访问机制的前提下做动态车辆更新。模型靠两层主信任：

* **服务级权限：** 规定某台 VM 上某个服务，在 mesh 上能访问或暴露哪些具体资源。
* **VM 级权限：** 规定某台 VM 上所有托管服务的跨 VM 通信边界。

这套模型让 OEM 在安全与可更新性之间做平衡。对非安全敏感服务，宽松的 VM 级策略允许用轻量 APEX 更新安装，而不必整台 VM 重部署。

反过来，安全敏感信号的权限必须硬编码进每台 VM。代价是：把安全敏感服务引入新 VM，就要在全系统更新 VM 级权限——也就是更新 mesh 里所有 VM。

![分层访问控制：服务级与 VM 级权限示意](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgeUW8vWGonJma4AmCmiFS2k7ECKwN1jL8H-eYRHqmmSZ8OEtPE-G6YVK31df5bEyRUxDHNv3JR7S0YJQ1bBNl96WnHi42mxeY5nd1QjSgTaCWZ3-coH9V4Pb4lZC6auZcRZhsAuKvi_xGsPXLEWv8lw0o_3wODGe33VcHQMHfR3Ox8edRxHDwaP12uBnA/s1600/Android-2-Blog.jpg)

## [结论](#conclusion)

AAOS SDV 把 Android 的安全架构延伸到汽车侧的具体要求，走默认安全设计。靠虚拟化做域隔离，并强制「默认拒绝」访问策略，平台为软件定义车辆建起有韧性的环境。密码学完整性则靠硬件强制、对执行代码的即时校验来维持。

平台还接入持续安全生命周期：从主动漏洞管理，到经 DICE 做的硬件扎根身份核验。这些多层防御让 OEM 能在先进功能的可更新性，与现代汽车环境所需的扎实安全之间取得平衡。技术规格与实现细节见 [AAOS SDV Overview](https://source.android.com/docs/automotive/sdv)。
