---
source_url: https://swmansion.com/blog/react-native-gesture-handler-s-touchable-the-button-we-wish-we-had-sooner/
fetched_at: 2026-09-05T10:51:33Z
fetch_method: jina
issue: 240
author: Jakub Piasecki
published_at: 2026-08-20
cover_image: https://strapi-production-5f3f.up.railway.app/uploads/ver_3_83144fea89.png
title_zh: React Native Gesture Handler 的 Touchable：我们早该有的按钮
tech_domain: frontend
---

# Gesture Handler's Touchable: Button We Wish We Had Sooner

I like buttons. I think most people like buttons, especially when they give satisfying feedback when pressed. So you need a lot of them, with different kinds of feedback, right? Well, not really – that’s how you end up with multiple components doing the same thing, but slightly differently. And we learned it the hard way, during React Native Gesture Handler’s years-long development.

## How did we get here?

When you install a library for handling touch in your app, you expect it to have a ready-to-use button component. And we did have a few of them, each with different visual feedback. As React Native evolved, there came a need for drop-in replacements for its Touchable components. Then React Native got Pressable, and we needed a drop-in for that as well. Suddenly, we were exporting 9 separate button components.

We realized this when consulting a large financial app about button usage. After a lot of discussions about the expectations and assumptions, we decided that there’s no one-size-fits-all preset here. But we can share the tools to fit a vast majority of use cases, so we decided to solve this once and for all.

## Don’t reinvent the Pressable, we already did it for you

Obviously, the solution to “there are too many buttons” is one button to rule them all. We did that in React Native Gesture Handler 3 with Touchable, our new button component. Now that we have one more button component, the situation is clear (we did deprecate the other ones). One exception is our Pressable – it became a small wrapper around Touchable to preserve a drop-in replacement in cases where a gesture-aware button is needed.

## How is it better?

First of all, it’s customizable, allowing you to set a custom scale, opacity, and underlay for each of the states: default, pressed, and hovered. Oh, it also supports hover on mobile (both with mouse and pencils). Additionally, you can set custom transition times for each of the states separately. All of that lives at the platform level (ObjectAnimator on Android, CoreAnimation on iOS, and CSS transitions on the web), which also respects the OS accessibility settings like animation scale and reduce motion.

**Opacity:**

```
<Touchable
 style={styles.button}
 activeOpacity={0.7}
 onPress={onPress}>
 <Text style={styles.text}>activeOpacity: 0.7</Text>
</Touchable>
```

**Scale:**

```
<Touchable
 style={styles.button}
 activeScale={1.05}
 onPress={onPress}>
 <Text style={styles.text}>activeScale: 1.05</Text>
</Touchable>
```

**Underlay:**

```
<Touchable
 style={styles.button}
 underlayColor="black"
 onPress={onPress}>
 <Text style={styles.text}>underlayColor: black</Text>
</Touchable>
```

The JS component is basically a simple wrapper over the codegen spec. If you rely on the built-in animations, Touchable doesn’t re-render by itself.

If you need more configuration options, you can use your favourite animation library to drive the transitions yourself, just like with React Native’s Pressable.

## I heard you like numbers

We prepared them for you – 50 runs of 1000 Buttons rendered at once, lower is better.

### Absolute values (in milliseconds)

**Component****Oppo A16 mean****Oppo A16 median****Pixel 9 Pro mean****Pixel 9 Pro median**
Touchable 7838.4 7737.0 574.0 573.0
Pressable 8180.3 8197.0 651.0 652.0
RectButton 8281.0 7995.0 1067.9 1057.0

### Relative values (compared to Pressable)

**Component****Oppo A16 mean****Oppo A16 median****Pixel 9 Pro mean****Pixel 9 Pro median**
Touchable 0.96 0.94 0.88 0.88
Pressable 1.00 1.00 1.00 1.00
RectButton 1.01 0.98 1.64 1.62

The new Touchable component is faster to render than the old RectButton, and scores a win against React Native’s built-in Pressable as well. The differences are most pronounced on more powerful devices, which aren’t overwhelmed by the JavaScript workload.

## Why Touchable?

Pressable was already taken ¯\_(ツ)_/¯… oh, “when would I use this”, not “why did you call it that”, got it. Currently, there are three ways to handle tap interaction in Gesture Handler: useTapGesture, Touchable, and Pressable. In the vast majority of cases, Touchable should be the default choice, and the decision on which one to use should be much simpler now:

*   **Use useTapGesture when you need to customize the behavior**, like the number of taps, maximum tap duration, or you need more complex relations between different gestures.

*   **Use Pressable, a Touchable in a trenchcoat, when you have existing components using React Native’s Pressable**, and you want to migrate to Gesture Handler using a drop-in replacement.

*   **Otherwise, just use Touchable.**

## What about migrating?

We plan to remove the deprecated buttons in the next major release of Gesture Handler, so we strongly recommend using Touchable instead. You can migrate manually, or leave that to your agent of choice using our [migration skill](https://github.com/software-mansion-labs/skills/blob/main/skills/react-native-best-practices/references/gestures/v2-to-v3-migration.md).

<!-- media:section-anim index="1" duration_s="4" -->

<!-- media:section-anim index="2" duration_s="4" -->

<!-- media:section-anim index="3" duration_s="4" -->

<!-- media:video-gif src="https://strapi-production-5f3f.up.railway.app/uploads/opacity_f6c97c4613.mp4" -->

<!-- media:video-gif src="https://strapi-production-5f3f.up.railway.app/uploads/scale_c77394df9a.mp4" -->

<!-- media:video-gif src="https://strapi-production-5f3f.up.railway.app/uploads/underlay_c3378e8980.mp4" -->

<!-- media:section-anim index="4" duration_s="4" -->

<!-- media:section-anim index="5" duration_s="4" -->

<!-- media:section-anim index="6" duration_s="4" -->

<!-- media:section-anim index="7" duration_s="4" -->

<!-- media:section-anim index="8" duration_s="4" -->

<!-- media:section-anim index="9" duration_s="4" -->

<!-- media:section-anim index="10" duration_s="4" -->

<!-- media:section-anim index="11" duration_s="4" -->

![](https://strapi-production-5f3f.up.railway.app/uploads/ver_3_ce489e3336.png)

![Jakub Piasecki](https://strapi-production-5f3f.up.railway.app/uploads/author_jakub_piasecki_fae555b804.jpeg)
