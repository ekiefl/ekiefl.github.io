---
layout: post
title: "How to make your code fast"
categories: [pooltool]
series: 6
excerpt: "I speed up my python billiards simulator by a factor of FIXME using profiling software, numba, and some ingenuity"
comments: true
authors: [evan]
image:
  feature: pooltool/pooltool_banner.png
  display: true
---

{% capture images %}{{site.url}}/images/pooltool/pooltool-speedup{% endcapture %}
{% include _toc.html %}

## Backstory

If you don't know what [pooltool]({{ site.url }}/projects/pooltool) is, its a pool/billiards simulator I've created over the last 2 years. I'm proud of what I've accomplished, but its currently very slow at calculating shots. For example, here is a shot that takes 13 seconds to calculate:

FIXME vv this has sound in it

{% include youtube_embed.html id="fP-Hmz5Q2XE" %}

This post serves as a practical guide for improving the speed performance of your numerical Python code, and I'll be using pooltool as a vehicle for demonstration.

## Tools

### pprofile

The plan is to measure my program's performance using a code profiler. A code profiler is a program that measures the performance of my code. How many times is each method called? How much time is spent on each line? These are things a code profiler can answer.

For Python, there are many code profiler options, but I've found that I like [pprofile](https://github.com/vpelletier/pprofile). Like other profilers, it can print out line-by-line timings of your code, however these can be really hard to interpret without a graphical interface. In addition, pprofile can output a cachegrind file, which look something like this:
```
# callgrind format
version: 1
creator: pprofile
event: usphit :microseconds/hit
events: hits microseconds usphit
cmd: sandbox/break.py --no-viz --seed 42
fl=<__array_function__ internals>_104
fn=<module>:2
2 2 17 8
cfl=/Users/evan/anaconda3/envs/pooltool/lib/python3.8/functools.py
cfn=wraps:64
calls=1 64
2 1 10 10
3 1 10 10
cfl=/Users/evan/anaconda3/envs/pooltool/lib/python3.8/functools.py
cfn=update_wrapper:34
calls=1 34
3 1 67 67
fl=/Users/evan/anaconda3/envs/pooltool/lib/python3.8/site-packages/numpy/core/records.py
fn=<module>:1
1 2 48 24
36 1 9 9
37 1 11 11
38 1 32 32
cfl=<frozen importlib._bootstrap>
cfn=_handle_fromlist:1017
(...)
```

It details each function call and how much time is spent on each line of code.

{:.notice}
You can download pprofile with a `pip install pprofile`

### kcachegrind

Reading cachegrind files manually is an exercise in torture. Thankfully, there exists a software called [kcachegrind](http://kcachegrind.sourceforge.net/html/Home.html) (or qcachegrind if you're Windows or MacOS) which graphically displays this information in a GUI:

[![qcache_example]({{images}}/qcache_example.png)]({{images}}/qcache_example.png){:.center-img .width-100}
*A screenshot of qcachegrind.*

This is an incredibly powerful, if not overwhelming interface for code introspection, and later in this post I'll be showing you how I use it.

{:.notice}
I'm not sure how to install qcachegrind on Windows or kcachegrind on Linux, but I recently created a [resource page](https://github.com/ekiefl/qcachegrind-mac-instructions) that provides some suggestions for getting your hands on qcachegrind for MacOS.

### Numba

If you're dealing with numerical operations in Python and you don't know what [Numba](https://numba.pydata.org/) is, your life is about to change forever. Here is the gist of Numba, taken from their website:

<blockquote>
Numba translates Python functions to optimized machine code at runtime using the industry-standard LLVM compiler library. Numba-compiled numerical algorithms in Python can approach the speeds of C or FORTRAN.

You don't need to replace the Python interpreter, run a separate compilation step, or even have a C/C++ compiler installed. Just apply one of the Numba decorators to your Python function, and Numba does the rest.
</blockquote>

To be perfectly honest, I am a practitioner of Numba: I know how to use its basic features, and I don't understand how any of it works. If you're looking for a full introduction, I would suggest this [youtube video](https://www.youtube.com/watch?v=-4tD8kNHdXs).

{:.notice}
You can install numba with `pip install numba`.

## Tests

Improving performance comes at the expense of refactoring your code. This could include small changes, or quite substantial changes. Regardless, its essential that you can be confident that your changes preserve the functionality of your program. Your goal is to speed up your program without changing its functionality.

Before attempting to make pooltool faster, I first created a series of tests that ensure functionality is preserved for any future changes. I added these tests in a pull request you can view [here](https://github.com/ekiefl/pooltool/pull/29). Now, pooltool is now hyper aware of any changes made within the `physics.py` module, which is the area most amenable to speed increases.

Since I used [pytest](pytest.org) to develop my tests, I can verify my program produces the exact ball trajectories of a cached break shot by typing `pytest`:

```bash
$ pytest
=================================== test session starts ===================================
platform darwin -- Python 3.8.10, pytest-6.2.5, py-1.11.0, pluggy-1.0.0
rootdir: /Users/evan/Software/pooltool
collected 10 items

pooltool/tests/integration/test_trajectory.py .                                     [ 10%]
pooltool/tests/unit/test_ball.py ..                                                 [ 30%]
pooltool/tests/unit/test_physics.py .......                                         [100%]

=================================== 10 passed in 9.82s ====================================
```

If I then go into `physics.py` and change the functionality, even if just a little bit, pytest will complain that functionality is no longer preserved. For example, if I modify `physics.get_rel_velocity` from

```python
def get_rel_velocity(rvw, R):
    _, v, w = rvw
    return v + R * np.cross(np.array([0,0,1]), w)
```

to 

```python
def get_rel_velocity(rvw, R):
    _, v, w = rvw
    v *= 0.9999999
    return v + R * np.cross(np.array([0,0,1]), w)
```

and rerun my tests, pooltool complains

```python
=================================== test session starts ===================================
platform darwin -- Python 3.8.10, pytest-6.2.5, py-1.11.0, pluggy-1.0.0
rootdir: /Users/evan/Software/pooltool
collected 10 items

pooltool/tests/integration/test_trajectory.py F                                     [ 10%]
pooltool/tests/unit/test_ball.py ..                                                 [ 30%]
pooltool/tests/unit/test_physics.py ......F                                         [100%]

======================================== FAILURES =========================================
____________________________________ test_trajectories ____________________________________

ref = <pooltool.system.System object at 0x11be49fa0>
trial = <pooltool.system.System object at 0x11bd67520>

    def test_trajectories(ref, trial):
        for ball_ref in ref.balls.values():
            ball_trial = trial.balls[ball_ref.id]

            np.testing.assert_allclose(ball_ref.rvw, ball_trial.rvw)
            np.testing.assert_allclose(ball_ref.s, ball_trial.s)
            np.testing.assert_allclose(ball_ref.t, ball_trial.t)
>           np.testing.assert_allclose(ball_ref.history.rvw, ball_trial.history.rvw)
E           AssertionError:
E           Not equal to tolerance rtol=1e-07, atol=0
E
E           Mismatched elements: 282 / 945 (29.8%)
E           Max absolute difference: 0.001852446
E           Max relative difference: 0.0013338636
E            x: array([[[  0.495305,   1.485917,   0.028575],
E                   [  0.      ,   0.      ,   0.      ],
E                   [  0.      ,   0.      ,   0.      ]],...
E            y: array([[[  0.495305,   1.485917,   0.028575],
E                   [  0.      ,   0.      ,   0.      ],
E                   [  0.      ,   0.      ,   0.      ]],...

pooltool/tests/integration/test_trajectory.py:14: AssertionError
_________________________________ test_evolve_ball_motion _________________________________

(...)
```

How you preserve functionality as you refactor your code is totally up to you, but you'll want to have something in place to make sure you don't make a mess of things.

## Getting started

### Make a new branch

Speaking of making a mess of things, it's best not to mess up the state of your code until you're convinced your refactor is paying dividends. I'm going to create a git branch of my codebase.

```
git checkout -b fast
```

### Creating some benchmarks

In order to see whether your speed improvements are helping or hurting, you'll want to establish a benchmark case. You'll run this every time you want to test the performance of your program. Naturally, this script should produce reproducible results each time its ran.

On one hand, a benchmark case should provide an overall assessment of how fast your program runs in practice. Often times this will run over the course of seconds or minutes.

On the other hand, a minute-long script is not ideal when assessing whether your small changes are affecting things. Like measuring a pebble's ripple in a wavy ocean, variability in runtime will make accurate timing measurements impossible.

To get the best of both worlds, I've opted for two benchmark cases, one that runs on the order of seconds, and one on the order of milliseconds.

For my long benchmark I'll use a break shot, which has wide testing coverage with lots of events and computation. I'll use this for profiling and assessing how my overall refactoring is going. This benchmark calculates the ball trajectories in this simulation:

FIXME

For my short benchmark, I'll use a bank shot. Significantly less complex, I'll be using this for accurate timing measurements. Since it runs much faster, I can run this benchmark thousands of times to get accurate timings. This benchmark calculates the ball trajectories in this simulation:

FIXME

It's important that the benchmarks are reproducible. I accomplished this by pickling some system states that are loaded in each benchmark. Then, I created the following python scripts.

First is `benchmark_long.py`, aka the long benchmark used for profiling and overall assessment.

```python
#! /usr/bin/env python

import pooltool as pt

# Run once to compile all numba functions. By doing this,
# compilation times will be excluded in the timing.
system = pt.System(path='benchmark_long.pkl')
system.simulate(continuize=False, quiet=False)

with pt.terminal.TimeCode():
    system = pt.System(path='benchmark_long.pkl')
    system.simulate(continuize=False, quiet=False)
```

`TimeCode` is a context manager I wrote that spits out how long some code took to execute. If your benchmark doesn't have a built in timing feature like this, just run `time python benchmark_long.py`

Next is `benchmark_short.py`, which looks a little different.

```python
#! /usr/bin/env python

import pooltool as pt
import IPython

# Run once to compile all numba functions. By doing this,
# compilation times will be excluded in the timing.
system = pt.System(path='benchmark_short.pkl')
system.simulate(continuize=False, quiet=True)

def setup_and_run():
    system = pt.System(path='benchmark_short.pkl')
    system.simulate(continuize=False, quiet=True)

ipython = IPython.get_ipython()
ipython.magic("timeit setup_and_run()")
```

What I'm doing here is using IPython's magic function `timeit`, which will run `setup_and_run()` many, many times. Since I'm using the IPython API, I'll need to run this benchmark with `ipython benchmark_short.py`

### Initial speeds

Let's see the runtime for the long benchmark:

```bash
$ python benchmark_long.py
Warning: pandac.PandaModules is deprecated, import from panda3d.core instead

NA
===============================================
starting energy ..............................: 16.75J
Finished after ...............................: 0:00:07.635092

✓ Code finished after 0:00:07.636700
```

As you can see, the **current codebase takes around 7.6 seconds to execute**. And here is the short benchmark:

```bash
$ ipython benchmark_short.py
Warning: pandac.PandaModules is deprecated, import from panda3d.core instead
189 ms ± 11.6 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)
```

## Profiling the code

Alright, so we know the speed of the code and now its time to diagnose it.

### Don't assume

It is best not to diagnose code performance based on intuition. There is quite a bit of distance between the syntax we write and the machine code that gets exected, and for this reason alone you should set aside any preconceived notions about where your code is slow and where it's fast.

That's why code profilers are so great. They do the diagnosing so we do not.

### Profile the benchmark

Time to figure out where the code is slow.

pprofile can be run by simply prepending `pprofile` in front of your python file (see github for other ways to interact with [pprofile](https://github.com/vpelletier/pprofile)). This will print some stuff to the standard out. I don't find this output very useful, so I add the parameters necessary to output a cachegrind file that can be opened with q/kcachegrind. Let's run it on the benchmark:

```bash
pprofile --format callgrind --out cachegrind.out.benchmark benchmark.py
```

### q/kcachegrind

To visualize the results, open q/kcachegrind and load in `cachegrind.out.benchmark`. You should see something like so.

[![qint_1]({{images}}/qint_1.png)]({{images}}/qint_1.png){:.center-img .width-100}

It's quite a lot of information and to get a grip on what you're looking at, I would suggest this short introduction to the interface:

{% include youtube_embed.html id="h-0HpCblt3A" %}

The left hand side shows a series of functions called some time during the program's execution.

[![qint_2]({{images}}/qint_2.png)]({{images}}/qint_2.png){:.center-img .width-100}

_Incl._ is the percentage of total time spent in a given function, including all of the function calls it makes. I'm going to call this the _inclusive time_. Naturally, we see that the inclusive time for `benchmark.py` is 100%, since all functions are called from wthin this script. _Self_ refers the percentage of total time spent in a given function, **excluding** all of the function calls it makes, which I'll call the _self time_. Since `benchmark.py` is just a few lines of code, it delegates all of the computation to function calls. Therefore, the self time for `benchmark.py` is 0.

The right-hand side shows a collection of nested boxes, where each box is a function and its area represents the inclusive time spent in the function. For example, if I click the `evolve_roll_state` function on the left-hand side, the right-hand side shows the time spent in each function `evolve_roll_state` calls.

[![qint_3]({{images}}/qint_3.png)]({{images}}/qint_3.png){:.center-img .width-100}

Here we learn that nearly half the time spent in `evolve_roll_state` is carrying out calls to `unit_vector`. And if you click Source Code, you can view a line-by-line analysis of how much time was spent on each line.

[![qint_4]({{images}}/qint_4.png)]({{images}}/qint_4.png){:.center-img .width-100}

As you can see, this a very powerful tool for snooping around your code.

## Diagnosing the problem

Now comes the issue of figuring out why this thing takes so damn long to execute. While one expects high level functions to have high inclusive times, it is less expectant that a low level function would have a high inclusive time. So I'll start by I'm looking low-level functions that have high inclusive times.

### Blatant issues

[![roots_cross]({{images}}/roots_cross.gif)]({{images}}/roots_cross.gif){:.center-img .width-100}
The inclusive times for `numpy.roots` and `numpy.cross` are respectively 41.6% and 23.8%. This means that 65.4% of the execution is spent in just these 2 functions! I think I found what I'm looking for. This is exactly what I mean when I say its best not to use your intuition. Because most people's intuition is that `numpy` is fast since its written in C, but clearly something is awry here.

#### Cross product

In the case of `numpy.cross`, a numpy function that calculates the cross product between two vectors, it has to be kept in mind that this function is designed for n-dimensional calculations, even though I'm working strictly in 3D. So to start, let's replace this function with my own 'manual' implementation of the cross product.

```python
def cross(v, u):
    """Compute cross product v x u, where v and u are 3-dimensional vectors"""
    return np.array([
        v[1]*u[2] - v[2]*u[1],
        v[2]*u[0] - v[0]*u[2],
        v[0]*u[1] - v[1]*u[0],
    ])
```

See the commit [here](4d2a6a14e5b8a8e1dfedf96d1fb1d87d16baa030). Now let's reprofile and see if it improved things:

```bash
pprofile --format callgrind --out cachegrind.out.cross benchmark.py
```

[![cross_fast]({{images}}/cross_fast.png)]({{images}}/cross_fast.png){:.center-img .width-100}

Wow, the inclusive time went from 23.8% to 1.2%. **In other words the program is about 22% faster**. Cross product calculation is no longer a bottleneck, so I'm going to move on--at least for now.

#### Solving polynomial roots

An even larger issue is `numpy.roots`. 42% of my programs execution is spend in `numpy.roots`! After some digging, the issue is that `numpy.roots` computes roots using an eigenvalue approach, which is robust because you can solve n-degree polynomials, but for me it is kind of overkill.

In almost all my calls to `numpy.roots`, I am trying to solve a quartic polynomial with respect to $t$. That means I want to solve $t$ in the equation

$$
at^4 + bt^3 + ct^2 + dt + e = 0
\notag
$$

{.notice}
For details on why I need to solve these quartic polynomials, and the exact equations I need to solve, see my blog post on the [event-based shot evolution algorithm]({{ site.url }}/2020/12/20/pooltool-alg/#3-the-strategy)

For `numpy.roots`, this means finding the eigenvalues of a $4\times4$ matrix, which is a pretty expensive operation.

I also solve a sprinkling of quadratic polynomials. Regardless, since my polynomials are not arbitrarily dimensioned, but specifically quartic or quadratic in nature, my hope is that I can write some quartic and quadratic polynomial solvers that are faster than the eigenvalue approach taken by `numpy.roots`.

And indeed, there are analytic solutions to quadratic polynomials (like you know from high school) and also quartic solutions. Furthemore, people have implemented numba solutions for these equations. For example, a small python module called `fqs` ([here](https://github.com/NKrvavica/fqs)) does exactly this and boasts a 20-fold speed increase compared to `numpy.roots`.

Unfortunately, for whatever unfortunate reason, all analytical polynomial algorithms I have tried lead to very occassional differences from `numpy.roots`. While one expects differences between analytics and numerics, these very minute changes observed consistently lead to [non-physical intersections](https://github.com/NKrvavica/fqs/issues/1) of pool balls. After failing to determine why, I've decided to scrap this idea altogether in lieu of a different approach.

While searching for an alternate fast quartic polynomial implementations, I stumbled upon [this](https://stackoverflow.com/a/35853977) insightful stackoverflow answer.

<blockquote>
If polynomial coefficients are known ahead of time, you can speed up by vectorizing the computation in roots (given Numpy >= 1.10 or so):
</blockquote>

This is the function the code that they wrote:

```python
import numpy as np

def roots_vec(p):
    p = np.atleast_1d(p)
    n = p.shape[-1]
    A = np.zeros(p.shape[:1] + (n-1, n-1), float)
    A[...,1:,:-1] = np.eye(n-2)
    A[...,0,:] = -p[...,1:]/p[...,None,0]
    return np.linalg.eigvals(A)

def roots_loop(p):
    r = []
    for pp in p:
        r.append(np.roots(pp))
    return r

p = np.random.rand(2000, 4)  # 2000 polynomials of 4th order

assert np.allclose(roots_vec(p), roots_loop(p))

In [35]: %timeit roots_vec(p)
100 loops, best of 3: 4.49 ms per loop

In [36]: %timeit roots_loop(p)
10 loops, best of 3: 81.9 ms per loop
```

At each timestep, my program solves all possible future collisions. For example, if there are 10 moving balls, then all 45 pairwise collisions must be tested for. Determing the collision time for a pair of balls means solving one quartic polynomial, so that's 45 polynomials that need to be solved at this time step. Currently, these are calculated in a for loop, akin to `roots_loop` above. But if I compile all of the coefficients and then implement something akin to `roots_vec`, I may be able to speed things up significantly.

So I refactored my code slightly to solve quartic polynomials _en masse_ (commits [here](4cce1426d7cac2e0db3adcc8b2dc154153ac360f), [here](e81794ca640722b6e2c9a962c25efa14295171f3), [here](c088f31252e1150469299a844475e0cf5c99642d)), which lead a pretty substantial speed gain.

FIXME describe speed gain

### Use numba for low level functions

Next I went through all of the low-level functions that are frequently called and I implemented faster solutions with Numba. Since most of these functions are just a couple of lines, I'm not expecting to see 100X speed gains for any given function. However, there are two pivotal reasons why I'm doing this.

First, given how frequently many of these utility functions are called, even small speed increases could lead to substantial improvement overall.

And second, numba functions can only call numba functions. By implementing numba functions for all of the low level functions, I open up the possibility of numba implementations for higher level functions that call these functions. For example, `physics.get_ball_circular_cushion_collision_coeffs` returns the polynomial coefficients required to determine if/when a given ball collides with a given circular cushion. Since this function makes calls to `utils.angle`, `utils.coordinate_rotation`, `utils.get_rel_velocity`, and `utils.unit_vector`, this function can only be implemented in numba once these child functions are implemented in numba.

It is for these two reasons I decided to craft numba implementations of the low level functions.

#### Strategy

I have become a stickler about preserving functionality, so for each numba function I've implemented, I've kept around the python counterpart. Before calling the numba version within my codebase, I've created a `speed` folder in my tests that houses scripts that measure speed comparisons and ensure the identicality of both implementations.

To start, I've implemented numba functions for 8 frequently called utility functions. They are always suffixed for `_fast`. Here are the corresponding commits for each of the functions: [cross_fast](https://github.com/ekiefl/pooltool/commit/749d2d66d39a528f59b46666f4ffe6b443583137), [get_rel_velocity_fast](https://github.com/ekiefl/pooltool/commit/30e0525468f0ccc7ff4bfdda7d201d8619c46249) (and [this](https://github.com/ekiefl/pooltool/commit/73f28818cf8da970a135367bb5935d58df977047)), [quadratic_fast](https://github.com/ekiefl/pooltool/commit/5dd3244ed438d0d7b3abe1caf74ea65bfd55b7ef), [roots_fast](https://github.com/ekiefl/pooltool/commit/28c6c6bdd024e3755e58dfe2fbc3ac4809010b23), [unit_vector_fast](https://github.com/ekiefl/pooltool/commit/bfb20b4cab1f239c090fd40e6a3c39a9b73ece9e), [angle_fast](https://github.com/ekiefl/pooltool/commit/02d786186d8038daece970c1364f1b93587377a6), [min_real_root_fast](https://github.com/ekiefl/pooltool/commit/012155e407a44ab05d1239a402520469ca74e2b7), and [coordinate_rotation_fast](https://github.com/ekiefl/pooltool/commit/612edee0d56d9419b3d91df0905d46980ee6a282).

Now, I'm going to introduce these into the codebase one at a time, making sure they don't break the state of the codebase, and measure any increases in speed.

#### cross_fast

[[See commit](https://github.com/ekiefl/pooltool/commit/749d2d66d39a528f59b46666f4ffe6b443583137)]

Let's ensure identicality and test the speed increase per-call. Here is the test script I've written to `pooltool/tests/speed/cross.py`:

```python
#! /usr/bin/env python

import pooltool as pt
import IPython

ipython = IPython.get_ipython()

def old():
    pt.utils.cross(np.random.rand(3), np.random.rand(3))

def new():
    pt.utils.cross_fast(np.random.rand(3), np.random.rand(3))

new()

ipython.magic("timeit old()")
ipython.magic("timeit new()")

args = np.random.rand(3), np.random.rand(3)
output1 = pt.utils.cross(*args)
output2 = pt.utils.cross_fast(*args)

assert np.isclose(output1, output2).all()
```

Running it yields the time save:

```bash
$ ipython pooltool/tests/speed/cross.py
4.37 µs ± 146 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)
3.01 µs ± 194 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)
```

Not bad, `cross_fast` is about 45% faster than `cross`.

Since I now know `cross_fast` produces the same results as `cross`, I feel comfortable replacing every instance of `cross` within the codebase with `cross_fast` (see [commit](https://github.com/ekiefl/pooltool/commit/74e2331532e1963260b6e9faa0f90656ec406152)).

Running `pytest`, I am confident this didn't change any functionality. But it also didn't yield a measurable increase in speed.

Before: 72.2 ms ± 377 µs per loop (mean ± std. dev. of 7 runs, 10 loops each)
After: 72.8 ms ± 360 µs per loop (mean ± std. dev. of 7 runs, 10 loops each)

#### unit_vector_fast

[[See commit](https://github.com/ekiefl/pooltool/commit/bfb20b4cab1f239c090fd40e6a3c39a9b73ece9e)]

Now that you've got the idea, I'll move more operationally through the other functions.

`unit_vector_fast` functions the same as `unit_vector` and runs 176% faster.

```bash
$ ipython pooltool/tests/speed/unit_vector.py
10.2 µs ± 176 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)
4.59 µs ± 44 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)
```

After replacing all instances in the codebase (see [commit](https://github.com/ekiefl/pooltool/commit/95deb843ebcf9f5b3584c3507299b97df31b87f7)), here are results of running the short benchmark.

Before: 73.2 ms ± 293 µs per loop (mean ± std. dev. of 7 runs, 10 loops each)
After: 70.3 ms ± 492 µs per loop (mean ± std. dev. of 7 runs, 10 loops each)

#### angle_fast

[[See commit](https://github.com/ekiefl/pooltool/commit/02d786186d8038daece970c1364f1b93587377a6)]

`angle_fast` functions the same as `angle` and runs 120% faster.

```bash
$ ipython pooltool/tests/speed/angle.py
6.61 µs ± 260 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)
2.39 µs ± 43.3 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)
```

After replacing all instances in the codebase (see [commit](https://github.com/ekiefl/pooltool/commit/058cf7052ee1183ce70c5e4dc3b028e910570566)), here are results of running the short benchmark.

Before: 71.9 ms ± 2.67 ms per loop (mean ± std. dev. of 7 runs, 10 loops each)
After 66 ms ± 654 µs per loop (mean ± std. dev. of 7 runs, 10 loops each)

#### coordinate_rotation_fast

[[See commit](https://github.com/ekiefl/pooltool/commit/612edee0d56d9419b3d91df0905d46980ee6a282)]

`coordinate_rotation_fast` functions the same as `coordinate_rotation` and runs 146% faster.

```bash
$ ipython pooltool/tests/speed/coordinate_rotation.py
7.11 µs ± 77.7 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)
2.88 µs ± 106 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)
```

After replacing all instances in the codebase (see [commit](https://github.com/ekiefl/pooltool/commit/73c246cd28c5314de9bbbd6eb9436998b5bb80ed)), here are results of running the short benchmark.

Before: 65.3 ms ± 593 µs per loop (mean ± std. dev. of 7 runs, 10 loops each)
After: 59.6 ms ± 561 µs per loop (mean ± std. dev. of 7 runs, 10 loops each)

#### get_rel_velocity_fast

[See commits [here](https://github.com/ekiefl/pooltool/commit/30e0525468f0ccc7ff4bfdda7d201d8619c46249) and [here](https://github.com/ekiefl/pooltool/commit/73f28818cf8da970a135367bb5935d58df977047)]

`get_rel_velocity_fast` functions the same as `get_rel_velocity` and runs 752% faster.

```bash
$ ipython pooltool/tests/speed/get_rel_velocity.py
22.6 µs ± 994 ns per loop (mean ± std. dev. of 7 runs, 10000 loops each)
2.65 µs ± 108 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)
```

After replacing all instances in the codebase (see [commit](https://github.com/ekiefl/pooltool/commit/785bf29a8732a38de017054d8b0fc340f76553ac)), here are results of running the short benchmark.

Before: 58.6 ms ± 534 µs per loop (mean ± std. dev. of 7 runs, 10 loops each)
After: 44.7 ms ± 416 µs per loop (mean ± std. dev. of 7 runs, 10 loops each)

#### quadratic_fast

[[See commit](https://github.com/ekiefl/pooltool/commit/5dd3244ed438d0d7b3abe1caf74ea65bfd55b7ef)]

`quadratic_fast` functions the same as `quadratic` and runs 83% faster.

```bash
$ ipython pooltool/tests/speed/coordinate_rotation.py
3.58 µs ± 44.6 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)
1.96 µs ± 16.2 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)
```

After replacing all instances in the codebase (see [commit](https://github.com/ekiefl/pooltool/commit/30f4fe5a433788c4931aa57db059b1fde2a7429d)), here are results of running the short benchmark.

Before: 44.9 ms ± 465 µs per loop (mean ± std. dev. of 7 runs, 10 loops each)
After: 44.1 ms ± 687 µs per loop (mean ± std. dev. of 7 runs, 10 loops each)

#### min_real_root_fast and roots_fast

`roots_fast` is only called by `min_real_root_fast`, so I'm lumping these together.

[See commits [here](https://github.com/ekiefl/pooltool/commit/28c6c6bdd024e3755e58dfe2fbc3ac4809010b23) and [here](https://github.com/ekiefl/pooltool/commit/012155e407a44ab05d1239a402520469ca74e2b7)]

`min_real_root_fast` functions the same as `min_real_root` but runs 109% **slower**.

```bash
$ ipython pooltool/tests/speed/min_real_root.py
228 µs ± 7.72 µs per loop (mean ± std. dev. of 7 runs, 1000 loops each)
477 µs ± 9.1 µs per loop (mean ± std. dev. of 7 runs, 1000 loops each)
```

The reason I couldn't make the numba version faster is because I ultimately had to call `np.roots` within my implementation, which if you remember, I was able to avoid calling in my non-numba implementation.

Since numba is slower in this case, I'm not going to replace instances within the codebase. Moving on.

#### Net results

I wasn't expecting much, but I am really happy with the results. Here are the benchmarks before the implementing the numba functions:

```bash
$ git checkout 612edee0d56d9419b3d91df0905d46980ee6a282
$ ipython benchmark_short.py
76.7 ms ± 606 µs per loop (mean ± std. dev. of 7 runs, 10 loops each)
$ python benchark_long.py
✓ Code finished after 0:00:03.251435
```

And here they are now:

```bash
$ git checkout fast
$ ipython benchmark_short.py
45.9 ms ± 696 µs per loop (mean ± std. dev. of 7 runs, 10 loops each)
$ python benchark_long.py
✓ Code finished after 0:00:02.083865
```

Things are almost twice as fast.

### Use numba for low level functions

Now that the low level functions are numba-ized many mid level functions that call these are also amenable to numbaization.
