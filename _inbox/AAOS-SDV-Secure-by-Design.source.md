---
source_url: https://android-developers.googleblog.com/2026/08/aaos-sdv-secure-by-design.html
fetched_at: 2026-08-25T11:36:21Z
fetch_method: jina
issue: 97
cover_image: https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEh5wMRO7HwquRHIzH0qLwRDKkYVq-nIB4DwG5R2mLK3R3p1lo9nAVblduqSjSFc7rC3xo0bFBXB9iiTv662Bs4y7Ex_35labdsyXi9rM6FNWECqz19Nl7UrI5pO28Un6GBeInO2-yEJeNx0v3thcG5QWWTrCFQvvAIaYB60GEumMmHulA3mmYTtDL68isQ/s2048/Android-1-Meta.jpg
title_zh: AAOS 与 SDV：默认安全设计
tech_domain: security
---

# AAOS SDV - Secure by Design

_Posted by Markus Vill, Software Engineer, Sean Keys, Security Engineer, and Istvan Nador, Software Engineer, Android Auto_

[

![](https://www.gstatic.com/images/icons/material/system/2x/news_grey600_24dp.png)

![](https://www.gstatic.com/images/icons/material/system/1x/rss_feed_grey600_24dp.png)

![Google Play Site](https://developer.android.com/static/images/logos/google-play.svg)

![hero android logo](https://developer.android.com/static/images/logos/android.svg)

<!-- media:svg src="https://developer.android.com/static/images/logos/google-play.svg" -->

<!-- media:svg src="https://developer.android.com/static/images/logos/android.svg" -->

![Image 1](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgKJVr7S37jvQ8V8UUzRD7mv7llfrTAKcLx7MnEZGB-jUOdhHqLl1-82xTmhFQzVE6XEyUCMWZb2KM9tjthzS1NQMzAMaiXtaK7SYfXTmghcttgCoDcJMLFTcZx6BiE7fWevJZdde_jENeuhz6LLciWSqzhruVCllLP-7pU4yBjj8fzdOXMEUl-D1lok9Q/s1600/Android-1-Blog.jpg)](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgKJVr7S37jvQ8V8UUzRD7mv7llfrTAKcLx7MnEZGB-jUOdhHqLl1-82xTmhFQzVE6XEyUCMWZb2KM9tjthzS1NQMzAMaiXtaK7SYfXTmghcttgCoDcJMLFTcZx6BiE7fWevJZdde_jENeuhz6LLciWSqzhruVCllLP-7pU4yBjj8fzdOXMEUl-D1lok9Q/s4209/Android-1-Blog.jpg)

At Google, we believe our products should be secure by design, which is why we built the Android Automotive Operating System for Software Defined Vehicle (AAOS SDV) on existing, [market-proven platforms](https://source.android.com/docs/automotive/sdv/workstreams/hardware/sdv-on-qnx), leveraging virtualization technologies like [Cuttlefish](https://source.android.com/docs/devices/cuttlefish). While our [release announcements](https://blog.google/products-and-platforms/platforms/android/android-automotive-os/) focused on the features, this blog post outlines some of the security concepts.

### Foundation: Domain Isolation

### Virtualization to isolate co-hosted instances

The current trend of consolidating Electronic Control Units (ECUs) into a single chip reduces isolation by running multiple domains side-by-side.

While AAOS SDV instances provide internal isolation mechanisms, it is often preferable to run logical domains independently. For instance, a cluster and an infotainment system have distinct requirements. We use virtual machines to run multiple instances in parallel, ensuring that sharing remains explicit and isolation is the default behavior.

### Inherited Android Security

AAOS SDV evolved from [Microdroid](https://source.android.com/docs/core/virtualization/microdroid), a minimalistic Android version optimized for privacy virtual machines (pVM). This lineage provides Android platform engineers with established security features they already know.

### Process Isolation & Deny by Default

AAOS SDV follows Android’s User ID (UID)-based isolation model to set up a sandbox for each application. Each service runs in a dedicated process with a unique UID to manage access rights, data directories, and other restrictions. We employ Portable Operating System Interface (POSIX) capabilities to strictly limit operations and pair this with Security-Enhanced Linux (SELinux) to enforce a "deny-by-default" posture. This approach restricts each service to the absolute minimum required, meaning missing configurations block access rather than creating an over-permissive system. We apply this same strategy to our [communication permission system](https://docs.google.com/document/d/1_q-l1FyhNgYZWMYg5BlCbp165oCzs1_wPRdQaO-9DGE/edit?resourcekey=0-1ed5JHEP0tz16QD0v0xUBQ&tab=t.0#heading=h.a39ozyiarfpb), as explained later in this article.

### Proven Vulnerability Management

AAOS SDV integrates Android’s mature security response and vulnerability management infrastructure to identify, triage, remediate, and disclose security findings. This lifecycle incorporates continuous automated scanning, annual deep-dive penetration testing, and partner-driven intelligence via the [Android security vulnerability reporting process](https://source.android.com/docs/security/overview/updates-resources). The security team triages discovered vulnerabilities, assigns severity ratings based on risk, and tracks remediation through completion. We coordinate disclosure and release policies through the monthly [Android Security Bulletins](https://source.android.com/docs/security/bulletin), supplemented by rigorous periodic security audits and comprehensive architectural reviews to ensure long-term platform resilience.

## Integrity: Secure Software Delivery

Beyond guaranteeing process isolation, a secure platform must ensure code integrity before execution. We secure software delivery through the following approaches:

### Authenticated Software Delivery

AAOS SDV provides two installation methods. First, we install software directly to read-only system, product, or vendor partitions, which validate signatures on every boot. This secures basic system components.

Second, we utilize Android Pony EXpress ([APEX](https://source.android.com/docs/core/ota/apex)) packages for services. Each APEX encapsulates software and its dependencies, treating the package as a partition with mandatory signature validation. In AAOS SDV, APEX treats code signing as a continuous, hardware-enforced contract. APEX ensures malicious code execution is mitigated through four core pillars:

#### 1. Immutable Storage

*   **The Mechanism:**The Android kernel loops the `apex_payload.img` file directly as a raw storage device using the **read-only loopback**, mounting it with the strict `MS_RDONLY` flag.
*   **Why it's more secure:**This exposes no write path to the OS because the files are not unpacked onto the vehicle's storage. Even if an attacker gains `root` privileges, they cannot modify the running APEX code because the file system layer rejects all write commands.

#### 2. Cryptographic Integrity

*   **The Mechanism:**The cryptographic signature validates a [Merkle Tree](https://en.wikipedia.org/wiki/Merkle_tree) of the entire file system image.
*   **Why it's more secure:** The kernel uses per-block `dm-verity` to verify the signature for every 4KB data block on-the-fly. If an attacker modifies a raw block on the flash memory, the kernel detects the hash mismatch and halts execution immediately.

#### 3. Strict Isolation

*   **The Mechanism:**This applies the process isolation rules as described in the [Process Isolation section](https://docs.google.com/document/d/1_q-l1FyhNgYZWMYg5BlCbp165oCzs1_wPRdQaO-9DGE/edit?resourcekey=0-1ed5JHEP0tz16QD0v0xUBQ&tab=t.0#heading=h.yy1a1k1zo4rf) to create a sandbox, with the APEX mounted as a dedicated partition under `/apex`.
*   **Why it's more secure:** Each service receives its own user and data directory, restricting access unless sharing is explicit. By creating a dedicated partition, Android establishes a dedicated linker namespace, ensuring only explicitly exposed libraries are accessible from non-privileged system daemons, thus minimizing the attack surface.

#### 4. Atomic Recovery

*   **The Mechanism:**APEX uses an "Active/Backup" design to enable **double-buffered rollbacks**. The factory-flashed APEX remains on the immutable `/system` partition, while updates reside on the mutable `/data` partition.
*   **Why it's more secure:** If an update fails or appears malicious, the `apexd` daemon marks it as "failed" during early boot. The system instantly swaps symbolic links back to the `/system` partition. This atomic recovery helps ensure the system does not remain in a broken state.

## Resilience: Memory-Safe Development

Verified loading protects the system from external modification, but platform resilience also depends on how the underlying code is built. For new components developed for AAOS SDV, we prioritized memory safety.

### Rust as the primary language

AAOS SDV targets small systems with fast availability requirements; this prevents building on the full Android stack, so we limited our scope to the native framework. To create the required infrastructure for a distributed system, we developed multiple components in addition to existing infrastructure and adopted Rust as the primary language. We also use Rust to develop the business logic of services, helping partners write secure software. By design, [Rust leverages memory safety features to help prevent common classes of memory safety vulnerabilities, while supporting team throughput when writing native code](https://blog.google/security/rust-in-android-move-fast-fix-things/).

## Distributed Trust: Network & Access Control

Software-defined vehicles require secure interactions between isolated domains. The AAOS SDV mesh provisioning architecture addresses this complexity by cryptographically verifying the version and author of every communication endpoint.

### Device and Mesh Provisioning

The AAOS SDV Mesh establishes authentication by [mathematically binding the network identity of every component](https://source.android.com/docs/automotive/sdv/workstreams/core/vm-attestation/dice-profile) to its **actual binary execution state**. This model replaces implicit software trust with hardware-rooted verification.

Mesh authentication is designed to be continuous and cryptographic. This prevents scenarios where, for example, a service like a vehicle gateway trusts a compromised infotainment VM just because it has the right IP address.

Hardware-enforced isolation and automated quarantine protocols secure the platform. Peer devices within the SDV mesh use DICE-based authentication and attestation, as detailed in the following section, to help identify and contain unauthorized code execution or configuration tampering.

### DICE-based TLS to secure VM-to-VM communication

#### Grounding the Host Identity in Reality

**The Golden Rule of DICE (Device Identifier Composition Engine)**: If a single line of code in the firmware changes (even a minor update or a malicious exploit), the derived Compound Device Identifier (CDI) changes entirely, generating a completely different Alias Key.

**DICE**and **TLS (Transport Layer Security)**integrate to solve the fundamental challenge of zero-trust architecture: authenticating a machine while simultaneously verifying its software integrity.

The combination of DICE’s hardware-backed identification and TLS’s encrypted handshake allows a receiving machine to verify both the caller's identity and its exact software state.

Traditional certificates only prove possession of a secret; they cannot detect firmware tampering. DICE addresses this via measured boot layering:

*   **The Unique Device Secret (UDS)**: A random cryptographic secret generated during manufacturing. Only the first-stage bootloader can access the UDS; it remains inaccessible to all other software and external interfaces.
*   **Layered Measurements (The Compound Device Identifier)**: The hardware ROM initiates the chain by hashing the UDS with the exact code and configuration of the next firmware layer. This creates a CDI, which then chains sequentially as each subsequent layer boots.

Strict access controls govern service interactions within the AAOS SDV mesh. Just like all AAOS SDV software, these access controls are authenticated, and their integrity is protected at the device level and across devices in the mesh through the DICE-based authentication.

### Layered Access Control

AAOS SDV employs a defense-in-depth strategy to enable dynamic vehicle updates without compromising access mechanisms. This model relies on two primary trust layers:

*   **Service-level permissions**: Define the specific resources a service on a given VM can access or expose across the mesh.
*   **VM-level permissions**: Define the cross-VM communication boundaries for all services hosted on a specific VM.

This model allows OEMs to balance security with updatability. For non-security-sensitive services, permissive VM-level policies enable installation via lightweight APEX updates rather than full VM redeployments.

Conversely, permissions for security-sensitive signals must be hard-coded into every VM. The tradeoff is that introducing a security-sensitive service to a new VM requires updating the VM-level permissions system-wide. This necessitates an update to all VMs within the mesh.

[![Image 2](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgeUW8vWGonJma4AmCmiFS2k7ECKwN1jL8H-eYRHqmmSZ8OEtPE-G6YVK31df5bEyRUxDHNv3JR7S0YJQ1bBNl96WnHi42mxeY5nd1QjSgTaCWZ3-coH9V4Pb4lZC6auZcRZhsAuKvi_xGsPXLEWv8lw0o_3wODGe33VcHQMHfR3Ox8edRxHDwaP12uBnA/s1600/Android-2-Blog.jpg)](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgeUW8vWGonJma4AmCmiFS2k7ECKwN1jL8H-eYRHqmmSZ8OEtPE-G6YVK31df5bEyRUxDHNv3JR7S0YJQ1bBNl96WnHi42mxeY5nd1QjSgTaCWZ3-coH9V4Pb4lZC6auZcRZhsAuKvi_xGsPXLEWv8lw0o_3wODGe33VcHQMHfR3Ox8edRxHDwaP12uBnA/s4209/Android-2-Blog.jpg)

## Conclusion

AAOS SDV extends Android’s security architecture to address specific automotive requirements through a secure-by-design approach. By leveraging virtualization for domain isolation and enforcing "deny-by-default" access policies, the platform establishes a resilient environment for software-defined vehicles. Cryptographic integrity is maintained via hardware-enforced, on-the-fly verification of executed code.

The platform integrates continuous security lifecycles, ranging from proactive vulnerability management to hardware-rooted identity verification via DICE. These multi-layered defenses allow OEMs to balance advanced feature updatability with the robust security necessary for modern automotive environments. Technical specifications and implementation details are available on the [AAOS SDV Overview page](https://source.android.com/docs/automotive/sdv).

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

![](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEh5wMRO7HwquRHIzH0qLwRDKkYVq-nIB4DwG5R2mLK3R3p1lo9nAVblduqSjSFc7rC3xo0bFBXB9iiTv662Bs4y7Ex_35labdsyXi9rM6FNWECqz19Nl7UrI5pO28Un6GBeInO2-yEJeNx0v3thcG5QWWTrCFQvvAIaYB60GEumMmHulA3mmYTtDL68isQ/s2048/Android-1-Meta.jpg)
