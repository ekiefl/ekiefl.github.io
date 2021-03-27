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

## The bare-bones code structure

This project started with 2 main modules: `engine.py` and `physics.py`. The rationale for this design was to separate the **physics** from the **objects** that the physics acts on (balls, cues, cushions, etc).

With this in mind, `engine.py` implements the shot evolution algorithm by coordinating when object states should be modified, and `physics.py` implements the physics that provides the specific rules for how the modification should be carried out. This separation of responsibility allows different physics models to be plugged in or out at will.

Though the codebase has changed dramatically since this original implementation, this principle has remained unchanged.

## Running a simulation

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

I'm going to strike the cue ball with a center-ball hit $(a=0, b=0)$ straight down the table $(\phi=90)$ with the cue completely level with the table $(\theta = 0)$. I'll use a relatively slow impact speed of $V_0 = 1 \text{m/s}$.

```python
In [5]: shot.cue.strike(
   ...:     ball = shot.balls['cue'],
   ...:     V0 = 1,
   ...:     phi = 90,
   ...:     theta = 0,
   ...:     a = 0,
   ...:     b = 0,
   ...: )

In [6]: shot.balls['cue'].rvw
Out[6]:
array([[0.686, 0.33 , 0.   ],
       [0.   , 1.754, 0.   ],
       [0.   , 0.   , 0.   ]])
```

After calling the method, the cue ball now has a $1.75 \text{m/s}$ velocity in the $y-$direction. Since it was a center ball hit with no cue elevation, the ball has no spin. _i.e._ $\vec{\omega} = <0,0,0>$.

At this point, no time has passed--the ball state has merely been modified according the physics of `shot.cue` striking `self.balls['cue']`. So then **how does the shot evolve**?

Rather than implementing the continuous event-based shot evolution algorithm I [wouldn't shut up about]({{ site.url }}/2020/12/20/pooltool-alg/#continuous-event-based-evolution), I implemented some dinky discrete time evolution algorithm just to get the _ball rolling_. It's a for loop that increments by $50 \text{ms}$.

```python
q = self.balls['cue']

for t in np.arange(0, 10, 0.05):
    r, v, w, s = physics.evolve_ball_motion(
        *q.rvw,
        R=q.R,
        m=q.m,
        u_s=self.table.u_s,
        u_sp=self.table.u_sp,
        u_r=self.table.u_r,
        g=psim.g,
        t=t,
    )
    q.store(t, r, v, w, s)
```

The workhorse is [`evolve_ball_motion`](https://github.com/ekiefl/pooltool/blob/51552ff7704376682359059b5dbd8a093f4ded17/psim/physics.py#L25), which calculates the new state for each time step. It delegates to `evolve_slide_state`, `evolve_roll_state`, and `evolve_spin_state`, all of which update the ball state according to the appropriate equations of motion.

To test if `evolve_ball_motion` and its delegates are behaving, I called `shot.start`, which carries out the discrete time evolution and plots the ball's trajectory over time.

```python
In [5]: shot.cue.start()
```

[![ball_traj_0]({{images}}/ball_traj_0.png)]({{images}}/ball_traj_0.png){:.center-img .width-100}


### A straight shot down the table

Consult with the above docstring for a detailed look at what the parameters mean.

First is a center-ball hit straight down the table with low velocity:

```python
self.cue.strike(
    ball = self.balls['cue'],
    V0 = 0.6,
    phi = 90,
    theta = 0,
    a = 0.0,
    b = 0.0,
)
```

<img src="media/ball_traj_0.png" width="450" />

Since ball has no initial spin but is thrust into motion, it is intially sliding against the cloth.
The frictional force applies a torque that quickly equilibrates (decays to 0) to create an angular velocity that
matches the center of mass speed of the ball. The decreased spacing between points indicates the
ball is slowing down, but was hit too hard to come to rest, There is no interaction with the cushion
so the ball rolls past the end of the table.

### A softer shot at 45 degrees with top spin

Now, I hit a similar shot but softer and at $45 \deg$ instead of 90. Instead of a center ball hit, I
hit the ball $2/5 R$ above center, where $R$ is the ball radius. This is a "sweet spot", where the
induced spin exactly matches the center of mass velocity. The ball therefore avoids sliding on the
table and immediately rolls, independent of the cue striking velocity. Read more about this physical oddity
[here](https://www.real-world-physics-problems.com/physics-of-billiards.html) (search for "sweet
spot").

```python
self.cue.strike(
    ball = self.balls['cue'],
    V0 = 0.2,
    phi = 45,
    theta = 0,
    a = 0.0,
    b = 0.4,
)
```

<img src="media/ball_traj_1.png" width="450" />

### A slight massé

This is a common shot to hit the object ball by bending the cue ball _around_ another ball. Here is
the legend Efren Rayes doing a whole bunch of them:

[![Efren Masse](http://img.youtube.com/vi/OEQvcGljLXI/0.jpg)](https://www.youtube.com/watch?v=OEQvcGljLXI "Efren Masse")

To achieve this effect, I strike down on the cue ball and apply a sizable amount of right=hand
spin:

```python
self.cue.strike(
    ball = self.balls['cue'],
    V0 = 0.6,
    phi = 90,
    theta = 20,
    a = -0.5,
    b = 0.0,
)
```

<img src="media/ball_traj_2.png" width="450" />

You may be interested to know that during the sliding state, the trajectory takes the form of a
parabola. Once it transitions into the rolling state, it becomes linear.

### A huge massé

Let's apply insane levels of masse, like this guy:

[![Florian Kohler](http://img.youtube.com/vi/t_ms6KjSoS8/0.jpg)](https://www.youtube.com/watch?v=t_ms6KjSoS8 "Florian Kohler")

Specifically, I tried to tune the parameters to remake the shot at 0:30

```python
self.cue.strike(
    ball = self.balls['cue'],
    V0 = 2.8,
    phi = 335,
    theta = 55,
    a = 0.5,
    b = -0.0,
)
```

<img src="media/ball_traj_3.png" width="450" />

The paths look pretty identical to me, but I don't think I found a unique solution. I'm sure that
mine has more speed, a lower $\theta$ value, and who even knows about how the friction forces of the
tables match. Regardless, this is really promising!
pygame](https://www.pygame.org/news).
 





















## Extra:

## Droning on about class structure


This module is a compilation of function definitions that implement the pool physics [equations]({{ site.url }}/2020/04/24/pooltool-theory/) into code. For example, the equations of motion for evolving a ball in the rolling state is given by

<div class="extra-info" markdown="1">
<span class="extra-info-header">Rolling equations of motion (**table coordinates**)</span>

Displacement:

$$ r_x(t) = r_{0x} + v_0 \cos(\phi) \, t - \frac{1}{2} \mu_r g \cos(\phi) \, t^2 \label{rolling_rx_table} $$

$$ r_y(t) = r_{0y} + v_0 \sin(\phi) \, t - \frac{1}{2} \mu_r g \sin(\phi) \, t^2 \label{rolling_ry_table} $$

$$ r_z(t) = 0 \label{rolling_rz_table} $$

Velocity:

$$ v_x(t) = v_0 \cos(\phi) - \mu_r g \cos(\phi) \, t \label{rolling_vx_table} $$

$$ v_y(t) = v_0 \sin(\phi) - \mu_r g \sin(\phi) \, t \label{rolling_vy_table} $$

$$ v_z(t) = 0 \label{rolling_vz_table} $$

Angular velocity:

$$ \omega_x(t) = - \frac{1}{R} \lvert \vec{v}(t) \rvert \sin(\phi) \label{rolling_ox_table} $$

$$ \omega_y(t) = \frac{1}{R} \lvert \vec{v}(t) \rvert \cos(\phi) \label{rolling_oy_table} $$

$$ \omega_z(t) = \omega_{0z} - \frac{5\mu_{sp}g}{2R}t \label{rolling_oz_table} $$

Validity:

$0 \le t \le \frac{\lvert \vec{v}_0 \rvert}{\mu_r g}$. If $\frac{2R}{5\mu _{sp} g}
\omega _{0z} < \frac{\lvert \vec{v}_0 \rvert}{\mu_r g}$, then $\omega_z(t) = 0$ for $t >
\frac{2R}{5\mu _{sp} g} \omega _{0z}$.

{:.notice}
I derive these equations [here]({{ site.url }}/2020/04/24/pooltool-theory/#--case-3-rolling).

</div>

The corresponding function is `physics.evolve_roll_state`.

```python
def evolve_roll_state(rvw, R, u_r, u_sp, g, t):
    r_0, v_0, w_0 = rvw

    v_0_hat = utils.unit_vector(v_0)

    r_T = r_0 + v_0 * t - 1/2*u_r*g*t**2 * v_0_hat
    v_T = v_0 - u_r*g*t * v_0_hat
    w_T = utils.coordinate_rotation(v_T/R, np.pi/2)

    # Independently evolve the z spin
    w_T[2] = evolve_perpendicular_spin_state(rvw, R, u_sp, g, t)[2,2]

    # This transformation governs the z evolution of angular velocity
    return np.array([r_T, v_T, w_T])
```

By the way, the same inputs are used across functions in this module so frequently that they are defined in the module [docstring](https://github.com/ekiefl/pooltool/blob/master/pooltool/physics.py), rather than in each individual function docstring.

The most frequently used variable name is `rvw`, which represents the [ball state](https://ekiefl.github.io/2020/12/20/pooltool-alg/#what-is-the-system-state) as a 3x3 `numpy` array where `rvw[0,:]` is the displacement vector $\vec{r}(t_0)$, `rvw[1,:]` is the velocity vector $\vec{v}(t_0)$, and `rvw[2,:]` is the angular velocity vector $\vec{\omega}(t_0)$. In `physics.evolve_roll_state` we can see that an initial ball state is passed as input along with an amount of time `t` that the ball is to be evolved, and then a new evolved ball state is returned.

### `engine.py`

Pool simulations require balls, a table, and a cue stick. In an object-oriented language, I'd be crazy not to create a `Ball` class, `Table` class, and `Cue` class.py`.

```python
class Table(object):
    def __init__(self, w=None, l=None, u_s=None, u_r=None, u_sp=None):

        self.w = w or psim.table_width
        self.l = l or psim.table_length

        self.L = 0
        self.R = self.w
        self.B = 0
        self.T = self.l

        self.center = (self.w/2, self.l/2)

        # rail properties
        pass

        # felt properties
        self.u_s = u_s or psim.u_s
        self.u_r = u_r or psim.u_r
        self.u_sp = u_sp or psim.u_sp


class Ball(object):
    def __init__(self, ball_id, m=None, R=None):
        self.id = ball_id

        # physical properties
        self.m = m or psim.m
        self.R = R or psim.R
        self.I = 2/5 * self.m * self.R**2

        self.rvw = np.array([[np.nan, np.nan, np.nan],  # positions (r)
                             [0,      0,      0     ],  # velocities (v)
                             [0,      0,      0     ]]) # angular velocities (w)

        # stationary=0, spinning=1, sliding=2, rolling=3
        self.s = 0

        # state history
        self.history = {'t': [], 'rvw': [], 's': []}


    def store(self, t, r, v, w, s):
        self.history['t'].append(t)
        self.history['rvw'].append(np.array([r, v, w]))
        self.history['s'].append(s)


    def update(self, r, v, w, s):
        self.rvw = np.array([r, v, w])
        self.s = s


class Cue(object):
    def __init__(self, M=psim.M, brand=None):
        self.M = M
        self.brand = brand


    def strike(self, ball, V0, phi, theta, a, b):
        v_T, w_T = physics.cue_strike(ball.m, self.M, ball.R, V0, phi, theta, a, b)

        ball.rvw[1] = v_T
        ball.rvw[2] = w_T
        ball.s = 2
```

These are the objects that the shot evolution algorithm will deal with. The evolution algorithm is handled by the ``













