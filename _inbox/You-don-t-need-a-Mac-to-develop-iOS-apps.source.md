---
source_url: https://expo.dev/blog/build-ios-apps-on-windows-with-cloud-simulators
fetched_at: 2026-09-18T14:45:41Z
fetch_method: jina
issue: 333
cover_image: https://cdn.sanity.io/images/9r24npb8/production/3cac54f661c659105f8148eeb8cf3173d9ad3ac9-1800x1012.png?w=1200&h=630&fit=crop&fm=webp&q=80&auto=format
title_zh: 不用 Mac 也能开发 iOS 应用
tech_domain: mobile
---

# You don't need a Mac to develop iOS apps

[Nearly three out of four desktops in the world](https://gs.statcounter.com/os-market-share/desktop/worldwide) are not Macs. With Expo, you could already build an iOS app from any of them through [EAS Build](https://docs.expo.dev/build/introduction/). But in the age of agentic development, we are faced with another bottleneck: agents need instant feedback to keep iterating on their code changes. The iOS Simulator only ships with Xcode, and Xcode only runs on macOS, so without a Mac every change you or your agent makes has to be checked on a physical iPhone. [EAS Simulator](https://docs.expo.dev/preview/eas-simulator/introduction/) removes that requirement.

Functionally speaking, EAS Simulator runs a simulator session in the cloud and streams it to a browser tab. What this service unlocks is going to change the way mobile software gets built: any laptop becomes an iOS development machine, any coding agent gets a real device to prove its work on, and anyone with the URL can control the same phone alongside you.

Keith Kurak, one of our engineers, [took EAS Simulator somewhere none of us had tried yet](https://x.com/llamaluvr/status/2094414188181332015): an iOS Simulator with Fast Refresh, on a Windows on ARM laptop. This post covers what Keith showed and the five capabilities I've been using to develop apps.

Prefer watching? The short version is here:

A demo of EAS Simulators

Here is what [Keith](https://x.com/llamaluvr/) posted:

This weekend, EAS Simulators helped me achieve a long-unfulfilled dream: running a simulator next to VS Code on Windows on ARM. WOA doesn't support Android Studio or even 3rd party Android emulators and MS dropped support for Windows Subsystem for Android on the Snapdragon X.

Windows on ARM cannot run Android Studio, and Microsoft dropped Windows Subsystem for Android on the Snapdragon X. That laptop had no simulator or emulator of any kind. Now it has an iPhone in a browser tab, and edits in VS Code land on it through Fast Refresh.

All you need is two commands. You need a [development build](https://docs.expo.dev/develop/development-builds/introduction/) that targets the simulator, because a release build does not hot reload: its JavaScript is fixed at build time. Then start Metro with a tunnel, and start the session pointing at it:

EXPO_UNSTABLE_TUNNEL_V2=1 npx expo start --tunnel

eas simulator:start --platform ios --type agent-device \

--build-id <your-build-id> \

--open-url "<your-scheme>://expo-development-client/?url=<encoded-metro-url>" \

--name "windows hot reload" --non-interactive

The command gives you a `webPreviewUrl`. Open it and your app is running on a cloud iPhone. Edit a file, save, and the change appears on the device. Keith ran this inside WSL. The full walkthrough, including the [Expo Go](https://expo.dev/go) variant, is in the [Run and control docs](https://docs.expo.dev/preview/eas-simulator/run-and-control/).

That alone changes what you can build from a Windows or Linux machine. But here are five more things EAS Simulator does that you should know about:

I am building a camera app called [OpenMulticam](https://github.com/rami-maalouf/open-multicam). It records from several iPhone cameras at once, and testing it has always required a physical device, because a simulator has never had a camera. EAS Simulator's web preview changes that. It has a Camera section in its tools panel, and when you turn it on, the app receives a simulated camera feed.

![OpenMulticam running on a cloud iPhone in the EAS Simulator web preview, with the simulated camera feed showing and a badge reading Simulated Camera Back (serve-sim)](https://cdn.sanity.io/images/9r24npb8/production/16e55d4bd7bed683fa6f270654d69e287e583cef-1920x1080.png?auto=format&fit=max&q=75&w=800)

Press record, stop, and open the take. The whole camera capture pipeline runs on a device in the cloud, and you drive it from a browser tab.

![Recording in progress in OpenMulticam on the cloud simulator, with the timer running](https://cdn.sanity.io/images/9r24npb8/production/ef5393e77bcd1a85630e3bc504b2faef9c9684fd-1920x1080.png?auto=format&fit=max&q=75&w=800)

Two things to keep in mind when you try it. The default source is an animated test pattern, and you can also drop a video or a photo from your computer into the panel and use it as the feed. Your app has to use the standard AVFoundation capture APIs for the injection to work, which most camera libraries do.

One limitation to know about: today the camera panel is something you click in the browser. It is not exposed to agents yet, so an agent cannot inject a camera on its own. Everything else in this post, an agent can do.

A cloud agent or your local coding agent can drive the simulator through [agent-device](https://docs.expo.dev/agents/agent-device/). [Argent](https://docs.expo.dev/agents/argent/) works too, and so does computer use if you prefer it.

The fastest way to set this up is the [eas-simulator skill](https://github.com/expo/skills/tree/main/plugins/expo/skills/eas-simulator). Install it into Claude Code, Cursor, or Codex, tell the agent what to check, and it does the rest: it builds the app, starts a cloud session, taps through the screens, and sends back screenshots. When it is done, you review the session replay instead of pulling the branch and testing it yourself.

The preview is a website. Send the URL to a coworker and they see what you are working on in real time, and they can interact with the simulator too. **You, your coworkers, your cloud agents, and your local agents can all work on the same device at once.**

If you only need the shareable view and no agent control, there is a session type for exactly that:

eas simulator:start --platform ios --type web-preview-only --name "design review"

The preview also has a full screen button that strips away everything but the device.

Every session shows up on your project's page on expo.dev.

![The Simulator sessions page on expo.dev listing ten sessions for the open-multicam project, with names, type, platform, start time, and duration](https://cdn.sanity.io/images/9r24npb8/production/251a1c9e6a7bdf23e5dc9209af5be2dc5240c1b1-1920x1080.png?auto=format&fit=max&q=75&w=800)

Open a finished one and you get the full video of what happened on the device, plus a timeline of every interaction. In the session from the video, you can watch the agent tap through the app, testing the features I asked it to test, with a screenshot at each step.

![A finished session's recording on expo.dev with a timeline of screenshots taken during the run](https://cdn.sanity.io/images/9r24npb8/production/01bdb7ec978ab951ce4c8db344ca147b167fa7ea-1920x1080.png?auto=format&fit=max&q=75&w=800)

I have started using these links as evidence in pull requests. "Here is the bug, here is the fix, here is the replay" makes for a much better review than "trust me, I ran it."

Your app does not have to use Expo or React Native. The device starts blank, and you can upload any iOS Simulator build or Android APK to it: SwiftUI, Kotlin, Flutter, anything that runs on a simulator.

eas simulator:exec npx agent-device@latest install com.example.app ./path/to/MyApp.app --platform ios

EAS Simulator is a limited-access preview, and we are opening it up from the waitlist in batches.

*   **Join the waitlist** at [expo.dev/services/simulators](https://expo.dev/services/simulators).
*   **Read the docs.**[Get started](https://docs.expo.dev/preview/eas-simulator/get-started/) covers session types, and [Run and control an app](https://docs.expo.dev/preview/eas-simulator/run-and-control/) has the Fast Refresh recipe from this post.
*   **Give it to your agent.** Install the [eas-simulator skill](https://github.com/expo/skills/tree/main/plugins/expo/skills/eas-simulator) and ask it to verify something on a real device runtime.

If you would like a full tutorial on setting this up on your own machine, let us know. We are also curious how you would use a cloud simulator. Share your use cases in the #eas-simulator channel of [our Discord community](https://chat.expo.dev/).

**What is EAS Simulator?** A service from Expo that runs a remote iOS Simulator or Android Emulator on EAS infrastructure. You control it from the CLI, a REST API, a coding agent, or a browser. Supported iOS sessions include a live web preview. It is in limited-access preview.

**Can you build iOS apps on Windows with Expo?** Yes. EAS Build compiles the app on Expo's Mac infrastructure, and EAS Simulator runs the iOS Simulator there too. A development build connected to Metro over a tunnel gives you Fast Refresh in the browser. The CLI runs in WSL.

**Can you test camera features in an iOS Simulator?** With EAS Simulator's web preview, yes. The Camera section of the tools panel gives the app a simulated camera feed: an animated test pattern by default, or a photo or video you drop in. The app has to use standard AVFoundation capture APIs.

**Can an AI agent use EAS Simulator?** Yes. Agents drive the device through agent-device or Argent. The eas-simulator skill teaches Claude Code, Cursor, and Codex the full loop: access check, build, session, device control, evidence, cleanup.

**Does my app have to use Expo or React Native?** No. Any iOS Simulator build or Android APK works.

**Can you share an EAS Simulator session with someone?** Yes. The web preview is a URL. Anyone with it can watch and interact with the same device at the same time. Use the `web-preview-only` session type if you do not need agent control.

<!-- media:section-anim index="1" duration_s="4" -->

<!-- media:section-anim index="2" duration_s="4" -->

<!-- media:section-anim index="3" duration_s="4" -->

<!-- media:section-anim index="4" duration_s="4" -->

<!-- media:section-anim index="5" duration_s="4" -->

<!-- media:section-anim index="6" duration_s="4" -->

<!-- media:section-anim index="7" duration_s="4" -->

<!-- media:section-anim index="8" duration_s="4" -->

<!-- media:section-anim index="9" duration_s="4" -->

<!-- media:section-anim index="10" duration_s="4" -->

<!-- media:section-anim index="11" duration_s="4" -->

<!-- media:section-anim index="12" duration_s="4" -->

<!-- media:section-anim index="13" duration_s="4" -->

<!-- media:section-anim index="14" duration_s="4" -->

<!-- media:section-anim index="15" duration_s="4" -->

<!-- media:section-anim index="16" duration_s="4" -->

<!-- media:section-anim index="17" duration_s="4" -->

<!-- media:section-anim index="18" duration_s="4" -->

<!-- media:section-anim index="19" duration_s="4" -->

<!-- media:section-anim index="20" duration_s="4" -->

<!-- media:section-anim index="21" duration_s="4" -->

<!-- media:section-anim index="22" duration_s="4" -->

<!-- media:section-anim index="23" duration_s="4" -->

<!-- media:section-anim index="24" duration_s="4" -->

<!-- media:section-anim index="25" duration_s="4" -->

<!-- media:section-anim index="26" duration_s="4" -->

![Rami Maalouf](https://cdn.sanity.io/images/9r24npb8/production/56e0e8aa9e033d08ae9435e14163fbae4f7261ee-512x512.png?auto=format&fit=max&q=75&w=48)

![Rami looking surprised beside an iPhone marked Live, a Windows logo, and the words Running on Windows](https://cdn.sanity.io/images/9r24npb8/production/3cac54f661c659105f8148eeb8cf3173d9ad3ac9-1800x1012.png?auto=format&fit=max&q=75&w=1200)

![The saved take in OpenMulticam: Sep 3, 2026 at 8:04 AM, 1080 by 1920 at 30 fps, with Share and Save to Photos buttons](https://cdn.sanity.io/images/9r24npb8/production/5c0a5d33269e9ae446b5c8c1c99a4f35fceb585c-1920x1080.png?auto=format&fit=max&q=75&w=800)

![A habit tracker app being built across three AI workflow lanes: skills, MCP, and branched conversations.](https://cdn.sanity.io/images/9r24npb8/production/a3de30477fd8205c4222130c78198ebdc49e3d43-2400x1350.png?rect=2,0,2396,1350&w=300&h=169&auto=format)

![Rami pointing at the Codex and Claude app icons, labeled GPT 5.6 and Fable 5, above the words The ultimate test](https://cdn.sanity.io/images/9r24npb8/production/e65d024aa4fdd819b9449b69e6c26bb4067de9a2-1920x1080.png?rect=2,0,1917,1080&w=300&h=169&auto=format)
