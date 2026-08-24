---
title: "可验证领域将吞噬世界"
title_en: "Verifiable Domains Will Eat The World"
source_url: https://x.com/jon_stokes/status/2091383885569405025
author: Jon Stokes
published_at: 2026-08-23
translated_at: 2026-08-24
tech_domain: ai
tags: [ai, watermarking, anthropic, writing, llms]
cover_image: https://pbs.twimg.com/media/HQYSYeZWAAA8yr0.jpg:large
---

# 可验证领域将吞噬世界

原文链接：<https://x.com/jon_stokes/status/2091383885569405025>

原文作者：Jon Stokes

![文章头图](https://pbs.twimg.com/media/HQYSYeZWAAA8yr0.jpg:large)

作者：[Jon Stokes](https://x.com/jon_stokes)（[@jon_stokes](https://x.com/jon_stokes)）

发布于 2026 年 8 月 23 日。

**在「信息」与「真理」之间的缝隙里，藏着一整族古老又现代的学问；Anthropic 的水印之争，正落在这条缝上。**

很久以前，在社交媒体和 iPhone 之前——甚至在双子塔倒下、现代安全国家在废墟上立起来之前——我们这帮网上人会互相逗乐子，嘲讽 PowerPoint。PowerPoint 是办公软件界的 Nickelback，表演式地恨它，是一种办公室幽默文化的一部分；那种文化如今似乎已随办公室与幽默一并远去。

那个年代最出名的 PowerPoint 恶搞，大概是 Peter Norvig 用幻灯片重述林肯葛底斯堡演说。

林肯那两百七十二个词，每个词与其他词咬合得如此精确，尽管语域抬得很高，却仍有一种自然与完整，让人觉得它只能以这种形态诞生。

Norvig 的 PowerPoint（扭曲）版之所以意外又好笑，是因为我们隐约却深刻地感到：那篇演说构造里那些有说服力的细节，携带着一种干巴巴复述同一堆事实所无法承载的「真」。

有信息，也有真理。两者显然相关，却又不完全等同。而在「信息」与「真理」之间的缝隙里，住着一整族古老与现代的学科，名字叫「修辞」「美学」「诠释学」之类。

## [承重的复杂](#load-bearing-complications)

我其实讨厌再纠缠「形式 vs 实质」，因为我想你们已经懂了；但在转到 Anthropic 水印争议、以及围绕该争议的 AI 宅元争议之前，我想再抽一根线。

几周前，在 Arday 事件和 Hugging Face 被黑之前——甚至在 Nolan 的《奥德赛》上映之前——我们刚熬完一整轮 Discourse Cycle：Emily Wilson 荷马译本的政治。

请把注意力拉回那段被反复讨论的、Wilson《奥德赛》开篇：

> Tell me about a complicated man.  
> Muse, tell me how he wandered and was lost  
> when he had wrecked the holy town of Troy,  
> and where he went, and who he met, the pain  
> he suffered in the storms at sea, and how  
> he worked to save his life and bring his men  
> back home.

批评者盯住的词之一是 πολύτροπος（polytropos），她译成 “complicated”。它由部件提示出一串含义——“poly” 是「多」，“tropos” 是「路」或「转折」。Lattimore 经典译本译成 “many ways”，传达奥德修斯四处游荡的感觉，但至少对我来说有点木。

多年前我在哈佛神学院念书时，听过已故的 Ellen Aitken 一场求职演讲。Ellen 讨论《希伯来书》开篇对 polytropos 的用法，机智地论证：匿名作者有意在古代读者心里，把奥德修斯与耶稣拴在一起。

看看书信开篇几节，看你能不能发现：

> Long ago God spoke to our ancestors in many and various ways by the prophets,  
> but in these last days he has spoken to us by a Son, whom he appointed heir of all things, through whom he also created the worlds.  
> He is the reflection of God’s glory and the exact imprint of God’s very being, and he sustains all things by his powerful word. When he had made purification for sins, he sat down at the right hand of the Majesty on high.

NRSV 译成 “various ways” 的，正是 Wilson 译成 “complicated” 的那个希腊词。经文接着写到君王耶稣的尘世旅居、受苦、拯救他的民、最终归回本有宝座。

在 Ellen 把两段并读的理解里，《希伯来书》作者有意在漂泊受苦的君王奥德修斯与漂泊受苦的君王耶稣之间，立起互文关系。还有一点隐含对照：《奥德赛》开篇在我们引文切断之后立刻点明，奥德修斯试图救同伴却失败了；而耶稣成功救了我们所有人。

可以想象《希伯来书》作者小心拧着用词旋钮——像 Rick Rubin 在混音台上拧「选词」（polytropos）与「词序」（离开王室之家、受苦、拯救、归家）——直到奥德修斯的形象与耶稣的形象在听众心里对焦，再彼此重叠。

当然，作者本可以用别的词开篇，但那就做不到把奥德修斯与耶稣并置的修辞工作。选词是交际行为里有意的一部分；用一个讨人厌的 Claude 腔词说，它是「承重的（load-bearing）」。

## [AI 水印之争](#the-ai-watermarking-controversy)

上面绕这么大，是为了点出一个多数人凭直觉就懂的事实：选词对文本冲击读者的完整效果事关重大。所以当一位技术界兄弟用数学给我们 mansplain，说 Anthropic 加水印的文本相对无水印文本「没有质量损失」时，我们可能会想回一句：「不，两段措辞不同的文本并不相同，你这绝对的超级宅小丑。回你的火车话题去吧，把品味的事留给有品味的人。」

看看下面这段、一篇还算不错的水印问题解说：

> Now the prompt is: today’s weather is “cold,” and a possible answer could be, for example, “gray” or “overcast”. So in contrast to the “Berlin” example, I would say “gray” and “overcast” kind of are interchangeable.  
>  
> They are both reasonable next tokens for this prompt, given the goal of completing this text or writing the next token. So it’s almost like a coin flip which one we want to select. There is not really an objectively worse one of one or the other.

会写出「There is not really an objectively worse one of one or the other」这种别扭句子、来谈两个形容词之差的人，大概正是那种对写作手艺至多只有极不发达意识的人。

对我们其余人来说，选词问题与品味、身份、作者性紧密相连，而这些又连着所有权、地位与利润。

这种直觉层面的反应，在下面这则对水印决定的回应里抓得很准。

至于对 Anthropic 水印里不那么「靠 vibe」的作者性 / 所有权异议，Ben Thompson 概括得很利落：

> I am deeply philosophically opposed to watermarking in the context of the entire meta question about the relationship between humans and AI. Implicit in the E.U.’s regulation is the idea that an AI is an independent entity that needs to be distinguished from humans; the alternative view — that I hold — is that AI is (at least for now) a tool that is wielded by humans. From this perspective, to insist on watermarking is no different than insisting that a ballpoint pen advertise itself as the author, a concept that is clearly absurd.

反水印阵营的抱怨，或许可以意译成：

我用 LLM 与其他人类沟通；我或许还没熟练到总能知道该用 “gray” 还是 “overcast”，但我知道有差别，读者也会感到差别；所以我信任这工具为我的文本挑最好的词。可你现在告诉我：你不总会挑最好的词，有时会挑第二好的词，而且你这么做是因为你想抢走我对这段文字的作者性与所有权，据为己有。

当然，无论公开怎么坚称，我认为 AI 圈人其实也分享非技术人的常识：相近的词并不是可以自由互换的。有人觉得必须否认或淡化这个直觉上显然的事实——这本身就指向一种取舍；我认为随着 LLM 吞噬正在吞噬世界的软件，我们会越来越常看到它。

在解释这取舍是什么之前，先交代两边的两个概念。

## [可验证与不可验证的领域](#verifiable-and-unverifiable-domains)

所有回推水印反弹的 AI 人，至少部分依据一种有数学背景的理解：AI 并不是在挑「最好的词」——因为说到选词（相对比如下一步棋），「最好」落在**不可验证（unverifiable）**的领域。

没有普遍适用、可客观度量的「下一个最好的词」，能让一次 LLM 训练跑去优化——因为「最好」（至少对我们这里民间诠释学、以作者为中心的目的来说）完全取决于作者打算对听众造成怎样的冲击。

「最好的词」——若这概念甚至可能成立——由作者在某一刻是谁、她在对谁说话、她想用言语行为做什么，来管辖。

把问题挪到另一领域，好建立直觉：想象你在中学打躲避球，球在手里。对面是你暗恋的女孩 Susie。你投球极烂，你自己也知道。

再看两种情形：

你想砸 Susie，却不小心正中 Biff 脸。Biff 会为这冒犯在车站揍你。

你有一副 Iron Man 手套，投球准得要命。手套的 Jarvis 不知道你喜欢 Susie，但知道 Biff 昨天揍过你。于是你想砸 Susie，手套却把球直接送进 Biff 的脸……

最好的躲避球目标是 Susie 还是 Biff？

天真答案或许是「Susie」，因为那是你打算砸的人。可若你砸中了 Susie，她或许会讨厌你、躲着你，你才发现她其实是最差目标。但这或许教你关于女孩的一课，下一场你不再在躲避球场上瞄准暗恋对象，结果最终赢得第二个女孩的好感。或者，手套帮你砸中 Biff，他要揍你——手套当然可以在车站教训 Biff，或许让你成校园英雄……又或许你被送进某种超级反派少年管教所。谁他妈知道？

我的意思是：即便投球技能无限、对意图与意外后果的知识也完全，**「最好的躲避球目标」**也只能相对你在某一刻的私人意图与处境来理论化。

你可能行动前意图一事，事后不久就后悔。又或许你甚至无法真正说清行动时想要什么；你能可验证地知道的，或许只是你现在对结果有多高兴（或不高兴）……而这也会随后果展开而变。

最好的躲避球目标，深深地、根本地不可验证。AI benchmark 制作者再怎么劳动，也很难把它挪进可验证领域。

「最好的词」当然也一样。

……等等，是吗？即便没有「最好的词」，有些选词显然比另一些好，人人都知道，对吧？！

……于是我们咬进一个很老的问题，这里解决不了。但至少有足够背景，可以把反感水印者与尊重水印者之间的核心差别磨得更尖：

讨厌水印的 AI 用户，怕的是 AI 不会为**她特定的语境与意图**挑最好的词——无论那是什么。

爱水印的 AI 忧虑者，怕的是 AI 或许真会为**AI 的语境与（高度可疑的）意图**挑最好的词；所以我们至少要可验证地知道 AI 何时在说话。

再用 AI 领域自己的话，把挺水印立场再说一遍：

「最好的词」问题不可验证，你在乎什么？但出处（provenance）问题在数学上可验证，许多担心 AI 计划与意图的人，极在乎文本是不是 AI 写的——所以至少做那件我们在乎、又可验证的事（水印）。

## [这把我们留在哪](#where-does-this-leave-us)

我认为挺水印与反水印阵营，其实被同一套关于语言的核心信念驱动：

- 选词真的要紧，相近的词并非完全可互换（所有 Anthropic 或 AIsplainer 关于 “gray” vs “overcast” 的挥手，除外）。
- 在给定语境里，有更好与更差的选词。
- 能挑出会造成你意图中精确冲击的词，是强大、也可能危险的能力。
- 因此，选词那一方的意图很要紧。
- 若必须在「可能让未知数量的用户拿到第二好的词」（完全不可验证）与「给社会数学上可证明的出处」（100% 可验证）之间选，我们显然该选后者优化目标。

最后一条里，就是我上面说的取舍：

⚖️ 当一个价值不可验证（手艺、「最好的词」），而竞争的价值可验证（出处）时，技术资本机器总会优化可验证的那个，牺牲不可验证的那个。

只要无法量化有多少（若有）用户拿到第二好的词，也无法度量次优词对这些用户的成本，「最好的词排成最好的顺序」这令人困惑又不便的概念，差不多等于不存在。

（可怜的诗人。人人都知道他们什么意思，又没人知道他们什么意思。难怪他们常常又穷又想自杀。）

不妨把这取舍收成一句警告收尾：凡是人类经验里真实又宝贵、却量不出的东西，我们在引入优化压力的每个地方，都有看不见它们的风险；而 LLM 会把人类经验的全新区域暴露在优化压力之下。

正如至少回溯到书写的每一次技术革命（柏拉图对书面文字心情很复杂），保留什么、允许什么消散，仍取决于我们。
