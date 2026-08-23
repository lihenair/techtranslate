---
source_url: https://qiita.com/Tks_Yoshinaga/items/cfc9d6575afd78f12f31
fetched_at: 2026-08-23T10:00:16Z
fetch_method: jina
issue: 26
cover_image: https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-user-contents.imgix.net%2Fhttps%253A%252F%252Fcdn.qiita.com%252Fassets%252Fpublic%252Farticle-ogp-background-afbab5eb44e0b055cce1258705637a91.png%3Fixlib%3Drb-4.1.1%26w%3D1200%26blend64%3DaHR0cHM6Ly9xaWl0YS11c2VyLXByb2ZpbGUtaW1hZ2VzLmltZ2l4Lm5ldC9odHRwcyUzQSUyRiUyRnFpaXRhLWltYWdlLXN0b3JlLnMzLmFwLW5vcnRoZWFzdC0xLmFtYXpvbmF3cy5jb20lMkYwJTJGNjE3NDIlMkZwcm9maWxlLWltYWdlcyUyRjE3NjU5NDEzNzA_aXhsaWI9cmItNC4xLjEmYXI9MSUzQTEmZml0PWNyb3AmbWFzaz1lbGxpcHNlJmJnPUZGRkZGRiZmbT1wbmczMiZzPTI2OTJiN2VmOTNkNDc1MGUxMTJlZWU2ZTQxYmJkZmQy%26blend-x%3D120%26blend-y%3D467%26blend-w%3D82%26blend-h%3D82%26blend-mode%3Dnormal%26s%3Da179f47212dadfb85e49684e5c637334?ixlib=rb-4.1.1&w=1200&fm=jpg&mark64=aHR0cHM6Ly9xaWl0YS11c2VyLWNvbnRlbnRzLmltZ2l4Lm5ldC9-dGV4dD9peGxpYj1yYi00LjEuMSZ3PTk2MCZoPTMyNCZ0eHQ9R2V0dGluZyUyMFN0YXJ0ZWQlMjB3aXRoJTIwM0QlMjBHYXVzc2lhbiUyMFNwbGF0dGluZyUyMGZyb20lMjAzNjAlQzIlQjAlMjBJbWFnZXMlMjAlMjgzNjAlQzIlQjAlMjBHYXVzc2lhbiUyMFBybyUyMEVkaXRpb24lMjkmdHh0LWFsaWduPWxlZnQlMkN0b3AmdHh0LWNvbG9yPSUyMzFFMjEyMSZ0eHQtZm9udD1IaXJhZ2lubyUyMFNhbnMlMjBXNiZ0eHQtc2l6ZT01NiZ0eHQtcGFkPTAmcz1hYjVjZjE1NTE3MDBkY2RjMjhiNWI4Zjk5MjBmOGViZA&mark-x=120&mark-y=112&blend64=aHR0cHM6Ly9xaWl0YS11c2VyLWNvbnRlbnRzLmltZ2l4Lm5ldC9-dGV4dD9peGxpYj1yYi00LjEuMSZ3PTgzOCZoPTU4JnR4dD0lNDBUa3NfWW9zaGluYWdhJnR4dC1jb2xvcj0lMjMxRTIxMjEmdHh0LWZvbnQ9SGlyYWdpbm8lMjBTYW5zJTIwVzYmdHh0LXNpemU9MzYmdHh0LXBhZD0wJnM9NWQwMmIwYTAzMzg5YTUyMDM0OTY5MjIyMDk1Yjk0ZTE&blend-x=242&blend-y=480&blend-w=838&blend-h=46&blend-fit=crop&blend-crop=left%2Cbottom&blend-mode=normal&s=b9cc1a0eae2a987e6137581a2d6afd08
title_zh: 从 360° 影像入门 3D Gaussian Splatting（360° Gaussian Pro 版）
tech_domain: other
---

# Getting Started with 3D Gaussian Splatting from 360° Images (360° Gaussian Pro Edition)

## [](https://qiita.com/Tks_Yoshinaga/items/cfc9d6575afd78f12f31#introduction)Introduction

In a previous article, [Getting Started with 360° Image Gaussian Splatting (Basic Workflow)](https://qiita.com/Tks_Yoshinaga/items/354e9082bd607f3cefee), I introduced the workflow for generating 3D Gaussian Splatting (3DGS) from 360° video using **360° Gaussian**.

Since then, the developer of that tool has released a **Pro version that generates 3DGS more easily and much faster** than the original.

 This article is a quick-start guide to using **360° Gaussian Pro**.

* * *

## [](https://qiita.com/Tks_Yoshinaga/items/cfc9d6575afd78f12f31#environment)Environment

### [](https://qiita.com/Tks_Yoshinaga/items/cfc9d6575afd78f12f31#pc-specs)PC Specs

| Item | Spec |
| --- | --- |
| OS | Windows 11 |
| GPU | NVIDIA GeForce RTX 4070 SUPER |
| CPU | AMD Ryzen7 8700G |
| RAM | 32 GB |

### [](https://qiita.com/Tks_Yoshinaga/items/cfc9d6575afd78f12f31#360-camera)360° Camera

*   **Insta360 X4 Air**

 ※ Other manufacturers' cameras such as THETA are also supported. **8K or higher** is recommended.

### [](https://qiita.com/Tks_Yoshinaga/items/cfc9d6575afd78f12f31#software)Software

| Software | Purpose |
| --- | --- |
| [LichtFeld Studio v0.5.3](https://lichtfeld.io/) | GUI tool for 3D Gaussian Splatting ※ |
| [360° Gaussian Pro v1.0.1](https://www.360gaussianpro.com/) | Tool that automates frame extraction, masking, and SfM |

> **※ About obtaining LichtFeld Studio**
> 
>  Free distribution of pre-built binaries for LichtFeld Studio v0.5.x has ended. v0.4.0 remains available for free download. To use v0.5.3, you must either purchase a paid license or build it from source.
> 
>  If you want to try the latest features available on GitHub, or try it before purchasing a license, please refer to the notes below and try building it yourself.
> 
> 
> **Notes for building from source**
> 
> 
> 
> Click to expand
> To build it yourself, follow the [build instructions here](https://github.com/MrNeRF/LichtFeld-Studio/wiki/Build-Instructions-%E2%80%90-Windows).
> 
> **Tip 1**
> 
>  Although not mentioned in the official build instructions, **Perl** may be required. Install it from [Strawberry Perl](https://strawberryperl.com/).
> 
>  Be aware that the cmake bundled with Perl may take precedence over your system cmake, so first temporarily rename `C:\Strawberry\c\bin\cmake.exe`, and delete it only if it turns out to be unnecessary. To be safe, restart your PC afterward.
> 
> **Tip 2**
> 
>  In the official documentation's **Clone repository** section, the following command did not always download all required files correctly in the author's environment:
> 
> `git clone https://github.com/MrNeRF/LichtFeld-Studio`
> 
>  Instead, to avoid missing submodule downloads, it is recommended to add the `--recursive` flag, or use a client tool such as Fork or GitHub Desktop:
> 
> `git clone --recursive https://github.com/MrNeRF/LichtFeld-Studio`
> 
> **Tip 3**
> 
>  Note: **skip** the `git checkout v0.4.0` command in the **Checkout stable version** step.
> 
>  The build process takes a long time, so plan to run it when you have plenty of time available.

* * *

## [](https://qiita.com/Tks_Yoshinaga/items/cfc9d6575afd78f12f31#differences-from-the-previous-version)Differences from the Previous Version

The most notable differences are as follows:

*   **Camera alignment now uses the latest COLMAP / GLOMAP**
*   **Wider range of input formats**: in addition to equirectangular images, you can now feed in **dual-fisheye images** and even ordinary (non-360°) video shot on a smartphone
*   **Masking powered by SAM3**
*   **Support for adding detail photos** taken with a smartphone or digital camera
*   **Significant speedup of every processing step**

### [](https://qiita.com/Tks_Yoshinaga/items/cfc9d6575afd78f12f31#who-is-it-for)Who Is It For?

*   **Those who want a simple workflow**: after adding your video, if you are happy with the default settings, you can go **all the way to 3DGS generation with a single button**
*   **Those who want to tune parameters themselves**: the COLMAP alignment parameters are exposed in the UI. This suits anyone who needs to state not just "I aligned it with a tool" but **exactly which parameters were used** — for example, when writing a paper

* * *

## [](https://qiita.com/Tks_Yoshinaga/items/cfc9d6575afd78f12f31#overall-workflow)Overall Workflow

Gaussian Splatting generally involves the following four steps.

| # | Step | Description |
| --- | --- | --- |
| 1 | **Capture** | Record the scene with a 360° camera |
| 2 | **SfM** (Structure from Motion) | Estimate the position from which each image was taken |
| 3 | **Point Cloud Generation** | Generate a point cloud based on the camera positions obtained from SfM |
| 4 | **Gaussian Splatting** | Generate a 3D Gaussian Splatting model from the point cloud |

* * *

## [](https://qiita.com/Tks_Yoshinaga/items/cfc9d6575afd78f12f31#step-1-capturing--exporting-the-video)Step 1. Capturing & Exporting the Video

Record your scene with a 360° camera. Since processing can take a long time, I recommend testing with a **short clip under one minute** until you get used to the workflow.

As mentioned above, equirectangular images still work just as they did in the previous version, but since we have the option, let's use **dual-fisheye** this time.

 If you would rather try equirectangular, see [Step 1 of the previous article (Basic Workflow)](https://qiita.com/Tks_Yoshinaga/items/354e9082bd607f3cefee#step-1-capturing--exporting-the-video) for the Insta360 Studio export procedure and the stabilization settings.

If you are using an Insta360 camera:

1. Connect the Insta360 to your PC with a USB cable

 2. Copy the **`.insv` file** you want to process to your PC

**That's it.** Not having to convert to equirectangular makes this nice and simple.

* * *

## [](https://qiita.com/Tks_Yoshinaga/items/cfc9d6575afd78f12f31#step-2-sfm-and-point-cloud-generation)Step 2. SfM and Point Cloud Generation

This is where **360° Gaussian Pro** comes in.

In the previous version you had to choose your own SfM tool, such as SphereSfM or Metashape. This tool **standardizes on COLMAP**, so no additional applications need to be installed.

The steps are also covered in detail in the following video:

*   📺 [How to use 360° Gaussian Pro](https://www.youtube.com/watch?v=njYAUpHk_VI)

### [](https://qiita.com/Tks_Yoshinaga/items/cfc9d6575afd78f12f31#21-image-extraction)2.1 Image Extraction

1. Launch **360° Gaussian Pro**

 2. Drag and drop your `.insv` file onto **Add footage to start**

 ※ If you are testing with equirectangular or ordinary video files, drag and drop an `.mp4` instead

[![Image 1: add-image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F61742%2F858c86ae-3ac2-48df-80d7-be63b2623faa.png?ixlib=rb-4.1.1&auto=format&gif-q=60&q=75&s=8525bbaacb61d6d3a21e077a97340e28)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F61742%2F858c86ae-3ac2-48df-80d7-be63b2623faa.png?ixlib=rb-4.1.1&auto=format&gif-q=60&q=75&s=8525bbaacb61d6d3a21e077a97340e28)

3. Configure the extraction settings

The defaults are fine to start with, but **Frame Extraction** offers the following options:

| Parameter | Description |
| --- | --- |
| **Extract frame every** | Extracts images at the specified interval, in seconds (or frames) |
| **Pick sharpest frame per interval** / **window** | Toggles whether to prefer the least blurry image by comparing neighboring frames, and sets the comparison range. With `10`, for example, it compares 5 frames on either side and picks the sharpest one |
| **Pinhole Split** | How many pinhole tiles the fisheye image is reprojected into. `1 split` is the fastest but covers only about half of the fisheye, `5 splits` (default) covers the full sphere with overlapping tiles, and `9 Splits` gives the most overlap between tiles for complex scenes |

For details, see the [official documentation](https://www.360gaussianpro.com/docs/extraction/).

> **ℹ️ For equirectangular input**
> 
>  Equirectangular input does not use **Pinhole Split**; it is always converted into **6 cube-map faces**.

4. **(Optional)** These steps make the masking setup in the next section easier

 4.1 Click on the video timeline to select the frame you want to use for previewing the mask

 4.2 Click **Extract one frame**

### [](https://qiita.com/Tks_Yoshinaga/items/cfc9d6575afd78f12f31#22-image-masking)2.2 Image Masking

This feature automatically masks out regions that are not needed for Gaussian Splatting.

1. Click the **Masking** tab

 2. If you clicked **Extract one frame** in the previous section, the image will be displayed

[![Image 2: masking1.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F61742%2Fd2ff8abb-2b4b-4a5c-b1c6-c1bbeb56d869.png?ixlib=rb-4.1.1&auto=format&gif-q=60&q=75&s=731db368a4bc26d7a6568cb1fb43b025)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F61742%2Fd2ff8abb-2b4b-4a5c-b1c6-c1bbeb56d869.png?ixlib=rb-4.1.1&auto=format&gif-q=60&q=75&s=731db368a4bc26d7a6568cb1fb43b025)

> **ℹ️ If you did not click Extract one frame**
> 
>  No image will be shown, but masking itself still works correctly.

3. **Keyword SAM3** lets you mask by keyword (specify multiple keywords **separated by commas**)

 4. Click **Detect this frame** to preview the result after a few seconds (feel free to skip this if you don't need a preview)

Below is the result when specifying `person,sky`. You can see that people and the sky are masked (shown in pink).

[![Image 3: masking2.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F61742%2Fb2ac362b-5a5e-4bb6-9d1b-7577fa727af3.png?ixlib=rb-4.1.1&auto=format&gif-q=60&q=75&s=301347bdbecc244fc6dd502ab65a67d6)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F61742%2Fb2ac362b-5a5e-4bb6-9d1b-7577fa727af3.png?ixlib=rb-4.1.1&auto=format&gif-q=60&q=75&s=301347bdbecc244fc6dd502ab65a67d6)

5. **Paintbrush** lets you trace over objects you want to exclude with the mouse (OK to skip)

 6. **Circle Mask** (dual-fisheye only) masks the area outside the camera's image circle. You can also reduce the radius to narrow down the region used for processing

> **💡 Two reasons masking matters**
> 
>  First, moving subjects such as people and cars, and low-texture objects with few feature points, tend to become **noise for SfM** and reduce the accuracy of camera pose estimation. Since SfM accuracy directly affects the quality of the resulting Gaussian Splatting, excluding these with masks is important.
> 
>  Second, **the same noise degrades quality during training as well**. When the same subject appears differently depending on where it was shot, the Gaussians struggle to converge on the correct shape and color. Masking protects quality in both stages.

### [](https://qiita.com/Tks_Yoshinaga/items/cfc9d6575afd78f12f31#23-sfm-configuration)2.3 SfM Configuration

Here too, the defaults are fine to start with.

[![Image 4: alignment.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F61742%2Ff1e4e5a3-532b-43d0-ba1a-0228474aec27.png?ixlib=rb-4.1.1&auto=format&gif-q=60&q=75&s=3af6842e8d3112a27c9340faca284818)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F61742%2Ff1e4e5a3-532b-43d0-ba1a-0228474aec27.png?ixlib=rb-4.1.1&auto=format&gif-q=60&q=75&s=3af6842e8d3112a27c9340faca284818)

For reference, **Matcher** lets you choose the matching method.

| Matcher | Description |
| --- | --- |
| **Sequential** | Compares each frame only with its neighbors in capture order. Fast, and usually the best choice for video input where consecutive frames overlap |
| **Exhaustive** | Compares every image against every other. The most robust and highest quality for unordered photo sets, but the slowest, since the pair count grows with the square of the image count |
| **Spatial** | Uses GPS to compare only images that were physically close. Fast and high quality when the footage has reliable GPS, and it also scales the result to real-world size (still experimental with `.osv` files) |

The remaining options are as follows:

| Setting | Description and benefit |
| --- | --- |
| **GLOMAP global mapper** | Instead of registering frames one at a time, it **solves all camera positions at once**. **10–100× faster**, and enabled by default. |
| **Geometry Timeline Check** | Experimental. Detects and auto-repairs cases where similar-looking but different locations (identical room interiors, a stairwell walked up and back down, etc.) are mistaken for the same place, causing **the model to fold onto itself**. It applies the rule that **frames far apart in time should not be at the same location**. Processing time increases by a few minutes only when a fold is actually detected |
| **Reuse Fisheye features** | Reuses the features detected in Stage 1 instead of detecting new ones on the pinhole tiles. **The pinhole stage becomes faster and needs only about 1 GB of VRAM** (versus the usual 4–8 GB). However, fine details come out slightly softer and some may be missing |

Here is a quick note on the other items visible in the screenshot:

*   **Overlap**: for Sequential, how many neighboring frames on either side to compare
*   **Loop detection**: toggles the processing that detects returning to the same place and closes the loop
*   **Lens priors**: initial lens parameters. `Auto (recommended)` is fine
*   **Preset quality**: quality preset. Use `Save...` to store your own settings under a name

Opening **Advanced settings** exposes a wide range of COLMAP options as well (for example, the maximum number of SIFT features defaults to 32,768 for fisheye and 8,192 for pinhole tiles).

For details, see the [official documentation](https://www.360gaussianpro.com/docs/alignment/).

### [](https://qiita.com/Tks_Yoshinaga/items/cfc9d6575afd78f12f31#24-adding-detail-photos-optional)2.4 Adding Detail Photos (Optional)

The Pro version lets you mix in **high-resolution photos taken with a smartphone or DSLR**, not just 360° images.

 This makes it possible to reproduce **text and illustrations** in the scene, details that 360° photos tend to lose.

To add them, just use **Detail photos** → **Add detail photos...** on the right side of the screen and select the folder containing your detail images.

[![Image 5: additional-photo.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F61742%2F17ee58c1-3997-4ace-a545-6a5866c749bb.png?ixlib=rb-4.1.1&auto=format&gif-q=60&q=75&s=60380c8de0a155f6f0f6a5eeda94f746)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F61742%2F17ee58c1-3997-4ace-a545-6a5866c749bb.png?ixlib=rb-4.1.1&auto=format&gif-q=60&q=75&s=60380c8de0a155f6f0f6a5eeda94f746)

> **⚠️ Note**
> 
>  The detail images go through SfM as well, so **provide photos from multiple viewpoints** to make estimation easier. In the example above, the information board was shot 14 times, changing the angle slightly each time.

### [](https://qiita.com/Tks_Yoshinaga/items/cfc9d6575afd78f12f31#25-choosing-the-3d-gaussian-splatting-training-tool)2.5 Choosing the 3D Gaussian Splatting Training Tool

Click the **Train** tab.

The Pro version supports **LichtFeld Studio**, **Postshot**, and **Brush**.

 If you want training automated as well, install one of them and configure it accordingly. The executable path, Iterations, Strategy, Max Splats, and other options can all be set from this screen.

I usually want to watch the 3DGS training process, so I select **No Train**.

[![Image 6: train.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F61742%2F783be057-b742-4041-9e01-cb481e368be9.png?ixlib=rb-4.1.1&auto=format&gif-q=60&q=75&s=6c4d6789d13cf8da07d927f8c7af441f)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F61742%2F783be057-b742-4041-9e01-cb481e368be9.png?ixlib=rb-4.1.1&auto=format&gif-q=60&q=75&s=6c4d6789d13cf8da07d927f8c7af441f)

### [](https://qiita.com/Tks_Yoshinaga/items/cfc9d6575afd78f12f31#26-running-the-pipeline)2.6 Running the Pipeline

Once everything is set up, click **Run Pipeline** at the bottom of the screen.

 Progress is displayed at the bottom as well, so just wait until it finishes.

[![Image 7: progress.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F61742%2F525e858d-ffa2-44dc-948a-6ea24d72a9cd.png?ixlib=rb-4.1.1&auto=format&gif-q=60&q=75&s=a537d1039a543a42aec8dd951c954935)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F61742%2F525e858d-ffa2-44dc-948a-6ea24d72a9cd.png?ixlib=rb-4.1.1&auto=format&gif-q=60&q=75&s=a537d1039a543a42aec8dd951c954935)

> **⚠️ If processing appears stuck for a long time**
> 
>  Click the **Log** button at the bottom left of the screen to check the log.

When it finishes, open the **Alignment** tab to review the result. The output is saved to **`0_train_data`**.

[![Image 8: alignment-result.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F61742%2Ff77ad714-2660-4a3f-ac6f-48bc2f6b2e2e.png?ixlib=rb-4.1.1&auto=format&gif-q=60&q=75&s=caea9c29e2e8d67068d3dcf86348d88b)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F61742%2Ff77ad714-2660-4a3f-ac6f-48bc2f6b2e2e.png?ixlib=rb-4.1.1&auto=format&gif-q=60&q=75&s=caea9c29e2e8d67068d3dcf86348d88b)

If the result isn't what you expected at this point, you can change the settings and run alignment again.

 If the result is tilted or offset, you can adjust it by dragging the **Rotate** / **Translate** parameters (X, Y, Z) with the mouse (**Align ground** can also snap it to the ground plane).

 Finally, click **Apply edits** to write the changes into the output files.

> **ℹ️ Either tool can adjust position and orientation**
> 
>  LichtFeld Studio can also change position and orientation, so use whichever you find more convenient.

Note that the **cameras shown in red** in the screenshot above are the detail photos added in 2.4. You can see them clustered around the information board.

* * *

## [](https://qiita.com/Tks_Yoshinaga/items/cfc9d6575afd78f12f31#step-3-gaussian-splatting)Step 3. Gaussian Splatting

### [](https://qiita.com/Tks_Yoshinaga/items/cfc9d6575afd78f12f31#31-loading-data)3.1 Loading Data

1. Launch **LichtFeld Studio**

 2. Drag and drop the **`0_train_data`** folder generated above onto the window

 3. When the **Load Dataset** dialog appears, click **Load**

[![Image 9: lfs.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F61742%2F01f8f026-371f-4258-8508-65aa32a62a11.png?ixlib=rb-4.1.1&auto=format&gif-q=60&q=75&s=729f72c3a9ca5a9a62e672800d404f0f)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F61742%2F01f8f026-371f-4258-8508-65aa32a62a11.png?ixlib=rb-4.1.1&auto=format&gif-q=60&q=75&s=729f72c3a9ca5a9a62e672800d404f0f)

[![Image 10: lfs2.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F61742%2F71d701b2-78a3-46eb-b2ec-29d62b3c0d12.png?ixlib=rb-4.1.1&auto=format&gif-q=60&q=75&s=44fe8d4148e4a9b6d92bfd966963da02)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F61742%2F71d701b2-78a3-46eb-b2ec-29d62b3c0d12.png?ixlib=rb-4.1.1&auto=format&gif-q=60&q=75&s=44fe8d4148e4a9b6d92bfd966963da02)

Confirm that the point cloud and images loaded correctly.

 If you don't need the camera images displayed, uncheck **Camera Frustums** in the **Rendering** tab on the right side of the screen.

[![Image 11: lfs3.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F61742%2F18fbaced-e518-4cbf-aebb-3423906bc5bf.png?ixlib=rb-4.1.1&auto=format&gif-q=60&q=75&s=747befaf2d809fc0fec76aff31e17d97)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F61742%2F18fbaced-e518-4cbf-aebb-3423906bc5bf.png?ixlib=rb-4.1.1&auto=format&gif-q=60&q=75&s=747befaf2d809fc0fec76aff31e17d97)

### [](https://qiita.com/Tks_Yoshinaga/items/cfc9d6575afd78f12f31#32-training-configuration)3.2 Training Configuration

Here is one example of a training configuration. Once you're comfortable, try experimenting with other settings.

1. Click the **Training** tab

 2. Select `MRNF` for **Strategy**

 3. Set **Steps Scaler** as appropriate

| Condition | Recommended value |
| --- | --- |
| 300 images or fewer | `1` |
| More than 300 images | `number of images / 300` |

> **⚠️ If training doesn't go well**
> 
>  If training fails to converge and the view whites out even with the settings above, setting Steps Scaler to **2–3×** the `number of images / 300` value tends to stabilize it.

4. Set the maximum number of Gaussians with **Max Gaussians**

 The default is a little high, so depending on the size of your scan area, starting around **1,500,000** and seeing how it goes is a good approach. Increase the value if you feel detail is lacking.

**Optional setting 1:**

 If you want to use mask images, configure the following:

*   Set **Mask Mode** to `Ignore`
*   Uncheck **Alpha Mask**

**Optional setting 2:**

 If you added detail photos, turn on **Undistort**.

[![Image 12: lfs4.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F61742%2Fe33a0698-acfb-41ab-b0c9-4e84f280bc42.png?ixlib=rb-4.1.1&auto=format&gif-q=60&q=75&s=5e726e953c926f0c3eb200074b5c147c)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F61742%2Fe33a0698-acfb-41ab-b0c9-4e84f280bc42.png?ixlib=rb-4.1.1&auto=format&gif-q=60&q=75&s=5e726e953c926f0c3eb200074b5c147c)

For the other parameters, start with the settings above and experiment once you're more familiar with the tool.

### [](https://qiita.com/Tks_Yoshinaga/items/cfc9d6575afd78f12f31#33-running-training)3.3 Running Training

1. Use the mouse to zoom in on the area where you want to watch training progress

 (in my case, around the object in the center)

 2. Click **Start Training** to begin

 3. The view starts out blurry and gradually becomes clearer as the steps progress

[![Image 13: lfs5.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F61742%2F60748314-8dda-4250-a50d-2903c18ad144.png?ixlib=rb-4.1.1&auto=format&gif-q=60&q=75&s=6734027887b80ed62510163e30797f58)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F61742%2F60748314-8dda-4250-a50d-2903c18ad144.png?ixlib=rb-4.1.1&auto=format&gif-q=60&q=75&s=6734027887b80ed62510163e30797f58)

Training ends automatically once it reaches the step limit.

 If you want to save an intermediate result, click **Save Checkpoint** to record the state at that point.

### [](https://qiita.com/Tks_Yoshinaga/items/cfc9d6575afd78f12f31#34-export)3.4 Export

The output data can be used with tools such as [SuperSplat Editor](https://superspl.at/editor) for creating videos or viewing in a viewer.

1. Click **File → Export**

 2. Select the output format (e.g. `.ply`)

* * *

## [](https://qiita.com/Tks_Yoshinaga/items/cfc9d6575afd78f12f31#summary)Summary

I had been using the original free version until now, but with the Pro version **SfM accuracy has improved, and as a result the quality of the 3DGS output has improved too**.

**Masking accuracy has also improved.** Every step runs faster as well, so there is less waiting around.

This article covered the dual-fisheye workflow, but the flow is the same for equirectangular.

 In my test environment, **equirectangular was actually faster to process**. I also personally preferred the results from the equirectangular images. Since this varies by scene and by taste, why not try both and find the flow that suits you?

The Pro version costs **149 EUR**. It isn't free, but that is roughly the same price bracket as Metashape, a long-standing standard in this space.

 Given that frame extraction, masking, and SfM can all be run with a single click without switching between applications, I think the convenience makes it well worth considering. If you're interested, please give it a try.

> **📝 About questions**
> 
>  I recommend the official Discord for questions, but feel free to ask me directly about minor things.

### [](https://qiita.com/Tks_Yoshinaga/items/cfc9d6575afd78f12f31#sample-outputs-with--without-detail-photos)Sample Outputs (with / without detail photos)

For reference, here are the outputs with and without detail photos.

*   [With detail photos](https://superspl.at/scene/93b5d306)
*   [Without detail photos](https://superspl.at/scene/ea533b5f)

<!-- media:youtube id="njYAUpHk_VI" url="https://www.youtube.com/watch?v=njYAUpHk_VI" -->
