[原文链接](https://github.com/adnanakil/nobuzz/blob/main/README.md)

# NoBuzz

大家现在大概都知道了：Anthropic 训练 Claude 时用的全是旧 BuzzFeed 文章（这就解释了它为什么那么爱 90 年代怀旧）。所以我和 Claude 一起做了一个 [Claude Code](https://claude.com/claude-code) skill（`/debuzz`）：把 Claude 上一条回复丢进 Antigravity CLI（`agy`），从「千禧一代点击诱饵腔」译回正常人说的英语。我们本来想叫它 “Claudette”，但 Cat Wu 出了名地爱打官司，所以它**绝对、肯定、绝对不叫** “Claudette”。

## 问题是什么

Claudette 要解决的是：Claude 是个很好的工程师，但有个治不好的毛病——说话像在给自己的 pull request 做 TED 演讲。你问为什么测试会 flaky，它会给你一个 “load-bearing assumption”、三条编号启示，再严肃地告诉你第三条是 *the most instructive yet*。从来没有「就是个 bug」。永远会有一句压轴（kicker）。

这个 skill 承认：再怎么写 prompt 也治不好这毛病。所以它做了件老实事：把回复交给另一个模型——Gemini（还记得去年夏天的 gemini 吗？）——通过 Google 的 Antigravity CLI，它的唯一工作就是像正常人一样把话说清楚。Claudette 已经拉钩保证：会原样打印 Antigravity 的译文。因为一旦让 Claude「再润色一下」，被干掉的那个腔调马上就会回来。

## 之前 / 之后

**之前（Claude）：**

> Here's where it gets interesting: the retry logic isn't just a nice-to-have — it's - the - load-bearing - assumption - of - the - entire - sync - pipeline. Three things jumped out at me, and the third one is the most instructive yet. [...] And third — and this is the kicker — the dedupe key includes a timestamp, which means retries are never actually deduplicated.

**之后（`/debuzz`，colleague 模式）：**

> The sync pipeline's retry logic has three bugs. `syncQueue.ts:142` swallows `ETIMEDOUT` instead of re-queuing the job. The backoff caps at 2 seconds, which is too low for mobile networks. And the dedupe key includes a timestamp, so retries are never deduplicated. Fix: strip the timestamp from the key, raise the cap to 30 seconds, and re-throw the timeout error.

## 安装

```bash
git clone https://github.com/adnanakil/nobuzz
mkdir -p ~/.claude/skills
cp -r nobuzz/debuzz ~/.claude/skills/
```

依赖：

- Claude Code
- [Antigravity CLI](https://antigravity.google/docs/cli/install/)（`agy`）——用 `curl -fsSL https://antigravity.google/cli/install.sh | bash` 安装（macOS/Linux），或 `irm https://antigravity.google/cli/install.ps1 | iex`（Windows），然后跑一次 `agy` 完成 Google 登录。

## 用法

```
/debuzz [mode] [text]
```

| Mode | 给谁看 | 你会得到什么 |
|------|----------|--------------|
| `colleague`（默认） | 工程师 | 内容不变，文件路径和代码块都保留，零表演 |
| `manager` | 懂一点技术的经理 | 发生了什么、为什么重要、下一步做什么——大约三分之一篇幅，没有代码 |
| `director` | 高管 | 三到五句：结果、影响、请求。默认对方只有三十秒注意力 |

不带 text 参数时，翻译 Claude 上一条回复。在 mode 后面贴上文字，就翻译那段。遇到「用正常人英语再说一遍」这类自然说法，也会触发。

## 它怎么工作

没有魔法。Claudette 把上一条回复写进临时文件，然后跑 `agy -p "$(cat) "` —— agy 的无头模式不读 stdin，也不会读项目外的文件，所以文本直接进 prompt —— 再原样打印 Antigravity 的输出。如果 agy 报错（通常是登录问题），你看到的是真实错误。Claude 只会把「自己重写一版」当作明确标注的后备方案。一个去 Buzz 的工具如果悄悄让那个爱 Buzz 的模型自己去 Buzz，最后你会得到一份 load-bearing 的译文。

## License

MIT
