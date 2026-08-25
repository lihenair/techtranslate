---
source_url: https://dev.to/arshtechpro/devicecheck-and-app-attest-stopping-fraud-in-ios-apps-472e
fetched_at: 2026-08-25T05:16:11Z
fetch_method: jina
issue: 77
cover_image: https://media2.dev.to/dynamic/image/width=1200,height=627,fit=cover,gravity=auto,format=auto/https%3A%2F%2Fdev-to-uploads.s3.us-east-2.amazonaws.com%2Fuploads%2Farticles%2F2v0s8k3i3jjrly8jp09m.png
title_zh: devicecheck-and-app-attest-stopping-fraud-in-ios-apps-472e
tech_domain: mobile
---

# DeviceCheck and App Attest: Stopping Fraud in iOS Apps

Your API has no idea what is calling it.

A request arriving at `POST /api/redeem` looks identical whether it came from your app on a real iPhone, from a modified build running on a jailbroken device, or from a Python script someone wrote after reading your traffic in Charles Proxy. HTTPS proves the connection is encrypted. It proves nothing about the client.

Apple gives you two frameworks to close that gap. This post covers what each one actually guarantees, what it does not, and how to implement both without the mistakes that show up in most tutorials.

* * *

## [](https://dev.to/arshtechpro/devicecheck-and-app-attest-stopping-fraud-in-ios-apps-472e#table-of-contents) Table of contents

*   [What DeviceCheck actually does](https://dev.to/arshtechpro/devicecheck-and-app-attest-stopping-fraud-in-ios-apps-472e#what-devicecheck-actually-does)
*   [What App Attest actually does](https://dev.to/arshtechpro/devicecheck-and-app-attest-stopping-fraud-in-ios-apps-472e#what-app-attest-actually-does)
*   [Choosing between them](https://dev.to/arshtechpro/devicecheck-and-app-attest-stopping-fraud-in-ios-apps-472e#choosing-between-them)
*   [Implementing DeviceCheck](https://dev.to/arshtechpro/devicecheck-and-app-attest-stopping-fraud-in-ios-apps-472e#implementing-devicecheck)
*   [Implementing App Attest](https://dev.to/arshtechpro/devicecheck-and-app-attest-stopping-fraud-in-ios-apps-472e#implementing-app-attest)
*   [Fraud scenarios](https://dev.to/arshtechpro/devicecheck-and-app-attest-stopping-fraud-in-ios-apps-472e#fraud-scenarios)
*   [Mistakes to avoid](https://dev.to/arshtechpro/devicecheck-and-app-attest-stopping-fraud-in-ios-apps-472e#mistakes-to-avoid)

* * *

## [](https://dev.to/arshtechpro/devicecheck-and-app-attest-stopping-fraud-in-ios-apps-472e#what-devicecheck-actually-does) What DeviceCheck actually does

DeviceCheck (iOS 11+) does two things, and it is worth being precise because it is routinely oversold.

**One.** It confirms a token came from a genuine Apple device that has your app installed, where your app is tied to your developer account.

**Two.** It gives you two bits of storage per device, per developer, held on Apple's servers. Two bits means four states. It survives app deletion and reinstall, which is the entire point.

That's it. Read the list again for what is _not_ on it. DeviceCheck does not detect jailbreaks. It does not tell you whether your app binary was modified. It does not identify the user. It is not authentication.

The two-bit storage is the interesting part. Because it persists across reinstalls, it answers questions that a locally-stored flag cannot:

*   Has this device already claimed the new-user promo?
*   Has this device been flagged for chargeback fraud?

A user who deletes your app, reinstalls it, and creates a fresh account still hits the same two bits.

One gotcha: the device token from `generateToken` is **single-use**. You should treat the token you receive in the completion block as single-use — although it remains valid long enough to retry a specific request, you should not use it multiple times. Generate a fresh one per request.

## [](https://dev.to/arshtechpro/devicecheck-and-app-attest-stopping-fraud-in-ios-apps-472e#what-app-attest-actually-does) What App Attest actually does

App Attest (iOS 14+) answers a harder question: _is this specific request coming from an unmodified copy of my app?_

It works by generating a key pair in the device's Secure Enclave. The private key never leaves the hardware and cannot be extracted. Apple then issues a certificate chain vouching that this key belongs to a legitimate instance of your app, with your Team ID and Bundle ID baked in.

Once that key is attested, your app signs each sensitive request with it. Your server verifies the signature. A tampered app cannot produce valid signatures, because it cannot get its own key attested.

The flow splits into two phases, and conflating them is the most common implementation error.

**Attestation** happens once per key install. Apple's servers are involved. It is relatively expensive.

**Assertion** happens per request afterward. It is cheap. Critically, the assertion flow is simpler than attestation, as the Apple servers are no longer involved — your server does the verification with the public key it stored during attestation.

There is no Apple REST endpoint that validates attestations or assertions for you. Your server, not the app, must validate attestations — a compromised client cannot be trusted to validate its own integrity. You parse the CBOR attestation object and check the certificate chain against Apple's App Attest root CA yourself, or you use a library that does it.

## [](https://dev.to/arshtechpro/devicecheck-and-app-attest-stopping-fraud-in-ios-apps-472e#choosing-between-them) Choosing between them

|  | DeviceCheck | App Attest |
| --- | --- | --- |
| Confirms genuine Apple device | Yes | Yes |
| Confirms app binary unmodified | No | Yes |
| Persistent per-device state | Yes (2 bits) | No |
| Secure Enclave keys | No | Yes |
| Replay protection | No | Yes (counter + nonce) |
| Minimum iOS | 11 | 14 |
| Apple servers in the loop | Every call | Attestation only |
| Server work | Call Apple's API | Verify crypto yourself |

They solve different problems and compose well. App Attest tells you the request is authentic. DeviceCheck remembers that this device already burned its free trial. Plenty of production apps run both.

## [](https://dev.to/arshtechpro/devicecheck-and-app-attest-stopping-fraud-in-ios-apps-472e#implementing-devicecheck) Implementing DeviceCheck

### [](https://dev.to/arshtechpro/devicecheck-and-app-attest-stopping-fraud-in-ios-apps-472e#client) Client

```
import DeviceCheck

func fetchDeviceToken() async throws -> String {
    guard DCDevice.current.isSupported else {
        throw DeviceCheckError.unsupported
    }
    let token = try await DCDevice.current.generateToken()
    return token.base64EncodedString()
}
```

`isSupported` returns `false` on the Simulator. Plan for that in your dev workflow.

### [](https://dev.to/arshtechpro/devicecheck-and-app-attest-stopping-fraud-in-ios-apps-472e#server) Server

You need a `.p8` key with DeviceCheck enabled from the Apple Developer portal, and you sign an ES256 JWT with it. The HTTP header field in each request must contain the authentication key you receive from Apple in a JSON web token.

Three endpoints, all POST:

*   `validate_device_token` — is this a real device?
*   `query_two_bits` — read the stored state
*   `update_two_bits` — write it

Swap `api.devicecheck.apple.com` for `api.development.devicecheck.apple.com` in dev.

```
import jwt from 'jsonwebtoken';
import { randomUUID } from 'crypto';

function appleJWT() {
  return jwt.sign({}, PRIVATE_KEY_P8, {
    algorithm: 'ES256',
    keyid: KEY_ID,        // 10-char Key ID
    issuer: TEAM_ID,      // 10-char Team ID
  });
}

async function queryBits(deviceToken) {
  const res = await fetch(
    `https://${HOST}/v1/query_two_bits`,
    {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${appleJWT()}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        device_token: deviceToken,
        transaction_id: randomUUID(),
        timestamp: Date.now(),   // milliseconds, not seconds
      }),
    }
  );

  // A device with no bits set yet returns a plain-text body,
  // not JSON. Handle it before parsing.
  const text = await res.text();
  if (text.includes('Failed to find bit state')) {
    return { bit0: false, bit1: false, isNew: true };
  }
  return { ...JSON.parse(text), isNew: false };
}
```

Two things bite people here: `timestamp` is in **milliseconds**, and `transaction_id` must be unique per request. A brand-new device returns a non-JSON body, so parse defensively.

## [](https://dev.to/arshtechpro/devicecheck-and-app-attest-stopping-fraud-in-ios-apps-472e#implementing-app-attest) Implementing App Attest

### [](https://dev.to/arshtechpro/devicecheck-and-app-attest-stopping-fraud-in-ios-apps-472e#phase-1-attestation-once) Phase 1: attestation (once)

```
import DeviceCheck
import CryptoKit

func attest() async throws {
    let service = DCAppAttestService.shared
    guard service.isSupported else { throw AttestError.unsupported }

    // 1. Server issues a one-time random challenge.
    let challenge = try await api.fetchChallenge()

    // 2. Create a Secure Enclave key. Persist the ID in Keychain.
    let keyId = try await service.generateKey()
    try Keychain.store(keyId, for: "appattest.keyId")

    // 3. Hash the challenge. This must be SHA256.
    let clientDataHash = Data(SHA256.hash(data: Data(challenge.utf8)))

    // 4. Attest. Apple's servers participate in this step.
    let attestation = try await service.attestKey(keyId, clientDataHash: clientDataHash)

    // 5. Ship it to your server for verification.
    try await api.verifyAttestation(
        keyId: keyId,
        challenge: challenge,
        attestation: attestation.base64EncodedString()
    )
}
```

Persist that `keyId`. If you lose it you must attest a fresh key, and each call to `generateKey` returns a new keyId referring to a unique key pair — the old ones do not get replaced.

Your server then verifies the attestation object. Do not write the CBOR and X.509 parsing yourself unless you have a reason to; use `node-app-attest`, `appattest-checker-node`, or `veehaitch/devicecheck-appattest` for JVM.

```
import { verifyAttestation } from 'node-app-attest';

const { keyId, publicKey, receipt } = verifyAttestation({
  attestation: Buffer.from(req.body.attestation, 'base64'),
  challenge: storedChallenge,          // the one YOU issued
  keyId: req.body.keyId,
  bundleIdentifier: 'com.example.app',
  teamIdentifier: 'ABCDE12345',
  allowDevelopmentEnvironment: !isProd,
});

// Store publicKey for assertions, receipt for the fraud metric,
// and signCount starting at 0.
await db.saveAttestation({ keyId, publicKey, receipt, signCount: 0 });
```

Burn the challenge after use. A reused challenge defeats the whole mechanism.

### [](https://dev.to/arshtechpro/devicecheck-and-app-attest-stopping-fraud-in-ios-apps-472e#phase-2-assertion-every-sensitive-request) Phase 2: assertion (every sensitive request)

```
func signedRequest(payload: [String: Any]) async throws -> Data {
    let keyId = try Keychain.read("appattest.keyId")
    let challenge = try await api.fetchChallenge()

    var body = payload
    body["challenge"] = challenge
    let bodyData = try JSONSerialization.data(withJSONObject: body)

    let clientDataHash = Data(SHA256.hash(data: bodyData))
    let assertion = try await DCAppAttestService.shared
        .generateAssertion(keyId, clientDataHash: clientDataHash)

    // Send bodyData AND the assertion AND the keyId.
    // The assertion object does not contain the keyId.
    return try await api.send(body: bodyData, assertion: assertion, keyId: keyId)
}
```

Server side, no Apple call:

```
const stored = await db.getAttestation(req.body.keyId);

const { signCount } = verifyAssertion({
  assertion: Buffer.from(req.body.assertion, 'base64'),
  payload: req.rawBody,
  publicKey: stored.publicKey,
  bundleIdentifier: 'com.example.app',
  teamIdentifier: 'ABCDE12345',
});

// The counter must strictly increase. A repeat or a
// decrease means someone is replaying a captured assertion.
if (signCount <= stored.signCount) {
  return res.status(401).json({ error: 'replay detected' });
}
await db.updateSignCount(req.body.keyId, signCount);
```

The authenticator data includes an ever-increasing counter — checking it is what gives you replay protection, and skipping the check throws that away.

### [](https://dev.to/arshtechpro/devicecheck-and-app-attest-stopping-fraud-in-ios-apps-472e#the-fraud-metric) The fraud metric

That `receipt` you stored is worth something. The fraud metric is an approximate 30-day count of unique attested keys associated with your app on a particular device, retrieved by your server from the App Attest data server using a stored attestation receipt. A device generating hundreds of keys is very likely an attestation broker feeding a bot farm. A device with two or three has probably just reinstalled the app.

## [](https://dev.to/arshtechpro/devicecheck-and-app-attest-stopping-fraud-in-ios-apps-472e#fraud-scenarios) Fraud scenarios

**Bot traffic and credential stuffing.** A script hitting your API cannot produce an assertion, because it has no Secure Enclave key and cannot get one attested. App Attest turns "rate limit the abuse" into "the abuse cannot reach the endpoint."

**Simulator and emulator abuse.** Both frameworks report `isSupported == false` on the Simulator. Free-tier farming through simulators stops working.

**Repeat promo abuse.** DeviceCheck's bits outlive app deletion. Set bit0 when the promo is claimed; check it before granting.

**Modified builds.** Someone patches your IPA to skip the receipt validation and sideloads it. The modified app's key will not attest, because the attestation includes a hash of your app's identity that Apple signs.

**Account takeover.** Attestation gives you a stable per-install identity independent of credentials. Stolen password plus unrecognized attested key equals a good reason to demand a second factor.

## [](https://dev.to/arshtechpro/devicecheck-and-app-attest-stopping-fraud-in-ios-apps-472e#mistakes-to-avoid) Mistakes to avoid

**Treating App Attest as a boolean.**Do not reject every new key for an existing user — app reinstall and device restore can legitimately invalidate a key and require key rotation. Legitimate users rotate keys. Feed the signal into a risk score; do not hard-block on it.

**Validating on the client.** If the app decides whether its own attestation is valid, an attacker patches out the check. Verification belongs on the server, always.

**Reusing challenges.** One challenge, one use, short expiry, stored server-side. Otherwise a captured assertion replays forever.

**Skipping the counter check.** It is three lines and it is the difference between replay protection and none.

**Attesting during checkout.**Perform attestation outside critical user flows when possible, retry later on failures, and use exponential backoff instead of hard-coded retry loops. Attestation can fail transiently. Do it at launch or during onboarding, not while the user is trying to pay.

**Shipping the `.p8` in the app.** Your DeviceCheck key lives on the server. Nowhere else.

**Assuming this replaces everything else.** Attestation raises the cost of attack; it does not make it infinite. A determined attacker with a jailbroken device and Frida can hook the call and relay valid assertions from a script. Keep your rate limiting, your behavioral analysis, and your server-side validation.

### [](https://dev.to/arshtechpro/devicecheck-and-app-attest-stopping-fraud-in-ios-apps-472e#references) References

*   [App Attest documentation](https://developer.apple.com/documentation/devicecheck/establishing_your_app_s_integrity)
*   [Accessing and modifying per-device data](https://developer.apple.com/documentation/devicecheck/accessing_and_modifying_per-device_data)

<!-- media:svg src="https://assets.dev.to/assets/sparkle-heart-5f9bee3767e18deb1bb725290cb151c25234768a0e9a2bd39370c382d02920cf.svg" -->

<!-- media:svg src="https://assets.dev.to/assets/multi-unicorn-b44d6f8c23cdd00964192bedc38af3e82463978aa611b4365bd33a0f1f4f3e97.svg" -->

<!-- media:svg src="https://assets.dev.to/assets/exploding-head-daceb38d627e6ae9b730f36a1e390fca556a4289d5a41abb2c35068ad3e2c4b5.svg" -->

<!-- media:svg src="https://assets.dev.to/assets/raised-hands-74b2099fd66a39f2d7eed9305ee0f4553df0eb7b4f11b01b6b1b499973048fe5.svg" -->

<!-- media:svg src="https://assets.dev.to/assets/fire-f60e7a582391810302117f987b22a8ef04a2fe0df7e3258a5f49332df1cec71e.svg" -->

![DEV Community](https://media2.dev.to/dynamic/image/width=190,height=,fit=scale-down,gravity=auto,format=auto/https%3A%2F%2Fdev-to-uploads.s3.amazonaws.com%2Fuploads%2Farticles%2F8j7kvp660rqzt99zui8e.png)

![](https://assets.dev.to/assets/sparkle-heart-5f9bee3767e18deb1bb725290cb151c25234768a0e9a2bd39370c382d02920cf.svg)

![](https://assets.dev.to/assets/multi-unicorn-b44d6f8c23cdd00964192bedc38af3e82463978aa611b4365bd33a0f1f4f3e97.svg)

![](https://assets.dev.to/assets/exploding-head-daceb38d627e6ae9b730f36a1e390fca556a4289d5a41abb2c35068ad3e2c4b5.svg)

![](https://assets.dev.to/assets/raised-hands-74b2099fd66a39f2d7eed9305ee0f4553df0eb7b4f11b01b6b1b499973048fe5.svg)

![](https://assets.dev.to/assets/fire-f60e7a582391810302117f987b22a8ef04a2fe0df7e3258a5f49332df1cec71e.svg)
