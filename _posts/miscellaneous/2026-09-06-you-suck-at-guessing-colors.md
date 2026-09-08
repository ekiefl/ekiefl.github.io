---
layout: post
title: "You suck at memorizing colors"
categories: [miscellaneous]
series: 2
excerpt: "I built a two-agent color telephone game to find out whether language models communicate color better than you remember it."
comments: true
authors: [evan]
---

{% capture images %}{{site.url}}/images/miscellaneous/llm-color-eval{% endcapture %}

## The game

My friends tend to be competitive. Especially about anything trivial, exceptionally niche, or generally void of utility. Like geography, or this dinky color game we started braggadociously sharing our high scores for ([dialed.gg](https://dialed.gg)). The premise is to memorize a color flashed on the screen, then to reconstruct it blind.

I'm so bad at this game (not colorblind) that I wondered whether a large language model (LLM), which has never seen a color---and is therefore definitely colorblind---might outperform me in this game.

Long story boring, it turns out that LLMs are much better at color than I am. And before you cast judgment, I urge you to see how well you do:

<iframe src="https://ekiefl.github.io/llm-color-eval/" height="680" scrolling="no"
        style="border:none; border-radius:18px; margin: 8px 0 24px; width:1px; min-width:100%;"></iframe>

If you won, congrats. STOP READING.

## So you're a loser, too

Welcome. But in fairness to us, it's not even an apples-to-apples comparison. Here's what the AI was actually doing, which is totally different than the truly impossible task *we* were given.

Basically, it's a game of telephone between two agents. The first agent is given the hexadecimal code for the color and its task is to---from only the code---describe the color in **5 words**. Then, a second agent is given that description and tasked with guessing the hexcode of the color.

[![pipeline]({{images}}/pipeline.svg)]({{images}}/pipeline.svg){:.center-img .width-90}
_**Figure 1**. The two-agent telephone game. The describer is shown a color and gets a budget of plain-English words to convey it (a validator rejects and retries any attempt to smuggle in privileged information like hexcodes themselves or "70% red, 20% green, 10% blue"). The guesser answers with a color based on nothing but those words._

Honestly, it's miraculous it does so well. Starting from just six ASCII characters, the describer writes a description faithful enough that a second agent can guess the color better than my ape brain can recreate a color I imprinted into my visual cortex just seconds earlier.

So it's not apples-to-apples because the tasks are different. But the AI's task seems way harder, so shame is definitely still on the table.

Anyways, enjoy the game. The rest of this post outlines some interesting LLM color perception analyses I ran along the way.

## Description length helps, then plateaus

I parameterized a word budget for the describer and then scanned to see how description length impacted guess accuracy.

Hover over the chart to read how the describer actually spent each budget on one example color:

<iframe src="https://ekiefl.github.io/llm-color-eval/budget.html" height="660" scrolling="no"
        style="border:none; margin: 8px 0 16px; width:1px; min-width:100%;"></iframe>

_**Figure 2**. Guess accuracy versus the describer's word budget. Hover or tap a budget to read a real description written at that length, and the score it earned. You lost against the 5-word budget version._

Going in, I was confident this would be a hump: too few words starve the guesser, too many confuses it with noise. But as the chart shows, it's more of a plateau.

## Cross-model guessing

I ran these experiments with Sonnet 5 (the one you went up against) and gpt-oss-20b (a small, open, free, bad model). I was curious whether the smaller, worse, bad one was bad at writing the descriptions, or bad at guessing a color from them. So I took every description gpt-oss wrote and had Sonnet guess from them.

| describer &rarr; guesser | 5 words | 15 words | 30 words |
|---|---:|---:|---:|
| gpt-oss &rarr; gpt-oss | 7.81 | 8.04 | 7.96 |
| gpt-oss &rarr; Sonnet | 8.20 | 8.41 | 8.36 |
| Sonnet &rarr; Sonnet | 8.48 | 8.56 | 8.62 |

So in other words, gpt-oss's descriptions were mostly fine all along, with maybe a little room for improvement. And Sonnet 5 is able to work with them and still get pretty good scores. It's mostly gpt-oss's ability to guess that struggles.

## We're obsessed with red and we hate green

Some colors take the limelight. No one likes pukey green or yellow tuna, but everyone is obsessed with crimson. I'm not just being opinionated. In the *World Color Survey*, MIT scientists ([Gibson et al. 2017](https://www.pnas.org/doi/10.1073/pnas.1619666114)) found that across more than a hundred languages, warm colors are communicated more efficiently than cool ones. Their offered explanation was evolutionarily grounded: the things humans handle, eat, and bleed---fruit, berries, animals, each other---are mostly warm-colored, while cool colors are just the background like sky, ocean, foliage. Objects obviously need distinguishing, so warm colors got all the good words.

If that's true, then an LLM trained on our language should inherit a similar bias.

[![hue difficulty]({{images}}/hue_combined.svg)]({{images}}/hue_combined.svg){:.center-img .width-100}
_**Figure 3**. Left: each of the two thousand colors, plotted in its own color, and the score the AI got on a five-word budget. Right: the same data on a color wheel. Hue runs around and brightness grows outward. Cells are shaded according to model score. The outer wavy black ring is the left panel's rolling mean, wrapped around._

So as we can see, the model has a *green problem*. Scores dip a full point compared to red, which the model is much more attuned to. This is just what those MIT scientists wanted you to believe and honestly, it tracks. There's like 4 descriptors for green and one of them is *booger green*. Meanwhile there's a way tighter linguistic resolution on red: crimson, scarlet, burgundy, maroon, ruby, cherry, brick, vermilion, and rose. I'm obviously bad at color so I didn't come up with those, I copy-pasted them from Google.

If you look at the color wheel heatmap you also see where the model has blind spots as a function of brightness. Bright colors are on the outside of the circle, dark colors on the inside, and the cells shade the model's score for that *hue + brightness* combo. This provides a little more insight into the model's shortcomings. In particular it struggles in that booger green region, whereas it does OK in the brighter greeny neon region. *God*, if only I had the words to properly describe what I'm talking about.

So once again, we see these language models are merely a reflection of ourselves. Just as ChatGPT regurgitates racist 4chan rhetoric that it was trained on---unless it's strapped tightly into its shareholder-approved harness---the model's color biases are a reflection of ourselves. The end.
