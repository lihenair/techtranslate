---
title: "在 React Native 中构建 3D AI 形象"
title_en: "Building a 3D AI assistant using React Native and GPT-Realtime"
source_url: https://margelo.com/blog/building-a-3d-ai-avatar-in-react-native
author: Dave Mkpa-Eke
published_at: 2026-08-17
translated_at: 2026-09-05
tech_domain: ai
tags: [ai, react-native, 3d, filament, realtime, openai]
cover_image: https://margelo.com/blog/building-a-3d-ai-avatar-in-react-native/opengraph-image
---

# 在 React Native 中构建 3D AI 形象

原文链接：<https://margelo.com/blog/building-a-3d-ai-avatar-in-react-native>

原文作者：[Dave Mkpa-Eke](https://github.com/DaveyEke)

![文章头图](https://margelo.com/blog/building-a-3d-ai-avatar-in-react-native/opengraph-image)

作者：[Dave Mkpa-Eke](https://github.com/DaveyEke)

发布于 2026 年 8 月 17 日。

**用 React Native 做的对话式 3D 角色：Filament 渲染的松鼠，经原生 WebSocket 由 OpenAI gpt-realtime 发声，振幅驱动口型，并用工具调用写入真实日历。**

如果你玩过手机游戏，多半见过 [Talking Tom](https://en.wikipedia.org/wiki/Talking_Tom_%26_Friends)。没见过的话：Talking Tom and Friends 里有一个可点的 3D 角色，会把你说的话再说回去，并播各种好玩动画。

据估计 Talking Tom 系列下载量[超过 230 亿次](https://wnhub.io/news/other/item-44340)，足见这类移动应用有多火、多赚钱。今天我们做的东西有点像，但加了几处有趣改动，用途不同。现在的技术圈里有一样原版 Talking Tom 开发者没有的东西：生成式 AI。先别急着翻白眼觉得又是一篇「AI 水文」——我们会用 OpenAI 的 [gpt-realtime](https://openai.com/index/introducing-gpt-realtime/) 让 3D 角色真正能对话（带实时语音），还能通过工具调用（tool calling）办事。

> 工具调用指 AI 模型与外部工具、应用编程接口（API）或系统交互以增强能力。*[来源](https://www.ibm.com/think/topics/tool-calling)*

此外，这款用 React Native 做的应用叫 **AvatarAssist**：一个 3D AI 角色助手，能回答动物相关问题，还能通过程序化操作手机日历，帮我们安排去动物园。

好，开始。

## [让模型活起来](#bringing-the-model-to-life)

如上所述，应用要有一个*对话式 3D 角色*——但在 React Native 里怎么渲染 3D？我们用 Margelo 做的 [react-native-filament](https://margelo.github.io/react-native-filament/)！

> react-native-filament 是 Google [Filament](https://github.com/google/filament) 的 React Native 移植版。Filament 是面向 Android、iOS、Windows、Linux、macOS 与 WebGL2 的实时基于物理的渲染引擎。

[嵌入内容（原站视频）](https://margelo.com/videos/avatarassist-rendering-character.mp4)
![嵌入内容（原站视频）](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Building-a-3D-AI-assistant-using-React-Native-and-GPT-Realtime/avatarassist-rendering-character.gif)

Amy 用 react-native-filament 渲染，在森林里 idle。

我们的 3D 模型是现成资源：[Ivana Boskovic 的 “Cute Character with Animations”](https://sketchfab.com/3d-models/cute-character-with-animations-477a8bdf8488431799fbfb5e6fcc94af)，从 [Sketchfab](https://sketchfab.com/) 以 [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) 下载。格式是 `.glb`：单个二进制文件，装着网格、骨架、贴图，以及作者做好的每一段动画。最后这一点比听起来重要，后面会再提。

把模型摆上屏幕要三块：`FilamentView` 是 Filament 画进去的表面，`useModel` 加载资源，`ModelRenderer` 把已加载模型放进场景：

```tsx
import {FilamentView, ModelRenderer, useModel} from 'react-native-filament';

export function SquirrelScene() {
  const model = useModel(require('../../assets/squirrel.glb'));

  return (
    <FilamentView style={StyleSheet.absoluteFill}>
      <ModelRenderer model={model} />
    </FilamentView>
  );
}
```

`useModel` 是异步的，并通过 `model.state` 报告进度。我们这份约 1.8 MB，解析并上传到 GPU 要几百毫秒，所以场景已挂载但还空着的窗口真实存在。后面用这个状态决定应用何时真正可展示，而不是先甩出一片空森林。

再说动画片段。这只松鼠带着 **二十** 段：`idle`、`happy`、`happy.001` 到 `happy.006`、四种 `touch me`、`hungry`、`kupanje` 等等。我们只用两段：永远循环的 `idle`，以及第一次开口说话时挥手的 `happy welcome 2`。

`useAnimator` 给出播放句柄，还能告诉我们每段有多长，这样就不用写死时长——作者一重新导出模型就会悄悄坏掉：

```tsx
const animator = useAnimator(model);

useEffect(() => {
  if (animator != null && animator.getAnimationCount() > IDLE_ANIM) {
    idleDuration.value = animator.getAnimationDuration(IDLE_ANIM);
    waveDuration.value = animator.getAnimationDuration(WAVE_ANIM);
  }
}, [animator, idleDuration, waveDuration]);
```

真正好玩的是播放方式：我们不从 React 里播。Filament 给你一个**每帧触发的 render callback**，作为 worklet 跑在 UI 线程，不在 JS 线程。里面我们为每段动画自备时钟，每帧决定播哪段、播到哪里：

```tsx
RenderCallbackContext.useRenderCallback(({timeSinceLastFrame}) => {
  'worklet';

  // 有人请求挥手：启动时钟并清掉请求。
  if (waveRequested.value > 0 && waveClock.value < 0) {
    waveClock.value = 0;
    waveRequested.value = 0;
  }

  let clipIndex = IDLE_ANIM;
  let clipTime = 0;

  if (waveClock.value >= 0) {
    waveClock.value += timeSinceLastFrame;
    if (waveClock.value < waveDuration.value) {
      clipIndex = WAVE_ANIM;      // 挥手期间接管
      clipTime = waveClock.value;
    } else {
      waveClock.value = -1;       // 结束，退回 idle
    }
  }

  if (waveClock.value < 0) {
    idleClock.value += timeSinceLastFrame;
    clipTime = idleClock.value % idleDuration.value;  // 循环
  }

  animator.applyAnimation(clipIndex, clipTime);
  animator.updateBoneMatrices();
});
```

所以 idle 用时钟对自身时长取模来循环；挥手则抢占 idle，直到时钟超过挥手长度。同一时间只有一段，每帧选定。

时钟按回调给的 `timeSinceLastFrame` 推进，因此无论 60Hz 还是 120Hz，片段速度一致。

值得多说的是 `waveRequested`。它是**共享值（shared value）**：JS 侧随便哪都能设成 `1`，这个循环下一帧就接住，一次 React 重渲染都不需要。这里很关键：角色得在 60fps 动画，同时应用还在干真的重活，比如解码模型流式音频。

### [把相机对准模型](#pointing-a-camera-at-the-model)

场景里有模型还不等于有画面。得有东西决定你站哪、透过什么镜头看——在 Filament 里就是相机。`useFilamentContext` 给出属于当前视图的那一台：

```tsx
const {camera, view} = useFilamentContext();
```

我们要两件事：模型好好落在画面里，以及用户拖动能转它。两者同样放在 render callback 里，理由同上：手指在屏上拖，相机应在手指移动的那一帧跟上。

[嵌入内容（原站视频）](https://margelo.com/videos/avatarassist-dragging.mp4)
![嵌入内容（原站视频）](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Building-a-3D-AI-assistant-using-React-Native-and-GPT-Realtime/avatarassist-dragging.gif)

在屏幕上拖动以旋转模型。

取景是镜头选择。我们给相机 35mm 焦距：够宽能装下模型，又不像更短镜头那样鱼眼：

```tsx
camera.setLensProjection(35, aspect, 0.1, 100);
```

`aspect` 里藏着小坑。投影依赖视图宽高比，比例一变就要重建：转屏、键盘弹出、平板窗口缩放。每帧都调 `setLensProjection` 最省事，但那是在为同一个答案反复建投影矩阵。所以我们把上次宽高比放进共享值，真变了才重建：

```tsx
const aspect = view.getAspectRatio();
if (prevAspect.value !== aspect) {
  prevAspect.value = aspect;
  camera.setLensProjection(FOCAL_MM, aspect, NEAR, FAR);
}
```

然后是环绕。我们不转模型，而是让相机绕着转，灯光和阴影位置就不动。相机在球面上：离目标点 `radius`，角度随用户拖动，始终看回目标：

```tsx
const eye: [number, number, number] = [
  tx + radius * Math.cos(vertical) * Math.sin(horizontal),
  ty + radius * Math.sin(vertical),
  tz + radius * Math.cos(vertical) * Math.cos(horizontal),
];
camera.lookAt(eye, [tx, ty, tz], [0, 1, 0]);
```

目标是 `[0, 2.65, 0]` 而不是原点，这样相机看向模型胸口，而不是脚边地板。

这段里有个细节比看起来干得多。`horizontal` 不是一个值，是两个之和：

```tsx
const horizontal = horizontalTurn.value + gyroHorizontalTurn.value;
```

一个来自拖动，一个来自手机陀螺仪；相加后，倾斜设备会轻微产生视差，拖动仍叠在上面。

第二个值得拆开说：场景随手机倾斜而动，是那种挺舒服的细节。它来自重力传感器，经 Reanimated 读取：

```tsx
const gravity = useAnimatedSensor(SensorType.GRAVITY, {
  interval: 'auto',
  adjustToInterfaceOrientation: true,
});
```

用重力而不是陀螺仪角速度，因为重力告诉我们哪边是下，也就是手机此刻怎么被握着。向量归一化后取水平分量，再和启动时的朝向比，于是「无倾斜」= 用户碰巧怎么握着，而不是必须完全放平：

```tsx
const normalizedX = gravityVector.x / magnitude;
if (baseX.value == null) {
  baseX.value = normalizedX;      // 第一次读数成为静息姿势
}
const deltaX = normalizedX - baseX.value;
```

这个 delta 干两件事。它变成上面的 `gyroHorizontalTurn`，轻推相机，倾斜时多露出模型一侧。它还把身后的森林平移几个像素：

```tsx
const bgSwayStyle = useAnimatedStyle(() => ({
  transform: [{scale: BG_OVERSCAN}, {translateX: sway.value}],
}));
```

这里的 `scale` 是承重的。若背景刚好等于屏幕，横滑会把空边拖进视野，所以略放大再在余量里滑。

摆动也做了平滑而非精确跟踪，因为原始传感器抖得能让整场发抖：

```tsx
sway.value += (targetSway - sway.value) * SWAY_SMOOTH;
```

[嵌入内容（原站视频）](https://margelo.com/videos/avatarassist-tilting.mp4)
![嵌入内容（原站视频）](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Building-a-3D-AI-assistant-using-React-Native-and-GPT-Realtime/avatarassist-tilting.gif)

手机倾斜时场景随之摆动。

### [把模型放进某处](#putting-the-model-somewhere)

Filament 场景里只有松鼠和两盏灯：没有树、没有路、没有地板。身后的森林是视频，用强大的基于 [Nitro](https://nitro.margelo.com/) 的 React Native 播放器 [react-native-video](https://github.com/TheWidlarzGroup/react-native-video) 播，视图叠在 Filament 下面。Filament 视图没有 skybox，模型以外全透明，森林直接透出来。

用视频而不是静图，因为静止森林衬着会呼吸的角色像影棚布景，风里晃的叶子才有对味。代价是必须循环，而我们原来不循环：尾帧和首帧肉眼可见不同，每四秒森林就跳一下。

我们在资源侧修，而不是应用侧，用 [`ffmpeg`](https://www.ffmpeg.org/) 把片段尾部交叉淡入头部，让结尾融进开头。结果是真正能循环的文件，应用不用耍花招：

```tsx
import {VideoView, useVideoPlayer} from 'react-native-video';

// 撰写时仍为 beta 的 v7 API
export function ForestVideoBackground() {
  const player = useVideoPlayer(SRC, player => {
    player.muted = true;
    player.loop = true;
  });

  return (
    <VideoView
      player={player}
      resizeMode="cover"
      style={styles.video}
      // Android 上 SurfaceView 不能变换，而这层会随陀螺仪摆动。
      surfaceType="texture"
    />
  );
}
```

然后放进场景最底层，松鼠和森林就是按正确顺序叠的两层平面：

```tsx
<View style={styles.container}>
  <ForestVideoBackground />
  <SquirrelModel model={model} animator={animator} />
</View>
```

### [模型其实没怎么投下的影子](#the-shadow-the-model-doesnt-really-cast)

让角色感觉站在某处、而不是浮在前面的最便宜手段之一，是脚边有影子。我们有，但*有点假*。

确实有一盏会投射阴影的灯：

```tsx
<Light type="directional" intensity={20_000} colorKelvin={5_200} castShadows={true} />
```

麻烦在于投射阴影需要落点表面，而场景里没有。`.glb` 里没有地面，因为地面是 Filament 视图*后面*的森林视频。Filament 不能往不属于自己的像素上丢阴影，所以 `castShadows` 只换来身体自阴影，脚下什么都没有。

于是我们用一张柔和的深色椭圆 PNG 来假：

```tsx
<Animated.View style={styles.wrap} pointerEvents="none">
  <NitroImage image={SHADOW} style={styles.img} resizeMode="contain" />
</Animated.View>
```

注意它住哪：普通图片，用 [react-native-nitro-image](https://github.com/mrousavy/react-native-nitro-image) 渲染，不是 3D 场景的一部分，树里紧挨在 `<SquirrelModel />` 之前，画在模型下面。扁平椭圆、约 90% 不透明度，就够读成接触。

它还得粘在脚上，而且会动：键盘打开时整场会上移缩小。把影子放进与模型同一个动画包装里就免费得到——一次变换带走俩。

## [给模型一个声音](#giving-the-model-a-voice)

Amy 能渲染、idle、挥手。下一步是说话。最显而易见的路子，大概是我们都做过的：用户消息丢给 LLM，等文本，再交给 TTS，播放结果。

这条管线有个能*感觉到*的问题。TTS 能像样念出来的最小单位通常是整句，所以第一个声音要等模型写完第一句*并且*合成器变成音频。每次两段等待背靠背。我们后来在真机上量过这条路径，第一个词要 **6.1 秒**。

所以我们跳过它。[gpt-realtime](https://openai.com/index/introducing-gpt-realtime/) 自己以 token 形式经 WebSocket 吐音频。模型后面没有合成步骤，因为模型*就是*合成器；它能发的最小单位是音节的一截，而不是整句。

传输用 WebSocket，我们用 [react-native-nitro-websockets](https://fetch.margelo.com/docs/websockets)，而不是 React Native 内置——主要是因为内置做不到的一点：能在应用启动、JS bundle 跑起来之前就在原生侧开连接。Galaxy S22 上，32 次启动的中位握手从 1,249ms 降到 620ms，大约一半，这些时间首轮回复就不用耗在等 socket 上。

Amy 说话期间，音频以连续 base64 块到达，每一块都从原生跨进 JS。

开连接是普通部分：

```tsx
import {NitroWebSocket} from 'react-native-nitro-websockets';

const ws = new NitroWebSocket(REALTIME_URL, undefined, {
  Authorization: `Bearer ${OPENAI_API_KEY}`,
});
```

> API key 打进应用里，谁有你的 `.apk` 就能抠出来花。演示可以；生产请把 key 放服务器，给应用短命的[临时 token](https://platform.openai.com/docs/api-reference/realtime-sessions)。

有趣的是连上后说的第一句话。Realtime 会话一开始很泛，我们得告诉它在扮演谁：用什么声音、要什么音频格式、怎么表现、允许调哪些工具。

```tsx
ws.onopen = () => {
  ws.send(
    JSON.stringify({
      type: 'session.update',
      session: {
        type: 'realtime',
        output_modalities: ['audio'],
        audio: {
          output: {
            voice: 'marin',
            format: {type: 'audio/pcm', rate: 24000},
          },
        },
        instructions: buildInstructions(new Date()),
        tools: [ADD_CALENDAR_EVENT_TOOL],
      },
    }),
  );
};
```

有几项值得一提。`output_modalities: ['audio']` 表示我们根本不要文本回复：仍会拿到 Amy 说了什么的转写，但是音频的旁路，而不是生成目标。`instructions` 里住着 Amy 的人设，每次用当前日期现编，好让模型知道「明天九点」是什么意思；写日历时再细说。

### [把数据块变成声音](#turning-chunks-into-a-voice)

会话配好后，一轮就是听回来的事件。我们关心的两个会交错到来，每轮回复几十次：

```tsx
case 'response.output_audio.delta':
  activeTurn?.onAudioDelta(event.delta);       // base64 PCM16 @ 24kHz
  break;
case 'response.output_audio_transcript.delta':
  activeTurn.transcript += event.delta;        // 字幕用的词
  activeTurn.onTranscriptDelta(event.delta);
  break;
```

播放交给 [react-native-audio-api](https://github.com/software-mansion/react-native-audio-api)，原生应用上的 Web Audio API。创建 context，里面有个数特别要紧：

```tsx
const audioContext = new AudioContext({sampleRate: 24000});
```

这个 `24000` 必须和向模型要的采样率一致。错了音频仍会开开心心播，只是速度不对，嗓音尖得吓人。

接着块进入缓冲队列，首尾相接成连续流，而不是一段段独立音：

```tsx
const queue = audioContext.createBufferQueueSource({pitchCorrection: false});
```

填队列有个坑。解码在原生且异步，若每来一块就开火解码，完成顺序可能乱掉，乱序入队立刻听成搅碎的语音。我们用 promise 链强制到达顺序：

```tsx
enqueue(base64Pcm: string) {
  decodeChain = decodeChain
    .then(async () => {
      const buffer = await audioContext.decodePCMInBase64(base64Pcm, sampleRate, 1);
      queue.enqueueBuffer(buffer);
      if (!started) {
        started = true;
        queue.start(0, 0);
      }
    })
    // 某块解码失败就丢掉；后面的仍播。
    .catch(error => console.warn('[voice] pcm chunk failed', error));
}
```

注意播放只启动一次，在第一块上。之后全是往已在跑的队列追加，所以回复能一边生成一边开口。

最后一块是知道 Amy 何时真正停。模型结束本轮与扬声器安静是不同时刻，有时差几秒——队列里还有音频。我们计缓冲进出，模型结束*且*队列排空才 settle：

```tsx
queue.onBufferEnded = () => {
  pending -= 1;
  settle();
};
```

这样应用才能在对的时机把 Amy 状态切回 idle，而不是话说到一半就切。

## [让模型的嘴动起来](#animating-the-models-mouth)

声音从静止脸上出来会很怪，所以嘴得跟着音频动。

正经唇形同步要认音素再映射口型，还要在手机上实时做，同时还在渲染 3D。我们便宜得多：听音频有*多响*，下巴就开多大。这绝称不上唇形同步，但看起来已经够像。

[嵌入内容（原站视频）](https://margelo.com/videos/avatarassist-greeting.mp4)
![嵌入内容（原站视频）](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Building-a-3D-AI-assistant-using-React-Native-and-GPT-Realtime/avatarassist-greeting.gif)

应用打开时 Amy 向访客打招呼。

响度得有来源，最干净的地方是音频图内部。`react-native-audio-api` 允许往链里插 worklet 节点，在样本去往扬声器的路上收到原始样本：

```tsx
const measureLevel = (audioData: Float32Array[]) => {
  'worklet';
  const channel = audioData[0];
  let sumOfSquares = 0;
  for (let i = 0; i < channel.length; i++) {
    sumOfSquares += channel[i] * channel[i];
  }
  const rms = Math.sqrt(sumOfSquares / channel.length);
  speechLevel.value = Math.min(1, rms * MOUTH_SENSITIVITY);
};

const levelNode = audioContext.createWorkletNode(
  measureLevel,
  1024,          // 每次读多少样本
  1,             // 声道
  'UIRuntime',
);

// 声音经该节点到扬声器，所以每个样本它都看得见。
queue.connect(levelNode);
levelNode.connect(audioContext.destination);
```

这是 1024 样本窗口的均方根，作为感知响度的不错代理，归一到 `0..1`，直接写入共享值。

注意跑在哪：`'UIRuntime'`。测量与 render callback 同运行时，数字根本不进 JS 线程。音频线程进样本，电平进共享值，Filament 渲染循环下一帧读。

于是嘴只差一行：

```tsx
transformManager.setEntityRotation(mouthEntity, mouthLevel * MOUTH_GAIN, [1, 0, 0], true);
```

`mouthEntity` 是模型下颌骨，资源加载时按名找一次：

```tsx
const mouthEntity = useMemo(() => asset.getFirstEntityByName('Mouth'), [asset]);
```

旋转一根碰巧叫 `Mouth` 的骨头，坦白说不是通用解。它绑死这款模型；换角色就得打开 `.glb` 查下颌叫什么。

把原始电平直接喂骨头，大半能对，但有两处会明显不对，都值得修。

其一是颤动。音频有噪声底，小幅波动会让下巴在 Amy 其实没说话时不停抽。于是做门限：低于阈值算静音，其余再缩放，让说话仍能张到最大：

```tsx
const target = rawLevel < MOUTH_GATE ? 0 : (rawLevel - MOUTH_GATE) / (1 - MOUTH_GATE);
```

其二是真下巴不像振幅那样动。它们猛地张开、较慢落下，所以我们按方向用两种速率朝目标平滑：

```tsx
mouthState.value +=
  (target - mouthState.value) *
  (target > mouthState.value ? MOUTH_ATTACK : MOUTH_RELEASE);
```

`MOUTH_ATTACK` 是 0.45，`MOUTH_RELEASE` 是 0.22，张嘴大约比闭嘴快一倍。小小不对称差别惊人：等速率时嘴像被弹簧拽，不对称时才像在说话。

同一信号上还挂两件小事。耳朵随下颌转三分之一角度，读起来像整颗头在动，而不只是一张嘴扇。脸颊和眉毛附近一组骨头在 Amy 说话时挪进微笑——不由响度驱动，而由「Amy 是否在说话」标志加自己的平滑，表情淡入淡出而不是硬切。

这些都不是模型作者做的。四根骨头加一点算术，叠在仍在底下播的 idle 片段上。

[嵌入内容（原站视频）](https://margelo.com/videos/avatarassist-talking.mp4)
![嵌入内容（原站视频）](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Building-a-3D-AI-assistant-using-React-Native-and-GPT-Realtime/avatarassist-talking.gif)

下颌、耳朵与眉毛随音频而动。

## [让模型办事](#making-the-model-do-things)

说话只是一半。另一半是：用户说「周六十一点给我约上」，日历里就该真出现一条。那就是我们在 `session.update` 里声明的工具调用：

[嵌入内容（原站视频）](https://margelo.com/videos/avatarassist-calendar.mp4)

请 Amy 安排动物园行程，事件落入真实日历。

```tsx
const ADD_CALENDAR_EVENT_TOOL = {
  type: 'function',
  name: 'add_calendar_event',
  description: "Add an event to the user's device calendar.",
  parameters: {
    type: 'object',
    properties: {
      title: {type: 'string', description: 'Short event title'},
      start_time: {
        type: 'string',
        description: 'Start datetime in ISO 8601, local time with the UTC offset',
      },
      end_time: {type: 'string', description: 'Optional end datetime in ISO 8601'},
      notes: {type: 'string', description: 'Optional notes'},
    },
    required: ['title', 'start_time'],
  },
};
```

模型当然不能自己调。它请求，我们干活，再把答案递回去。一轮若产出函数调用，我们执行并把结果帖进对话，再要一次响应，好让 Amy 说说刚发生了什么：

```tsx
const output = await turn.onToolCall(pending.name, pending.args);

socket.send(JSON.stringify({
  type: 'conversation.item.create',
  item: {type: 'function_call_output', call_id: pending.callId, output},
}));
socket.send(JSON.stringify({type: 'response.create'}));
```

第二条消息很要紧。没有它，模型有了答案却没有开口理由，就会在彻底沉默中写你的日历。

我们这边用 [react-native-nitro-event-kit](https://github.com/VladyslavMartynov10/react-native-nitro-event-kit) 对接 iOS EventKit：

```tsx
const startMs = Date.parse(args.start_time);
const event = await addCalendarEvent({
  title: args.title,
  startMs,
  endMs: Number.isNaN(endMs) ? undefined : endMs,
  notes: args.notes,
});
```

### [教模型「明天」是什么意思](#teaching-the-model-what-tomorrow-means)

容易漏掉的一点：模型不知道现在几点。让它「明天九点」约事，它会自信地吐一个日期，而且错——它在猜训练数据里的「现在」是什么时候。

所以每次开会话，我们在 instructions 里告诉它：

```tsx
`Local time now: ${now.toString()} (UTC offset ${tzOffset(now)}). `
```

然后还要规定返回格式，因为另一处翻车也在这：

```tsx
'call add_calendar_event with a title and ISO 8601 start_time (and end_time if given) ' +
`in LOCAL time with that offset, e.g. ${exampleLocalIso(now)}, never UTC, never a trailing "Z". `
```

末尾的 `Z` 值得强调。模型特爱给你 `2026-08-18T09:00:00Z`，这是合法时间戳，表示 UTC 上午九点——拉各斯访客是十点，洛杉矶是前一天凌晨两点。事件进了日历，时间错了，哪儿也不报错。给它一份按用户真实时钟生成的精确形状示例，才能稳住。

这些都假定 Amy 已在屏上就绪；启动头几百毫秒并不是这样，那段空隙是另一个问题。

## [启动要快，还不露缝](#starting-up-fast-without-showing-the-seams)

加载 3D 场景要时间。Galaxy S22 上我们大约启动后 400ms 可交互，其中大半不是 JavaScript：bundle 大约 65ms，其余是 Filament 解析模型、上传 GPU、画第一帧。

400ms 一般还行。不行的是这期间*用户看见什么*——应用完全有本事给你一片没有松鼠的空森林，那看起来像坏了，而不是在加载。

第一件值得做的是把模型本身变小。我们到手二十段动画、只用两段，另外十八段每次冷启动白解析。[gltf-transform](https://gltf-transform.dev/) 能丢掉不需要的，帮我们砍了 500KB。但剪什么要小心：我们的片段按*索引*引用，删一些会重编号，应用会开开心心播错动画，而不是报错。

### [在正确的那一帧藏起启动屏](#hiding-the-splash-on-the-right-frame)

更大的问题是何时收掉启动屏。常见答案是 effect 或 `onLayout`，两者错法一样：布局发生在*绘制之前*，于是你撤掉启动屏，交给一张还没画出来的屏。

两者还跑在 JS 线程，撤屏会排在启动时 JS 正忙的别的活后面——最不该排队的时刻。

所以我们用打过补丁的 [react-native-bootsplash](https://github.com/zoontek/react-native-bootsplash)：在视图真正被*绘制*时由原生撤掉。补丁加了一个不可见 Fabric 视图，唯一工作是注意到自己的 `onDraw`，从原生侧藏启动屏，不绕 JS：

```tsx
<BootSplash.HideOnDraw fade />
```

> 有兴趣的话，这是把补丁内容做成的 [react-native-bootsplash PR](https://github.com/zoontek/react-native-bootsplash/pull/792)。

最后一块是个妙招：因为它是 React 组件，*我们何时挂载它*就决定了启动屏何时能走。只在模型加载完成后才渲染：

```tsx
{model.state === 'loaded' && <BootSplash.HideOnDraw fade />}
```

于是整个加载期间启动屏都在，消失的那一帧就是有松鼠的那一帧。中间什么都看不见。

## [为何模型不在端侧跑](#why-the-model-isnt-running-on-device)

对上面一切有个显而易见的反对：会说话的松鼠凭什么还要联网？手机现在也能跑模型。把脑子留在设备上会更私密、免费跑，动物园没信号也能用。

我们先做了那个版本，然后量了它——这种事该查，不该吵。

基准跑在真实应用里，驱动与生产相同的管线，全程渲染 3D。十五个有标准答案的提示，六类：有事实可查的动物题、没有的动物题、带明确时间的日程、相对时间的日程（「明天九点」）、闲聊，以及一类**干扰项**——听起来像约事其实不是。*「提醒我为什么松鼠要埋坚果」* 该出趣闻，不该写日历。

五个端侧模型过了一遍，从 224MB 到 4.7GB。四个在真机 iPhone 16 上测；第五个太大装不进手机，单独在模拟器评、不进设备对比。头条是首音延迟：

**基准图：**

- qwen3-1.7b（端侧最佳）：6130 ms（基线）
- gpt-realtime（云端）：574 ms（相对基线约 11×）

慢十倍，还是*最好*的本地结果。其余画面也好不到哪去：

| | 端侧最佳 | 云端 |
| --- | --- | --- |
| 首音延迟 | 6,130 ms | **574 ms** |
| 一轮中的 CPU | 238% | **37%** |
| 日历时间正确 | 0 / 5 | **4 / 5** |
| 幽灵日历事件 | 2 | **0** |
| 应用体积增加 | +1.0 GB | **+0** |
| 可离线 | **是** | 否 |

这时本能是换模型，我们也换了。两个方向都不行。更小的很快，但从未产出合法工具调用，Amy 会开开心心聊动物园行程却从不落笔。再大又太慢，测试里还*更差*：从 qwen3-1.7b 换到 2B，工具召回从 5/5 掉到 1/5，峰值内存顶到 2.2GB。请它周一 9:30 把动物园行程写入日历，它回：*「哦，你是松鼠？太有趣了！」*

对这款应用，238% CPU 最要命。这是活着的 3D 场景，嘴还得继续动。模型在给出答案前把两核灌满六秒，体验相当难受。

但最深的问题根本不是模型，而是管线形状。端侧路径是：LLM 写句子 → TTS 合成那句 → 播放。这条路能开口的最小单位是*完整句子*，所以第一个声音要串行等两件事。`gpt-realtime` 直接出音频，最小单位是一小撮音频 token。更快的本地模型只能缩短第一段等待；去不掉后面的合成。

方法学提醒，若你自己复现：**别在模拟器上做基准。** 我们两边都跑过的那个模型，模拟器报 3,858ms，手机 6,130ms——真机比模拟器暗示的慢 59%。

## [额外部分](#extras)

写到这里你大概已经注意到演示 UI 里有些是*平台原生*的：液态玻璃输入区、按钮之类。这一节专门照亮它们，外加几处别处塞不下的小点缀。

### [玻璃按钮](#glass-buttons)

顶角两个按钮是 Callstack 的 [`LiquidGlassView`](https://github.com/callstack/liquid-glass)，包的是 UIKit 真玻璃材质，不是模糊冒充。坑在于液态玻璃只存在于 iOS 26 及以上，更旧系统和 Android 上这视图没东西可画。

库会告诉你设备支不支持，回退就是普通深色圆：

```tsx
{isLiquidGlassSupported ? (
  <LiquidGlassView style={styles.button} interactive effect="regular" colorScheme="dark">
    {icon}
  </LiquidGlassView>
) : (
  <View style={[styles.button, styles.fallback]}>{icon}</View>
)}
```

图标是同一问题的另一种口味。我们用仅属 Apple 的 SF Symbols，每个符号都要 Android 对应物。[react-native-nitro-symbols](https://github.com/DaveyEke/react-native-nitro-symbols) 有正好干这事的 `fallback`，我们传入 [Material Design](https://github.com/oblador/react-native-vector-icons) 图标：

```tsx
<SymbolView
  symbolName="text.bubble"
  fallback={<MaterialDesignIcons name="message-text-outline" size={20} color="#fff" />}
/>
```

### [给键盘让路](#getting-out-of-the-way-of-the-keyboard)

模型站在屏中央，文本输入在底部，键盘一开就会被挡住。它得动，而且要*跟着*键盘动，而不是事后再跳。

[react-native-keyboard-controller](https://kirillzyusko.github.io/react-native-keyboard-controller/) 把键盘位置做成动画值，滑动时逐帧更新：

```tsx
const {height: keyboardHeight, progress: keyboardProgress} =
  useReanimatedKeyboardAnimation();
```

模型随键盘升起略抬升并略缩小，都由同一值驱动，整段是一次连续运动：

```tsx
const avatarStyle = useAnimatedStyle(() => ({
  transform: [
    {translateX: sway.value},
    {translateY: keyboardHeight.value * AVATAR_LIFT_FRACTION},
    {scale: 1 - AVATAR_SHRINK * keyboardProgress.value},
  ],
}));
```

模型只抬键盘高度的一部分，而不是全部——完全对齐会顶出屏顶。轻微缩小让它读成后退让路，而不是被往上搡。

注意里面还有 `translateX: sway.value`：前面的倾斜与键盘抬升合成一次变换，可以同时发生、互不打架。

[嵌入内容（原站视频）](https://margelo.com/videos/avatarassist-keyboard.mp4)
![嵌入内容（原站视频）](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Building-a-3D-AI-assistant-using-React-Native-and-GPT-Realtime/avatarassist-keyboard.gif)

键盘打开时 Amy 后退让位。

### [转写稿](#the-transcript)

Amy 说的每句话也会写下来，从角落按钮打开一张 sheet。那是 [TrueSheet](https://github.com/lodev09/react-native-true-sheet)——真正的原生底部 sheet，而不是通用视图壳——里面用 [LegendList](https://www.legendapp.com/open-source/list/) 列消息。

Sheet 懒加载，有人点按钮才需要：

```tsx
const TranscriptSheet = React.lazy(() =>
  import('./TranscriptSheet').then(m => ({default: m.TranscriptSheet})),
);
```

[嵌入内容（原站视频）](https://margelo.com/videos/avatarassist-transcript.mp4)

打开转写并回翻对话。

## [收尾](#wrapping-up)

我们想做一只 Talking Tom 风格的 3D AI 助手，结果有意思的部分根本不是 AI。接上 `gpt-realtime` 就是 WebSocket 加一份 JSON。费脑子的是周围一切：音频流进来时把 3D 场景稳住在 60fps，只靠响度让嘴动得像样，以及确保一个不知道今天星期几的模型仍能把正确的事写进日历。

我最兴奋的是性能——这类 3D 体验要好玩，性能是关键因素。应用在 iOS（iPhone 16）和 Android（Galaxy S22）上都黄油般跑在 60fps，没有可见卡顿。

另外，AvatarAssist 源码已[开源](https://github.com/margelo/ai-character-demo)，拆开它，做你自己的会说话的动物吧。🐿️

非常感谢所有为演示用到的出色开源库的维护者。下列是这些库及其维护者：

- [react-native-filament](https://github.com/margelo/react-native-filament) - [Hanno Gödecke](https://github.com/hannojg) 与 [Marc Rousavy](https://github.com/mrousavy) / [Margelo](https://margelo.com/)
- [Filament](https://github.com/google/filament) - [Google](https://github.com/google)
- [react-native-worklets-core](https://github.com/margelo/react-native-worklets-core) - [Marc Rousavy](https://github.com/mrousavy) / [Margelo](https://margelo.com/)
- [react-native-video](https://github.com/TheWidlarzGroup/react-native-video) - [The Widlarz Group](https://github.com/TheWidlarzGroup)
- [react-native-audio-api](https://github.com/software-mansion/react-native-audio-api) - [Software Mansion](https://github.com/software-mansion)
- [react-native-reanimated](https://github.com/software-mansion/react-native-reanimated) - [Software Mansion](https://github.com/software-mansion)
- [react-native-keyboard-controller](https://github.com/kirillzyusko/react-native-keyboard-controller) - [Kiryl Ziusko](https://github.com/kirillzyusko) / [Margelo](https://margelo.com/)
- [react-native-true-sheet](https://github.com/lodev09/react-native-true-sheet) - [Jovanni Lo](https://github.com/lodev09)
- [Legend List](https://github.com/LegendApp/legend-list) - [Jay Meistrich](https://github.com/jmeistrich) / [Margelo](https://margelo.com/)
- [`@callstack/liquid-glass`](https://github.com/callstack/liquid-glass) - [Oskar Kwaśniewski](https://github.com/okwasniewski) 与 [Callstack](https://github.com/callstack)
- [react-native-bootsplash](https://github.com/zoontek/react-native-bootsplash) - [Mathieu Acthernoene](https://github.com/zoontek)
- [Nitro](https://github.com/margelo/nitro) - [Marc Rousavy](https://github.com/mrousavy) / [Margelo](https://margelo.com/)
- [react-native-nitro-websockets](https://github.com/margelo/react-native-nitro-fetch) - [Szymon Kapała](https://github.com/Szymon20000) / [Margelo](https://margelo.com/)
- [react-native-nitro-image](https://github.com/mrousavy/react-native-nitro-image) - [Marc Rousavy](https://github.com/mrousavy) / [Margelo](https://margelo.com/)
- [react-native-nitro-event-kit](https://github.com/VladyslavMartynov10/react-native-nitro-event-kit) - [Vladyslav Martynov](https://github.com/VladyslavMartynov10)
- [react-native-nitro-symbols](https://github.com/DaveyEke/react-native-nitro-symbols) - [Dave Mkpa-Eke](https://github.com/DaveyEke) / [Margelo](https://margelo.com/)
- ["Cute Character with Animations"](https://sketchfab.com/3d-models/cute-character-with-animations-477a8bdf8488431799fbfb5e6fcc94af) - Ivana Boskovic，[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/)
