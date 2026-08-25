---
source_url: https://androidadventures.dev/fun-animations-with-mesh-gradients-jetpack-compose-1-12-0f708eed6c56
fetched_at: 2026-08-25T12:19:40Z
fetch_method: jina
issue: 104
title_zh: 用 Mesh Gradients 做好玩动画：Jetpack Compose 1.12
tech_domain: android
---

# Fun Animations with Mesh Gradients: Jetpack Compose 1.12

[![Image 1: Kevin Desai](https://miro.medium.com/v2/resize:fill:64:64/0*Fk3vm4n-jigVR6oW.jpg)](https://androidadventures.dev/?source=post_page---byline--0f708eed6c56---------------------------------------)

5 min read

3 days ago

--

--

Press enter or click to view image in full size

![Image 2](https://miro.medium.com/v2/resize:fit:700/1*UohuoxlKJsokUs8lIf9TYQ.gif)

We’ve always had APIs for linear and radial gradients in Jetpack Compose. But if you wanted a more complicated color blending API, there was nothing like that. Enter [**MeshGradientPainter**](https://developer.android.com/develop/ui/compose/graphics/draw/mesh-gradient)introduced in Jetpack Compose 1.12.

## How MeshGradient works:

Think of a mesh gradient as a **grid of dots** across your screen. For every dot in the grid, you pick two things:

1.   **Where it sits** (X,Y)
2.   **What color it has**

Compose connects the dots and blends all the colors together automatically.

(Light Blue) --------- (Light Blue) --------- (Light Blue) <-- Top

 | | |

(Medium Blue) -------- (Medium Blue) -------- (Medium Blue) <-- Middle

 | | |

(Dark Navy) ---------- (Dark Navy) ---------- (Dark Navy) <-- Bottom
The Google developer website gives a great [example](https://developer.android.com/develop/ui/compose/graphics/draw/mesh-gradient#create-simple-mesh-gradient) to get started with.

## MeshGradient for water:

Lets say we are working on a water intake tracker style app. And we need to show how much water the user has consumed.

For a sort of realistic water look, I went with a 5×5 grid (6 rows of dots). Here’s how we make it feel like real deep water:

### 1. Colors that get darker with depth

*   **Top row:** Bright aqua and foam colors (where sunlight hits the water).
*   **Middle rows:** Rich ocean blues.
*   **Bottom row:** Dark navy.

### 2. Only the surface moves

**To make it look like deep water, we only wiggle the top row of dots. The bottom rows stay completely still. This gives the water a calm, heavy look underneath.**

If you just wanted the water gradient, without any animation, this is how it would look like

@Composable

fun WaterGradient(modifier: Modifier = Modifier) {

 val rowHeights = listOf(0.14f, 0.34f, 0.52f, 0.68f, 0.84f, 1.00f)

 val rowColors = listOf(

 Color(0xFF9BF0E8), 

 Color(0xFF4FD6E8), 

 Color(0xFF2AB0E0), 

 Color(0xFF1C86D4), 

 Color(0xFF1355B8), 

 Color(0xFF0B2E86) 

 )
val waterPainter = MeshGradientPainter(rows = 5, columns = 5, hasBicubicColor = true) {

 for (row in 0..5) {

 val y = rowHeights[row]

 val color = rowColors[row]

for (col in 0..5) {

 val x = col / 5.0f

 setVertex(row, col, Offset(x, y), color)

 }

 }

 }

Box(

 modifier = modifier

 .fillMaxSize()

 .paint(waterPainter)

 )

}

## The wave animation:

A good way to add user delight would be to add a simple water animation so the screen feels alive.

A water wave can be represented as a sine wave.

Imagine you are riding a Ferris wheel that spins at a constant speed.

If you track **only your height from the ground** over time:

![Image 3](https://miro.medium.com/v2/resize:fit:640/1*2gjhSYTVizaS_gdZ9DuolQ.gif)

At the bottom, you rise slowly.

In the middle, you shoot up fast.

At the top, you slow down, smoothly pause for a split second, and gently reverse direction.

That smooth, natural curve, slowing down at the peaks and speeding up in the middle **is a sine wave**and can be used to represent the water wave as well.

In our mesh gradient, our water surface is made of **6 dots (columns 0 to 5)** in a line across the screen. If we just tell all 6 dots: `height = sin(time)`:

*   All 6 dots go UP together.
*   All 6 dots go DOWN together.

That’s not a wave, it’s a flat line going up and down. 

So think of people doing the Mexican wave in the stadium.

## Get Kevin Desai’s stories in your inbox

Join Medium for free to get updates from this writer.

Remember me for faster sign in

Person 0 stands up first.

A split-second later, Person 1 stands up.

Then Person 2, Person 3, and so on.

Because each column starts with a **small delay**, the crest appears to **travel across the screen** from left to right!

In code, this delay is simply:

> Height=sin⁡(time−delay)

Now the issue with this formula. Modern phone screens refresh 120 times a second. 

Remember, **each row has 6 separate column dots**:

In 1 second at 120fps, the screen redraws **120 times**:

1.   **For Row 0 alone (6 dots):** 6 dots×120 frames=720 calculations / second
2.   **For Row 1 alone (6 dots):** 6 dots×120 frames=720 calculations / second
3.   **Both Row 0 and Row 1 combined (12 dots total):** 12 dots×120 frames=1,440 calculations / second

The math shortcut: The Angle Subtraction Identity

sin(time−delay)= sin(time)cos(delay) — cos(time)sin(delay)

1.   **Time (**_ωt_**):** There is only **one** clock for the whole screen. We calculate `sin(time)` and `cos(time)`**just once per frame**.
2.   **Space (**delay**):** Our 6 columns sit at fixed positions (X=0.0,0.2,0.4,0.6,0.8,1.0). Their delays never change!

Because the delays are fixed, cos⁡(delay) and sin⁡(delay) are **pure constants**. We write them down once ahead of time as `LEAD` and `LAG`:

private val LEAD = floatArrayOf(1.000f, 0.924f, 0.707f, 0.383f, 0.000f, -0.383f) 

private val LAG = floatArrayOf(0.000f, 0.383f, 0.707f, 0.924f, 1.000f, 0.924f) 
Now, finding the wave value for any column is just **two fast 1-cycle multiplications**:

fun surface(col: Int): Float = LEAD[col] * sinTime - LAG[col] * cosTime
`surface(col)` returns a smooth value oscillating between −1.0**and**+1.0

### Placing the Dots with `Offset(X, Y)`

1. The Base Grid Spacing

*   X-**spacing:** 6 dots evenly divided into 5 intervals (1.0/5=0.20).
*   Y**-spacing:** Row 0 starts at 0.14 (instead of 0.0) to leave 14% headroom so the wave crest never clips against the top edge.

2. Row 0 (The Surface): `crest` + `sway`

*   Y**Position (Height):** Base height is 0.14. We add `crest * surface(col)`. With `crest = 0.04`, the surface moves between 0.10**and**0.18
*   X**Position (Sway):** Interior dots drift left and right by `sway * surface(col)` (0.015). This combined _X_ and Y motion gives dots their natural circular orbit.
*   **Edge Pinning:** Columns 0 and 5 have X locked to `0.0` and `1.0` (pinned to screen edges), while their Y undulates freely so waves flow into and out of the viewport.

3. Row 1 (The Under-surface): `trail`

*   Y**Position:** Base height is 0.34. We add `trail * surface(col)`.
*   With `trail = 0.016` (only 40% of the surface wave), this layer bends softly beneath the crest, creating the illusion of sunlit water caustics.

_And that’s all! Math class is over. The big payoff? Smooth animation without dropping any frames!_

*   💻 **Complete Code:**[GitHub Repository](https://github.com/kevindesai777/compose-experiments/blob/main/composeApp/src/commonMain/kotlin/com/pixel/composeexperiments/WaterTracker.kt)
*   🌐 **Live Web Demo:**[Try it in your browser](https://kevindesai777.github.io/compose-experiments/#water_mesh_gradient) (Kotlin Multiplatform goodness!)
