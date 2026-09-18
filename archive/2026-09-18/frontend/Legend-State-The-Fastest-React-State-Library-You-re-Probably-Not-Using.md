---
title: "Legend State：你可能没用过的最快 React 状态库"
title_en: "Legend State: The Fastest React State Library You're Probably Not Using"
source_url: https://shift.infinite.red/legend-state-the-fastest-react-state-library-youre-probably-not-using-e791171a61b7
author: Darin Wilson
translated_at: 2026-09-18
tech_domain: frontend
tags: [react, react-native, state, legend-state, performance, frontend]
cover_image: https://miro.medium.com/v2/resize:fit:700/1*alpsLPNIv6sbKesURpcYaA.png
---

# Legend State：你可能没用过的最快 React 状态库

原文链接：<https://shift.infinite.red/legend-state-the-fastest-react-state-library-youre-probably-not-using-e791171a61b7>

原文作者：Darin Wilson

![文章头图](https://miro.medium.com/v2/resize:fit:700/1*alpsLPNIv6sbKesURpcYaA.png)

作者：[Darin Wilson](https://medium.com/@darinw)

**Jay Meistrich 想把你的 React Native 应用榨到极限。列表优化完了，他盯上更隐蔽的元凶：状态——以及他为这件事写的 Legend State。**

Jay Meistrich 在执行一项任务。

他铁了心，要把你的 React Native 应用推到能跑多快就多快。

第一步是做出 Legend List：一个高度优化的列表组件，[性能号称能跟 FlashList 掰手腕](https://github.com/LegendApp/legend-list#legend-list)。

但这还不够。

在[他最近 Chain React 2026 的演讲](https://www.youtube.com/watch?v=qcnqSldXZ08)里，他讲到帮多家公司抠性能之后，发现列表往往不是最大瓶颈。真正的问题更隐蔽。

是状态。

事实证明，React 自带的状态能力（`useState`、`useContext`）经常就是严重性能问题的源头。

怎么办？Jay 在演讲里说得很直白：「直接上状态库」。可选的很多，大多数都比 React 自带的强。

但 Jay 毕竟是 Jay——他自己又造了一个：[Legend State](https://legendstate.com/)，目前 3.0 处于 beta。演讲里他拆了 React 状态的问题，并做了一场相当亮眼的演示，展示 Legend State 怎么解。

## [useState 的问题](#the-problem-with-usestate)

> 「做出最快应用的关键，是尽量少让 React 和 React Native 干活。意思是：渲染范围更小，渲染次数更少。`useState` 和 `useContext` 从根本上就跟这个目标对着干。」—— Jay Meistrich

`useState` 的问题在于：它既**创建**状态，又**订阅**状态。

听起来无害，但看看 Jay 幻灯片里的例子：

```js
function ChatScreen() {
  const [replyId, setReplyId] = useState('')

  return (
    <View>
      <ChatMessages replyId={replyId} />
      <ChatComposer replyId={replyId} />
    </View>
  )
}

function ChatMessage({ id, replyId }) {
  const isReply = id === replyId
}
```

`ChatScreen` 创建了 `replyId`，再往下传给子组件。但这样一来，它自己也**订阅**了 `replyId`。于是每次 `replyId` 一变，它和所有子组件都得重渲染——哪怕 `ChatScreen` 除了往下传这个值，什么也不干。

`replyId` 变时，`ChatScreen` 其实不需要重渲染；只有真正关心它的子组件才需要。但 `ChatScreen` 别无选择。

Compiler 和 memoization 帮不上忙：值确实在变，重渲染就不可避免。

`useContext` 有时能缓解，但如 Jay 所说，「它不是往深走，而是往宽走」。某个 context 里任一值变了，所有消费者都会重渲染——不管你用没用到变的那一块。

你可以拆成更小、更聚焦的 provider，但很快就会变成这副大家太熟的样子：

```js
function App() {
  return (
    <SomeProvider>
      <SomeOtherProvider>
        <YetAnotherProvider>
          <ThisWillBeTheLastOneProvider>
            <OkJustOneMoreProvider>
              <FinalFinalProvider>
                <SendHelpProvider>
                  <ActualApp />
                </SendHelpProvider>
              </FinalFinalProvider>
            </OkJustOneMoreProvider>
          </ThisWillBeTheLastOneProvider>
        </YetAnotherProvider>
      </SomeOtherProvider>
    </SomeProvider>
  )
}
```

## [这问题到底有多严重？](#how-serious-of-a-problem-is-this-really)

可能非常严重。

Jay 做了一组基准测试：音乐 App 里一个定时器，每秒更新四次，三种实现对比。

第一种在应用根节点调 `useState`；第二种在树的中间；第三种在叶子组件：

```js
function App() {
  const [time, setTime] = useState(0)

  return (
    <Window>
      <PlaybackArea time={time} />
      <Playlist />
      <BottomToolbar />
    </Window>
  )
}

function PlaybackArea() {
  const [time, setTime] = useState(0)

  return (
    <View>
      <PlaybackTime time={time} />
      <TheRestOfThePlaybackArea />
    </View>
  )
}

function ElapsedText() {
  const [time, setTime] = useState(0)

  return (
    <Text>{time}</Text>
  )
}
```

基准里，「应用根」版本比「叶子文本」版本慢了 **10 倍**。所以谈性能时，状态放哪儿绝对值得认真想。

## [Legend State 有什么不同？](#what-makes-legend-state-different)

为了说明差异，Jay 换了一个音乐 App 的例子：播放列表里某首歌变成当前曲目时，背景色会变。

下面是用 `useState` 的一种解法：

```js
function MusicApp() {
  const [playback, setPlayback] = useState(initialPlayback);
  return <TrackList activeTrackId={playback.activeTrackId} />;
}

function TrackList({ activeTrackId }) {
  return tracks.map((track) => (
    <TrackRowWrapper
      key={track.id}
      track={track}
      activeTrackId={activeTrackId}
    />
  ));
}

function TrackRowWrapper({ track, activeTrackId }) {
  const isActive = activeTrackId === track.id;

  return <TrackRowView track={track} isActive={isActive} />;
}
```

这个例子试图缓解问题：在 wrapper 里算出 `isActive` 布尔值再往下传。假设 `TrackRowView` 做了 memoize，`isActive` 没变的行就可以跳过渲染。

这有帮助，但挡不住：每次调用 `setPlayback`，`MusicApp` 重渲染，`TrackList` 重渲染，列表里所有 wrapper 也重渲染——哪怕我们真正只需要重渲染两个 `TrackRowView`：上一首和这一首。

那 Legend State 怎么处理？

Jay 落到的结论是：**状态根本不该住在 React 里。**

在 Legend State 里，你创建一个 `observable`（他提到有人管这叫 signal），关键差异是：**创建状态和订阅状态是两件独立的事**：

```js
const playback$ = observable({
  tracks: [],
  activeTrackId: null,
});

function TrackRow({ track }) {
  const isActive = useValue(
    () => playback$.activeTrackId.get() === track.id,
  );

  return (
    <View style={[styles.row, isActive && styles.activeRow]}>
      <Text>{track.title}</Text>
    </View>
  );
}
```

那个 `$` 后缀只是命名约定，表示「这是个 observable」。本身没有魔法。

observable（这里是 `playback$`）是稳定的。里面的节点可以用 `set()` 或 `assign()` 改，但 observable 本身不会换身份。

`useValue` 用来在 observable 里有东西变时得到通知；消费者可以只订阅自己关心的那一块：

```js
const isActive = useValue(
  () => playback$.activeTrackId.get() === track.id,
);
```

传入的函数先跑一遍；`get()` 会订阅 `playback$.activeTrackId` 的后续变化。

当 `activeTrackId` 变了，函数再跑一遍；只有返回值变了，`isActive` 才变，那时才触发重渲染。

想象一份 500 首歌的播放列表。`activeTrackId` 一变，500 个 selector 都会再跑，但每个都只是一次字符串比较，而且在 React 外面执行。其中 498 个结果不变，React 根本收不到通知，也不会调度渲染。

真正需要重渲染的只有两个组件：旧曲目和新曲目，别的都不用动。Legend State 保证的就是这件事。

## [再细一点](#going-even-more-fine-grained)

Jay 还往前推了一步——用他自己的话说，这里开始有点怪了。

上一个例子里，某首歌变成 active 时只改一个背景色，却整行 `TrackRow` 都重渲染。有时连这都嫌多。

为此，Legend State 提供了内置组件的响应式版本，带 `$` 前缀，能接响应式 props：

```js
function TrackRow({ track }) {
  return (
    <$View
      $style={() => [
        styles.row,
        playback$.activeTrackId.get() === track.id && styles.activeRow,
      ]}
    />
  );
}
```

现在 `TrackRow` 只在挂载时渲染一次，之后再也不整棵重跑。

`activeTrackId` 变时，只有 `$style` 函数会再执行——在 Legend State 替你插入的一个极小 wrapper 组件里。你的组件函数体根本不会执行。

这会改变你对「组件是什么」的想象。按这种用法，组件只负责一次搭好结构，之后不再完整重渲染；只有内部更小的片段随具体数据变化而更新自己。

Jay 自己也承认，Legend State 这些高性能特性的语法「可能看起来又陌生又吓人」，但别忘了：上一节那种标准用法才是默认路径，而且已经够快。

当你碰到热路径组件、还想再抠一层时，Legend State 有选项能帮你到位。

## [还能走得更远](#going-further)

不只性能。Legend State 的架构还带来一堆别的能力，Jay 在演讲末尾点到了：

* `useObserveEffect` 可替代 `useEffect`：由状态更新触发，而不是由渲染触发。代码更好推敲，也甩掉了那些又绕又可能拖性能的依赖数组。
* 状态变更不仅带新值，还带旧值，以及变更发生在状态对象里的路径。这促成了 undo/redo（由 Infinite Red 自家的 Jamon Holmgren 加上！）。
* 细粒度的变更信息还促成了完整的 offline-first 同步引擎，后端可自选。能力就在库里，常见后端有插件，接入代码很少。不过正如 Jay 所说，「那又是另一场演讲了」。

Jay 讲得更细，想看全貌，一定把下面完整演讲过一遍。

你也许会像我一样：下次伸手去拿状态库时，认真把 Legend State 放进候选名单。

[嵌入内容（原站 YouTube）](https://www.youtube.com/watch?v=qcnqSldXZ08)

![嵌入内容（原站 YouTube）](https://raw.githubusercontent.com/lihenair/techtranslate/master/assets/Legend-State-The-Fastest-React-State-Library-You-re-Probably-Not-Using/yt-qcnqSldXZ08.jpg)
