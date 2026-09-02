---
source_url: https://dev.to/codewithsadee/how-to-build-a-secure-google-oauth-20-login-using-react-nodejs-41mp
fetched_at: 2026-09-02T14:55:51Z
fetch_method: jina
issue: 198
cover_image: https://media2.dev.to/dynamic/image/width=1200,height=627,fit=cover,gravity=auto,format=auto/https%3A%2F%2Fdev-to-uploads.s3.us-east-2.amazonaws.com%2Fuploads%2Farticles%2Fbrgw3z3n53dlg5m2ydfm.png
title_zh: 用 React 与 Node.js 构建安全的 Google OAuth 2.0 登录
tech_domain: security
---

# How to Build a Secure Google OAuth 2.0 Login Using React & Node.js

[Skip to content](https://dev.to/codewithsadee/how-to-build-a-secure-google-oauth-20-login-using-react-nodejs-41mp#main-content)

[![Image 3: DEV Community](https://media2.dev.to/dynamic/image/quality=100/https://dev-to-uploads.s3.amazonaws.com/uploads/logos/resized_logo_UQww2soKuUsjaOGNB38o.png)](https://dev.to/)

[Powered by Algolia](https://www.algolia.com/developers/?utm_source=devto&utm_medium=referral)

[Log in](https://dev.to/enter?signup_subforem=1)[Create account](https://dev.to/enter?signup_subforem=1&state=new-user)

## DEV Community

![Image 4](https://assets.dev.to/assets/heart-plus-active-9ea3b22f2bc311281db911d416166c5f430636e76b15cd5df6b3b841d830eefa.svg)8 Add reaction 

![Image 5](https://assets.dev.to/assets/sparkle-heart-5f9bee3767e18deb1bb725290cb151c25234768a0e9a2bd39370c382d02920cf.svg)3 Like ![Image 6](https://assets.dev.to/assets/multi-unicorn-b44d6f8c23cdd00964192bedc38af3e82463978aa611b4365bd33a0f1f4f3e97.svg)1 Unicorn ![Image 7](https://assets.dev.to/assets/exploding-head-daceb38d627e6ae9b730f36a1e390fca556a4289d5a41abb2c35068ad3e2c4b5.svg)1 Exploding Head ![Image 8](https://assets.dev.to/assets/raised-hands-74b2099fd66a39f2d7eed9305ee0f4553df0eb7b4f11b01b6b1b499973048fe5.svg)1 Raised Hands ![Image 9](https://assets.dev.to/assets/fire-f60e7a582391810302117f987b22a8ef04a2fe0df7e3258a5f49332df1cec71e.svg)2 Fire 

1 Jump to Comments 0 Save  Boost 

Pick as gem

Copy link

Copied to Clipboard

[Share to X](https://twitter.com/intent/tweet?text=%22How%20to%20Build%20a%20Secure%20Google%20OAuth%202.0%20Login%20Using%20React%20%26%20Node.js%22%20by%20Sadee%20%23DEVCommunity%20https%3A%2F%2Fdev.to%2Fcodewithsadee%2Fhow-to-build-a-secure-google-oauth-20-login-using-react-nodejs-41mp)[Share to LinkedIn](https://www.linkedin.com/shareArticle?mini=true&url=https%3A%2F%2Fdev.to%2Fcodewithsadee%2Fhow-to-build-a-secure-google-oauth-20-login-using-react-nodejs-41mp&title=How%20to%20Build%20a%20Secure%20Google%20OAuth%202.0%20Login%20Using%20React%20%26%20Node.js&summary=Learn%20how%20to%20build%20a%20fast%20and%20safe%20%22Log%20in%20with%20Google%22%20system%20for%20your%20website%21%20In%20this...&source=DEV%20Community)[Share to Facebook](https://www.facebook.com/sharer.php?u=https%3A%2F%2Fdev.to%2Fcodewithsadee%2Fhow-to-build-a-secure-google-oauth-20-login-using-react-nodejs-41mp)[Share to Mastodon](https://s2f.kytta.dev/?text=https%3A%2F%2Fdev.to%2Fcodewithsadee%2Fhow-to-build-a-secure-google-oauth-20-login-using-react-nodejs-41mp)

[Share Post via...](https://dev.to/codewithsadee/how-to-build-a-secure-google-oauth-20-login-using-react-nodejs-41mp#)[Report Abuse](https://dev.to/report-abuse)

[![Image 10: Sadee](https://media2.dev.to/dynamic/image/width=50,height=50,fit=cover,gravity=auto,format=auto/https%3A%2F%2Fdev-to-uploads.s3.us-east-2.amazonaws.com%2Fuploads%2Fuser%2Fprofile_image%2F647690%2F7201eed0-e45f-462a-b581-5ee15a3c19b9.jpg)](https://dev.to/codewithsadee)

[Sadee](https://dev.to/codewithsadee)
Posted on Aug 31

![Image 11](https://assets.dev.to/assets/sparkle-heart-5f9bee3767e18deb1bb725290cb151c25234768a0e9a2bd39370c382d02920cf.svg)3![Image 12](https://assets.dev.to/assets/multi-unicorn-b44d6f8c23cdd00964192bedc38af3e82463978aa611b4365bd33a0f1f4f3e97.svg)1![Image 13](https://assets.dev.to/assets/exploding-head-daceb38d627e6ae9b730f36a1e390fca556a4289d5a41abb2c35068ad3e2c4b5.svg)1![Image 14](https://assets.dev.to/assets/raised-hands-74b2099fd66a39f2d7eed9305ee0f4553df0eb7b4f11b01b6b1b499973048fe5.svg)1![Image 15](https://assets.dev.to/assets/fire-f60e7a582391810302117f987b22a8ef04a2fe0df7e3258a5f49332df1cec71e.svg)2

# How to Build a Secure Google OAuth 2.0 Login Using React & Node.js

[#webdev](https://dev.to/t/webdev)[#beginners](https://dev.to/t/beginners)[#react](https://dev.to/t/react)[#tutorial](https://dev.to/t/tutorial)

[Video 3](https://www.youtube.com/watch?v=P-3uIOu1EuU)

Learn how to build a fast and safe "Log in with Google" system for your website! In this step-by-step tutorial, we use React, Node.js, Express, and MongoDB to create a complete Google OAuth 2.0 login feature from scratch. You will learn how to get your API keys from the Google Cloud Console, write the backend code, and connect it to your frontend screen.

🔗 Get the Full Source Code: [https://www.patreon.com/codewithsadee/posts/google-oauth-2-0-168192757](https://www.patreon.com/codewithsadee/posts/google-oauth-2-0-168192757)

 🔗 Get the Full Source Code 2: buymeacoffee.com/codewithsadee/e/571467

In this video, you will learn:

*   How Google OAuth 2.0 works in simple terms.
*   How to set up a project in the Google Cloud Console.
*   How to build a secure backend server with Node.js and Express.
*   How to design a beautiful frontend with React and TailwindCSS.

⏱️ Video Chapters (Timestamps):

 0:00 Intro

 3:10 Initial project

 4:43 Initial backend server

 17:44 Setup middlewares

 18:37 Setup auth routes

 22:32 Setup google auth

 43:23 Setup error middleware

 45:52 Handle server graceful shutdown

 50:39 Update project configurations

 53:47 Test auth route

 55:32 Setup express session for auth state

 1:01:54 Setup auth callback route and request user info

 1:14:57 Setup MongoDB

 1:25:58 Define user model and store user info

 1:37:30 Generate and set tokens in cookies after successful authentication

 1:47:10 Setup user routes

 1:58:59 Initial Frontend

 2:01:25 Implement login page and functionality

 2:18:17 Create home page

🛠️ Tech Stack Used:

 Frontend: React, TypeScript, TailwindCSS

 Backend: Node.js, Express

 Database: MongoDB

If you found this tutorial helpful, please drop a LIKE and SUBSCRIBE to the channel for more easy-to-follow web development projects!

DEV Community

*   [What's a billboard?](https://dev.to/billboards)
*   [Manage preferences](https://dev.to/settings/customization#sponsors)

* * *

*   [Report billboard](https://dev.to/report-abuse?billboard=264105)

[![Image 16: MLH article image](https://media2.dev.to/dynamic/image/width=775%2Cheight=%2Cfit=scale-down%2Cgravity=auto%2Cformat=auto/https%3A%2F%2Fdev-to-uploads.s3.us-east-2.amazonaws.com%2Fuploads%2Farticles%2Fvgl260d6tco1w2cfieoz.png)](https://blog.mlh.com/the-data-is-in-ai-is-how-developers-learn-now-28p4?bb=264105)

## [](https://dev.to/codewithsadee/how-to-build-a-secure-google-oauth-20-login-using-react-nodejs-41mp#the-data-is-in-ai-is-how-developers-learn-now)[The data is in: AI is how developers learn now](https://blog.mlh.com/the-data-is-in-ai-is-how-developers-learn-now-28p4?bb=264105)

In Major League Hacking's latest Season Census, 75% of verified respondents said they use AI in some form to learn technical skills. That's ahead of YouTube (71%) and online courses (59%). AI is now the single most common way new developers learn.

[Read more →](https://blog.mlh.com/the-data-is-in-ai-is-how-developers-learn-now-28p4?bb=264105)

 Read More 

## Top comments (1)

Subscribe

![Image 17: pic](https://media2.dev.to/dynamic/image/width=256,height=,fit=scale-down,gravity=auto,format=auto/https%3A%2F%2Fdev-to-uploads.s3.amazonaws.com%2Fuploads%2Farticles%2F8j7kvp660rqzt99zui8e.png)

Personal Trusted User[Create template](https://dev.to/settings/response-templates)
Templates let you quickly answer FAQs or store snippets for re-use.

Submit Preview[Dismiss](https://dev.to/404.html)

[](https://dev.to/codewithsadee/how-to-build-a-secure-google-oauth-20-login-using-react-nodejs-41mp)

[![Image 18: crdtcto profile image](https://media2.dev.to/dynamic/image/width=50,height=50,fit=cover,gravity=auto,format=auto/https%3A%2F%2Fdev-to-uploads.s3.us-east-2.amazonaws.com%2Fuploads%2Fuser%2Fprofile_image%2F4097220%2F35f9b907-bfa3-4f90-bfb2-4070300345b6.png)](https://dev.to/crdtcto)

[Kane Lim](https://dev.to/crdtcto)

 Kane Lim 

[![Image 19](https://media2.dev.to/dynamic/image/width=90,height=90,fit=cover,gravity=auto,format=auto/https%3A%2F%2Fdev-to-uploads.s3.us-east-2.amazonaws.com%2Fuploads%2Fuser%2Fprofile_image%2F4097220%2F35f9b907-bfa3-4f90-bfb2-4070300345b6.png) Kane Lim](https://dev.to/crdtcto)

Follow

 I am Kane Lim (telegram@kanelim1997), tech leader of a small private Hong Kong Remote Development Team. We are currently recruiting partners for long-term collaboration to generate revenue. 

*    Location   Hong Kong  
*    Joined  Aug 27, 2026 

•[Aug 31](https://dev.to/codewithsadee/how-to-build-a-secure-google-oauth-20-login-using-react-nodejs-41mp#comment-3dp5n)

*   [Copy link](https://dev.to/codewithsadee/how-to-build-a-secure-google-oauth-20-login-using-react-nodejs-41mp#comment-3dp5n)

*    Hide 

*   [Report abuse](https://dev.to/report-abuse?url=https://dev.to/crdtcto/comment/3dp5n)

Hello Glad to see you, I am Kane Lim from Hong Kong. I have over 10 years of development experience. I am writing this because your post was interesting.

This is a solid practical introduction, but I would emphasize that OAuth security is mostly about correctly handling trust boundaries rather than simply obtaining a Google token. On the backend, I would use Authorization Code with PKCE, validate the ID token signature, issuer, audience, nonce, and expiry, then derive identity from the verified Google subject rather than trusting profile fields.

For session security, HttpOnly Secure cookies with SameSite controls, short lived sessions, rotation, CSRF protection, and server side session invalidation are important. I would also enforce strict redirect URI validation and never expose client secrets to React.

MongoDB should store the stable provider subject and account metadata, not raw OAuth credentials. Adding rate limiting, structured authentication telemetry, replay detection, and account linking rules would make this much closer to production grade.

Nice tutorial for beginners. The next step is showing the threat model behind each security decision.

2 likes Like Reply

[Code of Conduct](https://dev.to/code-of-conduct)•[Report abuse](https://dev.to/report-abuse)

Are you sure you want to hide this comment? It will become hidden in your post, but will still be visible via the comment's [permalink](https://dev.to/codewithsadee/how-to-build-a-secure-google-oauth-20-login-using-react-nodejs-41mp#).

- [x] 
Hide child comments as well

 
Confirm

For further actions, you may consider blocking this person and/or [reporting abuse](https://dev.to/report-abuse)

[![Image 20: profile](https://media2.dev.to/dynamic/image/width=64,height=64,fit=cover,gravity=auto/https%3A%2F%2Fdev-to-uploads.s3.us-east-2.amazonaws.com%2Fuploads%2Forganization%2Fprofile_image%2F3774%2F99e0624e-6fb6-4460-819d-3a0d967519cb.webp) Sentry](https://dev.to/sentry)Promoted

*   [What's a billboard?](https://dev.to/billboards)
*   [Manage preferences](https://dev.to/settings/customization#sponsors)

* * *

*   [Report billboard](https://dev.to/report-abuse?billboard=244055)

[![Image 21: Sentry image](https://media2.dev.to/dynamic/image/width=775%2Cheight=%2Cfit=scale-down%2Cgravity=auto%2Cformat=auto/https%3A%2F%2Fi.imgur.com%2FrmXrMli.jpeg)](https://blog.sentry.io/logs-generally-available/?utm_source=devto&utm_medium=paid-community&utm_campaign=logs-fy26q3-logslaunch&utm_content=static-ad-logs-ga-launch-learnmore&bb=244055)

## [](https://dev.to/codewithsadee/how-to-build-a-secure-google-oauth-20-login-using-react-nodejs-41mp#structured-logs-connected-to-your-stack-traces-sentry-has-logs-ga)[Structured logs. Connected to your stack traces. Sentry Has Logs (GA) 🪵](https://blog.sentry.io/logs-generally-available/?utm_source=devto&utm_medium=paid-community&utm_campaign=logs-fy26q3-logslaunch&utm_content=static-ad-logs-ga-launch-learnmore&bb=244055)

Logs is out of beta and generally available to everyone. The best part, we added a bunch of capabilities you asked for during the beta period.

[See more →](https://blog.sentry.io/logs-generally-available/?utm_source=devto&utm_medium=paid-community&utm_campaign=logs-fy26q3-logslaunch&utm_content=static-ad-logs-ga-launch-learnmore&bb=244055)

[![Image 22](https://media2.dev.to/dynamic/image/width=90,height=90,fit=cover,gravity=auto,format=auto/https%3A%2F%2Fdev-to-uploads.s3.us-east-2.amazonaws.com%2Fuploads%2Fuser%2Fprofile_image%2F647690%2F7201eed0-e45f-462a-b581-5ee15a3c19b9.jpg) Sadee](https://dev.to/codewithsadee)

Follow

 Web developer ◽ Self taught ◽ Youtuber ◽ Web3 enthusiast 

*    Education   Self Taught  
*    Work   Founder & CEO at codewithsadee  
*    Joined  Jun 11, 2021 

### More from [Sadee](https://dev.to/codewithsadee)

[How to build a Bento portfolio using ReactJs + Typescript #webdev#tutorial#beginners#react](https://dev.to/codewithsadee/how-to-build-a-bento-portfolio-using-reactjs-typescript-2khj)[Build an Advance Weather APP With ReactJS #webdev#react#tutorial](https://dev.to/codewithsadee/build-an-advance-weather-app-with-reactjs-2joa)[Build a SaaS Admin Dashboard with React, Shadcn UI & TypeScript #webdev#tutorial#react#beginners](https://dev.to/codewithsadee/build-a-saas-admin-dashboard-with-react-shadcn-ui-typescript-23o4)

[![Image 23: profile](https://media2.dev.to/dynamic/image/width=64,height=64,fit=cover,gravity=auto,format=auto/https%3A%2F%2Fdev-to-uploads.s3.us-east-2.amazonaws.com%2Fuploads%2Forganization%2Fprofile_image%2F1%2Fd908a186-5651-4a5a-9f76-15200bc6801f.jpg) The DEV Team](https://dev.to/devteam)Promoted

*   [What's a billboard?](https://dev.to/billboards)
*   [Manage preferences](https://dev.to/settings/customization#sponsors)

* * *

*   [Report billboard](https://dev.to/report-abuse?billboard=264202)

[![Image 24: Hacktoberfest image](https://media2.dev.to/dynamic/image/width=350%2Cheight=%2Cfit=scale-down%2Cgravity=auto%2Cformat=auto/https%3A%2F%2Fi.imgur.com%2Fq5xco4l.png)](https://dev.to/mlh/preptember-is-here-plan-a-fest-for-your-local-community-5ce3?bb=264202)

## [](https://dev.to/codewithsadee/how-to-build-a-secure-google-oauth-20-login-using-react-nodejs-41mp#preptember-is-here-plan-a-fest-for-your-local-community)[Preptember is here!! Plan a Fest for your local community. 🎉](https://dev.to/mlh/preptember-is-here-plan-a-fest-for-your-local-community-5ce3?bb=264202)

September marks the official start of Preptember, a month dedicated to organizers planning local gatherings and getting ready for [Hacktoberfest](https://hacktoberfest.com/?bb=264202).

[Read more →](https://dev.to/mlh/preptember-is-here-plan-a-fest-for-your-local-community-5ce3?bb=264202)

👋 Kindness is contagious

*   [What's a billboard?](https://dev.to/billboards)
*   [Manage preferences](https://dev.to/settings/customization#sponsors)

* * *

*   [Report billboard](https://dev.to/report-abuse?billboard=236876)

Explore this insightful piece, celebrated by the caring DEV Community. **Programmers from all walks of life** are invited to contribute and expand our shared wisdom.

A simple "thank you" can make someone’s day—leave your kudos in the comments below!

On DEV, **spreading knowledge paves the way** and fortifies our camaraderie. Found this helpful? A brief note of appreciation to the author truly matters.

## [](https://dev.to/codewithsadee/how-to-build-a-secure-google-oauth-20-login-using-react-nodejs-41mp#-cta-httpsdevtoenterstatenewuser-)[Let’s Go!](https://dev.to/enter?state=new-user&bb=236876)

[DEV Community](https://dev.to/) — A space to discuss and keep up software development and manage your software career

*   [Home](https://dev.to/)
*   [DEV Challenges](https://dev.to/challenges)
*   [DEV++](https://dev.to/++)
*   [Videos](https://dev.to/videos)
*   [DEV Education Tracks](https://dev.to/deved)
*   [DEV Help](https://dev.to/help)
*   [Advertise on DEV](https://dev.to/advertise)
*   [Organization Accounts](https://dev.to/organizations)
*   [DEV Showcase](https://dev.to/showcase)
*   [About](https://dev.to/about)
*   [Contact](https://dev.to/contact)
*   [Free Postgres Database](https://dev.to/free-postgres-database-tier)
*   [DEV Shop](https://shop.forem.com/)
*   [MLH](https://mlh.io/)

*   [Code of Conduct](https://dev.to/code-of-conduct)
*   [Privacy Policy](https://dev.to/privacy)
*   [Terms of Use](https://dev.to/terms)

Built on [Forem](https://www.forem.com/) — the [open source](https://dev.to/t/opensource) software that powers [DEV](https://dev.to/) and other inclusive communities.

Made with love and [Ruby on Rails](https://dev.to/t/rails). DEV Community © 2016 - 2026.

![Image 25: DEV Community](https://media2.dev.to/dynamic/image/width=190,height=,fit=scale-down,gravity=auto,format=auto/https%3A%2F%2Fdev-to-uploads.s3.amazonaws.com%2Fuploads%2Farticles%2F8j7kvp660rqzt99zui8e.png)

We're a place where coders share, stay up-to-date and grow their careers.

[Log in](https://dev.to/enter?signup_subforem=1)[Create account](https://dev.to/enter?signup_subforem=1&state=new-user)

![Image 26](https://assets.dev.to/assets/sparkle-heart-5f9bee3767e18deb1bb725290cb151c25234768a0e9a2bd39370c382d02920cf.svg)![Image 27](https://assets.dev.to/assets/multi-unicorn-b44d6f8c23cdd00964192bedc38af3e82463978aa611b4365bd33a0f1f4f3e97.svg)![Image 28](https://assets.dev.to/assets/exploding-head-daceb38d627e6ae9b730f36a1e390fca556a4289d5a41abb2c35068ad3e2c4b5.svg)![Image 29](https://assets.dev.to/assets/raised-hands-74b2099fd66a39f2d7eed9305ee0f4553df0eb7b4f11b01b6b1b499973048fe5.svg)![Image 30](https://assets.dev.to/assets/fire-f60e7a582391810302117f987b22a8ef04a2fe0df7e3258a5f49332df1cec71e.svg)

<!-- media:youtube id="P-3uIOu1EuU" url="https://www.youtube.com/watch?v=P-3uIOu1EuU" -->

<!-- media:svg src="https://assets.dev.to/assets/sparkle-heart-5f9bee3767e18deb1bb725290cb151c25234768a0e9a2bd39370c382d02920cf.svg" -->

<!-- media:svg src="https://assets.dev.to/assets/multi-unicorn-b44d6f8c23cdd00964192bedc38af3e82463978aa611b4365bd33a0f1f4f3e97.svg" -->

<!-- media:svg src="https://assets.dev.to/assets/exploding-head-daceb38d627e6ae9b730f36a1e390fca556a4289d5a41abb2c35068ad3e2c4b5.svg" -->

<!-- media:svg src="https://assets.dev.to/assets/raised-hands-74b2099fd66a39f2d7eed9305ee0f4553df0eb7b4f11b01b6b1b499973048fe5.svg" -->

<!-- media:svg src="https://assets.dev.to/assets/fire-f60e7a582391810302117f987b22a8ef04a2fe0df7e3258a5f49332df1cec71e.svg" -->
