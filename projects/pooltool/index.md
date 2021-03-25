---
layout: project-main
title: "Realistic pool simulator"
redirect_from:
excerpt: "pooltool project page"
project: pooltool
image:
  feature: "pooltool/pooltool_banner.png"
  display: true
  credit: 'https://www.youtube.com/watch?v=6nlLJnruYVA'
---

{% capture images %}{{site.url}}/images/pooltool/pooltool-intro{% endcapture %}
{% include _toc.html %}

## Homepage of **pooltool**

*pooltool* is an [open source](https://github.com/ekiefl/pooltool) sandbox billiards game that emphasizes realistic physics. You can play any form of billiards, experiment with different physics settings, or you use the API to investigate billiards-related research questions. Keep reading for an intro into the topic or **scroll down for posts of this blog series**.

### Backstory

Why am I doing this?

Seven years ago (2013) I was an in undergraduate math class called "_Non-linear Dynamical Systems
and Chaos_" taught by Dr. Anthony Quas at the Univerity of Victoria. The final project was to model
a chaotic system, and so Adam Paul (a good friend of mine) and I thought a pool break perfectly fit
the description of a chaotic system: a deterministic (non-random) system that exhibits extreme
sensitivity to initial conditions. The balls are governed by non-random, simplistic Newtonian
physics, yet each break outcome appears unique and irreproducible. And so to study this, we created
a physics simulation of the pool break.

It sounds like I'm chalking us up to having accomplished something amazing, but it was all far from
impressive. From a physics standpoint, our model was very skeletal, exhibiting instantaneous and
elastic collisions with trajectories restricted to 2D.

Basically, we applied conservation of
momentum and energy of idealistic particles, and voila, that was our physics.

From an implementation
standpoint, we used a discrete time integration approach with a constant time step, and implemented
everything with hardcoded variables and spaghetti logic that is physically painful to take
ownership of. Here is the product of our efforts:

[![2013-project]({{images}}/2013_project.gif)]({{images}}/2013_project.gif){:.center-img .width-50}

Not exactly what you would call realistic, or pretty.

Because of the drastic potential for improvement, making a realistic pool simulator has weighed on
me for years, and **I consider it unfinished business**.

As time passed, I got more involved in the
game, bought my own table, even joined a league. Concurrently, I started a PhD at the University of
Chicago doing computational biology, and developed considerably as a programmer due to my line of
research. Then the COVID-19 pandemic struck and I realized I needed something other than work to
keep me stimulated during quarantine. That's when I decided to undertake the project of making a
physically accurate pool simulator.

### What's out there?

Before starting, I wanted to scope out what's currently on the market. Apparently, the most
realistic 3D pool simulator is [ShootersPool
Billards Simulation](https://www.shooterspool.net/) (see [this discussion](https://steamcommunity.com/app/336150/discussions/0/1520386297698310602/) for comparison with [Virtual Pool 4](http://vponline.celeris.com/)). I checked out
some of the demo videos. And boy, are they beautiful.

{% include youtube_embed.html id="sDW0ENZzClk" %}

Both from a graphics and physics perspective, this appears very real. The only physical inaccuracy I
can spot is as balls are entering the pockets they seem to undergo a pre-baked animation rather than
interacting genuinely with the pocket. Interestingly, this game started as a university project by a
software developer / pool player. Goals.

Unfortunately, ShootersPool is a commerical project with closed source code.

### Open source

ShootersPool is a cool game, but I want to make more than a game. I want to make a **pool physics sandbox game** for exploring
and experimenting with billiards physics. I want to give that control to the user so they can create unique table
layouts with 10,000 balls on a spherical table with moon gravity. Because why not? And the only way to give **full** control is to make it open source.

I'm not the first person to make an open source pool physics simulator. In fact there's countless (see [here](https://github.com/topics/billiards?o=asc&s=forks) for example), and they vary in quality. The vast majority are half-baked course projects, but there are a couple that stood out to me (non-exhaustive list here):

[poolvr](https://jzitelli.github.io/poolvr/) is a very cool open source project for playing pool in VR. I couldn't take full advantage of the controls without a VR headset, but this [youtube playlist](https://www.youtube.com/watch?v=_zrm2e6uJDc&list=PLfO_NjmfXp1yuMxgKFfVMQyQRgpsEINGK&index=1) has me convinced there is some sophisticated physics for modelling ball-ball and ball-cushion interactions, however the implementation seems buggy at times.  This was recently reimplemented as a [python project](https://github.com/jzitelli/poolvr.py) with a new physics engine, so maybe it's better now.

[python-billiards](https://github.com/markus-ebke/python-billiards) is a 2D billiards engine written in Python that
allows one to programmatically define a table and balls, and will evolve evolve the system that emerges. I like this project because
it achieves one of the goals of pooltool, which is to have a fully functioning API by which other people can create their
own scenes, however ridiculous.

The amazingly titled [billiards-python-project](https://github.com/FlinnPond/billiards-python-project) deserves mention because it introduced me to
panda3d, a 3D game engine in python... More on that later.

Each of these projects have given me something to chew on in terms of inspiration. So thanks to all of you.

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

