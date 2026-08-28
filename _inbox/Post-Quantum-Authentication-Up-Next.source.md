---
source_url: https://www.ietf.org/blog/iab-pq-workshop-cfp/
fetched_at: 2026-08-28T13:37:22Z
fetch_method: jina
issue: 135
cover_image: https://www.ietf.org/media/images/ietf-logo-500-square-250x250.original.jpg
title_zh: IAB 后量子密码学研讨会征集
tech_domain: frontend
---

# Post-Quantum Authentication: Up Next

Post-quantum key establishment has moved from standards into deployment. Post-quantum authentication has not moved nearly as far, and specification work is no longer the only constraint. The IAB is holding a workshop in Prague on 11 and 12 October 2026 to bring deployment experience together with the people working on the relevant protocols and standards.

The [workshop is focused on accelerating the deployment of post-quantum authentication](https://www.iab.org/announcements/call-for-papers-iab-workshop-on-accelerating-the-deployment-of-post-quantum-authentication-pqws/). We want evidence about what actually delays deployment in production systems. More details about what position papers, due 4 September 2026, should cover and how they should be submitted are provided below.

Deployment of post-quantum authentication is complicated. The protocol standards are advancing, but more studies need to be conducted on constraints encountered in production systems.

There is no shortage of specification work. NIST has standardized [ML-DSA in FIPS 204](https://csrc.nist.gov/pubs/fips/204/final) and [SLH-DSA in FIPS 205](https://csrc.nist.gov/pubs/fips/205/final). The IETF has published the conventions for using them in X.509 as [RFC 9881](https://www.rfc-editor.org/rfc/rfc9881.html) and [RFC 9909](https://www.rfc-editor.org/rfc/rfc9909.html). There are also active proposals for [composite signatures](https://datatracker.ietf.org/doc/draft-ietf-lamps-pq-composite-sigs/), [Merkle Tree Certificates](https://datatracker.ietf.org/doc/draft-ietf-plants-merkle-tree-certs/), and [KEM-based authentication](https://datatracker.ietf.org/doc/draft-celi-wiggers-tls-authkem/).

What we largely do not have is evidence about what happens when these approaches meet production systems. We know the sizes of the keys and signatures, and we can benchmark individual operations. We know much less about their effect on certificate chains, handshake limits, cryptographic modules, firmware budgets, offline verification, and trust-store timelines.

We would like to hear from the people who have tried, measured, purchased, planned, or operated any part of this transition.

## Why "less urgent" does not mean "later"

Post-quantum authentication is often described as less urgent than post-quantum key establishment. There is a sound threat-model argument behind that ordering. Post-quantum key establishment protects against harvest-now-decrypt-later attacks, in which encrypted traffic collected today may be decrypted once a sufficiently capable quantum computer exists. Post-quantum authentication protects against an active attacker able to forge a signature or credential using such a computer, and nobody has one today.

The problem is that this compares when the threats may arrive without comparing how long the migrations will take.

Cloudflare began preparing its post-quantum migration in 2019, enabled post-quantum encryption for all websites and APIs in 2022, and [reported in April 2026](https://blog.cloudflare.com/post-quantum-roadmap/) that more than 65% of human traffic to its network was post-quantum encrypted. That figure describes one large network rather than the entire Internet, but the schedule is instructive. Several years after broad server-side enablement, a substantial minority of traffic had still not made the transition.

Key establishment also has a favorable deployment shape. Clients and servers can add support independently and negotiate the new mechanism whenever both sides are ready. For the Web TLS rollout, the key-establishment component did not require a new certificate chain, a new trust anchor, or an upgraded long-term signing key.

Authentication has more participants and dependencies because a verifier has to know in advance what it will accept. Deployment requires certificate authorities, relying parties, trust stores, cryptographic modules, and applications to make compatible changes. Some credentials are used in live handshakes, while others are embedded in firmware, software packages, identity tokens, or archived documents and may be verified offline years later. Each has a different deployment path, and many of these components move more slowly than ordinary software.

The threat may be further away, but the migration is also longer. If the work consumes most of the remaining warning period, treating authentication as the second priority cannot mean waiting until key establishment is finished.

## The costs are not abstract

The new objects are not just a little larger, they are a different size class.

At NIST security level 3, an ML-DSA-65 public key is 1,952 bytes and a signature is 3,309 bytes. An Ed25519 public key is 32 bytes and its signature is 64 bytes. Consider only the two public keys and two certificate signatures in a transmitted leaf-and-intermediate chain. With ML-DSA-65 those four fields contain 10,522 bytes. With Ed25519 they contain 192 bytes, a difference of nearly 55 times. That is a lower bound, excluding names, extensions, ASN.1 encoding, transparency information, and protocol framing.

[SLH-DSA](https://www.rfc-editor.org/rfc/rfc9909.html) makes a different trade. Its public keys are small, but the standardized signatures range from 7,856 bytes to 49,856 bytes depending on the parameter set.

Size is not the only cost, signature performance also varies substantially. ML-DSA can require significantly more CPU than commonly deployed elliptic-curve signatures, while some SLH-DSA parameter sets make signing orders of magnitude more expensive. At scale, that can affect certificate issuance, TLS termination, identity-token signing, software and firmware signing, and verification capacity.

The consequences of size depend on the surrounding protocol. In [QUIC](https://www.rfc-editor.org/rfc/rfc9000.html), a client Initial datagram must be at least 1,200 bytes, and a server that has not yet validated the client address may send no more than three times the number of bytes it has received. After one minimum-size Initial, that gives the server a 3,600-byte transmission budget. One ML-DSA-65 public key and signature total 5,261 bytes before the rest of the certificate is counted.

This does not make post-quantum authentication impossible in QUIC. The client can send more data, the server can validate the address, and the protocol can use other mitigations. It does mean that certificate size no longer fits comfortably inside assumptions that were harmless for elliptic-curve cryptography.

Other systems have different constraints. [RFC 9191](https://www.rfc-editor.org/rfc/rfc9191.html) documents EAP authenticators that abandon sessions after 40 to 50 round trips, and concludes that certificate chains larger than roughly 60 kilobytes cannot complete successfully in many existing EAP-TLS deployments. That problem predates the current post-quantum standards. Larger keys and signatures make it more important.

These examples show that both size and computational cost matter. They do not tell an operator what the change does to packet counts, retries, p50 and p99 latency, authentication failures, memory use, signing capacity, storage, or bandwidth. For that, we need measurements from production systems.

## Which constraints are actually binding?

Several different deployment problems are being discussed as though they were one problem. A useful comparison of the proposed approaches needs to distinguish at least the following constraints.

*   **Size and protocol behavior**. How large can a certificate chain, handshake flight, token, package, or firmware image become before it crosses a transport limit, fragmentation threshold, parser assumption, device budget, or billing threshold? QUIC and EAP show two very different ways in which size becomes operationally significant.
*   **Hardware and key custody**. Can the key be generated, imported, replicated for high availability, backed up where policy permits, rotated, and used through the available hardware security modules (HSM), trusted platform modules (TPM), secure elements, smartcards, or PKCS #11 interfaces? Does support require new firmware, replacement hardware, or a new [FIPS 140-3](https://csrc.nist.gov/pubs/fips/140-3/final) validation? A roadmap date does not reveal whether the limiting factor is silicon, an API, a certification process, or product prioritization.
*   **Long-lived and offline verification**. Will the verifier be online and updated regularly, or will it be sitting in a device that cannot be changed? Can it obtain new trust anchors, revocation information, Merkle checkpoints, timestamps, or algorithm policy? A design suited to a browser may be irrelevant to a boot ROM, an archived signed object, or a package verified years after it was built.
*   **Signing architecture and capacity**. How many signatures will the key produce, how quickly, and from how many sites? What CPU or hardware capacity is required to sustain that rate? Can the system preserve signing state through crashes, failover, backup restoration, and disaster recovery? NIST permits stateful LMS and XMSS signatures for controlled applications in [SP 800-208](https://csrc.nist.gov/pubs/sp/800/208/final), but the security of those schemes depends on careful state management.
*   **Operational cost**. What happens to latency, throughput, CPU, memory, bandwidth, storage, issuance capacity, monitoring, and failure rates? A design may fit within the protocol and still be too expensive or fragile to operate.
*   **Ecosystem coordination**. What sequencing do certificate authorities, trust stores, clients, hardware vendors, and operators need in order to implement and test compatible mechanisms? Which party has to move before the next one can test anything at all?

The workshop should identify which of these constraints bind in which systems, with enough evidence that operators and protocol designers can make different choices where their systems differ.

## Each approach moves the cost

There are multiple proposed approaches that involve more than just swapping a classical signing key with a post-quantum signing key, and each has additional trade-offs.

[Composite ML-DSA signatures](https://datatracker.ietf.org/doc/draft-ietf-lamps-pq-composite-sigs/) combine ML-DSA with a traditional signature algorithm, with both component signatures required to validate. They offer a hedge in which the composite remains unforgeable as long as at least one component remains secure, but consume additional wire, computation, key-management, implementation, and validation budget. They are attractive when retaining a traditional component is the binding requirement and less attractive when size, CPU, or module support is already the problem.

[Merkle Tree Certificates](https://datatracker.ietf.org/doc/draft-ietf-plants-merkle-tree-certs/) move repeated signature cost into shared log infrastructure, inclusion proofs, and an update channel. In one example in the current draft, a standalone subtree containing about 2,500 certificates produces a 384-byte inclusion proof in addition to the signatures needed by the relying party. A landmark-relative form produces a 736-byte proof with no signatures for a subtree covering about 4.4 million certificates, but applies only when the relying party has sufficiently current log information. This approach spends infrastructure and verifier-freshness budget to save wire and signing budget.

[KEM-based authentication](https://datatracker.ietf.org/doc/draft-celi-wiggers-tls-authkem/) proves possession of a long-term KEM private key through an interactive key exchange rather than by signing the TLS handshake transcript. That may offer a useful size and performance trade-off inside an online handshake, but it changes the protocol and credential model. By construction, it does not authenticate a firmware image, software package, or archived document that must be verified independently and offline. It spends protocol-change and interactivity budget to reduce the cost of online authentication.

There are also operational levers that require little or no new cryptography: reducing the number of intermediates, avoiding signatures where long-term public verifiability is unnecessary, changing credential lifetimes, or compressing repeated certificate structure. These may buy more than a new construction in some systems. We do not have enough published measurements to know where.

There is no single "efficient" approach. Each moves cost from one constraint to another, and the useful question is which resource a particular deployment can afford to spend.

## Who should send us something?

The workshop particularly needs reports from people responsible for parts of the system that protocol designers normally cannot see.

A useful paper from an HSM team might compare ML-DSA key generation, import, signing, replication, and failover across the devices or firmware versions it has tested. A certificate authority might report the exact size of its proposed chains and transparency material, the changes required in its issuance pipeline, and which client versions can validate the result. A QUIC, EAP, or VPN operator might report packet counts, tail latency, and authentication failure rates as chain sizes increase.

A firmware team might report the available flash and RAM in its verifier, the permitted startup delay, the intended lifetime of the device, and which candidates fit those limits. A trust-store operator might report its acceptance timeline for a new algorithm, what validation support it already has, what its root-program requirements would demand of an applicant, and how much of its client population could validate the result today.

These are examples of the evidence the workshop is seeking, not claims that these particular tests have failed. One table and five explanatory paragraphs may be more useful than a polished research paper.

## What to send us

Send one or two pages as PDF, to [pq-workshop-pc@iab.org](mailto:pq-workshop-pc@iab.org) by 4 September 2026. A short statement of interest is also fine, and you do not have to plan to attend. The[call for papers](https://www.iab.org/announcements/call-for-papers-iab-workshop-on-accelerating-the-deployment-of-post-quantum-authentication-pqws/) covers the rest: what to include, how submissions are published, and how the workshop will run.
