---
title: "DeviceCheck 与 App Attest：在 iOS 应用里拦住欺诈"
title_en: "DeviceCheck and App Attest: Stopping Fraud in iOS Apps"
source_url: https://dev.to/arshtechpro/devicecheck-and-app-attest-stopping-fraud-in-ios-apps-472e
author: arshtechpro
translated_at: 2026-08-25
tech_domain: mobile
tags: [mobile, ios, security, fraud, apple]
cover_image: https://media2.dev.to/dynamic/image/width=1200,height=627,fit=cover,gravity=auto,format=auto/https%3A%2F%2Fdev-to-uploads.s3.us-east-2.amazonaws.com%2Fuploads%2Farticles%2F2v0s8k3i3jjrly8jp09m.png
---

# DeviceCheck 与 App Attest：在 iOS 应用里拦住欺诈

原文链接：<https://dev.to/arshtechpro/devicecheck-and-app-attest-stopping-fraud-in-ios-apps-472e>

原文作者：arshtechpro

![文章头图](https://media2.dev.to/dynamic/image/width=1200,height=627,fit=cover,gravity=auto,format=auto/https%3A%2F%2Fdev-to-uploads.s3.us-east-2.amazonaws.com%2Fuploads%2Farticles%2F2v0s8k3i3jjrly8jp09m.png)

作者：[arshtechpro](https://dev.to/arshtechpro)

**你的 API 根本不知道是谁在调用它。**

打到 `POST /api/redeem` 的请求，无论来自真机上的正式 App、越狱机上的魔改包，还是有人用 Charles Proxy 看完流量后写的 Python 脚本，看起来都一模一样。HTTPS 只证明连接加密了，对客户端身份什么都证明不了。

Apple 给了两套框架来堵这个洞。这篇讲清楚每套**实际保证什么**、**不保证什么**，以及怎么实现、同时避开教程里常见的坑。

* * *

## [目录](#table-of-contents)

*   [DeviceCheck 实际做什么](#what-devicecheck-actually-does)
*   [App Attest 实际做什么](#what-app-attest-actually-does)
*   [怎么选](#choosing-between-them)
*   [实现 DeviceCheck](#implementing-devicecheck)
*   [实现 App Attest](#implementing-app-attest)
*   [欺诈场景](#fraud-scenarios)
*   [要避开的错误](#mistakes-to-avoid)

* * *

## [DeviceCheck 实际做什么](#what-devicecheck-actually-does)

DeviceCheck（iOS 11+）只做两件事。值得说精确，因为它经常被吹过头。

**一。** 确认某个 token 来自一台真正的 Apple 设备，且上面装了你的 App——而你的 App 绑定在你的开发者账号下。

**二。** 按「设备 × 开发者」给你在 Apple 服务器上存 **两个比特**。两个比特就是四种状态。删 App 再装回来还在，这才是它存在的全部意义。

就这些。再扫一遍，看看清单上**没有**什么。DeviceCheck 不检测越狱。不告诉你二进制有没有被改。不识别用户。更不是鉴权。

两个比特的存储才是有意思的部分。因为它跨重装仍在，能回答本地 flag 答不了的问题：

*   这台设备是不是已经领过新用户促销？
*   这台设备是不是被标过 chargeback 欺诈？

用户删 App、重装、再开一个新账号，撞上的还是那两个比特。

一个坑：`generateToken` 拿到的设备 token 是**一次性**的。completion 里拿到的 token 应按一次性处理——虽然有效期够你重试同一次请求，但不要反复复用。每次请求重新生成。

## [App Attest 实际做什么](#what-app-attest-actually-does)

App Attest（iOS 14+）回答更难的问题：*这个具体请求，是不是来自一份未篡改的我的 App？*

做法是在设备的 Secure Enclave（安全隔区）里生成一对密钥。私钥永不离开硬件，也抽不出来。随后 Apple 签发一条证书链，证明这把钥匙属于你 App 的合法实例，Team ID 和 Bundle ID 都烤进去了。

钥匙一旦完成证明（attestation），App 就用它给每条敏感请求签名。你的服务器验签。被篡改的 App 签不出合法签名，因为它没法给自己的钥匙做证明。

流程拆成两阶段，把它们混在一起是最常见的实现错误。

**Attestation（证明）** 每个钥匙安装只做一次。要走 Apple 服务器，相对贵。

**Assertion（断言）** 之后每次请求做。便宜。关键点是：断言流程比证明简单，不再经过 Apple 服务器——你的服务器用证明阶段存下的公钥自己验。

没有「帮你验 attestation / assertion」的 Apple REST 接口。必须由**服务器**验证明——被攻破的客户端不能被信任去验证自己的完整性。你自己解析 CBOR attestation 对象、对照 Apple 的 App Attest 根 CA 查证书链，或者用现成库。

## [怎么选](#choosing-between-them)

|  | DeviceCheck | App Attest |
| --- | --- | --- |
| 确认真 Apple 设备 | 是 | 是 |
| 确认 App 二进制未改 | 否 | 是 |
| 持久的每设备状态 | 是（2 bit） | 否 |
| Secure Enclave 密钥 | 否 | 是 |
| 防重放 | 否 | 是（计数器 + nonce） |
| 最低 iOS | 11 | 14 |
| 是否经 Apple 服务器 | 每次调用 | 仅证明阶段 |
| 服务端工作量 | 调 Apple API | 自己验密码学 |

它们解决不同问题，组合很好用。App Attest 告诉你请求是真的；DeviceCheck 记得这台设备已经烧掉过免费试用。不少线上 App 两套一起跑。

## [实现 DeviceCheck](#implementing-devicecheck)

### [客户端](#client)

```
import DeviceCheck

func fetchDeviceToken() async throws -> String {
    guard DCDevice.current.isSupported else {
        throw DeviceCheckError.unsupported
    }
    let token = try await DCDevice.current.generateToken()
    return token.base64EncodedString()
}
```

模拟器上 `isSupported` 返回 `false`。开发流程里要提前规划这一点。

### [服务端](#server)

你需要从 Apple Developer 门户拿到一把启用了 DeviceCheck 的 `.p8` 密钥，用它签 ES256 JWT。每次请求的 HTTP 头里要带上这份以 JSON Web Token 形式拿到的认证密钥。

三个端点，全是 POST：

*   `validate_device_token` — 是不是真设备？
*   `query_two_bits` — 读存储状态
*   `update_two_bits` — 写状态

开发环境把 `api.devicecheck.apple.com` 换成 `api.development.devicecheck.apple.com`。

```
import jwt from 'jsonwebtoken';
import { randomUUID } from 'crypto';

function appleJWT() {
  return jwt.sign({}, PRIVATE_KEY_P8, {
    algorithm: 'ES256',
    keyid: KEY_ID,        // 10 字符 Key ID
    issuer: TEAM_ID,      // 10 字符 Team ID
  });
}

async function queryBits(deviceToken) {
  const res = await fetch(
    `https://${HOST}/v1/query_two_bits`,
    {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${appleJWT()}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        device_token: deviceToken,
        transaction_id: randomUUID(),
        timestamp: Date.now(),   // 毫秒，不是秒
      }),
    }
  );

  // 还没设过 bit 的设备返回纯文本 body，不是 JSON。
  // 解析前先处理。
  const text = await res.text();
  if (text.includes('Failed to find bit state')) {
    return { bit0: false, bit1: false, isNew: true };
  }
  return { ...JSON.parse(text), isNew: false };
}
```

这里有两处常咬人：`timestamp` 是**毫秒**，`transaction_id` 必须每次请求唯一。全新设备返回非 JSON body，所以要防御性解析。

## [实现 App Attest](#implementing-app-attest)

### [阶段 1：证明（一次）](#phase-1-attestation-once)

```
import DeviceCheck
import CryptoKit

func attest() async throws {
    let service = DCAppAttestService.shared
    guard service.isSupported else { throw AttestError.unsupported }

    // 1. 服务器下发一次性随机 challenge。
    let challenge = try await api.fetchChallenge()

    // 2. 创建 Secure Enclave 密钥。把 ID 持久化到 Keychain。
    let keyId = try await service.generateKey()
    try Keychain.store(keyId, for: "appattest.keyId")

    // 3. 对 challenge 做哈希。必须是 SHA256。
    let clientDataHash = Data(SHA256.hash(data: Data(challenge.utf8)))

    // 4. 做证明。这一步有 Apple 服务器参与。
    let attestation = try await service.attestKey(keyId, clientDataHash: clientDataHash)

    // 5. 交给你的服务器验证。
    try await api.verifyAttestation(
        keyId: keyId,
        challenge: challenge,
        attestation: attestation.base64EncodedString()
    )
}
```

把那个 `keyId` 持久化好。丢了就得重新证明一把新钥匙；每次 `generateKey` 都会返回指向唯一密钥对的新 keyId——旧的不会被替换。

然后服务器验证 attestation 对象。除非有特殊理由，否则别自己手写 CBOR 和 X.509 解析；用 `node-app-attest`、`appattest-checker-node`，或 JVM 上的 `veehaitch/devicecheck-appattest`。

```
import { verifyAttestation } from 'node-app-attest';

const { keyId, publicKey, receipt } = verifyAttestation({
  attestation: Buffer.from(req.body.attestation, 'base64'),
  challenge: storedChallenge,          // 你自己签发的那个
  keyId: req.body.keyId,
  bundleIdentifier: 'com.example.app',
  teamIdentifier: 'ABCDE12345',
  allowDevelopmentEnvironment: !isProd,
});

// 存 publicKey 供断言用，存 receipt 供欺诈指标用，
// signCount 从 0 起。
await db.saveAttestation({ keyId, publicKey, receipt, signCount: 0 });
```

用完就烧掉 challenge。复用 challenge 等于整套机制作废。

### [阶段 2：断言（每条敏感请求）](#phase-2-assertion-every-sensitive-request)

```
func signedRequest(payload: [String: Any]) async throws -> Data {
    let keyId = try Keychain.read("appattest.keyId")
    let challenge = try await api.fetchChallenge()

    var body = payload
    body["challenge"] = challenge
    let bodyData = try JSONSerialization.data(withJSONObject: body)

    let clientDataHash = Data(SHA256.hash(data: bodyData))
    let assertion = try await DCAppAttestService.shared
        .generateAssertion(keyId, clientDataHash: clientDataHash)

    // 同时发送 bodyData、assertion 和 keyId。
    // assertion 对象里不含 keyId。
    return try await api.send(body: bodyData, assertion: assertion, keyId: keyId)
}
```

服务端这边，不调 Apple：

```
const stored = await db.getAttestation(req.body.keyId);

const { signCount } = verifyAssertion({
  assertion: Buffer.from(req.body.assertion, 'base64'),
  payload: req.rawBody,
  publicKey: stored.publicKey,
  bundleIdentifier: 'com.example.app',
  teamIdentifier: 'ABCDE12345',
});

// 计数器必须严格递增。重复或变小，
// 意味着有人在重放截获的 assertion。
if (signCount <= stored.signCount) {
  return res.status(401).json({ error: 'replay detected' });
}
await db.updateSignCount(req.body.keyId, signCount);
```

认证器数据里有一个只增不减的计数器——检查它才有防重放；跳过检查等于把防护扔掉。

### [欺诈指标](#the-fraud-metric)

你存下来的那个 `receipt` 有用。欺诈指标是一个大约 30 天的窗口，统计某台设备上与你的 App 关联的、已证明过的唯一钥匙数量——由服务器拿着存下的 attestation receipt 去 App Attest 数据服务器取。一台设备生成几百把钥匙，很像 attestation 中介在喂机器人农场；两三把则多半只是重装了 App。

## [欺诈场景](#fraud-scenarios)

**机器人流量和撞库。** 打你 API 的脚本产不出 assertion：没有 Secure Enclave 钥匙，也没法完成证明。App Attest 把「给滥用限速」变成「滥用根本到不了端点」。

**模拟器 / 模拟器农场。** 两套框架在 Simulator 上都报 `isSupported == false`。靠模拟器刷免费档就不灵了。

**反复薅促销。** DeviceCheck 的 bit 比删 App 活得久。领促销时置 bit0，发放前先查。

**魔改包。** 有人改 IPA 跳过收据校验再侧载。魔改 App 的钥匙过不了证明，因为证明里含有 Apple 签名的、你 App 身份的哈希。

**账号接管。** 证明给你一个不依赖凭证的、稳定的「每次安装」身份。密码被盗 + 认不出的 attested 钥匙 = 有充分理由要求第二因素。

## [要避开的错误](#mistakes-to-avoid)

**把 App Attest 当成布尔开关。** 不要因为已有用户来了一把新钥匙就一律拒绝——重装 App、恢复设备可以合法让旧钥匙失效并需要轮换。合法用户会轮换钥匙。把信号喂进风险分，不要硬拦。

**在客户端做验证。** 若由 App 自己决定 attestation 是否有效，攻击者改掉检查就完事。验证永远在服务器。

**复用 challenge。** 一个 challenge，用一次，短过期，存服务端。否则截获的 assertion 能一直重放。

**跳过计数器检查。** 就三行代码，却是「有防重放」和「没有」的差别。

**在结账流程里做证明。** 尽量把证明放在关键用户路径之外；失败就稍后重试，用指数退避而不是写死的重试循环。证明可能暂时失败。放在启动或引导阶段，别放在用户正在付钱的时候。

**把 `.p8` 打进 App。** DeviceCheck 密钥只住在服务器。别处不行。

**以为这就能替代一切。** 证明抬高了攻击成本，但不是无穷大。有决心的攻击者用越狱机和 Frida 可以 hook 调用，把合法 assertion 从脚本里中继出去。限速、行为分析、服务端校验一样都不能少。

### [参考资料](#references)

*   [App Attest 文档](https://developer.apple.com/documentation/devicecheck/establishing_your_app_s_integrity)
*   [访问和修改每设备数据](https://developer.apple.com/documentation/devicecheck/accessing_and_modifying_per-device_data)
