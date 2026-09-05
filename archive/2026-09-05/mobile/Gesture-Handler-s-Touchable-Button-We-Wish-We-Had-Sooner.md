---
title: "React Native Gesture Handler 的 Touchable：我们早该有的按钮"
title_en: "React Native Gesture Handler's Touchable: The Button We Wish We Had Sooner"
source_url: https://swmansion.com/blog/react-native-gesture-handler-s-touchable-the-button-we-wish-we-had-sooner/
author: Jakub Piasecki
published_at: 2026-08-20
translated_at: 2026-09-05
tech_domain: mobile
tags: [mobile, react-native, gesture-handler, touchable, ui]
cover_image: https://strapi-production-5f3f.up.railway.app/uploads/ver_3_83144fea89.png
---

# React Native Gesture Handler 的 Touchable：我们早该有的按钮

原文链接：<https://swmansion.com/blog/react-native-gesture-handler-s-touchable-the-button-we-wish-we-had-sooner/>

原文作者：[Jakub Piasecki](https://github.com/j-piasecki)

![文章头图](https://strapi-production-5f3f.up.railway.app/uploads/ver_3_83144fea89.png)

作者：[Jakub Piasecki](https://github.com/j-piasecki)

发布于 2026 年 8 月 20 日。

**Gesture Handler 3 的 Touchable：可定制、够快的按钮，用来取代一堆按钮组件。**

我喜欢按钮。我觉得大多数人也喜欢，尤其是按下时有扎实反馈的那种。那是不是就要很多种、反馈还各不相同？其实不必——那样最后会变成好几个组件干同一件事，只是细节略有差别。我们在 React Native Gesture Handler 多年开发里，把这坑踩明白了。

## [怎么走到这一步的？](#how-did-we-get-here)

装一个处理触摸的库，你会指望它自带开箱即用的按钮。我们确实有过好几个，视觉反馈还不一样。随着 React Native 演进，又需要能直接替换它的 Touchable 系列；后来 RN 有了 Pressable，我们也得给它做 drop-in。一眨眼，我们导出了 **9** 个独立按钮组件。

给一家大型金融应用咨询按钮用法时，我们才正视这件事。围绕期望与前提聊了很多之后，我们认定：没有放之四海而皆准的预设。但我们可以交出能覆盖绝大多数场景的工具，于是决定一次把问题做完。

## [别再造一遍 Pressable，我们已经替你做过了](#dont-reinvent-the-pressable-we-already-did-it-for-you)

「按钮太多了」的解法，显然是做一个统领全局的按钮。我们在 React Native Gesture Handler 3 里用 **Touchable** 做到了——新的按钮组件。现在多了一个按钮，局面反而清楚了（其余的我们标了弃用）。唯一例外是我们的 Pressable：它成了 Touchable 外的一层薄包装，好在需要手势感知按钮时，仍能当 RN Pressable 的 drop-in。

## [好在哪里？](#how-is-it-better)

首先可定制：能为 default、pressed、hovered 各状态分别设缩放、透明度和 underlay。对了，移动端也支持 hover（鼠标和手写笔都行）。此外，各状态还能单独设过渡时长。这些都落在平台层（Android 的 ObjectAnimator、iOS 的 CoreAnimation、Web 的 CSS transitions），也会尊重系统无障碍设置，比如动画倍率与减少动态效果。

**透明度：**

[嵌入内容（原站视频）](https://strapi-production-5f3f.up.railway.app/uploads/opacity_f6c97c4613.mp4)

![嵌入内容（原站视频）](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Gesture-Handler-s-Touchable-Button-We-Wish-We-Had-Sooner/opacity.gif)

```tsx
<Touchable
  style={styles.button}
  activeOpacity={0.7}
  onPress={onPress}>
  <Text style={styles.text}>activeOpacity: 0.7</Text>
</Touchable>
```

**缩放：**

[嵌入内容（原站视频）](https://strapi-production-5f3f.up.railway.app/uploads/scale_c77394df9a.mp4)

![嵌入内容（原站视频）](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Gesture-Handler-s-Touchable-Button-We-Wish-We-Had-Sooner/scale.gif)

```tsx
<Touchable
  style={styles.button}
  activeScale={1.05}
  onPress={onPress}>
  <Text style={styles.text}>activeScale: 1.05</Text>
</Touchable>
```

**Underlay：**

[嵌入内容（原站视频）](https://strapi-production-5f3f.up.railway.app/uploads/underlay_c3378e8980.mp4)

![嵌入内容（原站视频）](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Gesture-Handler-s-Touchable-Button-We-Wish-We-Had-Sooner/underlay.gif)

```tsx
<Touchable
  style={styles.button}
  underlayColor="black"
  onPress={onPress}>
  <Text style={styles.text}>underlayColor: black</Text>
</Touchable>
```

JS 组件本质上是 codegen 规格上的薄包装。若你依赖内置动画，Touchable 自己不会触发重渲染。

若要更多配置，可以用你喜欢的动画库自己驱动过渡，就像对待 React Native 的 Pressable 一样。

## [听说你喜欢数字](#i-heard-you-like-numbers)

我们准备好了——同时渲染 1000 个 Button，跑 50 次，越低越好。

### [绝对值（毫秒）](#absolute-values-in-milliseconds)

| 组件 | Oppo A16 均值 | Oppo A16 中位 | Pixel 9 Pro 均值 | Pixel 9 Pro 中位 |
| --- | --- | --- | --- | --- |
| Touchable | 7838.4 | 7737.0 | 574.0 | 573.0 |
| Pressable | 8180.3 | 8197.0 | 651.0 | 652.0 |
| RectButton | 8281.0 | 7995.0 | 1067.9 | 1057.0 |

### [相对值（相对 Pressable）](#relative-values-compared-to-pressable)

| 组件 | Oppo A16 均值 | Oppo A16 中位 | Pixel 9 Pro 均值 | Pixel 9 Pro 中位 |
| --- | --- | --- | --- | --- |
| Touchable | 0.96 | 0.94 | 0.88 | 0.88 |
| Pressable | 1.00 | 1.00 | 1.00 | 1.00 |
| RectButton | 1.01 | 0.98 | 1.64 | 1.62 |

新 Touchable 渲染比旧的 RectButton 更快，也赢过 React Native 内置 Pressable。差距在更强的设备上更明显——那里还没被 JavaScript 工作负载压垮。

## [为何用 Touchable？](#why-touchable)

Pressable 这名字已经被占了 ¯\\_(ツ)_/¯……哦，你问的是「什么时候该用它」，不是「为什么叫这名」，懂了。目前 Gesture Handler 里处理轻触有三种方式：`useTapGesture`、`Touchable` 和 `Pressable`。绝大多数情况下 Touchable 就该是默认选择，选哪个也简单多了：

- **需要定制行为时用 `useTapGesture`**，比如点击次数、最长按下时长，或手势之间更复杂的关系。
- **已有组件在用 React Native 的 Pressable、又想用 drop-in 迁到 Gesture Handler 时，用 Pressable**——披着外套的 Touchable。
- **其余情况，直接用 Touchable。**

## [迁移怎么办？](#what-about-migrating)

我们打算在 Gesture Handler 下一个大版本里删掉已弃用的按钮，因此强烈建议改用 Touchable。可以手动迁，也可以把活交给你选的 agent，用我们的[迁移 skill](https://github.com/software-mansion-labs/skills/blob/main/skills/react-native-best-practices/references/gestures/v2-to-v3-migration.md)。
