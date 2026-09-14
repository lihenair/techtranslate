---
title: "Android Restore Credentials API：从零讲清"
title_en: "Android’s Restore Credentials API, Explained From Zero"
source_url: https://medium.com/@lucf15/androids-restore-credentials-api-explained-from-zero-549fbbee35ae
author: Luca Fioravanti
published_at: 2026-08-30
translated_at: 2026-09-07
tech_domain: android
tags: [android, credentials, webauthn, passkey, backup]
cover_image: https://miro.medium.com/v2/resize:fit:700/1*qMsV-7sVYnAGk-MEf_Dxdg.png
---

# Android Restore Credentials API：从零讲清

原文链接：<https://medium.com/@lucf15/androids-restore-credentials-api-explained-from-zero-549fbbee35ae>

原文作者：Luca Fioravanti

![文章头图](https://miro.medium.com/v2/resize:fit:700/1*qMsV-7sVYnAGk-MEf_Dxdg.png)

作者：[Luca Fioravanti](https://medium.com/@lucf15)

发布于 2026 年 8 月 30 日。

**新手机上，应用怎么做到没人输入就自动登录？这比听起来大得多——Restore Credentials 靠的是 WebAuthn，不是把登录态塞进备份。**

从 2027 年 4 月起，Google Play 会要求凡带自有登录的应用支持 Restore Credentials（[公告](https://android-developers.googleblog.com/2026/08/app-quality-memory-optimization-secure-onboarding.html)）。卖点很直白：用户配新机、恢复应用、打开某个 App，已经登录好了。没有密码，没有「去邮箱点链接」，也没有多余点击。

Android 备份本来就会恢复应用数据，很容易以为这是同一回事——不是。Restore Credentials 跑在 WebAuthn（passkey 背后的协议）上，用 WebAuthn 证明身份和密码完全不是一路。本文假定你还不懂 WebAuthn、passkey、Credential Manager 或 Android backup；每个词第一次出现都会定义，并对照一份可跑的 demo（Kotlin/Compose 客户端 + Kotlin/Ktor 服务端）。

## [密码登录到底在证明什么](#what-a-password-login-actually-proves)

普通登录表单要密码，发给服务器，服务器对照自己存的东西校验。**秘密本身就是全部证明**：知道它、敲出来、进来。

这有个难受的性质。这串字符一旦落到不该去的地方（TLS 配砸了、库泄了、钓鱼页），谁拿到谁就能当你登录。服务器分不出你和「拿到那串字的人」。

WebAuthn（Web Authentication，W3C 与 FIDO Alliance 标准）躲开了这种失败模式。它不用共享密钥，而用**密钥对（key pair）**：私钥出签名，公钥验签名。公钥不能伪造签名，也不能反推私钥。你生成一次，私钥永远不离开设备，公钥随便发。

用 WebAuthn 登录时：服务器发一个 **challenge**（新鲜随机数）；设备用私钥签名，只回签名；服务器拿登记过的公钥验签。私钥以及任何等价于密码的东西，都不会过网。

对比可以画成一张图（原文配有对照示意图）。

**passkey** 就是这套密钥对拿来做日常登录：私钥在你设备上（或由手机的 passkey 系统在你自己的设备间同步）。**relying party** 是 WebAuthn 对「凭证绑定到的那一对应用+服务器」的叫法——它「依赖」这份凭证来认证人。demo 两侧都用这个词：Ktor 服务端建一个 `RelyingParty` 对象（`RestoreCredentialService.kt:37-44`），客户端请求里带同名身份的 `rp` 字段。API 到处写 relying party，却很少直说它只是「这对密钥当初是为哪个 App 和哪个服务器造的」。

## [恢复场景的关键：一把不用点名的钥匙](#the-twist-restore-needs-a-key-nobody-has-to-ask-for)

购物网站上的 passkey 登录仍会先问点东西：用户名，或至少选一个账号。服务器得先知道要验哪把公钥，才能发出有意义的 challenge；设备也得知道以哪个账号登录。

Restore Credentials 不能这么干。App 刚装上，没有已登录用户可问。它向系统问更粗暴的问题：你手上有没有**就是这个 App**、来自某台旧设备的钥匙？答案必须零用户输入。

WebAuthn 管这叫 **resident key**，也叫 **discoverable credential**。非 resident 的密钥要服务器在注册时发回不透明的 credential ID，登录时再带上——所以必须先查用户名。resident key 在设备上存够信息，只凭「哪个 App 在问」就能找到自己。

注册时显式要求一把，见 `RestoreCredentialService.kt:64-69`：

```kotlin
.authenticatorSelection(
    AuthenticatorSelectionCriteria.builder()
        .residentKey(ResidentKeyRequirement.REQUIRED)
        .userVerification(UserVerificationRequirement.PREFERRED)
        .build()
)
```

认证阶段则根本不要用户名。服务端 README 写得很直白：`POST /restore/authenticate/options` 是「no username, `userVerification: discouraged`」（`server/README.md:15`）；路由也不需要已认证调用方，因为此时还没人可认证（`RestoreCredentialRoutes.kt:46-49`）。功能名说的就是这个：一份**不用点名就能取回**的凭证。

## [为什么不能把登录 token 直接备份过去](#why-you-cant-just-back-up-the-login-token-instead)

反正新手机会备份应用数据，为什么不把「证明用户已登录」的东西一起捎上？

多数应用里，那份证明是 **session token**：常见是 JWT（签过名的 blob，大意是「这是用户 X，有效到时间 T」）再加更长寿命的 refresh token。demo 正是这样发的：15 分钟 JWT access token + 30 天轮转 refresh token（`server/README.md:54-56`）。session token 是 **bearer secret**：谁拿着谁就被当成那个用户，与设备没有密码学绑定。把它拷到第二台设备，按定义就是 session hijacking。

所以应用拒绝备份 session。数据提取规则把 session 存储从云备份和设备间传输里都剔掉了，见 `data_extraction_rules.xml:9-14`：

```xml
<cloud-backup>
    <exclude domain="file" path="datastore/session.preferences_pb" />
</cloud-backup>
<device-transfer>
    <exclude domain="file" path="datastore/session.preferences_pb" />
</device-transfer>
```

WebAuthn 凭证绕开了这个问题。私钥从不移动，恢复时也不例外。到达新设备的，是「用仍停在生成处的那把钥匙继续签新签名」的能力；云场景下则是离开原设备前就已端到端加密的密钥。没有任何 bearer 形状的东西易手。

## [为什么凭证不在应用备份里](#why-the-credential-lives-outside-your-apps-backup)

想让数据扛过换机的 Android 应用会实现 `BackupAgent`：系统调用它保存文件或键值数据，在新设备上再调一次恢复。它搬运你声明的本地库、偏好、缓存等。本 demo 有一个 `RestoreCredentialBackupAgent`，写在 manifest 里（`AndroidManifest.xml:9`）。

真正搬文件数据的 `onBackup()` / `onRestore()` 却是空实现，见 `RestoreCredentialBackupAgent.kt:25-27`：

```kotlin
override fun onBackup(oldState: ParcelFileDescriptor?, data: BackupDataOutput?, newState: ParcelFileDescriptor?) = Unit

override fun onRestore(data: BackupDataInput?, appVersionCode: Int, newState: ParcelFileDescriptor?) = Unit
```

那为什么还要声明 `BackupAgent`？`android:allowBackup="true"`、`android:fullBackupOnly="true"` 加上面的 XML 规则，已经能自动备份文件，不必自定义类。它们给不了的是 `onRestoreFinished()`：系统只有在你注册了对应类时才会调它。[Google 的 Auto Backup 指南](https://developer.android.com/identity/data/autobackup)把这一点列为子类化 `BackupAgent` 的理由，并说明在开了 `fullBackupOnly` 后，让 `onBackup()` / `onRestore()` 空着就是预期写法。

restore credential 本来就不在那条数据流里。Google Play Services 在自己的 credential store 里生成并持有它，与 `BackupAgent` 声明的任何东西分开，经自己的通道搬运：绑定 Google 账号的端到端加密云副本，或开箱时的设备直传。私钥不是你想塞进可拷贝备份归档的普通应用数据。

`CreateRestoreCredentialRequest` 有个 `isCloudBackupEnabled` 标志。若设备缺少云备份所需的锁屏与加密，调用会抛 `E2eeUnavailableException`，而不是默默降级，见 `AndroidRestoreCredentialGateway.kt:22-33`：

```kotlin
override suspend fun register(creationOptionsJson: String): String {
    val response =
        try {
            credentialManager.createCredential(appContext, CreateRestoreCredentialRequest(creationOptionsJson, isCloudBackupEnabled = true))
        } catch (e: E2eeUnavailableException) {
            credentialManager.createCredential(appContext, CreateRestoreCredentialRequest(creationOptionsJson, isCloudBackupEnabled = false))
        } catch (e: Exception) {
            Log.e("RestoreCredentialGateway", "createCredential failed for requestJson=$creationOptionsJson", e)
            throw e
        }
    return (response as CreateRestoreCredentialResponse).responseJson
}
```

这一切都走 `Credential Manager`——`androidx.credentials` 上 passkey、已存密码以及现在的 restore credentials 的入口。只有一个文件导入它：`AndroidRestoreCredentialGateway.kt`，挡在普通 Kotlin 接口（`RestoreCredentialGateway.kt`）后面，应用其余部分不依赖 Android 细节。

## [两阶段 ceremony，端到端](#the-two-phase-ceremony-end-to-end)

整套功能就是同一次 WebAuthn 交换跑两遍。（**Ceremony** 是规范用语：一次完整的请求/响应交换；注册一次，认证一次。）

**第一阶段，注册**：普通登录成功后静默跑一次。`SignInUseCase` 先登录，再在后台注册 restore credential；失败直接丢掉，绝不挡登录，见 `SignInUseCase.kt:12-17`：

```kotlin
suspend operator fun invoke(username: String, password: String): AuthSession {
    val session = authRepository.login(username, password)
    sessionStore.save(session)
    runCatching { registerRestoreCredential(session.accessToken) }
    return session
}
```

`RegisterRestoreCredentialUseCase` 拉 creation options，交给 `CredentialManager.createCredential()`，再把结果送回服务器校验并存储（`RegisterRestoreCredentialUseCase.kt:10-14`）。私钥在那次调用里设备端生成；回传的只有公钥，包在 **attestation response** 里——设备对新造密钥的签名声明。

**第二阶段，恢复**：之后应用出现在任意新设备上时跑，不要用户名，见 `TryRestoreSignInUseCase.kt:13-24`：

```kotlin
suspend operator fun invoke(): Boolean {
    val (requestId, requestJson) = restoreCredentialApi.authenticationOptions()
    val outcome = restoreCredentialGateway.signIn(requestJson)
    val authenticationResponseJson =
        when (outcome) {
            is RestoreSignInOutcome.Available -> outcome.authenticationResponseJson
            RestoreSignInOutcome.NotAvailable -> return false
        }
    val session = restoreCredentialApi.verifyAuthentication(requestId, authenticationResponseJson)
    sessionStore.save(session)
    return true
}
```

`signIn()` 用 `GetRestoreCredentialOption` 调 `CredentialManager.getCredential()`。没有本 App 的 resident key 会得到 `NoCredentialException`；gateway 打 debug 日志并变成 `NotAvailable`——「没什么可恢复」是正常结果。其它 `GetCredentialException`（错误的 RP ID、坏掉的 `assetlinks.json`）记成 error，但仍返回 `NotAvailable`，配置错了就回落到手动登录，而不是首启直接炸（`AndroidRestoreCredentialGateway.kt:35-49`）。若找到钥匙，设备签 challenge，用户还没碰屏幕，应用已经有 session。

两个阶段、网络两侧（原文配有端到端流程图）。

## [触发第二阶段的两个入口](#the-two-places-that-trigger-phase-two)

没有弹窗催用户，应用得自己决定何时尝试第二阶段。按 [Google 的指引](https://developer.android.com/identity/sign-in/restore-credentials-implementation)，demo 在两处调用同一套取回逻辑：

- **后台钩子** `RestoreCredentialBackupAgent.onRestoreFinished()`：应用恢复数据刚落到新设备、用户还没打开 App 时，Android 就会调用（`RestoreCredentialBackupAgent.kt:29-38`）。这才让「零点击」名副其实：交换可以在图标被点开之前就完成。
- **首次启动时的检查**：钩子没开火时的兜底——网络断了、关了 `allowBackup`，或走了从不调 `onRestoreFinished()` 的恢复路径。

两处都进同一个 `TryRestoreSignInUseCase`，只有一条取回路径，不是两套 ceremony 要维护。

## [自己试一遍](#try-it-yourself)

读代码和亲眼看凭证在第二台设备上跑一圈不是一回事。把 demo clone 下来，按 `TESTING.md` 起服务端和应用，再用 Android Studio 的 Backup App Data / Restore App Data（Otter 2025.2.1+，文档在 [developer.android.com/identity/sign-in/test-restore-credentials](https://developer.android.com/identity/sign-in/test-restore-credentials)，写明该流程「simulates the setup wizard flow」），在没有已登录 Google 账号的情况下把凭证挪到第二台设备。盯服务端日志里的 `POST /restore/authenticate/verify` 返回 `200`：证明真钥匙跑通了一圈，不管 UI 显不显眼。

服务端与客户端完整源码：[github.com/lucf15/RestoreCredentialsDemo](https://github.com/lucf15/RestoreCredentialsDemo)。
