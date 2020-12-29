---
layout: project-main
title: "Realistic pool simulator"
redirect_from:
excerpt: "psim project page"
project: psim
image:
  feature: "psim/psim_banner.png"
  display: true
  credit: 'https://www.youtube.com/watch?v=6nlLJnruYVA'
---

{% capture images %}{{site.url}}/images/psim/psim-intro{% endcapture %}
{% include _toc.html %}

## Homepage of **psim**

This is the homepage for my project *psim*, which focuses on creating a realistic billiards/pool
simulator. Keep reading for an intro into the topic or scroll down to the bottom to see the blog
posts of this series.

### History

Seven years ago (2013) I was an in undergraduate math class called "_Non-linear Dynamical Systems
and Chaos_" taught by Dr. Anthony Quas at the Univerity of Victoria. The final project was to model
a chaotic system, and so Adam Paul (a good friend of mine) and I thought a pool break perfectly fit
the description of a chaotic system: a deterministic (non-random) system that exhibits extreme
sensitivity to initial conditions. The balls are governed by non-random, simplistic Newtonian
physics, yet each break outcome appears unique and irreproducible. And so to study this, we created
a physics simulation of the pool break.

It sounds like I'm chalking us up to having accomplished something amazing, but it was all far from
impressive. From a physics standpoint, our model was very skeletal, exhibiting instantaneous and
elastic collisions with trajectories restricted to 2D. Basically, we applied conservation of
momentum and energy of idealistic particles, and voila, that was our physics. From an implementation
standpoint, we used a discrete time integration approach with a constant time step, and implemented
everything with hardcoded variables and spaghetti logic that is physically painful to take
ownership of. Here is the product of our efforts:

[![2013-project]({{images}}/2013_project.gif)]({{images}}/2013_project.gif){:.center-img .width-50}

Not exactly what you would call realistic, or pretty. The GIF has a shitty black bar on the bottom,
which I find deserving.

Because of the drastic potential for improvement, making a realistic pool simulator has weighed on
me for years, and I consider it unfinished business. As time passed, I got more involved in the
game, bought my own table, even joined a league. Concurrently, I started a PhD at the University of
Chicago doing computational biology, and developed considerably as a programmer due to my line of
research. Then the COVID-19 pandemic struck and I realized I needed something other than work to
keep me stimulated during quarantine. That's when I decided to undertake the project of making a
physically accurate pool simulator.

### What's currently out there?

Before starting, I wanted to scope out what's currently on the market. The two most
realistic 3D pool simulators are [Virtual Pool 4](http://vponline.celeris.com/), and [ShootersPool
Billards Simulation](https://www.shooterspool.net/). I haven't played ShootersPool, but according to
[this thread](https://steamcommunity.com/app/336150/discussions/0/1520386297698310602/), it seems to
be favored by most gamers for its graphics and increased realism. To get acquainted, I checked out
some of the demo videos. And boy, are they beautiful.

{% include youtube_embed.html id="sDW0ENZzClk" %}

Both from a graphics and physics perspective, this appears very real. The only physical inaccuracy I
can spot is as balls are entering the pockets they seem to undergo a pre-baked animation rather than
interacting genuinely with the pocket. Interestingly, this game started as a university project by a
software developer / pool player. Goals.

For comparison, let's look at Virtual Pool 4.

{% include youtube_embed.html id="mAxACAt6m8g" %}

The graphics are definitely less impressive and the frame rate seems lower, and there's no slow-mo
to scrutinize in careful detail. Nevertheless, I have played this game before and it is very
realistic--certainly an impressive feat.

These are both commerical projects, and I was unable to find any open source projects worth mentioning.
My hope is to create something open source that other pool enthusiasts can use for their own
project.

### Goals

Making a pool simulator is a pretty vague statement that can be ambiguously interpreted. To keep
things more concrete, here are the primary goals of this project:

1. **Create a physics engine that simulates the trajectories of pool balls that a layman finds indistinguishable from reality.**
2. **Visualize pool shots using 3D graphics.**
3. **Make an game that let's the user play 9-ball.**
4. **Create an AI capable of playing the game.**

There is a saying that if one "_cannot see the forest for the trees_", they lack the perspective
required to see the big picture. The idea is that one can walk up to each tree and comprehend it,
but cannot see the larger pattern that is the forest. In contrast to this proverb, I would argue
that **starting a large project is like being able to see the forest, but unable to see the trees it
is composed of**. Your vision is the forest: a product of the entire thing. For me, it is the goals
I have laid out above. But I can't yet see the trees that create this vision. This blog post series
lays out my journey in trying to achieve these goals.

