---
source_url: https://medium.com/@lucf15/androids-restore-credentials-api-explained-from-zero-549fbbee35ae
fetched_at: 2026-09-07T11:50:06Z
fetch_method: jina
issue: 267
title_zh: Android Restore Credentials API：从零讲清
tech_domain: android
---

# Android’s Restore Credentials API, Explained From Zero

## ANDROID · CREDENTIAL MANAGER

[![Image 1: Luca Fioravanti](https://miro.medium.com/v2/resize:fill:32:32/1*f6yB5hhVBY2TGqKcTUeYjw.jpeg)](https://medium.com/@lucf15?source=post_page---byline--549fbbee35ae-----------------------------------------)

8 min read

Aug 30, 2026

_What actually happens when an app signs you in on a brand-new phone, with nobody typing anything, and why that’s a much bigger claim than it sounds_

Press enter or click to view image in full size

![Image 2](https://miro.medium.com/v2/resize:fit:700/1*qMsV-7sVYnAGk-MEf_Dxdg.png)

Starting April 2027, Google Play will require any app with its own sign-in to support Restore Credentials ([announcement](https://android-developers.googleblog.com/2026/08/app-quality-memory-optimization-secure-onboarding.html)). The pitch: a user sets up a new phone, restores their apps, opens one, and is already signed in. No password, no “check your email,” no tapping.

Restoring app data is something Android backup already does, so it is tempting to assume this is the same thing. It is not. Restore Credentials runs on WebAuthn, the protocol behind passkeys, and proving identity with WebAuthn works nothing like a password. This article assumes no prior knowledge of WebAuthn, passkeys, Credential Manager, or Android backup. Each term is defined where it first appears, against a working demo (Kotlin/Compose client, Kotlin/Ktor server).

## What a password login actually proves

A normal login form asks for a password, sends it to a server, and the server checks it against what it has stored. The secret itself is the whole proof: know it, type it, get in.

That has an uncomfortable property. If that string ever ends up somewhere it should not (a bad TLS setup, a leaked database, a phishing page), whoever has it can log in as you. The server cannot tell you apart from anyone else who obtained it.

WebAuthn (Web Authentication, a W3C and FIDO Alliance standard) avoids that failure mode. Instead of a shared secret it uses a **key pair**: a private key that produces signatures, and a public key that verifies them. The public key cannot forge a signature or be worked backward into the private key. You generate the pair once, keep the private key somewhere it never leaves, and hand out the public key freely.

Signing in with WebAuthn: the server sends a **challenge**, a fresh random number. The device signs it with the private key and returns only the signature. The server verifies that signature against the public key it has on file. The private key, and anything equivalent to a password, never crosses the network.

The contrast, in one picture:

A **passkey** is this key pair used for everyday sign-in, with the private key held on your device (or synced across your own devices by your phone’s passkey system). A **relying party** is WebAuthn’s term for the app-and-server pair a credential is bound to, because it “relies on” the credential to authenticate someone. Both sides of the demo use it: the Ktor server builds a `RelyingParty` object (`RestoreCredentialService.kt:37-44`), and the client's requests carry an `rp` field naming that same identity. The APIs use the term everywhere without ever saying it just means "whichever app and server this key was made for."

## The twist restore needs: a key nobody has to ask for

A passkey login on a shopping site still asks for something first: a username, or at least an account to pick. The server has to know which public key it is checking before it can send a challenge that makes sense. The device has to be told which account to sign in as.

Restore Credentials cannot work that way. The app was just installed, so there is no signed-in user to ask about. The app asks the OS a blunter question instead: do you already have a key for this exact app, from some previous device? The answer has to come with zero input from the user.

WebAuthn calls this a **resident key**, also a **discoverable credential**. A non-resident key needs the server to hand back an opaque credential ID at registration and supply it again at login, which is why a username lookup has to come first. A resident key stores enough on the device to find itself, given nothing but which app is asking.

Registration asks for one explicitly, in `RestoreCredentialService.kt:64-69`:

.authenticatorSelection(

 AuthenticatorSelectionCriteria.builder()

 .residentKey(ResidentKeyRequirement.REQUIRED)

 .userVerification(UserVerificationRequirement.PREFERRED)

 .build()

)
Authentication then asks for a key with no username at all. The server README puts it plainly: `POST /restore/authenticate/options` is "no username, `userVerification: discouraged`" (`server/README.md:15`), and the route needs no authenticated caller, because there is nobody to authenticate yet (`RestoreCredentialRoutes.kt:46-49`). That is what the feature name describes: a credential retrieved without being asked for by name.

## Why you can’t just back up the login token instead

Android backs up app data on a new phone anyway. Why not back up whatever proves the user is signed in and let it ride along?

In most apps that proof is a **session token**: often a JWT (a signed blob that says “this is user X, until time T”) plus a longer-lived refresh token. The demo issues exactly that, a 15-minute JWT access token and a 30-day rotating refresh token (`server/README.md:54-56`). A session token is a **bearer secret**: whoever holds it is treated as that user, with no cryptographic tie to a device. Copying it onto a second device is session hijacking by definition.

So the app refuses to back the session up. Its data-extraction rules exclude the session store from both cloud backup and device-to-device transfer, in `data_extraction_rules.xml:9-14`:

<cloud-backup>

 <exclude domain="file" path="datastore/session.preferences_pb" />

</cloud-backup>

<device-transfer>

 <exclude domain="file" path="datastore/session.preferences_pb" />

</device-transfer>
A WebAuthn credential sidesteps this. The private key never moves, not even during restore. What reaches the new device is the ability to produce new signatures with a key still sitting where it was generated, or (in the cloud case below) a key encrypted end-to-end before it ever left the original device. Nothing bearer-shaped changes hands.

## Why the credential lives outside your app’s backup

Android apps that want their data to survive a device switch implement a `BackupAgent`: a class Android calls to save your app's files or key-value data, and calls again on the new device to restore them. It carries your local database, preferences, cached files, whatever you declared. This demo has one, `RestoreCredentialBackupAgent`, declared in the manifest (`AndroidManifest.xml:9`).

## Get Luca Fioravanti’s stories in your inbox

Join Medium for free to get updates from this writer.

Remember me for faster sign in

Its `onBackup()` and `onRestore()`, the callbacks that actually move file data, do nothing, in `RestoreCredentialBackupAgent.kt:25-27`:

override fun onBackup(oldState: ParcelFileDescriptor?, data: BackupDataOutput?, newState: ParcelFileDescriptor?) = Unit

override fun onRestore(data: BackupDataInput?, appVersionCode: Int, newState: ParcelFileDescriptor?) = Unit
So why declare a `BackupAgent` at all? `android:allowBackup="true"`, `android:fullBackupOnly="true"`, and the XML rules above already give you automatic file backup with no custom class. The one thing they do not give you is `onRestoreFinished()`: the system can only call it if you have registered a class for it. [Google's Auto Backup guide](https://developer.android.com/identity/data/autobackup) lists exactly that as a reason to subclass `BackupAgent`, and says leaving `onBackup()` and `onRestore()` empty is the intended pattern once `fullBackupOnly` is set.

The restore credential was never in that data stream. Google Play Services generates and holds it in its own credential store, separate from anything the `BackupAgent` declares, and moves it through its own channel: an end-to-end encrypted cloud copy tied to the Google account, or a direct device-to-device transfer at setup. A private key is not ordinary app data you want sitting copyable in a backup archive.

`CreateRestoreCredentialRequest` takes an `isCloudBackupEnabled` flag. If the device lacks the screen lock and encryption cloud backup needs, the call throws `E2eeUnavailableException` rather than downgrading silently, in `AndroidRestoreCredentialGateway.kt:22-33`:

override suspend fun register(creationOptionsJson: String): String {

 val response =

 try {

 credentialManager.createCredential(appContext, CreateRestoreCredentialRequest(creationOptionsJson, isCloudBackupEnabled = true))

 } catch (e: E2eeUnavailableException) {

 credentialManager.createCredential(appContext, CreateRestoreCredentialRequest(creationOptionsJson, isCloudBackupEnabled = false))

 } catch (e: Exception) {

 Log.e("RestoreCredentialGateway", "createCredential failed for requestJson=$creationOptionsJson", e)

 throw e

 }

 return (response as CreateRestoreCredentialResponse).responseJson

}
All of this goes through `CredentialManager`, the `androidx.credentials` entry point for passkeys, saved passwords, and now restore credentials. One file imports it: `AndroidRestoreCredentialGateway.kt`, behind a plain Kotlin interface (`RestoreCredentialGateway.kt`), so nothing else in the app depends on the Android specifics.

## The two-phase ceremony, end to end

The whole feature is one WebAuthn exchange, run twice. (**Ceremony** is the spec’s term for one complete request/response exchange: registration is one, authentication is another.)

**Phase one, registration**, runs once, silently, right after a normal sign-in. `SignInUseCase` logs in, then registers a restore credential in the background, discarding any failure so it never blocks sign-in, in `SignInUseCase.kt:12-17`:

suspend operator fun invoke(username: String, password: String): AuthSession {

 val session = authRepository.login(username, password)

 sessionStore.save(session)

 runCatching { registerRestoreCredential(session.accessToken) }

 return session

}
`RegisterRestoreCredentialUseCase` fetches creation options, passes them to `CredentialManager.createCredential()`, and sends the result back for the server to verify and store (`RegisterRestoreCredentialUseCase.kt:10-14`). The private key is generated on-device inside that call; only the public key goes back, in the **attestation response**, a signed statement from the device about the key it just made.

**Phase two, restoration**, runs later, on whatever device the app appears on next, with no username, in `TryRestoreSignInUseCase.kt:13-24`:

suspend operator fun invoke(): Boolean {

 val (requestId, requestJson) = restoreCredentialApi.authenticationOptions()

 val outcome = restoreCredentialGateway.signIn(requestJson)

 val authenticationResponseJson =

 when (outcome) {

 is RestoreSignInOutcome.Available -> outcome.authenticationResponseJson

 RestoreSignInOutcome.NotAvailable -> return false

 }

 val session = restoreCredentialApi.verifyAuthentication(requestId, authenticationResponseJson)

 sessionStore.save(session)

 return true

}
`signIn()` calls `CredentialManager.getCredential()` with a `GetRestoreCredentialOption`. No resident key for this app means a `NoCredentialException`, which the gateway logs at debug and turns into `NotAvailable`, since "nothing to restore" is a normal outcome. Any other `GetCredentialException` (a wrong RP ID, a broken `assetlinks.json`) is logged as an error but still returned as `NotAvailable`, so a misconfigured setup falls back to manual sign-in instead of failing first launch (`AndroidRestoreCredentialGateway.kt:35-49`). If a key is found, the device signs the challenge and the app has a session before the user has touched anything.

Both phases, both sides of the network:

## The two places that trigger phase two

Nothing prompts the user, so the app has to decide when to attempt phase two. Following [Google’s guidance](https://developer.android.com/identity/sign-in/restore-credentials-implementation), the demo calls the same retrieval logic from two places:

*   **A background hook**, `RestoreCredentialBackupAgent.onRestoreFinished()`, which Android calls right after your app's restored data lands on the new device, before the user has opened the app (`RestoreCredentialBackupAgent.kt:29-38`). This is what makes "zero taps" literal: the exchange can finish before the icon is ever touched.
*   **A check on first launch**, as a fallback for when the hook does not fire: dropped network, `allowBackup` turned off, or data restored through a path that never calls `onRestoreFinished()`.

Both call the same `TryRestoreSignInUseCase`, so there is one retrieval path, not two ceremonies to maintain.

## Try it yourself

Reading the code is not the same as watching a credential round-trip to a second device. Clone the demo, follow `TESTING.md` to run the server and app, then use Android Studio's Backup App Data / Restore App Data actions (Otter 2025.2.1+, documented at [developer.android.com/identity/sign-in/test-restore-credentials](https://developer.android.com/identity/sign-in/test-restore-credentials), which notes the flow "simulates the setup wizard flow") to move a credential to a second device with no signed-in Google account. Watch the server log for `POST /restore/authenticate/verify` returning `200`: proof a real key round-tripped, whatever the UI shows.

Full source for both the server and the client is at [github.com/lucf15/RestoreCredentialsDemo](https://github.com/lucf15/RestoreCredentialsDemo).
