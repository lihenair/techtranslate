---
title: "Android 端侧图像生成：边缘生成式 AI 的系统工程"
title_en: "On-Device Image Generation on Android: Systems Engineering for Edge Generative AI"
source_url: https://proandroiddev.com/on-device-image-generation-on-android-systems-engineering-for-edge-generative-ai-f4d0cd4bb649?sharedUserId=oguzhanaslann
author: Oğuzhan Aslan
published_at: 2026-08-30
translated_at: 2026-09-08
tech_domain: android
tags: [android, on-device, diffusion, litert, edge-ai, kotlin]
cover_image: https://miro.medium.com/v2/resize:fit:641/1*-Wu1XOn3IocnyB7ioaX_zw.png
---

# Android 端侧图像生成：边缘生成式 AI 的系统工程

原文链接：<https://proandroiddev.com/on-device-image-generation-on-android-systems-engineering-for-edge-generative-ai-f4d0cd4bb649?sharedUserId=oguzhanaslann>

原文作者：Oğuzhan Aslan

![文章头图](https://miro.medium.com/v2/resize:fit:641/1*-Wu1XOn3IocnyB7ioaX_zw.png)

作者：[Oğuzhan Aslan](https://oguzhanaslann.medium.com/)

发布于 2026 年 8 月 30 日。

**端侧图像生成今天技术上已经可行；真正难的是系统工程，而不是「把模型跑通一次」。**

设想你在飞行模式的长途航班上，或在企业工作流里——用户数据绝不能碰第三方服务器——在 App 里点「Generate」，看着一张细节图就在眼前合成出来：完全离线、更私密，也没有反复的云端 API 账单。

这些年，生成式 AI 总像绑死在云上。Stable Diffusion 一类 text-to-image 扩散模型改写了数字创作，但动辄数十亿参数的权重，往往要吃掉数 GB VRAM 和机房级 GPU 集群。于是移动应用把生成当成远程服务：socket 把 prompt 发出去，排队等服务器，按次付云费，再渲染下回来的 bitmap。

端侧图像生成把这套范式翻过来。把整条推理栈——从文本分词到迭代去噪再到像素解码——直接搬到手机 SoC 上，生成式 AI 就从「远程 API 依赖」变成本地的边缘原生能力。

可一旦离开云，工程现实立刻露出来：

> 在现代 Android 硬件上，端侧图像生成技术上已经可行；但量产落地主要是系统工程问题，而不是模型推理问题。

在受控基准里让扩散模型出一张图不难。要在成千上万台异构 Android 设备上稳定跑通——既不被 Android Low Memory Killer（LMK）OOM 杀掉，也不把设备热到严重降频，还不逼用户下好几 GB 的 App——才是真活。

本文面向想把 latent diffusion text-to-image 模型（如 Stable Diffusion 1.5、2.1 及衍生架构）部署到 Android 本地的 Android 开发者与 ML 工程师，谈真实取舍、内存管理、多运行时策略、组件级精度，以及可上线的 Kotlin 架构。

## [取舍与工程现实](#tradeoffs-and-engineering-realities)

在进实现细节、硬件机制或移动运行时流水线之前，先直接对比本地执行与云基础设施，以及核心 trade-off 落在哪。

### [本地执行 vs. 云基础设施](#local-execution-vs-cloud-infrastructure)

- **本地执行：** 推理期间 prompt 与生成图像缓冲不过网，生成流程可保持私密、完全离线。但别吹「绝对隐私」——量产 App 仍可能发遥测、崩溃日志或分析数据，除非明确关掉。耗时更长（按设备能力，通常每张 5 到 60+ 秒），量化后模型资源约需 1–2 GB 存储，但边际服务器成本为零，算力全在客户硅片上。画质受压缩权重限制。
- **云端执行：** prompt 与图像缓冲走网到远程 GPU 集群。要稳定网络，但出图快（约 1–5 秒）。有持续 API 费用（约每请求 $0.002–$0.04），并受提供商隐私政策约束。可用未压缩的数十亿参数模型，画质更高。

![本地与云端对比](https://miro.medium.com/v2/resize:fit:700/1*OJ1ZpbERNZUh0dIFzdWAnw.jpeg)

## [存储、下发与 APK 包体约束](#storage-delivery-and-apk-package-constraints)

生成图像模型对常规移动应用来说往往根本太大。未压缩的 text-to-image（例如 FP32 的 Stable Diffusion）大约 4 GB 到超过 10 GB。把数 GB 文件直接塞进 APK 或 Android App Bundle（AAB）会严重伤安装转化，也撞上 Google Play 分发限制（例如 200 MB 基础 APK 上限），所以模型资源必须在运行时动态下发。

要让这些大模型能走蜂窝网、落在消费级机子上，量化压缩几乎是硬前提。量化不只是缩小下载包，更要大幅降低推理时在 RAM 与 SoC 之间搬运数十亿参数所需的内存带宽。

量化用更低精度类型缩小扩散模型体积与内存占用。FP16 在质量与效率之间较均衡；INT8 更省内存，但敏感组件可能出伪影。因此混合精度往往最合适：

- **Text Encoder：** FP16 或 INT8——一般扛得住量化。
- **UNet / DiT Backbone：** FP16 或混合 INT8/FP16——主算力瓶颈；attention 层可能需要更高精度。
- **VAE Decoder：** FP16 或 FP32——更高精度有助于避免色彩与空间伪影。
- **Scheduler：** FP32——很轻，有助于抑制扩散步之间的数值漂移。

总体而言，混合 INT8/FP16 在边缘部署上对模型体积、速度与画质是务实折中。

即便压缩后再动态下发，仍有几道关键工程坎：

1. **App 体积与下发：** 安装后再拉 1–2 GB 权重会影响上手流程，需要显式进度与断点续传。
2. **网络与存储成本：** 按需拉模型吃掉大量磁盘与移动流量。在按量计费的蜂窝市场，下 1.5 GB 资源包会给用户带来真实费用，也可能因断网失败。
3. **存储压力：** 低端与中端机经常闪存吃紧，触发系统清理或运行时下载失败。

> 搭流水线往往不难；真正瓶颈是拿到可跑、且与 delegate 兼容的权重。与 MNN 或 QNN 不同，LiteRT 常要靠 `litert-torch` 做风险不小的自定义转换。复用社区或厂商验证过的 `.tflite`，通常比自己从零转 SD1.5 更稳。

## [Android 上的系统工程挑战](#systems-engineering-challenges-on-android)

数 GB 模型资源成功落到设备后，下一关从权重装进活跃 RAM 那一刻就开始。在 Android 上，运行时很快变成内存上限与硬件多样性之间的平衡术。

## [内存上限与 Android LMK](#memory-limits-and-the-android-lmk)

为什么边缘 AI 对内存这么敏感？服务器有专用高带宽 VRAM；手机是统一的 LPDDR，由 Linux 内核、显示合成器、后台服务、前台应用和 ML 运行时共用。

把扩散模型图连同厚重的中间 tensor 缓冲一起加载，应用的 Resident Set Size（RSS）可以瞬间涨 1.5–3 GB。系统内存压力越过阈值时，Android 的 Low Memory Killer（LMK）会在生成中途静默杀掉前台应用——创作会话直接没了，也几乎没有异常恢复机会。

## [硬件异构与后端层级](#hardware-heterogeneity-and-backend-hierarchy)

除了裸内存上限，Android 横跨成千上万种硬件配置。加速不是单一抽象，而是分层执行层级：

![硬件执行层级](https://miro.medium.com/v2/resize:fit:700/1*RLkO5y10UzNyDbi6m5GoMg.png)

- **ML Runtime：** 如 Google 的 LiteRT（前身 TensorFlow Lite）或 Microsoft 的 ONNX Runtime Mobile，管理计算图与 tensor 缓冲。
- **Hardware Delegates / Execution Providers：** 中间层（例如 Qualcomm QNN/QAIRT、Google LiteRT GPU Delegate、Android NNAPI HAL）把 ML 算子译成硬件指令。
- **Hardware Accelerators：** 物理硅——CPU（ARM Neon SIMD）、GPU（Adreno、Mali），或专用 NPU（Hexagon、Tensor 处理块等）。

在 Qualcomm Snapdragon NPU 上很快的 model delegate，到 MediaTek Dimensity 或 Google Tensor 上可能编译失败，或抛不支持的算子错误。

### [务实的多运行时执行](#pragmatic-multi-runtime-execution)

量产边缘流水线很少「纯一种运行时」。例如生产 Android App 可能用 LiteRT（`.tflite`）跑 CLIP text encoder 与 UNet denoiser，同时用 ONNX Runtime Mobile（`onnxruntime-android`）跑预优化的 `.ort` VAE decoder。混用运行时可避开高风险格式转换，同时把整体应用开销压住（原生运行时额外占用大约 50 MB）。

## [Latent Diffusion 架构](#the-latent-diffusion-architecture)

Latent diffusion 在压缩的 latent 空间做迭代去噪，而不是直接在像素空间，从而显著降低算力开销。

![Latent diffusion 管线](https://miro.medium.com/v2/resize:fit:408/1*VdM7mduJwnkyluFcGcIzZQ.png)

1. **Text Encoding（CLIP / T5）：** 把文本 token 变成语义向量。每个 prompt 执行一次，延迟低。
2. **Denoising Loop（UNet / DiT）：** 标准 SD 流水线的主算力瓶颈，通常占总执行时间的 85%–95%。
3. **Classifier-Free Guidance（CFG）：** CFG 分别评估条件噪声（由 prompt 引导）与无条件噪声（空 prompt）。未做 batch 时，每个 timestep 的 UNet 调用会翻倍（例如 20 步 = 40 次 UNet）。若运行时支持 batching，可把输入拼成单个 batched tensor `[2, 4, Latent_H, Latent_W]`，一次 pass 评估两种条件——前提是硬件 delegate 能高效处理动态 batch。
4. **Variational Autoencoder（VAE Decoder）：** 去噪结束后跑一次，把 latent tensor 投回空间 RGB 图像缓冲。VAE 内存消耗强烈依赖分辨率、tensor 布局，以及是否启用 tiled decoding。

> 预转换导出经常偏离标准 PyTorch / Diffusers 约定。tensor 布局（`NHWC` vs `NCHW`）、输入顺序（例如传 `[context, latent, timestep]` vs `[latent, timestep, context]`），或未缩放的 latent 空间，很少抛显式运行时错误——结果往往是视觉噪声。Manifest 必须按显式 tensor 索引与布局 profile 严格驱动输入绑定。

## [手机上到底装得下什么？](#what-actually-fits-on-a-mobile-device)

搭应用执行流水线之前，要先按硬件档位弄清设备上到底装得下什么。这些能力画像会变成运行时动态检测并瞄准的设计约束：

![设备能力档位](https://miro.medium.com/v2/resize:fit:700/1*no_T5xvLSBdZCwk3absPlw.jpeg)

把目标设备归进这些明确的操作基线后，硬件异构就从「不可预期的崩溃源」变成一组结构化工程目标。

## [量产应用架构](#production-application-architecture)

稳健的边缘 ML 架构要把模型下发、生命周期校验、硬件能力检测与引擎执行拆开。

![量产架构示意](https://miro.medium.com/v2/resize:fit:276/1*AxNj8XpESwuTbAwuQsLkzA.png)

### [详细的 Model Manifest](#detailed-model-manifest)

Manifest 定义技术参数、部署约束、内存启发式与校验 checksum：

```kotlin
@Serializable
data class ModelManifest(
    val modelId: String,
    val targetResolution: Int,
    val latentSize: Int,
    val latentChannels: Int = 4,
    val tensorLayout: String,
    val quantizationProfile: String,
    val systemRamHeuristicMultiplier: Float,
    val files: List<ModelFileSpec>,
    val schedulerConfig: SchedulerConfig
)

@Serializable
data class ModelFileSpec(
    val fileName: String,
    val downloadUrl: String,
    val expectedSizeBytes: Long,
    val sha256Checksum: String
)

@Serializable
data class SchedulerConfig(
    val type: String,
    val defaultSteps: Int,
    val guidanceScale: Float = 7.5f
)
```

> 用扁平倍数估 RAM 开销（例如模型大小的 2.5 倍）可能误伤 4–6 GB 机型上的用户。经 XNNPack 等后端走 CPU 时，`.tflite` 会从磁盘 `mmap`，权重页按需缺页，不会整包常驻 RAM。按 profile 的启发式（例如 CPU `mmap` 约 1.3 倍，活跃 GPU tensor 分配约 2.2 倍）能避免多余的预检拒绝加载。

### [硬件能力检测](#hardware-capability-detection)

加载模型前评估设备规格，选择合适的质量预设与执行后端：

```kotlin
class CapabilityDetector(private val context: Context) {

    fun evaluateDevice(): DeviceCapabilities {
        val activityManager = context.getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
        val memoryInfo = ActivityManager.MemoryInfo().also { activityManager.getMemoryInfo(it) }
        val powerManager = context.getSystemService(Context.POWER_SERVICE) as PowerManager

        val totalRamMb = memoryInfo.totalMem / (1024 * 1024)
        val isPowerSave = powerManager.isPowerSaveMode
        val thermalStatus = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            powerManager.currentThermalStatus
        } else 0

        val preset = when {
            totalRamMb < 4096 || isPowerSave -> QualityPreset.PERFORMANCE
            totalRamMb in 4096..7168 -> QualityPreset.BALANCED
            else -> QualityPreset.HIGH_QUALITY
        }

        return DeviceCapabilities(
            totalRamMb = totalRamMb,
            availableRamMb = memoryInfo.availMem / (1024 * 1024),
            isPowerSaveMode = isPowerSave,
            thermalStatus = thermalStatus,
            recommendedPreset = preset
        )
    }
}
```

### [带完整性校验的量产资源下载器](#production-asset-downloader-with-integrity-checks)

实现支持磁盘空间预留、HTTP Range 断点续传，以及 SHA-256 完整性校验：

```kotlin
class ResumableModelDownloader(private val destinationDir: File) {
    suspend fun downloadAndVerify(fileSpec: ModelFileSpec): Result<File> = withContext(Dispatchers.IO) {
        val targetFile = File(destinationDir, fileSpec.fileName)
        val tempFile = File(destinationDir, "${fileSpec.fileName}.tmp")

        if (targetFile.exists() && verifyChecksum(targetFile, fileSpec.sha256Checksum)) {
            return@withContext Result.success(targetFile)
        }

        if (destinationDir.usableSpace < fileSpec.expectedSizeBytes + (200 * 1024 * 1024)) {
            return@withContext Result.failure(IllegalStateException("Insufficient disk storage."))
        }

        val downloadedBytes = if (tempFile.exists()) tempFile.length() else 0L
        val connection = (URL(fileSpec.downloadUrl).openConnection() as HttpURLConnection).apply {
            if (downloadedBytes > 0) setRequestProperty("Range", "bytes=$downloadedBytes-")
            connectTimeout = 15000
            readTimeout = 30000
        }

        connection.inputStream.use { input ->
            RandomAccessFile(tempFile, "rw").use { output ->
                output.seek(downloadedBytes)
                val buffer = ByteArray(8192)
                var bytesRead: Int
                while (input.read(buffer).also { bytesRead = it } != -1) {
                    output.write(buffer, 0, bytesRead)
                }
            }
        }

        if (verifyChecksum(tempFile, fileSpec.sha256Checksum) && tempFile.renameTo(targetFile)) {
            Result.success(targetFile)
        } else {
            tempFile.delete()
            Result.failure(SecurityException("SHA-256 integrity check failed."))
        }
    }

    private fun verifyChecksum(file: File, expectedHash: String): Boolean {
        if (!file.exists()) return false
        val digest = MessageDigest.getInstance("SHA-256")
        file.inputStream().use { input ->
            val buffer = ByteArray(8192)
            var bytesRead: Int
            while (input.read(buffer).also { bytesRead = it } != -1) digest.update(buffer, 0, bytesRead)
        }
        return digest.digest().joinToString("") { "%02x".format(it) }.equals(expectedHash, ignoreCase = true)
    }
}
```

### [带热状态与取消监控的本地推理引擎](#local-inference-engine-with-thermal-and-cancellation-monitoring)

该引擎在主线程外处理扩散 timestep，并持续检查协程取消与设备热降频：

```kotlin
class DiffusionInferenceEngine(
    private val manifest: ModelManifest,
    private val textEncoder: HardwareModelRuntime,
    private val unetEngine: HardwareModelRuntime,
    private val vaeDecoder: HardwareModelRuntime
) {

    suspend fun generateImage(
        prompt: String,
        steps: Int,
        onProgress: (step: Int, totalSteps: Int) -> Unit
    ): Result<Bitmap> = withContext(Dispatchers.Default) {
        try {
            val condEmbeddings = textEncoder.execute(SimpleTokenizer.tokenize(prompt))
            val uncondEmbeddings = textEncoder.execute(SimpleTokenizer.tokenize(""))

            var latents = FloatArray(1 * manifest.latentChannels * manifest.latentSize * manifest.latentSize) {
                Random.nextFloat()
            }

            for (step in 0 until steps) {
                if (!coroutineContext.isActive) {
                    return@withContext Result.failure(CancellationException("Cancelled by user."))
                }

                val timestep = 1000 - ((step + 1) * (1000 / steps))
                val noiseUncond = unetEngine.executeDenoise(latents, uncondEmbeddings, timestep)
                val noiseCond = unetEngine.executeDenoise(latents, condEmbeddings, timestep)

                val cfgScale = manifest.schedulerConfig.guidanceScale
                val blendedNoise = FloatArray(noiseCond.size) { i ->
                    noiseUncond[i] + cfgScale * (noiseCond[i] - noiseUncond[i])
                }

                latents = SchedulerMath.stepDDIM(latents, blendedNoise, step, steps)
                onProgress(step + 1, steps)
            }

            val floatImageBuffer = vaeDecoder.execute(latents)
            Result.success(convertFloatsToBitmap(floatImageBuffer, manifest.targetResolution))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

把以上拼在一起，就得到完整流水线。

## [实测基准](#empirical-benchmarks)

> 免责声明：下列性能数字是示意性操作区间。真实延迟、吞吐与内存消耗会因模型修订、量化 profile、硬件 delegate 可用性、分辨率、去噪步数、环境温度与设备热历史而显著变化。

### [基准方法框架](#benchmark-methodology-framework)

要得到可复现指标，测试环境必须记录：

1. **硬件环境：** 精确 SoC、活跃 CPU/GPU/NPU 频率、系统总 RAM。
2. **模型参数：** 精度（如 FP16 vs INT8 混合）、tensor 布局（NHWC vs NCHW）、分辨率、scheduler 步数。
3. **执行状态：** 区分 Cold-Start（含 delegate 初始化、二进制加载、`mmap` 分配）与 Warm-Start（后续执行，内存池已预分配）。
4. **热状态：** 初始基线核心温度 vs. 持续状态（连续跑 5 次之后）。

### [性能摘要](#performance-summary)

![性能摘要](https://miro.medium.com/v2/resize:fit:700/1*ljmjefeHKJaERi-yu-epwQ.jpeg)

> 大型未量化 FP32 模型（800 MB+）可能触发 GPU **OOM 崩溃**。CPU 执行更稳，但每张图可能要 **数分钟**。

## [应避免的反模式](#anti-patterns-to-avoid)

试错与真实部署里，几类架构反模式反复导致崩溃、OOM 或性能劣化：

- ❌ 把原始 FP32 模型直接发到手机
- ❌ 假定每台手机的 NPU 都支持全部 UNet 算子
- ❌ 写死动态 tensor 布局（NHWC vs NCHW）
- ❌ 一次性把所有模型子组件装进内存
- ❌ 在 Android 主线程跑模型推理
- ❌ 对 VAE 层套未校准的 INT8 量化

## [结语](#conclusion)

把端侧生成图像 AI 当成系统工程来做，在 Android 上是可行的。尽管有热、RAM 与硬件兼容限制，本地执行仍带来隐私、离线能力与零基础设施成本。稳定上线需要高效资源管理、动态内存分配、delegate 选择、热控、模块化 model manifest，以及可回退的运行时。

往前看，LCM、SDXS 与减步蒸馏一类技术正把扩散从 20–50 步压到 2–4 步，延迟可降约 80%。面向移动优化的扩散模型与更标准化的 Android ML API，也在推动 NPU 加速下接近实时的生成。
