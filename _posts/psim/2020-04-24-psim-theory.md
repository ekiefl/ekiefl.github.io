---
layout: post
title: "Creating a billiards simulator: Theory"
categories: [psim]
excerpt: "A dive into the physics and algorithmic theory behind pool simulation"
comments: true
authors: [evan]
image:
  feature: psim/psim_banner.png
  display: true
---

{% capture images %}{{site.url}}/images/psim/psim-theory{% endcapture %}
{% include _toc.html %}

Alright, this post is the first of many in my journey to make a realistic simulator. Before jumping
into code, we have to trudge through the theory of both **(a)** the physics of pool, and **(b)** the
algorithims for evolving a pool shot. The physics of pool is what is covered in this post, where you'll
find very little code, and algorithms for evolving a pool shit will be covered in the second post. Both of these
will contain a lot of equations, and little if any code. If this sounds uninteresting to you, skip ahead to
the third post in this series by [clicking HERE](FIXME). With that said, let's get started.

{:.notice}
As I incorporate more and more realistic physics into my simulations, this post will grow
correspondingly.

## The physics of billiards

The thing about pool is that its pretty old. This is one of the first historical depictions of
billiards (please God let it be famous for no other reason), which dates back to 1674.

[![charles_cotton]({{images}}/1674.png)]({{images}}/1674.png){:.center-img .width-70}
*Two blokes shootin' the shit over a game of billiards. [Source](https://commons.wikimedia.org/w/index.php?curid=6903484).*

Coincidentally, at exactly this point in history Isaac Newton would have been busy inventing
calculus, his self-titled Newtonian physics, and a universal theory of gravitation that wholly
explained the previously disparate phenomena of tides, why things fall, and the motions of celestial
bodies. His contributions to science would spark a revolution in the physical sciences more
illustrious than anyone before him, and arguably ever since him. But most importantly by far, **Newton's
work would enable the theoretical treatment of the game of billiards**, and as such, the game has been
studied for at least 200 years.

As a result of its long history, the theoretical treatment of billiards has been sufficiently solved
for most scenarios: **(1)** ball-cloth interactions, aka how the balls slide, spin, roll, and lie on
the table; **(2)** ball-ball interactions aka ball-ball collisions; **(3)** ball-cushion
interactions, aka how balls bounce off rails; **(4)** ball-air interactions, aka how the ball
behaves when it becomes airborne due to jump shots, etc; **(5)** ball-slate interactions, aka how
the ball bounces on the table. The jury is still out on the finer details of many of these
interactions, and some treatments are less accurate than others, but each of these individual
scenarios have analytical solutions that are accurate to "sufficient" degree. What I mean by
sufficient is that all qualitative effects a pro-player may be expecting to observe manifest
directly from the equations. Depending on how well I do in balancing the degree of these effects
will determine how realistic my simulation ends up being.

So basically, I'm going to have to get my hands dirty with these equations. I decided having a
reference source was necessary, so I bought the non-exhaustive but heavily referenced "modern day"
treatment of billiards, "_The Physics of Pocket Billiards_" by Wayland C. Marlow. The physics I will
use comes in part from this book, and in part from random sources on the internet.

In what follows, I am going to lay out **all** of the physics I'm going to include in the
simulation. If I was a young and sprightly undergrad I would probably attempt to derive the
equations, but I'm old and withered so I'm just going to provide color commentary.

## **Section I**: ball-cloth interactions

In this section I review the ball-cloth interaction, aka how pool balls interact with their playing
surface. It is somewhat obvious that the cloth provides a frictional surface that slows the ball's
motion. Yet, depending on the ball's spin state, this same friction can also lead to curved
trajectories due to the application of forces orthogonal to the ball's motion. Therefore, modelling
the ball-cloth interaction is essential for realism, and quickly gets complicated. Let's go over
some models from least to most realistic.

### (1) No friction

This is the null model. The friction coefficients at the point of contact (PoC) between ball and
cloth are 0. This means no energy dissipates from the ball, and it rolls indefinitely. It also spins
indefinitely.

### (2) Spinless ball

In this model, a frictional force exists between the cloth and ball that opposes the ball's motion.
Therefore, the ball dissipates energy over time and eventually come to a halt. Sounds like pool to
me. However, what's unrealistic about this model is that the ball has **no spin**, which is
impossible for a ball moving on a cloth with friction. To see why, let's look at the force
contributions that act on the ball:

[![force_body_diagram]({{images}}/force_body_diagram.jpg)]({{images}}/force_body_diagram.jpg){:.center-img .width-70}
_**Figure 1**. Force contributions acting on a ball that has o spin. Here, $ \vec{v} $ is the
velocity of the ball, $ m $ its mass, and $ R $ its radius.  Additionally, we got good old $ \vec{g} $,
the gravitational constant, and the normal force $ \vec{N} $._

In this example, assume that the ball initially has no spin (*e.g.* it is not rolling) but is moving
in the $ +x $-direction with a speed $ |\vec{v}| $. In the $ y $-axis, there is a
gravitational force (mass $ \times $ gravitational constant $ = m\vec{g} $) pulling the ball
into the table. Since the table is supporting the ball, it exerts an equal and opposite force onto
the ball. This is called the normal force, $ \vec{N} $.  Without it, the ball would fall through
the table. And so even while the ball remains perfectly still on the table, there is a perpetual
tug-of-war between the ball wanting to accelerate towards the center of the earth, and the table
stopping it from doing so. This contention results in friction whenever the ball moves along the
table. The ball and cloth essentially rub each other the wrong way as the ball moves, and so a
frictional force is exerted on the ball in a direction opposite the ball's motion, that is denoted
here as $ \vec{F}_f $.

So what makes the ball spin? Well, since $ \vec{F}_f $ is applied at the point of contact (PoC) between
ball and cloth, this ends up creating a torque on the ball that causes it to rotate. Intuitively,
the bottom of the ball is slowing down, but the top of the ball isn't, and so it ends up going "head
over heels".

To demonstrate this, I took a slow-mo shot of an object ball being struck head on with the cue ball.

{% include youtube_embed.html id="8Wng2cUH8as" %}

Directly after impact, the object ball has a non-zero velocity and no spin. Yet quickly over time,
the ball transitions from "sliding" across the cloth (no spin) to "rolling" across the cloth (yes
spin). I hope it's convincing footage.

Wrapping things up for this model, where spin is ignored, you
can imagine that instead of the frictional force being applied at the PoC, it's applied at the
ball's center. Then, there is no torque on the ball, and therefore no spin. This provides a
mechanisms that slows the balls down, so it checks that box for realism. This is the kind of model
you can expect from a pool game that offers a primitive "overhead" perspective, since it provides a
passable playing experience for beginners and is simple to code.

### (3) Ball with arbitrary spin

{:.notice}
From this point on, I'll refer to a ball with "spin" as a ball with "angular momentum".

In this example, we take on the general case of the ball-cloth interaction. This is the most
realistic model I came across that can be solved analytically, and has the following assumptions:

1. The ball can be in an arbitrary state (but must be on the table)
2. There is a single point of contact (PoC) between ball and cloth

By "*the ball can be in an arbitrary state*", what I mean is that it may have an arbitrary velocity
($\vec{v}$), angular momentum ($\vec{\omega}$), and displacement relative to some origin
($\vec{r}$). These 3 vectors fully characterize the state of the ball, and the goal is to find
equations of motion that can evolve these 3 vectors through time. Essentially, these equations are
functions that, when given an initial state ($\vec{v}_0$, $\vec{\omega}_0$, $\vec{r}_0$), can give
you an updated state ($\vec{v}$, $\vec{\omega}$, $\vec{r}$) some time $t$ later.

As for the second assumption, a single point of contact is a fairly accurate assumption, but
technically the weight of the ball "bunches up" the cloth as it moves to a degree that depends upon
how loosely the cloth is stretched over the slate. Additionally, the cloth itself can be compressed,
and cloth fibres and other non-idealities can contact the ball at multiple points. And so in
actuality there does not exist a "point of contact", but rather, an "area of contact".

[![depression]({{images}}/depression.png)]({{images}}/depression.png){:.center-img .width-70}
_**Figure 2**. The cloth is a compressible surface, and so in actuality there does not exist a "point of
contact", but rather, an "area of contact"._

With the assumptions laid out, let's begin. The most important thing to realize is that throughout a
ball's trajectory, it will always be in any of these 4 different modes: **sliding, rolling, spinning,
or stationary**. The physics is different for each of these cases, so we tackle them piecewise from least
to most complicated.

### - Case 1: Stationary

If the ball is stationary, the ball stays where it is and there is no angular or linear momentum. In
other words:

<div class="extra-info" markdown="1">
<span class="extra-info-header">Stationary equations of motion</span>

Displacement:

$$ \vec{r}(t) = \vec{r}_0 \label{stationary_r}$$

Velocity:

$$ \vec{v}(t) = \vec{0} \label{stationary_p}$$

Angular momentum:

$$ \vec{\omega}(t) = \vec{0} \label{stationary_o}$$

Validity:

$0 \le t < \infty$.

</div>

{:.notice}
It's important to keep in mind each of Eqs. $\eqref{stationary_r}$,
$\eqref{stationary_p}$, and $\eqref{stationary_o}$ are vector equations that can be broken down into
3 scalar equations each, one for each spatial dimension. For example, Eq. $\eqref{stationary_o}$ can
be written as $\omega_x(t) = 0$, $\omega_y(t) = 0$, and $\omega_z(t) = 0$. I interchangably use both
scalar and vector equations, so make sure you are spotting the difference.


### - Case 2: Spinning

Spinning is a commonly observed ball state in which there is no linear momentum of the
ball, yet it is spinning like a top:

{% include youtube_embed.html id="A9mweRTxGiw" %}

Like in the stationary state, the ball has no linear momentum:

$$ \vec{v}(t) = \vec{v} \notag $$

Likewise, the ball remains in place:

$$ \vec{r}(t) = \vec{r}_0 \notag $$

However, since the ball is rotating, it has an angular momentum. You'll notice that the ball spins
around the $z-$axis, relative to the coordinate system in Figure 3:

[![spinning_diagram_1]({{images}}/spinning_diagram_1.jpg)]({{images}}/spinning_diagram_1.jpg){:.center-img .width-70}
_**Figure 3**. A ball spinning in place. In this coordinate system the table is in the $xy-$plane._

This is not by chance--it is a constraint of the state, since if the ball had any components of its
angular momentum in the $x$ or $y$ directions, it would create a friction with the cloth that would
translate into a linear momentum. Since "spinning" is characterized by 0 linear momentum
($\vec{v}=\vec{0}$), angular momentum is strictly in the $z-$axis. In otherwords,

$$ \omega_x(t) = 0 \notag $$

$$ \omega_y(t) = 0 \notag $$

$$ \omega_z(t) = \text{ }??? \notag $$

To characterize the $z-$axis angular momentum, we need to introduce some bullshit. I told you that
in this model, there is a single PoC between ball and cloth. If such were *truly* the case, there
is nothing to stop the ball from spinning forever (besides air, which we will ignore). This is
because a ball spinning in place has **zero speed** at the infinitesimally small PoC. In
other words, the relative velocity between the ball and cloth at the PoC is 0, and this means
there can exist no frictional force. Of course, we know that the ball *does* slow, which
is proof that there does not exist a "point of contact" but rather an "area of contact".

Rather than explicitly define an area of contact, which would greatly complicate the physics, we
account for this embarassing blunder of the model by introducing a phenomenological friction
parameter that slows down the $z-$component of the ball's angular momentum over time.  What's a
phenomenological parameter? It's a parameter that is added to a model *ad hoc*, that explains a
phenomenon (in this case, the slowing down of a ball's rotation) that does not come from assumptions
of the model. It's what people do when they want to model an observation but their model is bad and
does not cause the observation. Basically, its cheating, which my girlfriend knows I love to do. So
after adding a standard friction term, we have our equations of motion solved:

<div class="extra-info" markdown="1">
<span class="extra-info-header">Spinning equations of motion</span>

Displacement:

$$ \vec{r}(t) = \vec{r}_0 \label{spinning_r} $$

Velocity:

$$ \vec{v}(t) = \vec{0} \label{spinning_p}$$

Angular momentum:

$$ \omega_x(t) = 0 \label{spinning_ox}$$

$$ \omega_y(t) = 0 \label{spinning_oy}$$

$$ \omega_z(t) = \omega_{0z} - \frac{5\mu_{sp}g}{2R}t \label{spinning_oz} $$

Validity:

$0 \le t \le \frac{2R}{5\mu_{sp}g}\omega_{0z}$.

</div>

In Eq. $\eqref{spinning_oz}$, $\omega_{0z}$ is angular momentum in the $z-$axis at $t=0$, $\mu_{sp}$
is the coefficient of spinning friction, $g$ is the gravitational constant, and $R$ is the ball's
radius. The equation states that as time evolves, there is a linear decay in the ball's angular
momentum. Collectively, these equations are valid until the ball stops rotating, which happens when
$\omega_z(t)$ is $0$. This occurs when $t=(2R\omega_{0z})/(5\mu_{sp}g)$.

### - Case 3: Rolling

Think of rolling as driving your car on concrete, whereas sliding would be like driving your car on
ice. In the former, your tires grip the road such that at the point of contact, there is no relative
velocity between the tire and the road; each time the tire does one rotation, your car translates
the circumference of your tire. On the other hand, on ice, there is a lot of "slippage" between the
tire and the ice, and therefore a relative velocity; each time your tire does one rotation, your car
moves far less than one circumference of your tire.

{:.notice}
In physics textbooks, what I call rolling is actually called _rolling without slippage_ and what I call
sliding is actually called _rolling with slippage_. Sorry for the confusing terminology.

Alright, so let's get on with it. Consider a ball that is _rolling_ in the positive $x-$direction:

[![rolling_diagram_1]({{images}}/rolling_diagram_1.jpg)]({{images}}/rolling_diagram_1.jpg){:.center-img .width-70}
_**Figure 4**. A rolling ball, that moves in the $x-$direction. The left panel shows a bird's eye
view, and the right panel shows a profile view. In this coordinate system, the
angular momentum is in the $y-$direction._

Such a ball will move in a straight line until it comes to a rest. As it travels, it will be slowed
down by a frictional force proportional to its velocity, which implies that its velocity will decay
linearly with time:

$$ \vec{v}(t) = \vec{v}_0 - \mu_r g t \hat{v}_0 \label{rolling_momentum} $$

Here, $m$ is the ball's mass, $\mu_r$ is the coefficient of rolling friction, $g$ is the
gravitational constant, and $\hat{v}_0$ is the unit vector that points in the direction of the ball's
travel (according to this coordinate system, $\hat{v}_0 = \hat{i}$).

Integrating this equation with respect to time yields the displacement as a function of time:

$$ \vec{r}(t) = \vec{r}_0 + \vec{v}_0 t - \frac{1}{2} \mu_r g t^2 \hat{v}_0 \notag$$

----------------------------

Now for angular momentum. To discuss this, we need to formalize the concept of rolling, which is
formally defined as the state in which the **relative velocity**, $\vec{u}(t)$, between the ball and
cloth at the PoC is $\vec{0}$. $\vec{u}$(t) has two contributions: (1) the linear velocity of
the ball, _i.e._ the velocity of the center of mass, and (2) the velocity between ball and cloth
that exists because of the ball's rotation. Their sum defines the relative velocity:

$$ \vec{u}(t) = \vec{v}(t) + R \hat{k} \times \vec{\omega}(t) \label{rel_vel}$$

For example, here is a shot where I tried to make sure the cue ball _only_ has linear
velocity:

{% include youtube_embed.html id="Z7ghvKcEDIc" %}

{:.warning}
I think we both agree there is some amount of rotation, but let's just ignore it.

Since the ball does not rotate, there is no angular momentum, so Eq.  $\eqref{rel_vel}$ reduces to

$$ \vec{u}(t) = \vec{v}(t) \notag $$

Similarly, here is a shot that _only_ has velocity between ball and cloth that exists because of the
ball's rotation.

{% include youtube_embed.html id="G_aaXbdJavc" %}

Right at the moment of contact, the cue ball spins _in place_ and therefore has no center of mass
velocity. In this instant, Eq. $\eqref{rel_vel}$ becomes

$$ \vec{u}(t) = R \hat{k} \times \vec{\omega}(t) \notag $$

In the particular case shown, the ball has top spin, so the cross product dictates that $\vec{u}$
points in the direction opposite the cue ball's travel.

Both of the above examples are cases in which $\vec{u}(t) \ne \vec{0}$, so are therefore cases of
sliding, not rolling. To be rolling ($\vec{u}(t) = \vec{0}$), these contributions must match each other:

$$ -R \hat{k} \times \vec{\omega}(t) = \vec{v}(t) \label{roll_condition} $$

This refers to the condition in which every time the ball does a complete rotation about the
$y-axis$ (according to the axes defined in Figure 4), the ball must travel exactly one circumference
($2 \pi R$ in the $x-$axis). Unless this exact condition is met, a moving ball is _sliding_, not
_rolling_. For how particular this condition seems, it is interesting that in the game of pool,
balls are most often rolling. The reason is that any sliding ball experiences friction that reduces
the magnitude of $\vec{u}(t)$ until it is rolling. In that sense, rolling is somewhat of an
equilibrium state.

Now that we have a mathematical condition for rolling, _i.e._ Eq. $\eqref{roll_condition}$, there is a lot
we can learn about the angular momentum. According to our coordinate system in Figure 4, the RHS of
Eq. $\eqref{roll_condition}$ is strictly in the $+x-$direction. That means the LHS must also be
strictly in the $+x-$direction. Expanding the cross product on the LHS yields:

$$ -R\hat{k} \times \vec{\omega}(t) = R \begin{bmatrix} \omega_y(t) \\ -\omega_x(t) \\ 0 \end{bmatrix} \notag $$

3 really important things result from this equation:

1. In order for the RHS to point in the $+x-$direction, as it must, $\omega_x(t)$ is necessarily 0.
   So no angular momentum in the direction of motion.

2. Using Eq. $\eqref{roll_condition}$, it follows that $\omega_y(t) = \frac{|\vec{v}(t)|}{R}$. Since
   $\vec{v}(t)$ is known via Eq. $\eqref{rolling_momentum}$, this equation solves the time
   evolution of $\omega_y(t)$. Note that $\omega_y(t)$ is strictly positive, which intuitively
   refers to the fact that in order to be rolling, the ball must have _top spin_, not _back spin_.

3. $\omega_z(t)$ is absent from this equation, which means that it is a _free parameter_: it can
   take any value.

Points 1 & 2 solve the time evolution for $\omega_x(t)$ and $\omega_y(t)$, respectively. Meanwhile, point
3 has consequences that you may find highly surprising. For example, we know that in the
rolling state, the ball path is a straight line. Yet the model predicts this is true regardless of
$\omega_z$. Is that really sensical? It may not match your initial intuition, but it does match the
reality:

{% include youtube_embed.html id="sDPNKuwax14" %}

In the above example I apply a shit load of clockwise side spin ($\omega_z(t) < 0$) and as you can
see, the ball follows a straight line. Pretty hard to deny, but it might still be at odds with what
you know about pool. For example, look at O'Sullivan and the gang "swerving" the ball by applying
side spin:

{% include youtube_embed.html id="89g7sQ7zNqo" %}

So what's the difference between those shots, and the one I manufactured? The fundamental difference
is that these players are elevating their cue, which causes $\omega_x$ to be non-zero (angular
momentum _in the direction_ of motion). This "barrel-roll" rotation is what causes curved
trajectories, otherwise known as swerve or masse. (For more info on the cue-cueball interaction, see
FIXME). On the other hand, my shot did not have any significant amount of $\omega_x$, so whatever
small amount existed quickly dissipated within fractions of a section, yielding an otherwise straight trajectory.

The takeaway is that $\omega_z(t)$ is decoupled from everything else, and evolves according to Eq.
$\eqref{spinning_oz}$, which we dealt with Case 2. The only thing left to do is write down the
equations for a given frame of reference. Let's use a frame of reference that is centered
about the ball's _initial_ center of mass coordinates. Then,

Displacement:

$$ \vec{r}(t) = (v_0 t - \frac{1}{2} \mu_r g t^2) \, \hat{v}_0 \label{rolling_r_general} $$

Velocity:

$$ \vec{v}(t) = (v_0 - \mu_r g t) \, \hat{v}_0  \label{rolling_v_general} $$

Angular momentum:

$$ \vec{\omega}_{xy}(t) = \hat{k} \times \frac{\vec{v}(t)}{R} \label{rolling_oxy_general} $$

$$ \omega_z(t) = \omega_{0z} - \frac{5\mu_{sp}g}{2R}t \label{rolling_oz_general} $$

where $v_0$ is the initial speed of the ball. Since angular momentum has 2 decoupled components,
$\vec{\omega}(t)$ is represented by 2 equations.  $\vec{\omega} _{xy} (t)$ defines the angular
momentum projected onto the $xy-$plane, which is parallel with the table. 

The above equations are defined in terms of $\hat{v}_0$, which can point direction in the $xy-$plane.
If we take a frame of reference in which ball motion is in the $+x-$direction, we can drop the
vector notation:

<div class="extra-info" markdown="1">
<span class="extra-info-header">Rolling equations of motion (**ball coordinates**)</span>

Displacement:

$$ r_x(t) = v_0 t - \frac{1}{2} \mu_r g t^2 \label{rolling_rx_ball} $$

$$ r_y(t) = 0 \label{rolling_ry_ball} $$

$$ r_z(t) = 0 \label{rolling_rz_ball} $$

Velocity:

$$ v_x(t) = v_0 - \mu_r g t \label{rolling_vx_ball} $$

$$ v_y(t) = 0 \label{rolling_vy_ball} $$

$$ v_z(t) = 0 \label{rolling_vz_ball} $$

Angular momentum:

$$ \omega_x(t) = 0 \label{rolling_ox_ball} $$

$$ \omega_y(t) = \frac{v_x(t)}{R} \label{rolling_oy_ball} $$

$$ \omega_z(t) = \omega_{0z} - \frac{5\mu_{sp}g}{2R}t \label{rolling_oz_ball} $$

Validity:

$0 \le t \le \frac{\lvert \vec{v}_0 \rvert}{\mu_r g}$. If $\frac{2R}{5\mu _{sp} g}
\omega _{0z} < \frac{\lvert \vec{v}_0 \rvert}{\mu_r g}$, then $\omega_z(t) = 0$ for $t >
\frac{2R}{5\mu _{sp} g} \omega _{0z}$.

</div>

The chosen frame of reference (centered at ball's initial coordinates, x-axis in direction of
motion) is convenient, but annoying to deal when you are interested in knowing how the ball evolves
**in relation to the table coordinates**. Suppose $\hat{v}_0$ relates to the table in the following
way:

[![table_coordinates]({{images}}/table_coordinates.jpg)]({{images}}/table_coordinates.jpg){:.center-img .width-30}
_**Figure 5**. Coordinate system in which the table is described. $\phi$ relates the ball's unit vector
of motion, $\hat{v}_0$, to the table coordinates. The origin (0,0) is the bottom left pocket._

Then $\hat{v}_0$ can be expressed in terms of the table coordinates via the following rotation
matrix:

$$
R = \begin{bmatrix}
    \cos\phi & -\sin\phi & 0 \\
    \sin\phi & \cos\phi & 0 \\
    0 & 0 & 1
\end{bmatrix}
\label{rot_mat}
$$

We can rotate Eqs. $\eqref{rolling_rx_ball}$-$\eqref{rolling_oz_ball}$ via Eq. $\eqref{rot_mat}$
and subsequently add an initial displacement vector $\vec{r}_0$ to Eqs. $\eqref{rolling_rx_ball}$-$\eqref{rolling_rz_ball}$ in
order to rewrite the rolling equations of motion in the table coordinate system:

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

Angular momentum:

$$ \omega_x(t) = - \frac{1}{R} \lvert \vec{v}(t) \rvert \sin(\phi) \label{rolling_ox_table} $$

$$ \omega_y(t) = \frac{1}{R} \lvert \vec{v}(t) \rvert \cos(\phi) \label{rolling_oy_table} $$

$$ \omega_z(t) = \omega_{0z} - \frac{5\mu_{sp}g}{2R}t \label{rolling_oz_table} $$

Validity:

$0 \le t \le \frac{\lvert \vec{v}_0 \rvert}{\mu_r g}$. If $\frac{2R}{5\mu _{sp} g}
\omega _{0z} < \frac{\lvert \vec{v}_0 \rvert}{\mu_r g}$, then $\omega_z(t) = 0$ for $t >
\frac{2R}{5\mu _{sp} g} \omega _{0z}$.
</div>

### - Case 4: Sliding

{:.notice}
If you're ended up here without reading Case 3 (the rolling case), you might consider briefing specifically the
section on relative velocity, otherwise this won't make any sense.

Sliding occurs whenever there is a non-zero relative velocity, $\vec{u}(t)$,
between the ball and cloth at the point of contact. If you need to know whether you're sliding, take this
zaney flowchart questionnaire:

[![are_you_sliding]({{images}}/are_you_sliding.jpg)]({{images}}/are_you_sliding.jpg){:.center-img .width-50}
_**Figure 6**. Determine whether or not you are sliding.  $\lvert \vec{v} \rvert$ is the speed of the
ball, $\omega _{\parallel}$ is the angular momentum in the direction of motion, and $\omega _{\bot}$ is the
angular momentum that is both orthogonal to the direction of motion and parallel to the table. Note
that as discussed in Case 3, $\omega_z$ does not influence $\vec{u}(t)$, and therefore has no impact
on whether or not you are sliding._

If there is any curvature whatsoever in the trajectory of a ball, it occurs while the ball is
sliding (assuming the table is perfectly level). If you shoot a draw or stun shot, the cue ball is
sliding. Directly after an object ball is struck by the cue ball, it is in a sliding state until
friction with the cloth drives it into the rolling state. Starting to get the idea? Good.

What separates the sliding case from the rolling case is that $\vec{u}(t)$ can point in any
direction in the $xy-$plane. The most important thing to note about this case is that whichever
direction $\vec{u}(t)$ points, a frictional force opposes it. This can lead to curved trajectories.
To see how, consider Figure 7, in which a ball is initially moving in the $+x-$direction, along with angular
momentum also in the $+x-$direction. This is the kind of spin that a screw has when screwed into
wood, where the spin of the screw is about the same axis as the axis of motion--a rather unrealistic
spin to impart on a ball in the game of pool, but useful for the purposes of demonstration:

[![sliding_diagram]({{images}}/sliding_diagram.jpg)]({{images}}/sliding_diagram.jpg){:.center-img .width-70}
_**Figure 7**. A ball moving in the $+x-$direction with angular momentum also in the $+x-$direction. The
left panel shows a bird's eye view, and the right panel shows a side view of the table and ball, as
if looking down the barrel of the cue stick. Because $\vec{\omega}(t)$ is parallel to $\vec{v}(t)$,
the $R \hat{k} \times \vec{\omega}(t)$ component in Eq. $\eqref{rel_vel}$ is orthogonal to
$\vec{v}(t)$. The below paragraph defines the force terms._

I am used to thinking about friction opposing the ball's center of mass motion, and that frictional
force is still present in the sliding case and is shown in Figure 7 as $\vec{F}_S$ (straight-line
force).  Yet, the $R \hat{k} \times \vec{\omega}(t)$ contribution to $\vec{u}(t)$ (see Eq.
\eqref{rel_vel}) also creates a frictional force, $\vec{F}_C$ (curved-line force). The sum of these
two force terms, $\vec{F} = \vec{F}_C + \vec{F}_S$, yields the net frictional force manifesting from
the ball-cloth interaction, and is anti-parallel to the relative velocity, $\vec{u}(t)$. (Note that
because $\vec{\omega}(t)$ was exactly parallel to $\vec{v}(t)$, $\vec{F}_C$ and $\vec{F}_S$ are
orthogonal, but in general this is not true). Since there exists a force component, $\vec{F}_C$,
which is orthogonal to the ball's velocity, **this ball will begin curving to the right** (the
negative $y-$direction)! The ball will continue to curve until $|\vec{u}(t)| \rightarrow 0$, at
which point the ball enters the rolling state, where it will spend the rest of its days
transiting a line. The equation governing $|\vec{u}(t)| \rightarrow 0$ is

$$
\vec{u}(t) = (u_0 - \frac{7}{2} \mu_s g t ) \, \hat{u}_0
\label{rel_vel_evo}
$$

where $u_0$ is the magnitude of $\vec{u}(t=0)$ and $\mu_s$ is the sliding coefficient of friction.

To establish the equations of motion for the sliding case, let's again use a frame of reference
centered about the ball's _initial_ center of mass coordinates. Additionally, we assume the _initial_
center of mass velocity, $\vec{v}(0)$, points in the $+x-$direction. Then,

<div class="extra-info" markdown="1">
<span class="extra-info-header">Sliding equations of motion (**ball coordinates**)</span>

Displacement:

$$ \vec{r}(t) = \vec{v}_0 \, t - \frac{1}{2} \mu_s g t^2 \, \hat{u}_0 \label{sliding_r_ball} $$

Velocity:

$$ \vec{v}(t) = \vec{v}_0 - \mu_s g t \, \hat{u}_0  \label{sliding_p_ball} $$

Angular momentum:

$$ \vec{\omega}_{xy}(t) = \vec{\omega}_{0xy} - \frac{5 \mu_s g}{2 R} \, t \, (\hat{k} \times \vec{u}_0) \label{sliding_parallel_ball} $$

$$ \omega_z(t) = \omega_{0z} - \frac{5\mu_{sp}g}{2R}t \label{sliding_perp_ball} $$

Validity:

$0 \le t \le \frac{2}{7}\frac{u _0}{\mu _s g}$. If $\frac{2R}{5\mu _{sp} g}
\omega _{0z} < \frac{2}{7}\frac{u _0}{\mu _s g}$, then $\omega_z(t) = 0$ for $t >
\frac{2R}{5\mu _{sp} g} \omega _{0z}$.
</div>

These are essentially the same as the rolling equations, except the acceleration terms in the
$xy-$plane act in the $\hat{u}_0$ direction instead of the $\hat{v}_0$ direction, and the rolling
coefficient of friction $\mu_r$ is replaced with the sliding coefficient of friction $\mu_s$.

We can express these in table coordinates by applying the rotation matrix (Eq. $\eqref{rot_mat}$),
which yields

<div class="extra-info" markdown="1">
<span class="extra-info-header">Rolling equations of motion (**table coordinates**)</span>

Displacement:

$$ r_x(t) = r_{0x} + v_0 \cos(\phi) \, t - \frac{1}{2} \mu_s g \, ( u_{0x} \cos(\phi) - u_{0y} \sin(\phi) ) \, t^2 \label{sliding_rx_table} $$

$$ r_y(t) = r_{0y} + v_0 \sin(\phi) \, t - \frac{1}{2} \mu_s g \, ( u_{0x} \sin(\phi) + u_{0y} \cos(\phi) ) \, t^2 \label{sliding_ry_table} $$

$$ r_z(t) = 0 \label{sliding_rz_table} $$

Velocity:

$$ v_x(t) = v_0 \cos(\phi) - \mu_s g \, ( u_{0x} \cos(\phi) - u_{0y} \sin(\phi) ) \, t \label{sliding_vx_table} $$

$$ v_y(t) = v_0 \sin(\phi) - \mu_s g \, ( u_{0x} \sin(\phi) + u_{0y} \cos(\phi) ) \, t \label{sliding_vy_table} $$

$$ v_z(t) = 0 \label{sliding_vz_table} $$

Angular momentum:

$$
\omega_x(t) =
    \omega_{0x} \cos(\phi) - \omega_{0y} \sin(\phi) +
    \frac{5 \mu_s g}{2R} (u_{0y} \cos(\phi) + u_{0x} \sin(\phi)) \, t
\label{sliding_ox_table}
$$

$$
\omega_y(t) =
    \omega_{0x} \sin(\phi) + \omega_{0y} \cos(\phi) +
    \frac{5 \mu_s g}{2R} (u_{0y} \sin(\phi) - u_{0x} \cos(\phi)) \, t
\label{sliding_oy_table}
$$

$$ \omega_z(t) = \omega_{0z} - \frac{5\mu_{sp}g}{2R}t \label{sliding_oz_table} $$

Validity:

$0 \le t \le \frac{2}{7}\frac{u _0}{\mu _s g}$. If $\frac{2R}{5\mu _{sp} g}
\omega _{0z} < \frac{2}{7}\frac{u _0}{\mu _s g}$, then $\omega_z(t) = 0$ for $t >
\frac{2R}{5\mu _{sp} g} \omega _{0z}$.
</div>

This concludes the section of ball-cloth interactions, at least for now.

## **Section II**: ball-ball interactions

This section is dedicated to the collision physics between two balls. When physically modelling a
phenomenon, the sky is the limit in terms of how real you want to get. In consideration of the
ball-ball interaction, a complete classical description would entail treating the balls as
compressible objects--perhaps even modelling the pressure waves that emanate within each ball during
a collision. Perhaps this treatment is most necessary during the break shot, and I would be very
interested to know how the degree of realism of such a treatment compares to the more pragmatic
approaches I will be taking. Speaking of which, here are the two models I will present:

1. Elastic, instantaneous, frictionless
1. Elastic, instantaneous (TODO)

In each of these models, multi-ball collisions are not considered, _i.e._ each interaction is
pairwise.

###  (1) Elastic, instantaneous, frictionless

In this model, collisions are perfectly elastic, which means no energy dissipates as a result of the
collision. This is not true for several reasons. First of all, pool balls make noise when they
collide, and those sound waves are a form of energy dissipation from the system. Then there is heat
generated via the collision, another form of energy dissipation. Are there more instances of energy
dissipation? Those are the ones I can think of anyways.

Another assumption is that the balls interact instantaneously. Like everything, pool balls are
viscoelastic objects and have some minute degree of compressibility. When objects compress, they
exhibit a spring-like response, like how this bouncy ball compresses into the ground:

{% include youtube_embed.html id="tTt886y0rWI" %}

As seen in the clip, this creates an interaction between the bouncy ball and the ground that lasts a
finite period of time. Pool balls are subject to the same phenomenon, to a degree order**s** of
magnitude less exaggerated. However slight the effect may be, in reality pool balls interact over a
finite period of time, a time that this model will ignore.

The final assumption is that the ball-ball interaction is frictionless, _i.e._ perfectly slippery.
This implies that there is no transfer of spin from one ball to another, which is commonly known as
throw.

{:.notice}
The frictionless assumption is the worst of these assumptions, since friction between balls is what
causes spin- and cut-induced throw, which are effects that exhibit substantial influence on shot
outcome, and must be accounted for by amateurs and pros alike. In the next model, I will account for
friction between balls.

For this model, I first tackle the simple scenario in which a moving ball strikes a stationary ball.
Then, I handle the general case of 2 moving balls.

#### - Case 1: stationary ball

Assuming the elastic, instantaneous, and frictionless model, consider a moving ball that hits a
stationary ball, shown in Figure 8:

[![ball_ball_collision_1]({{images}}/ball_ball_collision_1.jpg)]({{images}}/ball_ball_collision_1.jpg){:.center-img .width-70}
_**Figure 8**. Ball A (blue) strikes ball B (red) with an incoming velocity $\vec{v}_0$ in the
$+x-$direction. The unfilled circle shows where ball A ends up striking ball B. During contact, the
line connecting the centers of the two balls (the line of centers) forms an angle $\alpha$ with
$\vec{v}_0$. The outgoing velocity of ball B, $\vec{v}_B$, runs along the line of centers, and the
outgoing velocity of ball A, $\vec{v}_B$, is perpendicular to $\vec{v}_B$._

If we imagine that Ball A is the cue ball and ball B is an object ball, this represents a "cut shot"
of $\alpha$ degrees. We would like to know how to resolve this collision. What do I mean by
"resolve"? I mean, Given the state of the balls the moment _before_ the collision, what is the state
of the balls the moment _after_ the collision. Just like in [Section
I](#section-i-ball-cloth-interactions), the state of a ball is defined by its position, velocity,
and angular momentum.

Some of these we can bang out right away.
Suppose the collision happens between $t = \tau$ and $t = \tau + dt$, keeping in mind instantaneity
of the collision dictates that $dt$ is infinitesimally small. There is thus no amount of time for
the balls to change position in the moments immediately before and after the collision. Therefore

$$ \vec{r}_A(\tau+dt) = \vec{r}_A(\tau) \notag $$

$$ \vec{r}_B(\tau+dt) = \vec{r}_B(\tau) \notag $$

One down. Since we are not accounting for friction effects, there is no loss or change in angular momentum due
to the collision:

$$ \vec{\omega}_A(\tau+dt) = \vec{\omega}_A(\tau) \notag $$

$$ \vec{\omega}_B(\tau+dt) = \vec{\omega}_B(\tau) \notag $$

Two down. This leaves only the velocities of the balls, which certainly do change. To solve the outgoing
velocities, we're going to need some conservation of momentum and energy. Figure 8 details the scenario above. For
convenience, the coordinate system is defined so that $\vec{v}_0$ points in the $+x-$direction.

Before getting into equations, what's clear immediately is that we know the outgoing direction of
Ball B just from geometry: it is parallel to the line that connects the centers of the balls at the
moment of impact. That's because this line marks the direction of force that Ball A applies to Ball
B. Now, let's figure out the outgoing direction of Ball B.

According to conservation of linear momentum, the momentum before the collision equals the momentum
after it:

$$
m\vec{v}_0 = m\vec{v}_A + m\vec{v}_B
\notag
$$

$$
\vec{v}_0 = \vec{v}_A + \vec{v}_B
\label{p_1}
$$

Concurrently, conservation of energy states that the energy before the collision equals the energy after it

$$
E(\tau) = E(\tau + dt)
\label{con_energy}
$$

Since the model ignores angular momentum transfer, we need only account for the kinetic energy resulting from
linear translation of the balls. Plugging kinetic energy terms into Eq. $\eqref{con_energy}$ yields

$$
\frac{1}{2} m \lvert \vec{v}_0 \rvert ^2 = \frac{1}{2} m \lvert \vec{v}_A \rvert ^2 + \frac{1}{2} m \lvert \vec{v}_B \rvert ^2
\notag
$$

$$
\lvert \vec{v}_0 \rvert ^2 = \lvert \vec{v}_A \rvert ^2 + \lvert \vec{v}_B \rvert ^2
\notag
$$

$$
\vec{v}_0 \cdot \vec{v}_0 = \lvert \vec{v}_A \rvert ^2 + \lvert \vec{v}_B \rvert ^2
\label{E_1}
$$

Plugging Eq. $\eqref{p_1}$ into the LHS of Eq. $\eqref{E_1}$ yields something very interesting:

$$
(\vec{v}_A + \vec{v}_B) \cdot (\vec{v}_A + \vec{v}_B) = \lvert \vec{v}_A \rvert ^2 + \lvert \vec{v}_B \rvert ^2
\notag
$$

$$
\lvert \vec{v}_A \rvert ^2 + \lvert \vec{v}_B \rvert ^2  +  2 \, \vec{v}_A \cdot \vec{v}_B = \lvert \vec{v}_A \rvert ^2 + \lvert \vec{v}_B \rvert ^2
\notag
$$

$$
\vec{v}_A \cdot \vec{v}_B = 0
\label{perp}
$$

The inner product of $\vec{v}_A$ and $\vec{v}_B$ is 0, which means that outgoing velocities of the 2
balls are $90^{\circ}$ to one another! Since we know the direction of $\vec{v}_B$ (from geometry),
we know the direction of $\vec{v}_A$ as well. To determine the magnitudes, we superpose the 3
velocity vectors on top of each other:

[![ball_ball_velocity_vectors]({{images}}/ball_ball_velocity_vectors.jpg)]({{images}}/ball_ball_velocity_vectors.jpg){:.center-img .width-50}
_**Figure 9**. Geometrical relationships between $\vec{v}_0$, $\vec{v}_A$, and $\vec{v}_B$._

This diagram contains 3 critical pieces of information.

1. $\vec{v}_B$ makes an angle, $\alpha$, with the incoming velocity, $\vec{v}_0$. This is known
   because Ball A imparts an impulse to Ball B in the direction parallel to the line connecting
   their two centers of mass.

2. The sum of $\vec{v}_A$ and $\vec{v}_B$ is $\vec{v}_0$. This is known from Eq. $\eqref{p_1}$, the
   conservation of linear momentum.

3. $\vec{v}_A$ is perpendicular to $\vec{v}_B$. This is known from Eq. $\eqref{perp}$, which used
   both conservation of energy and linear momentum.

Given these facts, we can soh-cah-toa our way to the answer. Expressed in terms of
$\alpha$ and $v_0$, we get:

$$
\vec{v}_A(t+\tau) = (v_0 \sin\alpha) \, \hat{v}_A
\notag
$$

$$
\vec{v}_B(t+\tau) = (v_0 \cos\alpha) \, \hat{v}_B
\notag
$$

Putting it all together, we have our equations for the elastic, instantaneous, and frictionless ball-ball collision
in the specific case where one ball is stationary:

<div class="extra-info" markdown="1">
<span class="extra-info-header">Elastic, instantaneous, frictionless ball-ball collision (**stationary case**)</span>

Displacement:

$$
\vec{r}_A(\tau+dt) = \vec{r}_A(\tau)
\label{rA_simple}
$$

$$
\vec{r}_B(\tau+dt) = \vec{r}_B(\tau)
\label{rB_simple}
$$

Velocity:

$$
\vec{v}_A(t+\tau) = (v_0 \sin\alpha) \, \hat{v}_A
\label{vA_simple}
$$

$$
\vec{v}_B(t+\tau) = (v_0 \cos\alpha) \, \hat{v}_B
\label{vB_simple}
$$

Angular momentum:

$$
\vec{\omega}_A(\tau+dt) = \vec{\omega}_A(\tau)
\label{oA_simple}
$$

$$
\vec{\omega}_B(\tau+dt) = \vec{\omega}_B(\tau)
\label{oB_simple}
$$

</div>

#### - Case 2: both moving

Relaxing the assumption that one ball is stationary may at first seem like a terrible idea--the
introduced complexity must be horrible. And that intuition is basically correct. Treating both balls as
moving would be a nightmare. Yet even when both balls are moving, we don't need to _treat_ it that
way. Instead, we can change to a frame of reference that moves with one of the balls. In such a frame
of reference, that ball is stationary. A picture of the situation is shown in Figure 10:

[![ball_ball_collision_2]({{images}}/ball_ball_collision_2.jpg)]({{images}}/ball_ball_collision_2.jpg){:.center-img .width-90}
_**Figure 10**. In the left panel, Ball A (blue) and Ball B (red) are both moving and due to collide at
the position of the unfilled circles. If $\vec{v}_B$ is subtracted from the velocities of both
balls ($-\vec{v}_B$ is shown as the yellow vectors), the frame of reference is changed to one that moves
with ball B, shown in the right panel. In this scenario, ball B is stationary, and the situation
reduces to Case 1, and specifically the situation depicted in Figure 8._

Since physics behaves the same as viewed from all inertial reference frames, we are well within our rights
to make this transformation during the collision. After solving the outgoing state post-collision,
we can reverse the transformation and voila, we are done. This makes Case 2 trivial, since it can be
reduced to Case 1. Explicitly, the procedure goes like this:


<div class="extra-info" markdown="1">
<span class="extra-info-header">Elastic, instantaneous, frictionless ball-ball collision (**both moving**)</span>

First, make the following transformation so Ball B is stationary:

$$
\vec{v}_B'(\tau) = \vec{v}_B(\tau) - \vec{v}_B(\tau) = \vec{0}
\label{trans_B}
$$

$$
\vec{v}_A'(\tau) = \vec{v}_A(\tau) - \vec{v}_B(\tau)
\label{trans_A}
$$

The velocities of the collisions are resolved via Eqs. $\eqref{vA_simple}$ and $\eqref{vB_simple}$,
where Eq. $\eqref{trans_A}$ is substituted as $\vec{v}_0$. This yields post-collision velocity
vectors $\vec{v}_A'(\tau + dt)$ and $\vec{v}_B'(\tau + dt)$, which can be transformed back to the table
frame of reference via the inverse transformation (adding back $\vec{v}_B(\tau)$):

$$
\vec{v}_A(\tau + dt) = \vec{v}_A'(\tau + dt) + \vec{v}_B(\tau)
\label{inv_trans_A}
$$

$$
\vec{v}_B(\tau + dt) = \vec{v}_B'(\tau + dt) + \vec{v}_B(\tau)
\label{inv_trans_B}
$$

</div>

## **Section III**: ball-rail interactions

The ball-rail interaction is probably the most difficult to model accurately. There are so many
factors to consider. The height, shape, friction, and compressibility of the cushion. The incoming
angle, velocity, and spin of the ball. All of these have significant effects on how the rail
influences the ball's outgoing state. Let's take a look in slow motion:

{% include youtube_embed.html id="yWH-CbV6BwQ" %}

First, you can really see that the rail deforms substantially throughout its interaction with the ball.

[![cushion_depression]({{images}}/cushion_depression.png)]({{images}}/cushion_depression.png){:.center-img .width-70}
*Pool ball significantly deforming the cushion [Source](https://www.youtube.com/watch?v=yWH-CbV6BwQ).*

The implication is two-fold. First, the interaction is non-instantaneous. In fact, it persists far
longer than the ball-ball interaction. Yet finite-time interactions open up a can of worms for
multi-body dynamics, since a second ball may join the party and collide with the first ball whilst
it is interacting with the cushion. For this reason, along with the inherent complexity of the
soft-body physics, modelling the interaction as non-instantaneous is likely unfeasible. Second,
there is no single point of contact (PoC) between ball and cushion. Rather, the interaction occurs
over a line of contact (LoC), each infinitesimal segment of which contributes to the applied force.
These complexities are why the ball-cushion interaction is the least accurately modelled aspect of
pool physics simulations.

Did you notice that the ball pops into the air post-collision? This happens
because the apex of the cushion is at a height greater than the ball's radius, and so the outgoing
velocity of the ball has a component that goes _into_ the table. Consequently, the slate of the
table applies a normal force to the ball, popping it up into the air.  Importantly, I want to
distinguish between the ball-slate interaction and the ball-cushion interaction: the ball-cushion
interaction creates the outgoing velocity of the ball, which under most circumstances has a
component _into_ the table. An infinitesimally small amount of time later, the ball-slate
interaction occurs, which prevents translation into the table's surface, and in some cases pops
the ball into the air if its speed is great enough. This section deals strictly with the
ball-cushion interaction, and in the next section I will treat the ball-slate interaction.

Given the complexity of the ball-cushion interaction, I'm unable to talk extensively through the equations,
as I have for the ball-cloth and ball-ball interactions. Instead, I will just discuss the models I considered,
and present the equations, with perhaps a sprinkle of the intuition behind them. So far, I have considered 3
models: Mathavan _et. al_, 2010; Marlow, 1994; Han, 2005. Let's take a look.

### (1) Mathavan _et. al_, 2010

After searching the literature, the most complete treatment I have found is [this work by Mathavan
_et. al_
(2010)](https://www.researchgate.net/publication/245388279_A_theoretical_analysis_of_billiard_ball_dynamics_under_cushion_impacts)
entitled, "_A theoretical analysis of billiard ball dynamics under cushion impacts_". They develop a
model that must be solved numerically using differential equations, which is relatively complex. To get
a rough idea of how involved this model is, check out the force body diagram in Figure 4:

[![mathavan_2010_1]({{images}}/mathavan_2010_1.png)]({{images}}/mathavan_2010_1.png){:.center-img .width-50}

_Force body diagram from Mathavan *et. al*, 2010. [source](https://www.researchgate.net/publication/245388279_A_theoretical_analysis_of_billiard_ball_dynamics_under_cushion_impacts)_

This is the kind of thing that takes a long time to wrap your ahead around the meaning of the
variables. Despite the model's complexity, it is still very simple in comparison to reality because
it assumes the cushion deformation is insignificant, and thus the interaction instantaneous. Despite
this being a large departure from reality, they report really good agreement with experiment.

This is definitely the best model I could find that I would be willing to implement, but at this
moment in time I don't _really_ want to solve differential equations on-the-fly everytime there is a
ball-cushion interaction. Perhaps I could solve the differential equations for the entire parameter
space and then parameterize the solution space somehow, but for now I would like to avoid this model
altogether and look for something simpler.

### (2) Marlow, 1994

So Marlow has a book called "The Physics of Pocket Billiards" that I use as a reference for pool
physics. In general, its very comprehensive, but in the case of the ball-cushion interaction he
presents an incomplete and inconsistent treatment. Moving on.

### (3) Han, 2005

I enjoy [this treatment by Han, 2005](https://link.springer.com/article/10.1007/BF02919180),
entitled, "_Dynamics in carom and three cushion billiards_". It assumes instantaneity and negligible
cushion deformation. It is simple, analytic, and appears to be physically plausible. That said, it
is less realistic than Mathavan _et. al_, 2010.

Alright, so let's go over the model. Han chooses the following frame of reference:

[![han_1]({{images}}/han_1.jpg)]({{images}}/han_1.jpg){:.center-img .width-50}

_**Figure 11**. A ball colliding with a rall viewed from above. The frame of reference is defined so
that the rail is perpendicular to the $x-$axis, and the $+x=$direction points away from the playing
surface. The incoming velocity makes an angle $\phi$ with the $x-$axis._

At the instant of contact, $t=\tau$, the ball has a state $(\vec{r}(\tau), \vec{v}(\tau),
\vec{\omega}(\tau))$, and immediately afterwards it has the state $(\vec{r}(\tau + dt), \vec{v}(\tau
+ dt), \vec{\omega}(\tau + dt))$.  Since Han assumes instantaneity, $dt$ is an infinitesimal amount
of time. Since there is no funny business going on with cushion deformation, we know that the
position at $\tau$ will equal the position at $\tau + dt$:

$$
\vec{r}(\tau + dt) = \vec{r}(\tau)
\notag
$$

Resolving the velocity and angular momentum requires some geometry of the ball-cushion interface.

[![han_0]({{images}}/han_0.jpg)]({{images}}/han_0.jpg){:.center-img .width-70}

_**Figure 12**. A ball colliding with a rall viewed from the side. It is the same scenario as in
Figure 11. $R+\epsilon$ defines the height of the cushion, where contact is made with the ball.
$\theta$ is determined uniquely by $\epsilon$, and defines the direction of the impulse the cushion
imparts on the ball._

One of the most important determinants in this model, and in reality, is the height of the rail.
This will determine the direction that the cushion applies force to the ball. Have
you ever played on a table with rails that are too short? The tendency is that any hard shots pop
into the air. <describe intution, then epsilon theta relationship>. Then hit them with the
equations.

After surveying the equations for consistency, I found 2 mistakes, that I outline in [this
worksheet]({{images}}/ball_cushion_inhwan_han.pdf). After accounting for them, the Han model yields
the following time evolution for the ball-cushion interaction:

<div class="extra-info" markdown="1">
<span class="extra-info-header"> ball-cushion interaction (**Han 2005 model**)</span>


</div>















## How do state of the art pool simulators work?

The shining greats in terms of physics realism are without a doubt ShootersPool Billiards
Simulation and Virtual Pool 4. Look at the pure beauty of this ShootersPool demo:

[![ShootersPool](http://img.youtube.com/vi/sDW0ENZzClk/0.jpg)](https://www.youtube.com/watch?v=sDW0ENZzClk "ShootersPool")

Both from a graphics and physics perspective, this appears very real. The only physical inaccuracy I
can spot is as balls are entering the pockets they seem to undergo a pre-baked animation rather than
interacting genuinely with the pocket. Here is the trailer for Virtual Pool 4:

[![Virtual Pool 4](http://img.youtube.com/vi/mAxACAt6m8g/0.jpg)](https://www.youtube.com/watch?v=mAxACAt6m8g "Virtual Pool 4")

Less impressive graphics and no slo-mo shots to scrutinize in careful detail, but having played the
game myself, I can attest to the quality of the physics.

So how do these pool simulators actually work? I have no idea, and that is understandably by design.
I wasn't able to gain any insight into how much money these companies are making from pool games but
let me know if you have any estimates. Regardless, both of these projects have been monetized and
have reason to keep their algorithms to themselves.

So the bottom line is that I have no idea what's going on under the hood in these games, but by
doing some research I think all pool simulators are going to fall under these two umbrellas:
discrete time integration, or continuous event-based integration. So let's talk about these.

## Pool simulator research

I never had any intention of developing this from scratch. To that end, I started researching
academical papers on pool simulation, which are surprisingly numerous. Usually, the research is
motivated by developing a realistic/fast physics engine as a necessary precursor to creating a robot
that can play pool:

[![Pool Robot](http://img.youtube.com/vi/4ArBw9kEMMw/0.jpg)](https://www.youtube.com/watch?v=4ArBw9kEMMw "Pool Robot")

Another application is to study game theory and make a billiards AI. In any case, during my literature
review I stumbled upon the work of Leckie and Greenspan entitled [An Event-Based Pool Physics
Simulator](https://link.springer.com/chapter/10.1007/11922155_19). A free pre-print of this
publication is available
[here](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.89.4627&rep=rep1&type=pdf). This is
a pretty groundbreaking paper, because they develop a method to solve the trajectories of pool balls
that avoid discrete time integration, the most common way to evolve many-body systems through time.
To contextualize their algorithm, I should first talk about what they avoid doing: time integration.

### Discrete Time Integration

Simply put, discrete time integration works by advancing the state forward in small time steps,
let's say an amount $dt$. At each timepoint $t$, the forces governing the motions are calculated,
and then all of the bodies' states (positions, velocities, etc.) are advanced to $t + dt$, under the
assumption that the forces are constant over that duration. It is critical that these time steps are
small enough, otherwise the evolution will be physically inaccurate. To see why, consider the example of
one ball hitting another:

Let's say the goal is to determine the collision time as accurately as possible. So Ball A on the
bottom is moving with a constant velocity towards Ball B. At each timestep, it is checked whether
the collision has occurred, which is done checking if the balls intersect. In the first panel a
large timestep is chosen, and we can see that the collision is detected well after the balls first
intersect. By choosing a smaller timestep like in the second panel we see a more accurate
determination of the time of collision.

So the smaller the time step, the more accurate this assumption is. But this comes at the cost of
subdividing your simulation time into smaller and smaller timesteps, each which come with increased
cost of computation. This can become brutal when dealing with pool simulations. Ball speeds commonly
reach $10$ m/s, and a reasonable requirement for realism is that 2 balls should never intersect more
than $1/100$th of a ball radius ($0.3$ mm). The required timestep for this level of realism is then
$30$ microseconds. If the time from the cue strike to the last ball rolling is 10 seconds, that is
$30,000$ time steps in total for one shot. If the level of realism is $1/1000$th a ball radius, that
is $300,000$ time steps. Yikes.

The problem with this is all of the wasted computation... I don't need $30$ microsecond time steps
when all of the balls are far apart and barley moving. It is only really in select scenarios, such a
pool break, that realism demands such miniscule time steps. So a smart numerical integration
scheme would be to cut down on the number of time steps by making them
[adaptive](https://en.wikipedia.org/wiki/Adaptive_step_size) depending on the state of the system.
There are an infinite number of ways you could develop heuristics for an adaptive time stepper, that
may be based on the distances between balls (if they are far apart, increase the time step), or
based on velocities (if they are moving fast, decrease the time step). I'm not even going to go
there because the possibilities are endless, although I am convinced that if Virtual Pool 4 or
ShootersPool are using discrete time integration, they are using adaptive time stepping.

### Continuous Event-based Simulation

Even with adaptive time stepping, there is going to be wasted computation. So ideally, you'd want to
avoid it altogether. In the example of the colliding balls, what if we could predict when the
collision happens by using knowledge of their positions and velocities? After all, it looks plainly
obvious that they are going to collide, so why waste our time advancing with so many time steps?
Let's add some variables to the picture and solve for $t$!

FIXME

$R$ is the ball radii, $v$ is the speed of the ball, and $d$ is the distance they are from collision
the collision state. If we assume that the Ball A moves with constant velocity, the time until
collision is quiter simply $\tau = d/v$.

This has some serious advantages over time integration. First, it is computationally much more
efficient. It was just one instance of arithmetic: $d/v$. Second, it is not subject to
discretization error. In the discrete time integration method above, the collision is detected
_after_ it happened since the collision is detected by seeing if the balls are intersecting. But if
they are intersecting, they already collided! This is what I'm calling discretization error. In
contrast, there is no error in $d/v$, save for floating point error.

This is actually a huge deal from the perspective of simulation, but it requires mathematical
formulas for the positions of the bodies as a function of time, and in most multi-body systems, this
is too much to ask. For example, the system of 3 planets exhibiting gravitational forces on one
another has no analytical mathematical formula for the positions as a function of time. Look at how
complex the solution becomes:

FIXME (embed and hyperlink goes to wiki)

<img src="media/3_body_problem.gif" width="450" />
By Dnttllthmmnm - Own work, CC BY-SA 4.0, https://commons.wikimedia.org/w/index.php?curid=59538221

#### The algorithm is essentially this

In the above case, discrete numerical integration is a necessity. So is a necessity for pool physics
too? Well, unlike the 3-body gravitational problem which exhibit forces on each other even at a
distance, balls only interact with each other during extremely brief collisions (OK fine, pool balls
also exhibit gravitational forces on each other at a distance, but you're just being pedantic).
Other than during these brief moments, the trajectories of the balls have closed-form equations that
describe their positions, velocities, and spins. So this doesn't solve the problem entirely, but I
can at least accurately simulate the evolution of a pool shot from $t=0$ up to the first collision
without any time integration because I have analytical forms of the trajectories as a function of
time! Then I could apply some well-trodden physics to resolve the
collision, and then evolve the state of all balls until the _next_ collision. Essentially, if you
can solve when a collision happens, you can evolve all balls up to that point in time, solve the
collision's physics by updating the states of the ball(s) involved in the collision, and then
advance time to the next collision. Rinse and repeat.

That's pretty good news, but it is still unknown how to calculate when the first collision occurs.
The solution employed by Leckie and Greenspan is to calculate all possible collision times and take
the one that occurs in the minimal amount of time. When I say all, I mean all.  Since the
trajectories of each ball are known as a function of time (they are quadratic with respect to time
because of the deceleration from the cloth), the collision time between each pair of balls can be
calculated from a fourth order polynomial with respect to time. The roots of this polynomial are the
time needed for the balls to collide. As we know, most balls will not collide--a typical shot will
have maybe 1 or 5 collisions.  The absence of a collision manifests mathematically as negative or
imaginary values to the roots of the fourth order polynomial. So if you have $15$ balls, that means
you have $105$ collision pairs to check, and most of these will not collide (yielding negative or
imaginary values). Yet a subset of these ball-pairs _will_ yield positive real values.  If a
ball-pair yields a non-negative real value, it means that if no other balls or cushions were to "get
in the way" of the collision, the balls would collide in a finite amount
of time. By picking the
one with a smallest postive and real-valued solution to the quartic polynomial, we ensure by
definition that this is the first collision that occurs.

With this time value in hand, we advance the trajectories of _all_ balls up to that point in time,
at which point a collision is occuring, i.e. 2 balls or a ball and a rail are touching. Then, we
apply well-trodden physics that explains the outgoing states of the balls as a result of the
collision (which we assume is instantaneous). After updating the states of the involved balls, we
rinse and repeat: We find the next event, advance the states of all balls up to that time by using
the analytical expressions we have, resolve the physics of the collision, and so on and so forth.

Here is my sketch of the algorithm:

FIXME

## Continuous Event-based simulation is da way man

After doing my resarch, I realized I have _got_ to do a continuous event-based approach. Leckie and
Greenspan give a very rough complexity analysis as to why this is far superior to discrete numerical
integration. For discrete numerical integration, the number of operations is on the order of 

$N (61 n - n^2) / 2$

where $n$ is the number of balls, and $N$ is the number of time steps. OK well writing this down
now, I see this is clearly quite a garbage expression because the number of operations grows
negative with large values of $n$. But the important part is this: time complexity scales linearly
with the number of time steps, i.e. accuracy. But assuming it works for small values of $n$, simulating 3 balls
for 1 second using a very coarse time step of 1 millisecond yields $87,000$ required computations.
In contrast, their derived time complexity expression for their continuous event-based approach is

$(645 n - 19 n^2) / 2$

Which yields only 882 operations. More critically, the complexity depends _only_ on the number of
balls.

The bottomline is this: after reading this paper, I decided this project was going to offer
continuous event-based simulations or it wasn't going to offer anything.
