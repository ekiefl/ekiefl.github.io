---
layout: post
title: "Prelude"
categories: [psim]
excerpt: "It's been a long time coming."
comments: true
authors: [evan]
image:
  feature: psim/psim_banner.png
  display: true
---

{% capture images %}{{site.url}}/images/psim/psim-intro{% endcapture %}
{% include _toc.html %}

{:.notice}
I'm going to talk about pool, physics, math, softare, video game design, 3D modelling, and a bunch
of things that this project has led me to. But I am not pro pool player, physicist, mathematician,
software developer, video game designer, Blender guru, or anything. So much of what I say may be
misinformative, or even rub experts the wrong way. My apologies in advance for when such instances
inevitably arise.

## Motivation

Seven years ago (2013) I was an in undergraduate math class called "_Non-linear Dynamical Systems
and Chaos_" taught by Dr. Anthony Quas at the Univerity of Victoria. Our final project was to
investigate a chaotic system. Adam Paul, a good friend of mine, and I decided we would work on the
same project.  Since we would regularly ditch working on class assignments to instead play pool at
the on-campus pub, it seemed natural to pick pool as our chaotic system.
[Chaos](https://en.wikipedia.org/wiki/Chaos_theory) is loosely speaking defined as a deterministic
(non-random) system that exhibits extreme sensitivity to initial conditions, and so we figured the
pool break perfectly fit this description: the balls are governed by non-random and some would argue
even simplistic Newtonian physics, yet each break outcome appears unique and irreproducible (unless
you're Shane Van Boening). Ignoring variability in the cue ball velocity, this implies that the
vastness of break outcomes are determined by the milli- or maybe even micro-meter pertubations in
ball spacings in a given rack. To study this, we decided would create a physics simulation in Python
that simulated the break.

It kind of sounds like I'm chalking us up to having accomplished something amazing, however I would
like to assure you our accomplishments were far from impressive. From a physics standpoint, our model was very
skeletal. Every collision was instantaneous and elastic, and the trajectories were restricted to 2D.
We applied conservation of momentum and energy, and voila, that was our physics. From an
implementation standpoint, we used a discrete time integration approach with a constant time step, which is
computationally very ineffecient. Algorithm aside, the program exhibits zero respect for the art of programming
and is so poorly implemented with hardcoded variables and spaghetti logic that no one in their right
mind should lay eyes on it. I think showing the product of our efforts is in order:


[![2013-project]({{images}}/2013_project.gif)]({{images}}/2013_project.gif){:.center-img .width-50}

Not exactly what you would call realistic, or pretty. The GIF has a shitty black bar on the bottom,
which I find deserving. The quality of the code is even worse than the animation. I refuse to upload
it.

Because of the drastic potential for improvement, this project kind of sat in the back of my head
for years as unfinished business. Time passed, I got more invested in pool, bought my own table,
joined a pool league. Concurrently, I started a PhD at the University of Chicago doing computational
biology, and developed considerably as a programmer due to my line of research. Then the COVID-19
pandemic struck and I realized I needed something other than work to keep me stimulated during
quarantine. That's when I decided to undertake the project of making a physically accurate pool
simulator.

## Starting a massive project is hard

Self-motivated projects are amazing. You get to create something limited only by your imagination.
You decide what to work on and determine for yourself what is worth your time. No one tells you what
to do and there are no deadlines. There are no job performance reviews to stress about. You can work
at home, in a coffee shop, or in your underwear.

Basically, you're in charge of yourself, which is also why self-motivated projects are hard. Usually
there is some grandiose vision of what you want to achieve, and very little thought has went into
how that can be built from nothing. There are many details to work out, so many decisions to make,
and each of them could have crucial consequences on the quality of my code. How am I going to
visualize? Which graphics engine should I use? Should I write my own physics or does a physics
engine already exist. Can I assume balls are all the same size/mass? Will I pre-bake the table
geometry or allow tables to be procedurally made with arbitrary shapes and pocket locations? How
should my directory structure be laid out? How does my initial feature set dictate my code
structure? What features will I want in 6 months that my code structure does not allow for?

There is a saying that if one "_cannot see the forest for the trees_", they lack the perspective
required to see the big picture. The idea is that one can walk up to each tree and comprehend it,
but cannot see the larger pattern that is the forest. In contrast to this proverb, I would argue
that starting a large project is like being able to see the forest, but unable to see the trees it
is composed of. Your vision is the forest: a product of the entire thing. For me, it is the pool
simulation. It looks amazing and the physics is indistinguishable from reality. But I can't yet see
the trees that create this vision. And I think that is basically why most self-motivated projects do
not survive to product launch. It's too hard to even start, especially when you're by yourself.
There isn't a team dedicated to the physics engine, another for graphics, and another for the user
interface. It's just you, alone. At first I found this immobilizing, that's why I sat on this
project for so many years. But the sometimes you just gotta start, and this is that time.

