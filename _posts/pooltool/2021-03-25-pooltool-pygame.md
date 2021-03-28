---
layout: post
title: "Billiards simulator III: visualizing simulated pool shots"
categories: [pooltool]
excerpt: "A preliminary implementation that supports visualization with pygame"
comments: true
authors: [evan]
image:
  feature: pooltool/pooltool_banner.png
  display: true
---

{% capture images %}{{site.url}}/images/pooltool/pooltool-pygame{% endcapture %}
{% include _toc.html %}

## Outline

In the [first]({{ site.url }}/2020/04/24/pooltool-theory/) and [second]({{ site.url }}/2020/12/20/pooltool-alg/) posts of this series, I discussed _ad nauseam_ the physics and algorithmic theory behind pool simulation. With this all now behind me, it's time to **take this theory to the streets**.

## The skeleton

This project started with 2 main modules: `engine.py` and `physics.py`. The rationale for this design was to separate the **physics** from the **objects** that the physics acts on (balls, cues, cushions, etc).

With this in mind, `engine.py` implements the shot evolution algorithm by coordinating when object states should be modified, and `physics.py` implements the physics that provides the specific rules for how the modification should be carried out. This separation of responsibility allows different physics models to be plugged in or out at will.

Though the codebase has changed dramatically since this original implementation, this principle has remained unchanged.

## Ball trajectories

<div class="extra-info" markdown="1">
<span class="extra-info-header">Want to follow along?</span>

If you want to follow along, go ahead and clone the repository, and then checkout this branch

```bash
git clone https://github.com/ekiefl/pooltool.git
cd pooltool
git checkout f79c801_offshoot
```

</div>

My first goal was to start dead simple: visualize the trajectory of the cue ball that has been struck with a cue stick, assuming there are no cushions, pockets, or other balls. I implemented this in the `engine.ShotSimulation` class.

Let's peer in.

```python
In [1]: from psim.engine import ShotSimulation
   ...: shot = ShotSimulation()
   ...: shot.setup_test()
```

`shot` instantiates objects you wouldn't be surprised to find in a pool simulation: `Ball`, `Table`, and `Cue` objects. For example, here are the attributes of the cue ball.

```python
In [2]: vars(shot.balls['cue'])
Out[2]:
{'id': 'cue',
 'm': 0.170097,
 'R': 0.028575,
 'I': 5.555576388825e-05,
 'rvw': array(
     [[0.686, 0.33 , 0.   ],
      [0.   , 0.   , 0.   ],
      [0.   , 0.   , 0.   ]]
 ),
 's': 0,
 'history': {'t': [], 'rvw': [], 's': []}}
```

Of these attributes, the most important is `rvw`, which stores the [ball state](https://ekiefl.github.io/2020/12/20/pooltool-alg/#what-is-the-system-state) as a 3x3 `numpy` array. `rvw` is named after the 3 state vectors $\vec{r}(t)$, $\vec{v}(t)$, and $\vec{\omega}(t)$.

1. `rvw[0,:]` is the displacement vector $\vec{r}(t)$
2. `rvw[1,:]` is the velocity vector $\vec{v}(t)$
3. `rvw[2,:]` is the angular velocity vector $\vec{\omega}(t)$.

This means the velocity of the cue ball is

```python
In [3]: shot.balls['cue'].rvw[1,:]
Out[3]: array([0., 0., 0.])
```

In other words, it's not moving. To simulate something meaningful, energy has to be added to the system. In billiards, that's done with the `Cue`:

```python
In [4]: vars(shot.cue)
Out[4]: {'M': 0.567, 'brand': 'Predator'}
```

This is a 20oz Predator--those are expensive. Unsurprisingly, `shot.cue` has a method for striking balls.

```python
In [5]: shot.cue.strike?
Signature: shot.cue.strike(ball, V0, phi, theta, a, b)
Docstring:
"""
Strike a ball
                          , - ~  ,
◎───────────◎         , '          ' ,
│           │       ,             ◎    ,
│      /    │      ,              │     ,
│     /     │     ,               │ b    ,
◎    / phi  ◎     ,           ────┘      ,
│   /___    │     ,            -a        ,
│           │      ,                    ,
│           │       ,                  ,
◎───────────◎         ,               '
  bottom rail           ' - , _ , -
                 ______________________________
                          playing surface
Parameters
==========
ball : engine.Ball
    A ball object
V0 : positive float
    What initial velocity does the cue strike the ball?
phi : float (degrees)
    The direction you strike the ball in relation to the bottom rail
theta : float (degrees)
    How elevated is the cue from the playing surface, in degrees?
a : float
    How much side english should be put on? -1 being rightmost side of ball, +1 being
    leftmost side of ball
b : float
    How much vertical english should be put on? -1 being bottom-most side of ball, +1 being
    topmost side of ball
File:      ~/Software/pooltool_testing/psim/engine.py
Type:      method
"""
```

{:.notice}
This method ultimately calls upon [`physics.cue_strike`](https://github.com/ekiefl/pooltool/blob/51552ff7704376682359059b5dbd8a093f4ded17/psim/physics.py#L102), which implements the cue-ball interaction physics described [here]({{ site.url }}/2020/04/24/pooltool-theory/#section-vi-ball-cue-interactions).

I'm going to strike the cue ball with a center-ball hit $(a=0, b=0)$ straight down the table $(\phi=90)$ with the cue completely level with the table $(\theta = 0)$. I'll use a relatively slow impact speed of $V_0 = 0.5 \, \text{m/s}$.

```python
In [5]: shot.cue.strike(
   ...:     ball = shot.balls['cue'],
   ...:     V0 = 0.5,
   ...:     phi = 90,
   ...:     theta = 0,
   ...:     a = 0,
   ...:     b = 0,
   ...: )

In [6]: shot.balls['cue'].rvw
Out[6]:
array([[0.686, 0.33 , 0.   ],
       [0.   , 0.877, 0.   ],
       [0.   , 0.   , 0.   ]])
```

After calling the method, the cue ball now has a $0.88 \, \text{m/s}$ velocity in the $y-$direction. Since it was a center ball hit with no cue elevation, the ball has no spin. _i.e._ $\vec{\omega} = \langle 0,0,0 \rangle$.

At this point, no time has passed--the ball state has merely been modified according the physics of `shot.cue` striking `self.balls['cue']`. So then **how does the shot evolve**?

Rather than implementing the event-based shot evolution algorithm I [wouldn't shut up about]({{ site.url }}/2020/12/20/pooltool-alg/#continuous-event-based-evolution), I implemented some dinky discrete time evolution algorithm just to get the _ball rolling_. It's a for loop that increments by $50 \text{ms}$.

```python
q = self.balls['cue']

for t in np.arange(0, 10, 0.05):
    rvw, s = physics.evolve_ball_motion(
        rvw=q.rvw,
        R=q.R,
        m=q.m,
        u_s=self.table.u_s,
        u_sp=self.table.u_sp,
        u_r=self.table.u_r,
        g=psim.g,
        t=t,
    )
    q.store(t, *rvw, s)
```

The workhorse is [`evolve_ball_motion`](https://github.com/ekiefl/pooltool/blob/51552ff7704376682359059b5dbd8a093f4ded17/psim/physics.py#L25), which calculates the new state for each time step. It delegates to `evolve_slide_state`, `evolve_roll_state`, and `evolve_spin_state`, all of which update the ball state according to the appropriate equations of motion.

To test if `evolve_ball_motion` and its delegates are behaving, I called `shot.start`, which carries out the discrete time evolution and plots the ball's trajectory over time.

```python
In [5]: shot.start()
```

[![ball_traj_0]({{images}}/ball_traj_0.png)]({{images}}/ball_traj_0.png){:.center-img .width-100}

Immediately after being hit, the ball is [sliding]({{ site.url }}/2020/04/24/pooltool-theory/#--case-4-sliding). Yet after a short amount of time, the relative velocity converges to $\vec{0}$, which defines the transition from sliding to [rolling]({{ site.url }}/2020/04/24/pooltool-theory/#--case-3-rolling). Once rolling, the ball continues to roll until it reaches the [stationary]({{ site.url }}/2020/04/24/pooltool-theory/#--case-1-stationary) state.

If a picture says a thousand words, a video says a thousand pictures. Before going any further, I needed a way to **animate** shots because I'm already bored of these static plots. I wasn't looking for perfection, I just needed something to animate trajectories. For this, I found [`pygame`](https://www.pygame.org/news). It just celebrated its 20th anniversary, which is pretty impressive for python package.

I implemented the module [`psim.ani.animate`](https://github.com/ekiefl/pooltool/blob/f79c801_offshoot/psim/ani/animate.py), which animates ball trajectories using `pygame`. For the sake of demonstration, this functionality already exists in the branch we're using.

Let's animate the shot.

```python
In [5]: shot.start(plot=False)
In [6]: shot.animate(flip=True) # Flip orientation to be horizontal
```

[![ball_traj_0]({{images}}/ball_traj_0.gif){:.no-border}]({{images}}/ball_traj_0.gif){:.center-img .width-90}

Getting a little more brave, I wanted to try a massé shot, which you can watch the pros do here:

{% include youtube_embed.html id="89g7sQ7zNqo" %}

To achieve this effect, you have to strike down on the cue ball $(\theta)$ with a sizable amount of side-spin $(a)$.

```python
In [7]: shot.cue.strike(
   ...:     ball = shot.balls['cue'],
   ...:     V0 = 1,
   ...:     phi = 90,
   ...:     theta = 20,
   ...:     a = -0.5,
   ...:     b = 0.0,
   ...: )
   ...: shot.start(plot=False)
   ...: shot.animate(flip=True)
```

[![ball_traj_2]({{images}}/ball_traj_2.gif){:.no-border}]({{images}}/ball_traj_2.gif){:.center-img .width-90}

And voila. Note that all of the curvature takes place in the sliding state. This is because the rolling state by [definition]({{ site.url }}/2020/04/24/pooltool-theory/#--case-3-rolling) has a relative velocity of $\vec{0}$. All sliding state trajectories under the [arbitrary spin model]({{ site.url }}/2020/04/24/pooltool-theory/#3-ball-with-arbitrary-spin) take the form of a parabola--here is Dr. Dave Billiard's [proof](https://billiards.colostate.edu/technical_proofs/new/TP_A-4.pdf).

Next, I tried to apply insane levels of massé, like this guy:

{% include youtube_embed.html id="t_ms6KjSoS8?t=29" %}

Specifically, I tried to tune the parameters to remake the shot at 0:30. After fumbling around, I ended up with this.

```python
In [8]: shot.balls['cue'].rvw[0] = [0.18, 0.37, 0]
   ...: shot.cue.strike(
   ...:     ball = shot.balls['cue'],
   ...:     V0 = 1.15,
   ...:     phi = 335,
   ...:     theta = 55,
   ...:     a = 0.5,
   ...:     b = -0.0,
   ...: )
   ...: shot.start(plot=False)
   ...: shot.animate(flip=False)
```

[![comparison]({{images}}/comparison.gif){:.no-border}]({{images}}/comparison.gif){:.center-img .width-90}

This may not be perfect, but it's close.

What amount of spin is required to pull off a shot like this? In RPMs, the initial rotational speed is

```python
In [21]: np.linalg.norm(shot.balls['cue'].rvw[2])/np.pi*60
Out[21]: 4374.123861245154
```

$4400$ RPM... That's too much, right? Well, the same guy put out [this](https://www.youtube.com/watch?v=UG92u3rClhA) video, in which he measures his RPM for some random shot to be $3180$. So I'm certainly in the ball park. Maybe he can get up to $4400$ RPM, or maybe my simulated cloth had a higher coefficient of sliding friction, such that a higher RPM was required.

Overall, these trajectories have me convinced I'm not screwing anything up royally.

## Event-based evolution algorithm

- Since no collisions are modelled, only a subset of events can occur, namely [motion state transition events](FIXME). That's fine for now, since we can use this to get the algorithm working

## Throwing in some other events

- ball-ball collision (w/ correct collision time algorithm but simple physics theory)
- ball-cushion collision (w/ with orthogonal assumptions and dead wrong physics theory)

## Conclusion

### Summary

- Ball motion is working
- Event-based evolution algorithm is working
- Motion state transition events, ball-ball collision events, and a placeholder ball-cushion collision event has been added

### Next time

Time to make this interactive
