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

### I tried once before

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

### Goals

Making a pool simulator is a pretty vague statement that can be ambiguously interpreted. To keep
things more concrete, here are the primary goals of this project:

1. **Create a physics engine that simulates the trajectories of pool balls that a layman finds indistinguishable from reality.**
2. **Visualize pool shots using 3D graphics.**
3. **Make a game that let's the user play 9-ball.**
4. **Create an AI capable of playing the game.**

There is a saying that if one "_cannot see the forest for the trees_", they lack the perspective
required to see the big picture. The idea is that one can walk up to each tree and comprehend it,
but cannot see the larger pattern that is the forest. In contrast to this proverb, I would argue
that **starting a large project is like being able to see the forest, but unable to see the trees it
is composed of**. Your vision is the forest: a product of the entire thing. For me, it is the goals
I have laid out above. But I can't yet see the trees that create this vision. This blog post series
lays out my journey in trying to achieve these goals.
