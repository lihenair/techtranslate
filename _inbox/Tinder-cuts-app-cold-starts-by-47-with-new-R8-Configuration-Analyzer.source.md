---
source_url: https://android-developers.googleblog.com/2026/08/tinder-app-cold-start-r8-configuration-analyzer.html
fetched_at: 2026-08-25T12:21:25Z
fetch_method: jina
issue: 107
cover_image: https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEg82eJ9rS0VwZn7vwxFSpuhpyNOEC3uWOY1VfEzVNvCdrHyhR9VWwf-oVom-WJCkTtMjA-waS9Ayv-6C6hOot3YiUP1uPGF51hgVrrd9UFWaVQDSVKkhOktJ4jBUG8fDdoOYgK_q-HMZvLeCMp-wxPcQR8MPyfRWynacE85SKaU42X4jU_DopOOAL4CqU4/s2048/Copy%20of%20ANDDM_TINDER_Metacard.png
title_zh: Tinder 冷启动与 R8 Configuration Analyzer
tech_domain: android
---

# Tinder cuts app cold starts by 47% with new R8 Configuration Analyzer

_Posted by Ajesh R Pai, Developer Relations Engineer, Ulises Uriel Verduzco Diaz, Software Engineer, Tinder, and Tracy Agyemang, Product Marketing Manager_

[

![](https://www.gstatic.com/images/icons/material/system/2x/news_grey600_24dp.png)

![](https://www.gstatic.com/images/icons/material/system/1x/rss_feed_grey600_24dp.png)

![Google Play Site](https://developer.android.com/static/images/logos/google-play.svg)

![hero android logo](https://developer.android.com/static/images/logos/android.svg)

<!-- media:svg src="https://developer.android.com/static/images/logos/google-play.svg" -->

<!-- media:svg src="https://developer.android.com/static/images/logos/android.svg" -->

![Image 1](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhx1eo31tv-p6uCvZCXHnzn7SB-JxMY9-7qzvU181JlCuexV18yelk-V3JTsvkkZVgdTzSPFfeE1OSe8VYQxHbVpL-KBlwSxcRwAHPYu9fxvUV3exhyphenhypheniwgM1vewbzihbYeHjaQGqh0EhQyGq_wR0_eo4vJxjC39T5YOrxElHel-iB3mRVBugPUCetgC-NQ/s1600/Copy%20of%20ANDDM_TINDER_Header.png)](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhx1eo31tv-p6uCvZCXHnzn7SB-JxMY9-7qzvU181JlCuexV18yelk-V3JTsvkkZVgdTzSPFfeE1OSe8VYQxHbVpL-KBlwSxcRwAHPYu9fxvUV3exhyphenhypheniwgM1vewbzihbYeHjaQGqh0EhQyGq_wR0_eo4vJxjC39T5YOrxElHel-iB3mRVBugPUCetgC-NQ/s4209/Copy%20of%20ANDDM_TINDER_Header.png)

Tinder is on a mission to power and inspire real connections by making meeting easy and fun for every new generation of singles. However, as their Android application codebase grew in size, so did its complexity. Prior to their latest optimization efforts, approximately 70% of the application was not optimized, carrying 17 dex files,including three dedicated just to startup. Although they had enabled R8, much of its optimization potential was blocked due to keep rules, and the team was unable to identify which specific rules were preventing optimization. To reduce startup time and decrease user-perceived Application Not Responding (ANR) errors, Tinder turned to the new R8 Configuration Analyzer to tackle these challenges.

By utilizing the [R8 Configuration Analyzer](https://developer.android.com/topic/performance/app-optimization/r8-configuration-analyzer), Tinder successfully identified and removed unintentional optimization blockers. The results were immediate and impactful: Tinder achieved a 47% reduction in app cold starts, shrank their app download size by 28.98% (down to 61.5 MB), and reduced user-perceived ANRs by 28%.

## Configuration analyzer

The [R8 Configuration Analyzer](https://developer.android.com/topic/performance/app-optimization/r8-configuration-analyzer) shows R8 optimization by tracking shrinking, optimization, and obfuscation scores to show available refinement areas. It shows the broad, redundant, or obsolete keep rules, including those from external libraries so that you can analyse the keep rule impact and refine the keep rules.

Key metrics shown in Configuration Analyzer include:

*   **Shrinking Score:** Code percentage available for R8 shrinking.
*   **Optimization Score:** Code percentage open to optimization (for example, method inlining, horizontal class merging).
*   **Obfuscation Score:** Percentage of classes, methods and fields that can be renamed by R8 to decrease size.

Use the analyzer to audit keep rules and their impacts:

*   **Find broad rules:** Narrow the scope of package-wide rules that restrict R8 optimization, and identify the specific classes, methods, and fields excluded from shrinking, optimization, and obfuscation.
*   **Refine rules:** Target only specific classes/methods requiring reflection to unlock optimization
*   **Remove redundant rules:** Remove rules that match zero classes, methods, or fields in your current build.
*   **Identical rules:** Identical keep rules means rules that target the same classes, fields, and methods or duplicate declarations of keep rule in same or across keep rule files.
*   **Find subsumed rules:** Clean up specific rules already covered by broader configurations.
*   **Identify problematic libraries:** Check the combined optimization impact of merged consumer keep rules from all libraries.

[![Image 2](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgktzdcmhthiZ0YkW7GM5k3ffQzw3KhmghGbFBLPV1PVcABkxIrnY9slhKYI_r2KzKh4T9anf7mFJDe2KFCgmb_XfNC15fPsJ-wbIvWxyU2EP6JsfqKybi0pkjVX11ORyHKFd3PuYA3rR2fhH_lmD-IyV4P2Kl3rr93lqxBJsvznOYpdStP0TlrHF7Bn2U/s1600/R8-Configuration-Analyzer-Screenshot.png)](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgktzdcmhthiZ0YkW7GM5k3ffQzw3KhmghGbFBLPV1PVcABkxIrnY9slhKYI_r2KzKh4T9anf7mFJDe2KFCgmb_XfNC15fPsJ-wbIvWxyU2EP6JsfqKybi0pkjVX11ORyHKFd3PuYA3rR2fhH_lmD-IyV4P2Kl3rr93lqxBJsvznOYpdStP0TlrHF7Bn2U/s3560/R8-Configuration-Analyzer-Screenshot.png)

R8 Configuration Analyzer report of a sample application

To assist you in using the R8 Configuration Analyzer with agentic tools, we have published an [R8 Analyzer skill](https://github.com/android/skills/blob/main/performance/r8-analyzer/SKILL.md). This skill optimizes automated development workflows by summarizing the R8 Configuration Analyzer report to display key metrics: optimization, obfuscation, and shrinking scores. It also highlights the five most impactful keep rules, giving you clear insight into what blocks code optimization.

## Pinpointing hidden optimization blockers

[![Image 3](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjHRi3Fc_mcgTBXdBskM5JFpROGI4DhkFxjmp64eDPS_3jYEqKMYpAhd6H6LubQjyuP1tiEuhsTpTb139s8jFG5F445HBJrlB25XZMc1viWBieiw9Ufi_kVbDyvABrkkGyJwpuhhWVlcyWEA0y7R-q9RaUOxxp33mncEYhhsVN4Nz2y20GUov2B7ofPCbc/s1600/Copy%20of%20AANDDM_TINDER_Quote_01.png)](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjHRi3Fc_mcgTBXdBskM5JFpROGI4DhkFxjmp64eDPS_3jYEqKMYpAhd6H6LubQjyuP1tiEuhsTpTb139s8jFG5F445HBJrlB25XZMc1viWBieiw9Ufi_kVbDyvABrkkGyJwpuhhWVlcyWEA0y7R-q9RaUOxxp33mncEYhhsVN4Nz2y20GUov2B7ofPCbc/s1280/Copy%20of%20AANDDM_TINDER_Quote_01.png)

Prior to integrating the R8 Configuration Analyzer, Tinder's Android app suffered from significant technical debt due to a heavily unoptimized codebase. This lack of optimization directly degraded the user experience, leading to users experiencing slow cold starts

To resolve these issues, the Tinder team utilized the R8 Configuration Analyzer to comprehensively audit their R8 configuration. The analyzer showed the R8 optimization of the codebase was around 28% even with R8 full mode. With R8 Configuration Analyzer, Tinder identified that an in-house library was introducing a broad, unscoped keep rule.

```
# Prevents optimization in all public classes along with all of their public and protected members

-keep public class * {
    public protected *;
}
```

This "wide" rule unintentionally covered various dependencies across the entire app, preventing optimization in a large number of classes. Because the over-inclusive rule prevented runtime crashes, developers frequently missed adding new rules for new features that used reflection, allowing hidden issues to compound over time.

By leveraging the insights provided by the R8 Configuration Analyzer, the team successfully traced and analyzed the specific classes affected by the broad keep rule from the library. The team immediately discovered that optimization was being blocked in larger, non-dynamically invoked classes where R8 could do optimization. Refining this specific keep rule allowed Tinder to unlock substantial optimization capabilities, untangle their legacy configurations, and drastically improve their overall optimization numbers, with R8 scores increasing from 28% to 50%, driving immediate performance gains across the application, and the Tinder team is actively working to further improve this figure.

*   **Faster Loading:** The team achieved a 47% reduction on users experiencing slow cold starts of the app.
*   **Smaller Footprint:** The App download size went from 86.6MB down to 61.5 MB (28.98% decrease).
*   **Improved Stability:** User-perceived Application Not Responding (ANR) errors decreased from 0.35% to 0.28%, bringing them significantly closer to the peer median numbers
*   **Reduced Complexity:** The total number of DEX files was cut down from 17 to 11, including just two startup files.

Beyond these technical performance enhancements, the increased application optimization directly translated into tangible business growth and higher user engagement, particularly in resource-constrained markets.

*   **Regional Engagement:** Countries where Low RAM devices take a huge portion of the market, presented the largest increase in engagement, and decreasing the ANR rates was key to improving engagement in this vast market.
*   **Engagement Growth:** Engagement has increased 3% since the increase in app optimization.

[![Image 4](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiLeXSQwvw-CLpu7OvvrGYnMzubz2UTWvXO7-oIlxYiTlbBJFHlRuVFDGUn80Ipn1rb9AOMd81m0VAskOhOusALLcttHbAB2STF7NARrW7b6d5gzesN4BU4UwWFdNBHzhUhyYJv5q0eQLSxLN8ph5uD4uzf8I6u7wjDGucpM8d3R0BI6ffgvRaOzLBkO3o/s1600/Copy%20of%20AANDDM_TINDER_Stat_01.png)](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiLeXSQwvw-CLpu7OvvrGYnMzubz2UTWvXO7-oIlxYiTlbBJFHlRuVFDGUn80Ipn1rb9AOMd81m0VAskOhOusALLcttHbAB2STF7NARrW7b6d5gzesN4BU4UwWFdNBHzhUhyYJv5q0eQLSxLN8ph5uD4uzf8I6u7wjDGucpM8d3R0BI6ffgvRaOzLBkO3o/s1280/Copy%20of%20AANDDM_TINDER_Stat_01.png)

## Safeguarding future performance with continuous integration

Addressing code minification isn't just a one-time fix; it requires continuous vigilance. Inspired by the massive gains achieved through the R8 Configuration Analyzer, Tinder’s Android team proactively integrated optimization monitoring into their daily workflow to prevent regressions.

Tinder’s team added a new job in their CI/CD pipeline to report changes in the optimization stats so everyone can see how their contribution is affecting optimization. When advising other developers considering R8 configuration integration, the team emphasizes the importance of auditing internal dependencies. While most popular third-party libraries come with well-defined rules, internal company projects that are considered "stable" might actually be introducing wide rules that negatively impact overall optimization.

## Key Takeaways

Faced with a heavily unoptimized codebase and a high volume of DEX files, Tinder needed a way to cleanly audit their app’s minification rules. The R8 Configuration Analyzer provided the ideal tooling necessary to identify overly broad internal library rules,the classes affected by the keep rule, allowing the team to confidently optimize their codebase. As a result, Tinder successfully cut cold starts by nearly half, shrank their APK size by over 28%, and established a healthier, more performant foundation for their users, with the team actively working to further improve these numbers.

## How to Use R8 Configuration Analyzer

The R8 Configuration Analyzer and its standalone features can be utilized based on your current Android Gradle Plugin (AGP) version:

*   **AGP 9.3 Release:** The R8 Configuration Analyzer is fully integrated and released with AGP 9.3. When running an R8 release build, the report will be generated in the `build/outputs/mapping/release/configanalyzer.html` folder.
*   **Standalone Gradle Task:** AGP 9.3 introduces a standalone Gradle task that allows you to generate the analyzer report without running a full release build, providing a much faster feedback loop when refining keep rules locally: `./gradlew :app:analyzeReleaseR8Config` The report is generated at `build/reports/r8/r8-config-analyzer-release.html`. 
*   **Usage on Older AGP Versions:** If you are using a version below AGP 9.3, you do not need to migrate your entire AGP version to analyze your configuration. You can update the R8 version independently to 9.3.7-dev or higher by following the [Replacing R8 in AGP instructions](https://r8.googlesource.com/r8/+/refs/heads/main/README.md#replacing-r8-in-agp). To generate the report locally, run your build with the property specified: `./gradlew assembleRelease  -Dcom.android.tools.r8.dumpkeepradiushtmltodirectory=<output_directory>`

To learn more, see the [R8 Configuration Analyzer](https://developer.android.com/topic/performance/app-optimization/r8-configuration-analyzer) documentation.

<!-- media:svg src="https://developers.google.com/static/homepage-assets/images/x.svg" -->

<!-- media:svg src="https://www.gstatic.com/dgc_blog/images/ic_linkedin_black.svg" -->

<!-- media:svg src="https://www.gstatic.com/dgc_blog/images/ic_facebook_black.svg" -->

<!-- media:svg src="https://www.gstatic.com/dgc_blog/images/ic_mail.svg" -->

<!-- media:svg src="https://www.gstatic.com/dgc_blog/images/ic_link.svg" -->

![Android Developers on YouTube](https://www.gstatic.com/images/icons/material/system/2x/video_youtube_grey600_24dp.png)

![Android Developers on LinkedIn](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhszO3n6Cp0Se7U-SHWbR3gNdcompQDQCx3gZiyTc0scuR4yJW_Nh2yKMwVURoBjGaQ71yNxTtfJvN7kjHOK4u4uPy32B4sIu3hrpWuWHT6w4V0NAtED9Z76G48nzMaqaZba95i21bfUspd3fn5EDsTBte-oJ2l-FEzbkAVeLQIzHaAMHOQocMDWN2MJD4/s1600/linkedin-4-48.png)

![Follow Android Developers on X](https://developers.google.com/static/homepage-assets/images/x.svg)

![Share on LinkedIn](https://www.gstatic.com/dgc_blog/images/ic_linkedin_black.svg)

![Share on Facebook](https://www.gstatic.com/dgc_blog/images/ic_facebook_black.svg)

![Share in mail](https://www.gstatic.com/dgc_blog/images/ic_mail.svg)

![Copy link](https://www.gstatic.com/dgc_blog/images/ic_link.svg)

![](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEg82eJ9rS0VwZn7vwxFSpuhpyNOEC3uWOY1VfEzVNvCdrHyhR9VWwf-oVom-WJCkTtMjA-waS9Ayv-6C6hOot3YiUP1uPGF51hgVrrd9UFWaVQDSVKkhOktJ4jBUG8fDdoOYgK_q-HMZvLeCMp-wxPcQR8MPyfRWynacE85SKaU42X4jU_DopOOAL4CqU4/s2048/Copy%20of%20ANDDM_TINDER_Metacard.png)
