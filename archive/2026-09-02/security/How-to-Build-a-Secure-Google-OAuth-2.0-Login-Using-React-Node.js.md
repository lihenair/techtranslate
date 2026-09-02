---
title: "用 React 与 Node.js 构建安全的 Google OAuth 2.0 登录"
title_en: "How to Build a Secure Google OAuth 2.0 Login Using React & Node.js"
source_url: https://dev.to/codewithsadee/how-to-build-a-secure-google-oauth-20-login-using-react-nodejs-41mp
author: Sadee
published_at: 2026-08-31
translated_at: 2026-09-02
tech_domain: security
tags: [oauth, security, react, nodejs, authentication, mongodb]
cover_image: https://media2.dev.to/dynamic/image/width=1200,height=627,fit=cover,gravity=auto,format=auto/https%3A%2F%2Fdev-to-uploads.s3.us-east-2.amazonaws.com%2Fuploads%2Farticles%2Fbrgw3z3n53dlg5m2ydfm.png
---

# 用 React 与 Node.js 构建安全的 Google OAuth 2.0 登录

原文链接：<https://dev.to/codewithsadee/how-to-build-a-secure-google-oauth-20-login-using-react-nodejs-41mp>

原文作者：Sadee

![文章头图](https://media2.dev.to/dynamic/image/width=1200,height=627,fit=cover,gravity=auto,format=auto/https%3A%2F%2Fdev-to-uploads.s3.us-east-2.amazonaws.com%2Fuploads%2Farticles%2Fbrgw3z3n53dlg5m2ydfm.png)

作者：[Sadee](https://dev.to/codewithsadee)

发布于 2026 年 8 月 31 日。

**一步步用 React、Node.js、Express 和 MongoDB，从零搭一套「用 Google 登录」（Log in with Google）的 Google OAuth 2.0 流程——从 Google Cloud Console 拿密钥，到后端与前端对接。**

[嵌入内容（原站 YouTube）](https://www.youtube.com/watch?v=P-3uIOu1EuU)

学怎么给网站做一套又快又安全的「用 Google 登录」。本教程用 React、Node.js、Express、MongoDB，从零写完整的 Google OAuth 2.0 登录。你会学到：在 Google Cloud Console 申请 API 密钥、写后端、再接到前端页面。

🔗 完整源码：[https://www.patreon.com/codewithsadee/posts/google-oauth-2-0-168192757](https://www.patreon.com/codewithsadee/posts/google-oauth-2-0-168192757)

🔗 完整源码 2：buymeacoffee.com/codewithsadee/e/571467

## [本视频你会学到](#in-this-video-you-will-learn)

* 用白话讲清 Google OAuth 2.0 怎么工作
* 如何在 Google Cloud Console 建项目
* 如何用 Node.js 与 Express 搭安全的后端
* 如何用 React 与 TailwindCSS 做前端界面

## [视频章节（时间戳）](#video-chapters-timestamps)

| 时间 | 内容 |
| --- | --- |
| 0:00 | 开场 |
| 3:10 | 初始化项目 |
| 4:43 | 初始化后端服务 |
| 17:44 | 配置中间件 |
| 18:37 | 配置鉴权路由 |
| 22:32 | 配置 Google Auth |
| 43:23 | 配置错误中间件 |
| 45:52 | 优雅关闭服务 |
| 50:39 | 更新项目配置 |
| 53:47 | 测试鉴权路由 |
| 55:32 | 用 Express Session 管鉴权状态 |
| 1:01:54 | 配置回调路由并请求用户信息 |
| 1:14:57 | 配置 MongoDB |
| 1:25:58 | 定义用户模型并落库 |
| 1:37:30 | 鉴权成功后签发 token 写入 cookie |
| 1:47:10 | 配置用户路由 |
| 1:58:59 | 初始化前端 |
| 2:01:25 | 实现登录页与登录逻辑 |
| 2:18:17 | 创建首页 |

## [技术栈](#tech-stack-used)

* 前端：React、TypeScript、TailwindCSS
* 后端：Node.js、Express
* 数据库：MongoDB

觉得有用的话，给视频点赞并订阅频道，后面还有更多易上手的 Web 开发项目。
