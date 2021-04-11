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

That's better.

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

Specifically, I tried to tune the parameters to remake the shot at 0:30s. After fumbling around, I ended up with this.

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

$4400$ RPM... That's too much, right? Well, the same guy put out [this](https://www.youtube.com/watch?v=UG92u3rClhA) video, in which he measures his RPM for some random shot to be $3180$. So I'm certainly in the ball park. Maybe he can get up to $4400$ RPM, or maybe my simulated cloth had a higher coefficient of sliding friction, requiring higher RPM.

Overall, these trajectories have me convinced I'm not screwing anything up royally.

## Event-based evolution algorithm

So far I've been evolving the simulation by incrementing time in small discrete steps (_aka_ a discrete time evolution algorithm). Yet moving forward, I've opted to use the event-based evolution algorithm for its superior accuracy and computational efficiency.

The premise of the algorithm is this:

- We have beautiful equations of motion for each ball that collectively describe the evolution of the [system state]({{ site.url }}/2020/12/20/pooltool-alg/#what-is-the-system-state). Great.
- But **events** between interfering parties (_e.g._ a ball-ball collision) disrupt the validity of these equations, since they assume each ball acts in isolation.
- Even still, the equations for each ball are valid **up until** the next event.
- So the algorithm works by evolving the system state directly up until the next event, at which time the event must be resolved (_e.g._ a [ball-ball collision event]({{ site.url }}/2020/12/20/pooltool-alg/#-ball-ball-collision) is resolved by applying the [ball-ball interaction equations)]({{ site.url }}/2020/04/24/pooltool-theory/#section-ii-ball-ball-interactions), and then the process repeats itself: the next event is found and the system state is evolved up until the next event.
- There's only one way to calculate when the next event occurs: calculating the time until every single possible next event. By definition of **next** event, the event that occurs in the least amount of time is the next event.

{:.notice}
If you want an in-depth explanation on the event-based evolution algorithm, I may have created the most extensive learning resource on the topic in my [last post]({{ site.url }}/2020/12/20/pooltool-alg/).

### Implementing transitions

All events are either **transitions**, or they are **collisions** (details [here]({{ site.url }}/2020/12/20/pooltool-alg/#2-what-are-events)). Since there are no collisions yet, I decided to implement the algorithm using just transition events to start. Transition events mark the transitioning of a ball from one motion state to another (_e.g._ from [rolling]({{ site.url }}/2020/04/24/pooltool-theory/#--case-3-rolling) to [stationary]({{ site.url }}/2020/04/24/pooltool-theory/#--case-1-stationary)).

Let's take a look.

<div class="extra-info" markdown="1">
<span class="extra-info-header">Want to follow along?</span>

For demo purposes, I compiled my progress into a [branch](https://github.com/ekiefl/pooltool/tree/edfc866_offshoot). If you want to follow along, go ahead and checkout it out.

```bash
git clone https://github.com/ekiefl/pooltool.git
cd pooltool
git checkout edfc866_offshoot
```

</div>

Like before, I created an instance of `ShotSimulation`, and then I set up a pre-baked system state specified by the keyword `straight_shot`

```python
In [1]: import psim.engine as engine
   ...: shot = engine.ShotSimulation()
   ...: shot.setup_test('straight_shot')
```

Next, I struck down on the cue ball with bottom-left english.

```python
In [2]: shot.cue.strike(
   ...:     ball = shot.balls['cue'],
   ...:     V0 = 1.35,
   ...:     phi = 97,
   ...:     a = 0.3,
   ...:     b = -0.3,
   ...:     theta = 10,
   ...: )
```

To see what this system state looks like and how it evolves, here is the **discrete time evolution**.

```python
In [3]: shot.simulate_discrete_time()
   ...: shot.animate(flip=True)
```

[![straight_shot_discrete]({{images}}/straight_shot_discrete.gif){:.no-border}]({{images}}/straight_shot_discrete.gif){:.center-img .width-90}

The cue ball starts sliding (<span style="color: red">red</span>) and then transitions to rolling (<span style="color: green">green</span>). Offscreen, it transitions to stationary. Because I struck down with side english, there is a slight masse (curve) in the trajectory. In total, there are **two transition events**: (1) a sliding-rolling transition event and (2) a rolling-stationary transition event.

In comparison, this is what happens when the system state is evolved using **event-based evolution**.

```python
In [4]: shot.setup_test('straight_shot')
   ...: shot.cue.strike(
   ...:     ball = shot.balls['cue'],
   ...:     V0 = 1.35,
   ...:     phi = 97,
   ...:     a = 0.3,
   ...:     b = -0.3,
   ...:     theta = 10,
   ...: )
   ...: shot.simulate_event_based()
   ...: shot.animate(flip=True)
```

[![cts_1]({{images}}/cts_1.gif){:.no-border}]({{images}}/cts_1.gif){:.center-img .width-90}

**There's only 3 snapshots of the system state**: at the initial time, at the sliding-rolling transition time, and at the rolling-stationary transition time. That is the beauty of the event-based evolution algorithm--rather than evolving in small time steps, the system state is evolved directly to the next event. For this case, this directness has resulted in the shot evolution being compressed into just 3 system state snapshots.

While algorithmically beautiful, it's an eye-sore to look at. So I wrote a `continuize` method that calculates all of the intermediate system states.

```python
In [4]: shot.setup_test('straight_shot')
   ...: shot.cue.strike(
   ...:     ball = shot.balls['cue'],
   ...:     V0 = 1.35,
   ...:     phi = 97,
   ...:     a = 0.3,
   ...:     b = -0.3,
   ...:     theta = 10,
   ...: )
   ...: shot.simulate_event_based(continuize=True)
   ...: shot.animate(flip=True)
```

[![cts_2]({{images}}/cts_2.gif){:.no-border}]({{images}}/cts_2.gif){:.center-img .width-90}

Now the intermediate system states are calculated _ad hoc_ for the purposes of a nice animation. Nice.

### Implementing collisions

The algorithm is a little boring without collisions. Let's add some.

With discrete time evolution, the only way to know if a ball-ball collision occurs is to use a collision detector to see if 2 balls are overlapping. However in the event-based algorithm, ball collisions are **predicted** ahead of time by solving [a quartic polynomial](({{ site.url }}/2020/12/20/pooltool-alg/#-ball-ball-collision-times)) defined from the balls' equations of motion.

For everyone's convenience, ball-ball collisions are already implemented in this demo branch, and can be turned on like so. If you're interested, [here](https://github.com/ekiefl/pooltool/blob/6bb8fb451d964f350243268c5342c6b1c82a5c53/psim/physics.py#L14) is the code for solving the quartic polynomial.

```python
In [5]: engine.include['ball_ball'] = True
```

Running the simulation again now yields a much more interesting picture.

[![cts_3]({{images}}/cts_3.gif){:.no-border}]({{images}}/cts_3.gif){:.center-img .width-90}

While we're at it, let's include ball-cushion collisions too.

```python
In [5]: engine.include['ball_cushion'] = True
```

{:.warning}
This implementation of ball-cushion interactions is non-physical. In fact, it's not even trying to be accurate, I just wanted to add another collision event to test the algorithm. In this overly simplistic implementation, ball-cushion collisions are resolved by reversing the linear momentum component perpendicular to the cushion surface. In the future, I will replace this with the [(Han, 2005)]({{ site.url }}/2020/04/24/pooltool-theory/#3-han-2005) physics model discussed previously.

Now, things are really starting to take shape.

[![cts_4]({{images}}/cts_4.gif){:.no-border}]({{images}}/cts_4.gif){:.center-img .width-90}

I find this to be a pretty clean visualization of how the event-based algorithm advances the system state state through time.

To me, its incredible to think that for a given event (frame), the proceeding event has been carefully chosen from the entire set of all possible next events. For example, the 3rd event is a sliding-rolling transition of the cue ball after its collision with the 8-ball. The 4th event is determined by considering all of the events in this diagram:

[![snapshot_1_2]({{images}}/snapshot_1_2.jpg){:.no-border}]({{images}}/snapshot_1_2.jpg){:.center-img .width-90}

In total 15 possible events were considered, and the time until each of them was calculated. Based on the system state, it turned out that the one that physically occurs is a collision of the 8-ball (<span style="color: black">black</span>) with the 3-ball (<span style="color: red">red</span>).

### Comparison to discrete time integration

How do these results compare to the discrete time evolution? With discrete time, collisions are [detected retrospectively]({{ site.url }}/2020/12/20/pooltool-alg/#discrete-time-evolution) by seeing if there is any overlapping geometry. This leads to an inherent inaccuracy, that can be reduced by **decreasing the time step**. But how small does the timestep have to be and **what effect does this have on performance**?

To compare the two algorithms, I moved the brown 7-ball from the previous simulation just slightly, such that the cue-ball barely grazes it when using the event-based algorithm.

[![slight_graze]({{images}}/slight_graze.gif){:.no-border}]({{images}}/slight_graze.gif){:.center-img .width-90}

Let's see the corresponding discrete time evolution using a timestep of 20ms.

```python
In [6]: import psim.engine as engine
   ...: engine.include['ball_ball'] = True
   ...: engine.include['ball_cushion'] = True
   ...: shot = engine.ShotSimulation()
   ...: shot.setup_test('straight_shot')
   ...: shot.cue.strike(
   ...:     ball = shot.balls['cue'],
   ...:     V0 = 1.35,
   ...:     phi = 97,
   ...:     a = 0.3,
   ...:     b = -0.3,
   ...:     theta = 10,
   ...: )
   ...: shot.simulate_discrete_time(dt=0.020)
   ...: shot.animate(flip=True)
```

[![discrete_bad]({{images}}/discrete_bad.gif){:.no-border}]({{images}}/discrete_bad.gif){:.center-img .width-90}

Wow, it didn't even come close to hitting the brown 7-ball after bouncing off the cushion. And the 8-ball is supposed to collide with the red 3-ball, but missed entirely. The problem is that the collision angle between the cue and 8-ball is slightly off due to discrete time error, and the net result is that the overlapping geometry overestimates how thin the cut on the 8-ball is.

So then how small must the timestep be for the sequence of events to match the event-based algorithm? To find out, I ran a series of shots evolved with smaller and smaller timesteps. Simulations are considered accurate if the cue ball contacts the brown 7-ball, as was observed in the event-based algorithm. Here is the script:

```python
```

[![discrete_comp]({{images}}/discrete_comp.png)]({{images}}/discrete_comp.png){:.center-img .width-80}

This plot shows that accurate simulations (_i.e._ simulations where the cue-ball grazes the 7-ball) require timesteps below about $250 \, \text{\mu s}$. Unfortunately, this comes at a monumental speed cost. The fastest calculation time for accurate simulations was about 6s, which is 30X slower than the compute time for the event-based algorithm (green line).

This is by no means an extensive comparison between the two algorithms. But it illustrates the fundamental difference between them: except for inaccuracies arising from floating point precision, the event-based algorithm is as accurate as the underlying physics models, and performs reasonably fast. In contrast, discrete time algorithms produce an entire spectrum of accuracies, and choosing timesteps that produce sufficiently accurate results typically lead to bad performance.

## Conclusion

At this point in the project, I'm pretty happy where things are. All of the physics I've
- Ball motion is working
- Event-based evolution algorithm is working
- Motion state transition events, ball-ball collision events, and a placeholder ball-cushion collision event has been added

Next time, I'm making this fully interactive.
