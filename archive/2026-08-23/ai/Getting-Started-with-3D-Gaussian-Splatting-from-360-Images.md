---
title: "从 360° 影像入门 3D Gaussian Splatting（360° Gaussian Pro 版）"
title_en: "Getting Started with 3D Gaussian Splatting from 360° Images (360° Gaussian Pro Edition)"
source_url: https://qiita.com/Tks_Yoshinaga/items/cfc9d6575afd78f12f31
author: Tks_Yoshinaga
published_at: 2026-08-23
translated_at: 2026-08-23
tech_domain: ai
tags: [3dgs, gaussian-splatting, colmap, vr, 360]
---

# 从 360° 影像入门 3D Gaussian Splatting（360° Gaussian Pro 版）

原文链接：<https://qiita.com/Tks_Yoshinaga/items/cfc9d6575afd78f12f31>

原文作者：Tks_Yoshinaga

作者：[Tks_Yoshinaga](https://qiita.com/Tks_Yoshinaga)

发布于 2026 年 8 月 23 日。

**用 360° Gaussian Pro，从 360° 影像更快做出三维高斯溅射（3D Gaussian Splatting, 3DGS）。**

## [引言](#introduction)

上一篇 [Getting Started with 360° Image Gaussian Splatting (Basic Workflow)](https://qiita.com/Tks_Yoshinaga/items/354e9082bd607f3cefee) 里，我介绍了用 **360° Gaussian** 从 360° 视频生成三维高斯溅射（3DGS）的流程。

那之后，工具作者发布了 **Pro 版，生成 3DGS 比原版更简单、快得多**。本文是 **360° Gaussian Pro** 的快速入门。

## [环境](#environment)

### [电脑配置](#pc-specs)

| 项 | 规格 |
| --- | --- |
| OS | Windows 11 |
| GPU | NVIDIA GeForce RTX 4070 SUPER |
| CPU | AMD Ryzen7 8700G |
| RAM | 32 GB |

### [360° 相机](#360-camera)

- **Insta360 X4 Air**

  其他厂家的相机比如 THETA 也支持。推荐 **8K 或更高**。

### [软件](#software)

| 软件 | 用途 |
| --- | --- |
| [LichtFeld Studio v0.5.3](https://lichtfeld.io/) | 三维高斯溅射的 GUI 工具 ※ |
| [360° Gaussian Pro v1.0.1](https://www.360gaussianpro.com/) | 自动抽帧、遮罩和运动恢复结构（SfM）的工具 |

> **※ 关于拿到 LichtFeld Studio**
>
> LichtFeld Studio v0.5.x 的预编译二进制已经停止免费分发。v0.4.0 仍可免费下载。要用 v0.5.3，必须买付费许可或从源码构建。
>
> 想试 GitHub 上的最新功能，或买许可前先试，请看下面的注意事项，自己构建。
>
> **从源码构建的注意事项**
>
> 自己构建请跟 [这里的构建说明](https://github.com/MrNeRF/LichtFeld-Studio/wiki/Build-Instructions-%E2%80%90-Windows)。
>
> **提示 1**
>
> 官方构建说明没写，但可能需要 **Perl**。从 [Strawberry Perl](https://strawberryperl.com/) 安装。
>
> 注意 Perl 自带的 cmake 可能压过系统 cmake，所以先临时把 `C:\Strawberry\c\bin\cmake.exe` 改名，确认不需要再删。保险起见，之后重启电脑。
>
> **提示 2**
>
> 官方文档 **Clone repository** 一节里，下面这条命令在作者环境里并不总能正确下完所有需要的文件：
>
> `git clone https://github.com/MrNeRF/LichtFeld-Studio`
>
> 为了避免子模块漏下，建议加 `--recursive`，或用 Fork、GitHub Desktop 这类客户端：
>
> `git clone --recursive https://github.com/MrNeRF/LichtFeld-Studio`
>
> **提示 3**
>
> 注意：**跳过** **Checkout stable version** 步骤里的 `git checkout v0.4.0`。
>
> 构建很久，请留出充足时间。

## [和上一版的差别](#differences-from-the-previous-version)

最明显的差别如下：

- **相机对齐现在用最新的 COLMAP / GLOMAP**
- **输入格式更宽**：除了等距柱状投影（equirectangular）图，现在还能喂 **双鱼眼图**，甚至手机拍的普通（非 360°）视频
- **用 SAM3 做遮罩**
- **支持加入用手机或数码相机拍的细节照片**
- **每一步处理都明显加速**

### [给谁用](#who-is-it-for)

- **想要简单流程的人**：加上视频之后，如果默认设置就满意，可以 **一个按钮走到 3DGS 生成**
- **想自己调参数的人**：COLMAP 对齐参数暴露在界面上。适合写论文时不能只说「我用工具对齐了」，还要说清 **到底用了哪些参数** 的人

## [整体流程](#overall-workflow)

高斯溅射一般有下面四步。

| # | 步骤 | 说明 |
| --- | --- | --- |
| 1 | **拍摄（Capture）** | 用 360° 相机录场景 |
| 2 | **SfM**（Structure from Motion，运动恢复结构） | 估计每张图是从哪个位置拍的 |
| 3 | **点云生成** | 根据 SfM 得到的相机位置生成点云 |
| 4 | **高斯溅射** | 从点云生成三维高斯溅射模型 |

## [第 1 步。拍摄并导出视频](#step-1-capturing--exporting-the-video)

用 360° 相机录场景。处理可能很久，熟悉流程之前建议用 **一分钟以内的短片** 试。

如上所述，等距柱状投影图仍和上一版一样能用，但既然有得选，这次用 **双鱼眼**。

如果更想试等距柱状投影，见上一篇（Basic Workflow）的第 1 步，里面有 Insta360 Studio 的导出步骤和防抖设置。

如果用的是 Insta360 相机：

1. 用 USB 线把 Insta360 连到电脑
2. 把要处理的 `.insv` 文件拷到电脑

就这样。不用转成等距柱状投影，很干脆。

## [第 2 步。SfM 和点云生成](#step-2-sfm-and-point-cloud-generation)

这里轮到 360° Gaussian Pro 上场。

上一版你得自己选 SfM 工具，比如 SphereSfM 或 Metashape。这个工具统一用 COLMAP，不用再装别的应用。

步骤在下面视频里也讲得很细：

[嵌入内容（原站 YouTube）](https://www.youtube.com/watch?v=njYAUpHk_VI)

- 📺 How to use 360° Gaussian Pro

### [2.1 抽图](#21-image-extraction)

1. 启动 360° Gaussian Pro
2. 把 `.insv` 拖到 Add footage 上开始 ※ 如果用等距柱状投影或普通视频试，改拖 `.mp4`

3. 配置抽取设置

先用默认即可，但 Frame Extraction 提供这些选项：

| 参数 | 说明 |
| --- | --- |
| Extract frame every | 按指定间隔抽图，单位是秒（或帧） |
| Pick sharpest frame per interval / window | 是否通过比较邻近帧优先选最不糊的图，以及比较范围。比如 `10` 会比较左右各 5 帧，挑最锐的 |
| Pinhole Split | 鱼眼图重投影成多少块针孔瓦片。`1 split` 最快但大约只覆盖鱼眼的一半，`5 splits`（默认）用重叠瓦片覆盖整球，`9 Splits` 瓦片重叠最多，适合复杂场景 |

细节见官方文档。

![添加素材](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/61742/858c86ae-3ac2-48df-80d7-be63b2623faa.png)

ℹ️ 等距柱状投影输入不使用 Pinhole Split；它总是转成 6 个立方体贴面。

4. （可选）这些步骤会让下一节的遮罩设置更轻松  
4.1 点时间轴，选一帧用来预览遮罩  
4.2 点 Extract one frame

### [2.2 图像遮罩](#22-image-masking)

这个功能会自动遮掉高斯溅射不需要的区域。

1. 点 Masking 标签
2. 如果上一节点了 Extract one frame，图会显示出来

ℹ️ 如果没点 Extract one frame，不会显示图，但遮罩本身仍能正确工作。

3. Keyword SAM3 让你按关键词遮罩（多个关键词用逗号分开）
4. 点 Detect this frame，几秒后预览结果（不需要预览可以跳过）

下面是指定 `person,sky` 的结果。可以看到人和天空被遮住（粉色）。

![遮罩设置](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/61742/d2ff8abb-2b4b-4a5c-b1c6-c1bbeb56d869.png)

![遮罩结果](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/61742/b2ac362b-5a5e-4bb6-9d1b-7577fa727af3.png)

5. Paintbrush 可以用鼠标描你想排除的物体（可以跳过）
6. Circle Mask（仅双鱼眼）遮掉相机成像圆以外的区域。也可以缩小半径，收窄用于处理的区域

💡 遮罩重要的两个原因。第一，人和车这类运动主体、以及特征点很少的低纹理物体，容易变成 SfM 的噪声，降低相机位姿估计精度。SfM 精度直接影响最终高斯溅射的质量，所以用遮罩排除它们很重要。第二，同样的噪声在训练时也会掉质量。同一主体因拍摄位置不同而看起来不一样时，高斯很难收敛到正确的形状和颜色。遮罩在两个阶段都保护质量。

### [2.3 SfM 配置](#23-sfm-configuration)

这里先用默认也行。

供参考，Matcher 让你选匹配方法。

![对齐设置](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/61742/f1e4e5a3-532b-43d0-ba1a-0228474aec27.png)

| Matcher | 说明 |
| --- | --- |
| Sequential | 每帧只和拍摄顺序上的邻居比。快，视频输入里连续帧有重叠时通常最好 |
| Exhaustive | 每张图跟其他所有图比。对无序照片集最稳、质量最高，但也最慢，因为配对数随图像数平方增长 |
| Spatial | 用 GPS 只比物理上靠近的图。有可靠 GPS 时又快又好，还会把结果缩放到真实世界尺寸（对 `.osv` 文件仍是实验性的） |

其余选项如下：

| 设置 | 说明和好处 |
| --- | --- |
| GLOMAP global mapper | 不是一帧一帧注册，而是一次解出所有相机位置。快 10–100 倍，默认打开。 |
| Geometry Timeline Check | 实验性。检测并自动修复长得像但其实是不同地点（一模一样的室内、上了又走下来的楼梯井等）被当成同一处、模型折到自己身上的情况。它用的规则是：时间上离得很远的帧不该在同一位置。只有真的检测到折叠时，处理时间才会多几分钟 |
| Reuse Fisheye features | 复用第 1 阶段检出的特征，而不是在针孔瓦片上重新检测。针孔阶段更快，大约只要 1 GB 显存（通常要 4–8 GB）。不过细部会稍软，有些可能缺失 |

屏幕截图里其他项的快速说明：

- Overlap：Sequential 时，左右各和多少邻近帧比较
- Loop detection：打开检测回到同一地点并闭环的处理
- Lens priors：初始镜头参数。`Auto (recommended)` 即可
- Preset quality：质量预设。用 `Save...` 把自己的设置存成名字

打开 Advanced settings 还会露出大量 COLMAP 选项（例如 SIFT 特征上限，鱼眼默认 32,768，针孔瓦片 8,192）。

细节见官方文档。

### [2.4 加入细节照片（可选）](#24-adding-detail-photos-optional)

Pro 版可以混入手机或单反拍的高分辨率照片，不只是 360° 图。这样就能复现 360° 照片容易丢掉的文字和插图。

要加入，用屏幕右侧的 Detail photos → Add detail photos...，选装细节图的文件夹即可。

![细节照片](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/61742/17ee58c1-3997-4ace-a545-6a5866c749bb.png)

⚠️ 注意：细节图也会走 SfM，所以请从多个视点提供照片，估计才容易。上面的例子里，信息板拍了 14 次，每次稍微换角度。

### [2.5 选择三维高斯溅射训练工具](#25-choosing-the-3d-gaussian-splatting-training-tool)

点 Train 标签。

Pro 版支持 LichtFeld Studio、Postshot 和 Brush。如果也想把训练自动化，装其中一个并配好。可执行文件路径、Iterations、Strategy、Max Splats 等都可以在这个屏幕设。

我通常想看 3DGS 训练过程，所以选 No Train。

![训练设置](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/61742/783be057-b742-4041-9e01-cb481e368be9.png)

### [2.6 跑流水线](#26-running-the-pipeline)

都设好之后，点屏幕底部的 Run Pipeline。进度也在底部显示，等它跑完即可。

![进度](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/61742/525e858d-ffa2-44dc-948a-6ea24d72a9cd.png)

⚠️ 如果处理看起来卡很久：点屏幕左下角的 Log 按钮看日志。

跑完后打开 Alignment 标签看结果。输出保存在 `0_train_data`。

![对齐结果](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/61742/f77ad714-2660-4a3f-ac6f-48bc2f6b2e2e.png)

如果这时结果不是你要的，可以改设置再跑一遍对齐。如果结果歪了或偏了，可以拖 Rotate / Translate 参数（X、Y、Z）用鼠标调（Align ground 也能吸到地平面）。最后点 Apply edits，把改动写进输出文件。

ℹ️ 两个工具都能调位置和朝向。LichtFeld Studio 也能改位置和朝向，哪个顺手用哪个。

注意上面截图里红色的相机是 2.4 加入的细节照片。可以看到它们聚在信息板周围。

## [第 3 步。高斯溅射](#step-3-gaussian-splatting)

### [3.1 加载数据](#31-loading-data)

1. 启动 LichtFeld Studio
2. 把上面生成的 `0_train_data` 文件夹拖到窗口上
3. 出现 Load Dataset 对话框时，点 Load

![加载数据集](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/61742/01f8f026-371f-4258-8508-65aa32a62a11.png)

确认点云和图像加载正确。如果不需要显示相机图像，取消勾选屏幕右侧 Rendering 标签里的 Camera Frustums。

![点云](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/61742/71d701b2-78a3-46eb-b2ec-29d62b3c0d12.png)

![渲染选项](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/61742/18fbaced-e518-4cbf-aebb-3423906bc5bf.png)

### [3.2 训练配置](#32-training-configuration)

下面是一份训练配置的例子。熟悉之后再试别的设置。

1. 点 Training 标签
2. Strategy 选 `MRNF`
3. 按情况设 Steps Scaler

| 条件 | 建议值 |
| --- | --- |
| 300 张图或更少 | `1` |
| 超过 300 张图 | `图像数 / 300` |

⚠️ 如果训练不顺利：即使用上面的设置也不收敛、画面发白，把 Steps Scaler 设成 `图像数 / 300` 的 2–3 倍往往更稳。

4. 用 Max Gaussians 设高斯数量上限。默认有点高，按扫描区域大小，从大约 1,500,000 开始看效果是好办法。觉得细节不够再加大。

可选设置 1：如果要用遮罩图，配下面这些：

- Mask Mode 设成 `Ignore`
- 取消勾选 Alpha Mask

可选设置 2：如果加了细节照片，打开 Undistort。

其他参数先用上面的设置，更熟了再试。

![训练参数](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/61742/e33a0698-acfb-41ab-b0c9-4e84f280bc42.png)

### [3.3 跑训练](#33-running-training)

1. 用鼠标放大你想看训练进展的区域（我这边是中间物体附近）
2. 点 Start Training 开始
3. 画面先糊，随着步数推进逐渐变清晰

![训练中](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/61742/60748314-8dda-4250-a50d-2903c18ad144.png)

到达步数上限后训练自动结束。想保存中间结果，点 Save Checkpoint 记录当时的状态。

### [3.4 导出](#34-export)

输出数据可以用 SuperSplat Editor 这类工具做视频，或在查看器里看。

1. 点 File → Export
2. 选输出格式（例如 `.ply`）

## [小结](#summary)

我之前一直用原来的免费版，但 Pro 版的 SfM 精度提高了，3DGS 输出质量也跟着提高。遮罩精度也提高了。每一步都更快，等的时间更少。

本文走的是双鱼眼流程，等距柱状投影的流程一样。在我的测试环境里，等距柱状投影处理其实更快。我也更喜欢等距柱状投影图的结果。这会因场景和口味而变，不妨两种都试，找到适合你的流程。

Pro 版售价 149 欧元。不是免费的，但大致和这个领域老牌标准 Metashape 同一价位。考虑到抽帧、遮罩和 SfM 都能一键跑、不用在应用之间切换，我觉得这份方便值得考虑。有兴趣的话请试一下。

📝 关于提问：建议去官方 Discord，小事也可以直接问我。

### [样例输出（有 / 无细节照片）](#sample-outputs-with--without-detail-photos)

供参考，下面是有细节照片和没有细节照片的输出。

- 有细节照片
- 没有细节照片
