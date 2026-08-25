---
source_url: https://capytoolkit.com/blog/security-privacy/post-quantum-tls-certificate-inspector-can-and-cannot-tell-you/
fetched_at: 2026-08-25T05:17:32Z
fetch_method: jina
issue: 78
cover_image: https://cdn.capytoolkit.com/img/2026/08/post-quantum-tls-certificate-inspector-can-and-cannot-tell-you.jpg
title_zh: 后量子 TLS 证书检查器能告诉你什么、不能告诉你什么
tech_domain: frontend
---

# Post-Quantum TLS in 2026: What a Certificate Inspector Can and Cannot Tell You Yet

The headlines say half the web is already quantum-ready. Then you click the padlock on your own site, export the certificate, squint at every field, and find nothing that mentions quantum anything. Meanwhile a vendor has emailed you twice this month offering a post-quantum migration package priced like an emergency. Nothing adds up, and the confusion gets expensive in both directions: you either panic-buy a migration nobody can sell you yet, or dismiss the whole subject while an adversary quietly records your traffic for later.

Here is the honest picture. One layer of TLS took its post-quantum upgrade years ago, quietly, and there are decent odds your server negotiated it the last time you loaded a page. The other layer has not moved at all. Certificates still carry classical signatures, and no tool can change that. This post separates the two layers, shows what a certificate can actually reveal about readiness in 2026, and hands you a five-minute audit to run on your own domains before you spend anything on migration advice.

## Why Your Padlock Looks the Same While Everything Underneath Changed

Across 32,011 measured domains, a June 2026 study found 49.3% completing TLS handshakes with a hybrid post-quantum key exchange built on `ML-KEM-768` and `X25519`, and essentially zero publicly trusted leaf certificates carrying a post-quantum signature.[1](https://capytoolkit.com/blog/security-privacy/post-quantum-tls-certificate-inspector-can-and-cannot-tell-you/#user-content-fn-1) Both numbers are true. They describe the same sites at the same moment, and most dashboards flatten them into one misleading word: ready.

The encryption half moved first because of a threat with a name: harvest-now-decrypt-later. An adversary records your encrypted traffic today, stores it cheaply, and waits for a cryptographically relevant quantum computer to arrive before decrypting.[2](https://capytoolkit.com/blog/security-privacy/post-quantum-tls-certificate-inspector-can-and-cannot-tell-you/#user-content-fn-2) Your session confidentiality therefore carries an expiry date. Forging a certificate signature is a different beast: that attack only works once the machine exists, so authentication can sit tight while standards and issuing policies catch up.

Keeping the two layers separate answers most of the questions you have been asked about quantum readiness lately. It also sets up the practical half of this post, where CapyToolkit’s [certificate inspector parses any PEM or DER chain entirely in your browser](https://capytoolkit.com/tools/security/cert-inspector/) and shows you exactly which layer your site has moved and which it has not.

## Two Different Layers Get Called “Post-Quantum TLS”

Part of the confusion is linguistic. A TLS connection does two jobs: it proves you are talking to the right server, and it builds a secret an eavesdropper cannot derive. Those jobs run on different cryptography, ship through different supply chains, and migrate on completely different schedules. Treating “post-quantum TLS” as one switch is how teams end up holding a padlock that promises more than it delivers.

### Key Exchange vs. Certificates

Key exchange answers the secrecy question. Since 2024, browsers and servers that both support hybrids have been combining `X25519`, a classical elliptic curve exchange, with `ML-KEM-768`, the lattice-based scheme NIST standardized as [`FIPS 203`](https://csrc.nist.gov/pubs/fips/203/final) in August 2024.[3](https://capytoolkit.com/blog/security-privacy/post-quantum-tls-certificate-inspector-can-and-cannot-tell-you/#user-content-fn-3) An attacker would need to break both halves to recover the session secret.[4](https://capytoolkit.com/blog/security-privacy/post-quantum-tls-certificate-inspector-can-and-cannot-tell-you/#user-content-fn-4) The negotiation happens inside the handshake and never touches a certificate field, which is why nothing you inspect in a certificate reflects it.

Certificates answer the identity question. Your server presents a chain of `X.509` certificates; a certificate authority signs the leaf, and browsers verify that signature using classical algorithms such as RSA and ECDSA. Replacing those signatures with ML-DSA requires issuers to offer the keys, root programs to trust them, and the CA/Browser Forum to set a baseline permitting them. As of August 2026, none of those pieces has landed on the public web.[1](https://capytoolkit.com/blog/security-privacy/post-quantum-tls-certificate-inspector-can-and-cannot-tell-you/#user-content-fn-1)

The split comes down to this:

*   Hybrid key exchange protects confidentiality now, against adversaries who record traffic today and decrypt it once quantum hardware matures.
*   Post-quantum certificate signatures protect authenticity later, against forgeries that need an actual quantum computer to succeed.

### Why Key Exchange Moved First

Chrome did the heavy lifting. Version 124 enabled a Kyber-based hybrid group by default in April 2024,[5](https://capytoolkit.com/blog/security-privacy/post-quantum-tls-certificate-inspector-can-and-cannot-tell-you/#user-content-fn-5) and version 131 switched to the standardized `X25519MLKEM768` group that [`RFC 10024` specifies for TLS 1.3](https://www.rfc-editor.org/rfc/rfc10024).[6](https://capytoolkit.com/blog/security-privacy/post-quantum-tls-certificate-inspector-can-and-cannot-tell-you/#user-content-fn-6) Firefox enabled the same group in version 132 and every Chromium-derived browser inherited the behavior automatically.[7](https://capytoolkit.com/blog/security-privacy/post-quantum-tls-certificate-inspector-can-and-cannot-tell-you/#user-content-fn-7) Once clients spoke the language, switching it on at the server collapsed into a CDN dashboard toggle, and large operators flipped it fast; by late October 2025, Cloudflare reported that most human-initiated web traffic was already protected by post-quantum key agreement.[2](https://capytoolkit.com/blog/security-privacy/post-quantum-tls-certificate-inspector-can-and-cannot-tell-you/#user-content-fn-2)

The certificate side has no equivalent fast path. Issuing an ML-DSA-signed leaf to the public requires a trusted root chain, and no major root program contains one. The CA/Browser Forum’s Server Certificate Working Group still lists an Allow ML-DSA ballot as draft with no update as of July 2026, so no baseline permitting ML-DSA in publicly trusted certificates has been merged; even the IETF draft covering ML-DSA in TLS remained an active working group document as of mid 2026.[8](https://capytoolkit.com/blog/security-privacy/post-quantum-tls-certificate-inspector-can-and-cannot-tell-you/#user-content-fn-8) Internal PKI moves faster because you control the roots, which explains why enterprises pilot post-quantum certificates internally while the public web waits. Until baselines change, the public certificate layer stays structurally stuck, and no tool can hurry it along.

## What the Certificate in Front of You Actually Shows

Paste a full chain into the inspector and every certificate renders as its own card: subject, issuer, validity window, SANs, serial, `SHA-256` fingerprint, plus the two fields this discussion turns on, public key algorithm and signature algorithm. Reading those fields correctly is the entire skill. Most quantum-readiness confusion dies the moment you can tell the two apart and know which one would move first.

### The Key Algorithm Field

On a typical production site in August 2026, the leaf card reads `RSA 2048` or `ECDSA P-256` with a `SHA-256` signature, and nothing exotic appears anywhere in the chain. That is the expected state even when the same site negotiates `X25519MLKEM768` on every connection. Against classical attackers, these keys hold plenty of margin; NIST’s [`SP 800-57` guidance rates `RSA 2048` at roughly 112 bits of security strength and ECDSA P-256 at about 128](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-57pt1r5.pdf), enough headroom for every validity window they will ever serve.[9](https://capytoolkit.com/blog/security-privacy/post-quantum-tls-certificate-inspector-can-and-cannot-tell-you/#user-content-fn-9) If you want the trade-offs side by side, the inspector’s [RSA versus ECDSA comparison lays out certificate size, handshake performance, and strength equivalents](https://capytoolkit.com/tools/security/cert-inspector/reference/#rsa-vs-ecdsa-certificate).

The tool does flag genuinely outdated cryptography loudly: weak keys below `2048-bit RSA` and any `SHA-1` signature earn coloured badges right on the card. A clean card with no badges still tells you nothing about the session’s key exchange, though. Clean does not mean quantum-ready. Those two facts live on different layers, and only one of them appears in this file.

### Signature Algorithm vs. Public Key Type

`SubjectPublicKeyInfo`, the block the inspector presents as the public key, describes what key the subject owns and uses to prove possession. The signature algorithm field describes how the issuer signed the certificate itself. Both are classical today. Both must migrate eventually, and both stay visible on every card from leaf to root, which lets you confirm the whole chain rather than assume anything.

That per-card visibility sounds mundane until you think about migration day. When CAs begin issuing ML-DSA options, the teams who already know which certificates run `RSA 2048`, which run `ECDSA P-256`, and which intermediate signs what will swap everything in an afternoon. Everyone else starts that day by rediscovering their own infrastructure. CapyToolkit’s tool page says it plainly: knowing each certificate’s current algorithm is exactly how you track which ones need replacing. Inventory first. Purchases later, if ever.

## A Five-Minute Audit Routine With the Certificate Inspector

Time to make it operational. Collect the chains for the domains you operate, inspect them locally, and record four facts per chain position. The routine runs on pasted text inside your browser tab, matching the house style of [CapyToolkit’s collection of browser tools that process everything locally](https://capytoolkit.com/); the one exception worth knowing is the optional domain lookup, which transmits only the hostname to a certificate-fetch service and renders the returned chain locally. Your certificate files themselves never travel anywhere.

### Reading the Chain Top to Bottom

1.   Export the full chain from wherever it lives: nginx’s `fullchain.pem`, a cert-manager secret, or `keytool` output.
2.   Paste the PEM text into the inspector or drop the file onto the drop zone; `.pem`, `.crt`, `.cer`, and `.der` files all parse.
3.   Read the cards leaf-first. The leaf starts expanded; intermediates and the root start collapsed.
4.   On every card, note the public key algorithm and size, then the signature algorithm beneath it.
5.   End at a ROOT CERTIFICATE card marked self-signed. If the last card reads INTERMEDIATE CERTIFICATE instead, the chain is incomplete and clients have been quietly papering over the gap.

Format quirks cause most of the friction in step 2. PEM is just DER bytes wrapped in Base64 between header lines, which is why one file happily carries a whole chain; DER is raw binary that usually holds a single certificate. Windows exports hand you `.der` files, appliances emit headerless Base64, and the [guide to PEM versus DER encodings shows how to tell the formats apart and convert between them](https://capytoolkit.com/tools/security/cert-inspector/pem-vs-der-certificate-format/). Completeness follows different rules; the [chain validation guide walks through the `RFC 5280` path checks, ordering included, that a sound chain satisfies](https://capytoolkit.com/tools/security/cert-inspector/certificate-chain-validation/).

What counts as clean in August 2026 is refreshingly boring: no expired or expiring-soon badges, no WEAK KEY or SHA-1 SIGNATURE warnings, a complete chain terminating at a self-signed root, and classical algorithms on every card. That chain is fully healthy by every current requirement and not one bit quantum-ready. Expect that result. Do not fix it.

### Recording What You Find

Write the findings into a plain inventory: one row per chain position, columns for domain, key algorithm, signature algorithm, and expiry date. The spreadsheet looks trivial today and becomes your migration checklist the day your CA offers post-quantum options, because the rows needing replacement will sort themselves. Teams without it spend that future day auditing their own fleet from scratch.

Add one more column while you are there: the `SHA-256` fingerprint from each card, copied straight from the inspector with its copy button. Fingerprints give you change detection for free. A reissued certificate produces a new digest while everything else stays constant, so a changed fingerprint later proves exactly which chain position was touched; practitioners lean on that same property for pinning and audit trails, as the [SHA-256 fingerprint reference explains](https://capytoolkit.com/tools/security/cert-inspector/reference/#sha256-fingerprint).

## What Actually Determines Your Migration Timeline

Your certificate is not the bottleneck. Ballot `SC-081v3`, adopted by the CA/Browser Forum in 2025, compresses maximum certificate lifetimes from 398 days down to 47 by March 2029, and ACME automation already renews most fleets without human involvement.[10](https://capytoolkit.com/blog/security-privacy/post-quantum-tls-certificate-inspector-can-and-cannot-tell-you/#user-content-fn-10) Churn accelerates no matter what quantum does, so the renewal pipeline you build now doubles as the delivery mechanism for whatever swaps the transition eventually demands. Putting [expiry alerts in place before the 47-day floor arrives](https://capytoolkit.com/tools/security/cert-inspector/tls-certificate-expiry-monitoring/) pays off twice: once against outages, once against migration scramble.

In practice, your server stack and your vendors decide key-exchange status, not any roadmap slide. Whether your edge speaks `X25519MLKEM768` depends on a toggle in your CDN or load balancer and on the OpenSSL, Go, or nginx versions sitting underneath; OpenSSL grew native ML-KEM and ML-DSA support in version 3.5, released April 2025, while older stacks need provider plugins.[11](https://capytoolkit.com/blog/security-privacy/post-quantum-tls-certificate-inspector-can-and-cannot-tell-you/#user-content-fn-11) Internal systems march to their own clocks, and enterprise roadmaps routinely target internal mTLS and code signing years before public TLS, because private roots let you deploy without waiting for a forum vote. Strip the noise away and three actions survive:

*   Decline anyone selling post-quantum certificate replacement for public websites today. No CA can issue a publicly trusted PQ leaf, so the pitch is theater.
*   Confirm hybrid key exchange is live on your edge, from your CDN dashboard or a single `openssl s_client` command, because that switch is what protects recorded traffic now.
*   Keep the per-chain algorithm inventory current as automated renewals churn through, so the day PQ issuance lands you execute a checklist instead of commissioning a discovery project.

## Where This Leaves You Before the Next Renewal Cycle

So, the honest summary. On the certificate layer, nothing about your site has gone quantum, because public PKI has not moved. On the handshake layer, roughly half of measured sites already defeat traffic recording, and checking yours takes minutes. Neither fact requires believing anyone’s marketing page, including mine.

Watch two milestones. The first is a CA/Browser Forum baseline permitting ML-DSA in publicly trusted certificates; the second is a major CA actually issuing one. When either lands, your inventory tells you which rows change, and until then your renewals keep automating while the question sits parked exactly where it is today.

One last detail deserves appreciation. Every step ran on text you pasted into a browser tab, so the chains you inspected, the domains you checked, and the inventory you built never touched a server. Nobody correlated your interest in post-quantum readiness with your certificate data, because there was nothing to correlate. Infrastructure reconnaissance stays yours, which is exactly how this kind of audit should work.

Sources

1.   [1.](https://capytoolkit.com/blog/security-privacy/post-quantum-tls-certificate-inspector-can-and-cannot-tell-you/#user-content-fnref-1)
Vanishka Mohan Dubey and Gaurav Varshney, “Measurement Study of Post-Quantum Readiness of Internet: 2026,” arXiv, June 2026. [https://arxiv.org/abs/2606.16473](https://arxiv.org/abs/2606.16473)

2.   [2.](https://capytoolkit.com/blog/security-privacy/post-quantum-tls-certificate-inspector-can-and-cannot-tell-you/#user-content-fnref-2)
Cloudflare, “State of the post-quantum Internet in 2025,” blog.cloudflare.com, October 2025. [https://blog.cloudflare.com/pq-2025/](https://blog.cloudflare.com/pq-2025/)

3.   [3.](https://capytoolkit.com/blog/security-privacy/post-quantum-tls-certificate-inspector-can-and-cannot-tell-you/#user-content-fnref-3)
Wikipedia contributors, “ML-KEM,” en.wikipedia.org, accessed August 2026. [https://en.wikipedia.org/wiki/ML-KEM](https://en.wikipedia.org/wiki/ML-KEM)

4.   [4.](https://capytoolkit.com/blog/security-privacy/post-quantum-tls-certificate-inspector-can-and-cannot-tell-you/#user-content-fnref-4)
D. Stebila, S. Fluhrer, and S. Gueron, “Hybrid key exchange in TLS 1.3,” draft-ietf-tls-hybrid-design-07, IETF, August 2023. [https://www.ietf.org/archive/id/draft-ietf-tls-hybrid-design-07.txt](https://www.ietf.org/archive/id/draft-ietf-tls-hybrid-design-07.txt)

5.   [5.](https://capytoolkit.com/blog/security-privacy/post-quantum-tls-certificate-inspector-can-and-cannot-tell-you/#user-content-fnref-5)
Google Chrome Team, “Chrome 124 release notes,” developer.chrome.com, April 2024. [https://developer.chrome.com/release-notes/124](https://developer.chrome.com/release-notes/124)

6.   [6.](https://capytoolkit.com/blog/security-privacy/post-quantum-tls-certificate-inspector-can-and-cannot-tell-you/#user-content-fnref-6)
K. Kwiatkowski, P. Kampanakis, B. E. Westerbaan, and D. Stebila, “Post-Quantum Traditional (PQ/T) Hybrid Key Agreement Mechanisms for TLS 1.3,” RFC 10024, IETF, 2026. [https://www.rfc-editor.org/info/rfc10024](https://www.rfc-editor.org/info/rfc10024)

7.   [7.](https://capytoolkit.com/blog/security-privacy/post-quantum-tls-certificate-inspector-can-and-cannot-tell-you/#user-content-fnref-7)
Mozilla, “Firefox 132 release notes for developers,” developer.mozilla.org, October 2024. [https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/132](https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/132)

8.   [8.](https://capytoolkit.com/blog/security-privacy/post-quantum-tls-certificate-inspector-can-and-cannot-tell-you/#user-content-fnref-8)
CA/Browser Forum, “Minutes of the Server Certificate Working Group, 2 July 2026,” cabforum.org, July 2026. [https://cabforum.org/2026/07/02/2026-07-02-minutes-of-the-server-certificate-working-group/](https://cabforum.org/2026/07/02/2026-07-02-minutes-of-the-server-certificate-working-group/)

9.   [9.](https://capytoolkit.com/blog/security-privacy/post-quantum-tls-certificate-inspector-can-and-cannot-tell-you/#user-content-fnref-9)
Wikipedia contributors, “Key size,” en.wikipedia.org, accessed August 2026. [https://en.wikipedia.org/wiki/Key_size](https://en.wikipedia.org/wiki/Key_size)

10.   [10.](https://capytoolkit.com/blog/security-privacy/post-quantum-tls-certificate-inspector-can-and-cannot-tell-you/#user-content-fnref-10)
CA/Browser Forum, “Ballot SC081v3: Introduce Schedule of Reducing Validity and Data Reuse Periods,” cabforum.org, April 2025. [https://cabforum.org/2025/04/11/ballot-sc081v3-introduce-schedule-of-reducing-validity-and-data-reuse-periods/](https://cabforum.org/2025/04/11/ballot-sc081v3-introduce-schedule-of-reducing-validity-and-data-reuse-periods/)

11.   [11.](https://capytoolkit.com/blog/security-privacy/post-quantum-tls-certificate-inspector-can-and-cannot-tell-you/#user-content-fnref-11)
OpenSSL Project, “Release OpenSSL 3.5.0,” github.com, April 2025. [https://github.com/openssl/openssl/releases/tag/openssl-3.5.0](https://github.com/openssl/openssl/releases/tag/openssl-3.5.0)

![TLS certificate inspection before quantum migration](https://cdn.capytoolkit.com/img/2026/08/post-quantum-tls-certificate-inspector-can-and-cannot-tell-you.jpg)

![Comparing where AI detectors process your text](https://cdn.capytoolkit.com/img/2026/08/where-your-text-goes-when-you-check-it-for-ai-six-detectors-compared.jpg)

![Confirm your security key is genuine](https://cdn.capytoolkit.com/img/2026/08/verifying-your-fido2-hardware-security-key-what-a-browser-can-confirm.jpg)

![Audit shared links for credential leaks](https://cdn.capytoolkit.com/img/2026/07/auditing-urls-share-catching-tracking-tokens-api-keys-credential-leaks.jpg)
