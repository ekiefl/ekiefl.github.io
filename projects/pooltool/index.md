---
layout: project-main
title: "Realistic pool simulator"
redirect_from:
excerpt: "pooltool project page"
project: pooltool
image:
  feature: "pooltool/pooltool_banner.png"
  display: true
---

{% include _toc.html %}

<img src="{{site.url}}/images/pooltool/pooltool_logo.png" alt="drawing" width="480px" class="no-border"/>

## Links

- [github](https://github.com/ekiefl/pooltool)
- [Read the docs](https://pooltool.readthedocs.io/en/latest/)

## Landing for the **pooltool** blog series

Pooltool is a general purpose billiards simulator crafted specifically for science and engineering (you can also play it as a game).

Its core design principles focus on speed, flexibility, and the ease of visualization and analysis. With an interactive 3D interface, a robust API, and extensive documentation, pooltool aims to be a systemic tool in billiards-related research. Continuously evolving through active maintenance and bolstered by a growing community, this vision for pooltool emphasizes not just its current capabilities, but also its potential for growth and adaptation within billiards simulation.

Much about pooltool has been blogged, particularly during its early days of development.

## Blog summaries

### [Blog #1 - 04/21/2020](https://ekiefl.github.io/2020/04/24/pooltool-theory/)

- I do a literature review on the physics of billiards
- I outline and explain the models I plan to use for each physical process

<img src="{{site.url}}/images/pooltool/pooltool-theory/sliding_diagram.jpg" alt="drawing" width="480px" class="no-border"/>

### [Blog #2 - 12/20/2020](https://ekiefl.github.io/2020/12/20/pooltool-alg/)

- I research different shot evolution algorithms
- I discover the event-based shot evolution algorithm by Leckie and Greenspan
- I describe in honestly excruciating detail the ins and outs of the algorithm

<img src="{{site.url}}/images/pooltool/pooltool-alg/all_events.jpg" alt="drawing" width="480px" class="no-border"/>

### [Blog #3 - 03/25/2021](https://ekiefl.github.io/2021/03/25/pooltool-start/)

- I start pooltool
- I develop a prototypical pool simulator that can evolve shots according to a discrete time stepping algorithm, or the event-based algorithm
- I create a 2D, non-interactive visualization of simulated shots using pygame

<img src="{{site.url}}/images/pooltool/pooltool-start/before_after.gif" alt="drawing" width="480px" class="no-border"/>


### [Blog #4 - 08/11/2021](https://ekiefl.github.io/2021/04/17/going-3d/)

- I graduate to panda3d
- I render all essential objects and HUD (badly)
- I implement all foreseeable user controls
- I defined different game modes that the user can play (8-ball and 9-ball)

<img src="{{site.url}}/images/pooltool/pooltool-going-3d/before_after.gif" alt="drawing" width="480px" class="no-border"/>

{% include youtube_embed.html id="aqjX0-A-YUw" %}


### [Blog #5 - 10/26/2021](https://ekiefl.github.io/2021/10/26/graphics/)

- I learn blender
- I model a table, balls, a cue, and a room
- I implement a collision resolver so the cue doesn't intersect with geometry

<img src="{{site.url}}/images/pooltool/pooltool-graphics/before_after.gif" alt="drawing" width="480px" class="no-border"/>
<img src="{{site.url}}/images/pooltool/pooltool-graphics/gallery_2.png" alt="drawing" width="480px" class="no-border"/>


### [Blog #6 - 05/03/2023](https://ekiefl.github.io/2023/05/03/update/)

- A general update with lots of gameplay footage

{% include youtube_embed.html id="dkH8vPI-rds" %}


