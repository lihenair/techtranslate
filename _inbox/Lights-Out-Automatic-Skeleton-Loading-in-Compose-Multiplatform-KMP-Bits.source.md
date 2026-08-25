---
source_url: https://medium.com/@kmpbits/lights-out-automatic-skeleton-loading-in-compose-multiplatform-kmp-bits-75a17db09327
fetched_at: 2026-08-25T12:17:12Z
fetch_method: jina
issue: 102
title_zh: Lights Out：Compose Multiplatform 自动骨架屏加载（KMP Bits）
tech_domain: android
---

# Lights Out: Automatic Skeleton Loading in Compose Multiplatform | KMP Bits

## Lights Out: Automatic Skeleton Loading in Compose Multiplatform | KMP Bits

[![Image 1: KMP Bits](https://miro.medium.com/v2/resize:fill:32:32/1*bEJYCym_LbPKYyPUA5hv6g.png)](https://medium.com/@kmpbits?source=post_page---byline--75a17db09327---------------------------------------)

6 min read

Aug 17, 2026

Press enter or click to view image in full size

![Image 2](https://miro.medium.com/v2/resize:fit:1000/0*v38tXVy0Bxj7FMEh.png)

Five red lights climb the gantry, one at a time. Every car on the grid is watching the same five lights, and no driver is running a private countdown of their own. The lights go out, and nineteen other engines respond to the exact same signal within the same fraction of a second.

That’s not automatic because each car happens to react quickly. It’s automatic because there’s only one signal for all of them to react to.

I already had a shimmer effect working. A small composable called `ShimmerBox`, copied from project to project for a couple of years, doing the one job it was built for: a gray box with a moving gradient, dropped in wherever a screen needed to look like it was loading. It worked. Nobody had ever complained about it, and I took that as proof it was fine. I decided to pull it out into a real library, something I could publish and reuse properly instead of pasting the same forty lines into every new app.

The moment I looked at it with fresh eyes, I found the bug it always had.

@Composable

fun shimmerEffect(): Brush {

 val transition = rememberInfiniteTransition

 val translateAnimation = transition.animateFloat(

 initialValue = 0f,

 targetValue = 1000f,

 animationSpec = infiniteRepeatable(

 animation = tween(800),

 repeatMode = RepeatMode.Restart

 )

 )
return Brush.linearGradient(

 colors = shimmerColors,

 start = Offset.Zero,

 end = Offset(x = translateAnimation.value, y = translateAnimation.value)

 )

}

Every `ShimmerBox` on screen calls this function. Every call creates its own `rememberInfiniteTransition`. A feed with twenty cards and four shimmering elements each means eighty independent animation drivers, each one running its own private clock, each one invalidating and redrawing on its own schedule. None of them agree on where the sweep is. Gray boxes shimmer, technically. A whole screen of them never reads as one system, though. It reads as eighty unrelated timers, each one keeping its own idea of what time it is.

## The fork in the road

The obvious fix for “developers keep writing loading UI by hand” is to make it automatic. Wrap the real content in a container, walk the composed layout tree, and paint a placeholder over whatever the container finds. No modifier to add, no shape to declare, the container figures it out.

I looked hard at that approach and ruled it out. Walking Compose’s internal layout node tree means depending on APIs that aren’t public and aren’t stable across versions. Even past that hurdle, I’d still need to guess what shape each leaf node should be, whether it’s a `Text` that wants lines, an `Image` that wants a rounded rect, or an `Icon` that wants a circle, and there’s no reliable way to tell them apart from outside the composable using anything Compose exposes safely. On top of that, the container would need to compose the real content using data that, by definition, doesn’t exist yet. The whole point of a loading state is that the data hasn’t arrived.

So I went the other way: a modifier, applied to the composables that are already there.

Text(

 text = post?.title ?: "",

 modifier = Modifier.fillMaxWidth(0.6 f).skeleton()

)
`Modifier.skeleton()` doesn’t need to guess anything about what kind of composable it’s attached to, because it doesn’t have to. Compose already measures every element before it draws it. The modifier reads that measurement and draws a placeholder shaped to match: a rounded rectangle by default, matching the element’s own width and height, corner radius as the one knob. Ask for a circle, and it’s a circle. The shape decision moves from “the library guesses” to “the caller states it once,” which is a smaller ask than it sounds, since most cards only need it stated once anyway, on the avatar.

## One clock, not eighty

None of that fixes the actual bug in `ShimmerBox`. The shape problem was solvable either way I went. The sync problem needed a different owner entirely.

## Get KMP Bits’s stories in your inbox

Join Medium for free to get updates from this writer.

Remember me for faster sign in

The fix is a container that owns exactly one animation, and a way for every skeleton element underneath it to read that same animation without knowing the container exists.

@Composable

fun SkeletonContainer(

 loading: Boolean,

 modifier: Modifier = Modifier,

 shimmerColors: List<Color> = SkeletonDefaults.shimmerColors,

 cornerRadius: Dp = SkeletonDefaults.cornerRadius,

 content: @Composable () -> Unit,

) {

 val shimmerPhase: State<Float> = if (loading) {

 val transition = rememberInfiniteTransition(label = "skeletal-shimmer")

 transition.animateFloat(

 initialValue = 0f,

 targetValue = 1f,

 animationSpec = infiniteRepeatable(

 animation = tween(durationMillis = SHIMMER_PERIOD_MILLIS, easing = LinearEasing),

 repeatMode = RepeatMode.Restart,

 ),

 label = "skeletal-shimmer-phase",

 )

 } else {

 remember { mutableStateOf(0f) }

 }
val scope = remember(loading, shimmerColors, cornerRadius, shimmerPhase) {

 SkeletonScope(loading, shimmerPhase, shimmerColors, cornerRadius)

 }

 CompositionLocalProvider(LocalSkeletonScope provides scope) {

 Box(modifier) { content() }

 }

}

One `rememberInfiniteTransition`, hosted once, per container. That `shimmerPhase`gets bundled into a small `SkeletonScope` and handed down through a `CompositionLocal`. Every `Modifier.skeleton()` underneath this container reads the same `State<Float>` instance during its own draw phase, so a card near the top of the feed and a card near the bottom paint the same sweep position on the same frame. Twenty cards, one clock.

The `if (loading)` branch matters for more than sync. The infinite transition only exists while `loading` is true. The moment loading flips to false, that whole branch leaves composition, the transition’s underlying frame callback gets disposed, and the animation genuinely stops instead of running forever in the background on a screen nobody’s looking at anymore.

The modifier side just reads whatever it’s handed:

fun Modifier.skeleton(shape: SkeletonShape = SkeletonShape.Auto): Modifier = composed {

 val scope = LocalSkeletonScope.current

 ?: return@composed this.semantics { skeletalLoading = false }
val loading = scope.loading

 val contentAlpha = remember { Animatable(if (loading) 0f else 1f) }

 LaunchedEffect(loading) {

 contentAlpha.animateTo(

 targetValue = if (loading) 0f else 1f,

 animationSpec = SkeletonDefaults.crossfadeSpec,

 )

 }

 this

 .semantics { skeletalLoading = loading }

 .drawWithContent { skeletalLoading = loading }

 .drawWithCache {

 drawContent()

 val shimmerAlpha = 1f - contentAlpha.value

 if (shimmerAlpha > 0f) {

 drawShimmer(shape, scope.shimmerColors, scope.cornerRadius, scope.shimmerPhase.value, shimmerAlpha)

 }

 }

 .graphicsLayer { alpha = contentAlpha.value }

}

No `SkeletonContainer` above it, no scope, nothing to read. The early return means the modifier draws the real content and stops there. That one line is what makes it safe to leave `.skeleton()` on an element permanently: it costs nothing on the frames where there’s nothing to skeletonize.

## The bug I almost shipped anyway

Read that modifier chain closely, and the order of `drawWithContent` and `graphicsLayer` at the bottom looks arbitrary. It isn’t.

`graphicsLayer { alpha = contentAlpha.value }` scopes its alpha over everything drawn by whatever comes after it in the chain. I wrote it the other way round the first time: `graphicsLayer` before `drawWithContent`. That meant the alpha wrapped the shimmer draw too, since the shimmer is painted inside that same `drawWithContent` block. The result: as the real content faded in, the shimmer faded out at the exact same rate, dragged down by the same alpha instead of crossfading independently against it. It still looked like something was happening on screen. It just wasn’t the crossfade I’d designed on paper.

I caught it during planning, before a line of the real implementation existed, by tracing through what each modifier actually wraps instead of trusting that the code compiled and moving on. `drawWithContent` has to be the outer one. Its `drawContent()` call triggers the inner `graphicsLayer`, which fades the real content on its own terms. The shimmer gets painted by the outer block afterward, using its own `alpha` parameter on the draw call, untouched by the inner layer’s alpha. Two independent fades in the same chain, moving in opposite directions, and the order is the only thing keeping them independent.

## Wrapping up

A container that owns one clock and a modifier that costs nothing when there’s nothing above it: that’s the whole design. It didn’t need to be bigger than that. The interesting part was never drawing a gray box that shimmers. It was noticing that my own working code had eighty gray boxes, each keeping their own private time, and that fixing it meant giving all of them one clock to read instead of giving each one a better one.

Skeletal is live on [Maven Central](https://central.sonatype.com/artifact/io.github.kmpbits/skeletal) now, under `io.github.kmpbits:skeletal`. GitHub: [skeletal](https://github.com/kmpbits/skeletal). If you’re putting together a KMP toolbox of your own, it sits alongside two other libraries I maintain: [Netflow](https://github.com/kmpbits/netflow), a lightweight networking library for Kotlin Multiplatform that provides a simple API for Flow and direct suspending calls with optional Jetpack Paging 3 support, and [KMP Splash](https://github.com/kmpbits/KMP-Splash), a splash screen plugin for Compose Multiplatform that skips Xcode entirely.

_Same five lights, every car, every time. 🏁_
