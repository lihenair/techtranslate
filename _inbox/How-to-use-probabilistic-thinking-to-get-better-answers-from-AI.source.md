---
source_url: https://x.com/free_ai_guides/status/2099549707232309621
fetched_at: 2026-09-15T04:51:52Z
fetch_method: fxtwitter-article
issue: 315
author: AI Guides
published_at: 2026-09-14
cover_image: https://pbs.twimg.com/media/HSMMPLVbkAAWJWM.jpg:large
title_zh: 用概率思维从 AI 拿到更好的答案
tech_domain: ai
---

# How to use probabilistic thinking to get better answers from AI

Stop asking whether the assistant got it right. Start asking how many answers were possible.

On a settled question, the set of possible answers is small, and the answer you get holds from one day to the next. An open question has a wide set, and the answer you get is one draw from it, delivered in the same even tone.

Stephen Wolfram, a physicist who has built computational software for decades, described the mechanism in a 2023 essay. A chat model is trying to produce a reasonable continuation of the text in front of it, where reasonable means the kind of thing people have written after similar text across billions of web pages.

Adam Kalai and three co-authors, writing for OpenAI in 2025, came to a similar conclusion. Companies train and score models the way schools score exams, they argued, and on most exams a confident guess earns more than a blank, so the models learn to guess.

Probabilistic thinking, applied to a chat assistant, means treating every answer as one likely continuation among several, and using your prompt either to shrink that set or to see it before you trust a single draw.

## Every answer is a draw from a set

Four things are happening when the assistant replies, and each one matters for how you read the reply.

The assistant is choosing the text most likely to follow your message. It measures "most likely" against everything it read during training plus everything in front of it at that moment, which includes your message, any file you attached, and anything it pulled from a search. Change any of those inputs and the odds change with them.

It does not always take the single most likely word. Wolfram notes that a model which only ever picks the top word produces flat, repetitive text, so the systems people use pick a lower-ranked word some of the time on purpose. That is why the same question can produce two different answers on two different days. The setting that controls this sits in developer tools, and the chat window most people type into does not have it.

Tools change the odds. As their makers described it in September 2026, the major assistants search the web, read a file you attach, or write and run a small program when they judge that the question needs it, and each one lets you ask for those steps in plain words. OpenAI's help center says its assistant may search on its own when a question would benefit from current information.

Anthropic's documentation says its model runs code when a request involves data or non-trivial math and answers from memory for simple arithmetic and conversational questions. The word to notice is "may." A retrieved answer narrows the set to whatever came back from the search or the file. A fluent answer with no citation, no indication that it searched, and no code shown may have come from memory, however polished it reads.

Confidence is a style. Anthropic's interpretability team found in 2025 that its model's default is to decline when it lacks information, and that a separate "known entity" signal switches that default off once the model recognizes the subject. The switch misfires when the model recognizes a name but knows nothing else about it, and the result is a fluent, wrong answer with no change in tone. Kalai's group had a plainer example. Asked for an author's birthday on separate occasions, one system gave three different dates. All of them were wrong but were stated like facts.

Putting all these points together can explain the difference. On a question the model has seen answered thousands of times, or on one where a tool retrieved the answer, the probability piles onto one continuation. A judgment call, a synthesis of several sources, a recommendation, or a question with no source to retrieve spreads the probability across many continuations that all read well. The delivery does not tell you which kind you got, and the prompts below are something you can use to answer that.

![](https://pbs.twimg.com/media/HSMNYpwaUAQYdaD.jpg)

## Ask what was checked and what was guessed

The simplest version is one line added to any question. Ask the assistant to label each claim by where it came from.

Three labels work better than two in this case. “Retrieved” means the claim came from a search or a file, and the assistant should attach the link or quote the line.

“Remembered” means it came from training, with no source to point to.

“Inferred” means the assistant reasoned it out from the other two. 

Many confident errors fall under "remembered," and a two-way split between verified and unverified can hide them there.

Anthropic's documentation recommends two related methods. Give the model explicit permission to say it does not know. The company even reports this cuts false statements by a wide margin. Also, ask it to cite a source for each claim so you can audit the answer line by line.

Use the labels on facts. A recommendation has no source to retrieve, and demanding one pushes the model to invent a citation for a judgment. One labeled answer on a question you will act on is worth more than ten unlabeled ones. Why? Because it tells you which sentences to check.

If the assistant marks a claim as “remembered” and you needed it retrieved, ask for the search or the file read in your next message. The tool was available. The model judged that it did not need it, and you can overrule that.

## Ask for the shape of the answer before the answer

An open question has several answers a careful person might give. A single reply hides that. Two prompts make the assistant show you the set before it picks from it.

The first asks for candidates. Katherine Tian and colleagues found in 2023 that models that list several possible answers before committing express better-calibrated confidence than models asked for one answer at once, which matches a much older finding in psychology that people become less overconfident once they consider alternatives.

The useful addition is asking what would make each candidate right, which turns a list of options into a decision you can check against your own situation.

The second asks for a range instead of a point. Any number the assistant gives you for a cost, a timeline, or an outcome is one draw from a spread, and a single figure hides how wide that spread was.

Left alone, models produce ranges that are too tight. A 2025 benchmark called FermiEval asked several models for ranges they were 99 percent sure of, and the true answer landed inside those ranges about 65 percent of the time.

A 2026 forecasting benchmark, QuantSightBench, found the fix in the prompt itself. Telling the model how often the range should be right widened the ranges and improved them.

So say how often the range should hold, ask what would push the result outside it, and ask for the likely case last so it does not anchor the ends

Both prompts belong on open questions. On a checkable fact, the answer set has one item, and asking for candidates wastes a turn and invites the model to invent alternatives that do not exist.

## Narrow the set before the assistant fills it

The prompts above reveal the set. The next two shrink it by changing what the model is continuing from.

Every question carries assumptions, some yours and some the model's, and the assistant builds on all of them. Anthropic's 2025 interpretability work showed this with a math problem. 

Given a hint pointing at a particular final answer, the model worked backward and produced plausible-looking steps that landed on the hinted number instead of solving the problem. A wrong premise in your question works the same way. The model treats it as a fixed point and reasons toward it.

Ask for the assumptions before the answer, and ask for both kinds. Then correct the wrong ones and rerun the question as a fresh message with the corrected assumptions stated up front. 

Replying "no, actually" inside the same thread leaves the first answer sitting in front of the model, and the first answer stays the most likely continuation.

The second way to shrink the set is to describe the test that the answer must pass. This differs from adding detail about the topic. "Explain compound interest in detail" narrows the topic and leaves the set of acceptable answers wide. 

Change it to "explain compound interest so that someone who has never used a spreadsheet could work an example by hand, in under 200 words, with any term defined in the same sentence," and the set of qualifying answers shrinks, because the model can check its own draft against each line.

Anthropic's prompt engineering guide puts defining success criteria ahead of every other technique. In probability terms, each criterion removes continuations that would have read well and failed you.

Keep it to two or three criteria. Past that point, the model may focus more on passing the rules than finding the right answer.

## Rerun it and read the spread

The last piece catches what the others miss. Open a new chat, paste the same question, and do it two or three times.

Read the results as a measurement. On a checkable question, agreement across runs tells you little, because the model already had the answer and a rerun confirms it.

For an open question, agreement means the model's view is settled, which you should still verify. A spread suggests the question is open or the model is guessing, and either way you should not treat any single reply as the answer.

Kalai's birthday example shows how the spread can reveal guessing. Three runs, three dates, and the disagreement on its own was enough to show that the system was guessing.

Anthropic's documentation lists this among its techniques, running the same prompt several times and treating inconsistency between the outputs as a hallucination signal.

The original 2022 research on repeated sampling, by Xuezhi Wang and colleagues at Google, used the reruns to vote for the most common answer, a design built for weaker models that made frequent errors.

A later study argued that later models land on the same answer to a checkable question so often that voting adds almost nothing. For you, the reruns measure the spread, and where a spread exists, you have learned something a single answer could not tell you.

Agreement is still not proof. A model can be wrong every time when the wrong answer is the common one in its training. Reruns also cost time, so reserve them for answers you will act on, and start a new chat each time. A rerun inside the same conversation leans toward the first answer because the first answer is already in front of it.

## The question you stop asking

After a few weeks of this, the change shows up in your own questions before it shows up in the assistant's answers.

You stop asking whether the assistant is right and start asking how wide the set was. A confident sentence stops reading as evidence and starts reading as tone. Checking moves from the end of the conversation, where you audit a finished answer, to the start, where you shape the question so the set is small or visible.

None of this is distrust. You are learning which of the assistant's answers came from a narrow set and which came from a wide one, and spending your checking time on the second kind.

The assistant did not get more accurate. You got better at telling which of its answers were stable, a difference the tone never showed.

![](https://pbs.twimg.com/media/HSMZCFubwAAmU1I.jpg)

Stop asking whether the answer is right. Ask how many answers were possible.

Every reply is one draw from a set, and your prompt decides how big the set is and whether you get to see it.

Pick two of these prompts and use them all week. By the following Monday, you will notice the set behind every answer, and the people who waited will still be trusting a tone.

If you found this useful, check out my newsletter below

I share one AI superpower every week

Subscribe, it's free

https://linktr.ee/alex_prompter

<!-- media:section-anim index="1" duration_s="4" -->

<!-- media:section-anim index="2" duration_s="4" -->

<!-- media:section-anim index="3" duration_s="4" -->

<!-- media:section-anim index="4" duration_s="4" -->

<!-- media:section-anim index="5" duration_s="4" -->

<!-- media:section-anim index="6" duration_s="4" -->

<!-- media:section-anim index="7" duration_s="4" -->

<!-- media:section-anim index="8" duration_s="4" -->
