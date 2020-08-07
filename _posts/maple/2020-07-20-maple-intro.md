---
layout: post
title: "Live audio processing: monitoring and responding to dog barks"
categories: [psim]
excerpt: "Creating an automated program for monitoring dog and responding to a dog"
comments: true
authors: [evan]
image:
  feature: psim/psim_banner.png
  display: true
---

{% capture images %}{{site.url}}/images/maple/maple-intro{% endcapture %}
{% include _toc.html %}

I recently moved in with my girlfriend who has a 6-month old puppy named Maple. She's a sweet girl
(the puppy), however she was born in the COVID era, and that comes with some behavioral challenges.
The biggest problem is that she's developed an unrealistic assumption that she can be with us 100%
of the time. And when that unrealistic expectation is challenged by us leaving the apartment, she
barks. **Loudly**. I wanted to create a program in Python that monitors and responds to her barks.

By the end of this post, the program (which you have full, open-access to) will detect dog barks,
and make decisions on whether to praise or scold based on the dog barks. At this point, praising
means playing a pre-recorded voice of the owner that is either of positive or negative sentiment.
The audio, statistics, and time of each bark, as well as statistics of owner responses are stored in
a SQLite database. Finally, the program can generate a very primitive interactive plot using
[Plotly](https://plotly.com/python/).

## Simple demo

It's always good to start simple so I just searched, "python live audio processing" and found
this blog post by [Scott W Harden](https://swharden.com/wp/2016-07-19-realtime-audio-visualization-in-python/).
In it, he posts a simple script that monitors in real-time the ampltitude of the audio signal. I
modified it slightly:

```python
#! /usr/bin/env python

import numpy as np
import pyaudio
import argparse

CHUNK = 2**11
RATE = 44100

class LiveStream(object):
    def __init__(self, args = argparse.Namespace()):
        self.args = args

        self.p = pyaudio.PyAudio()
        self.stream = None


    def start(self):
        while True:
            data = np.fromstring(self.stream.read(CHUNK), dtype=np.int16)
            self.process_data(data)


    def __enter__(self):
        self.stream = self.p.open(
            format = pyaudio.paInt16,
            channels = 1,
            rate = RATE,
            input = True,
            frames_per_buffer = CHUNK,
        )

        return self


    def __exit__(self, exception_type, exception_value, traceback):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()


    def process_data(self, data):
        peak=np.average(np.abs(data))*2
        bars="#"*int(2000*peak/2**16)
        print("%05d %s"%(peak,bars))

        # uncomment to push highest amplitude frequency to stdout
        #x = data
        #w = np.fft.fft(x)
        #freqs = np.fft.fftfreq(len(x))
        #max_freq = abs(freqs[np.argmax(w)] * RATE)
        #peak = max_freq
        #bars="o"*int(4000*peak/2**16)
        #print("%05d %s"%(peak,bars))


if __name__ == '__main__':
    with LiveStream() as s:
        s.start()
```

Here's a demo:

{% include youtube_embed.html id="QAOw4R7U4ls" %}
([Browse code](https://github.com/ekiefl/maple/tree/ac9515c525435f6c4500762036934e850a3ee1b0))


## Event detection

With a bare-bones script that demos a live stream of primitive audio processing, I then decided to
focus on detecting events, since in order to rationally respond to your dog, you need to be able to
detect when it is barking.  Additionally, this will eliminate the need to sift through large audio
files in any post-processing steps and to avoid storing large audio files that are mostly *not* dogs
barking (hopefully).

Events are basically anomalies in the background noise, and so to detect events, we need to
properly distinguish background from signal. To do this, I wrote a calibration method that runs at
the start of the program. The premise is to wait until the audio signal reaches an equilibrium, and
then measures the mean and standard deviation of signal strength. Equilibrium is established by demanding
that the coefficient of variation (the standard deviation divided by the mean, \$\sigma/\mu\$) is
less than some threshold value. The background mean and standard deviation that satisfied this
constrant for equilibrium can then be used to
distinguish signal from noise.

We can do some back of the envelope calculations to show that if the signal is drawn from a Normal
distribution, there is a ~16% chance that any given datapoint in the signal will exceed 1 standard
deviation about the mean (\$\mu + \sigma\$). That probability becomes ~2.5% that it will exceed 2
standard deviations (\$\mu + 2\sigma\$) and ~0.5% that it exceeds 3 standard deviations (\$\mu +
3\sigma\$). As a first step, I went ahead and wrote a detector that detects the start of an event
whenever the signal exceeds 3 standard deviations, and the end of the event whenever it dips below 2
standard deviations. Here is a demo showing the efficacy of this approach:

{:.notice}
From here on in, I started developing within a multi-file environment (the whole repo can
be found [here](github.com/ekiefl/maple)). To make everything accessible as possible, each code
snippet and demo video will be followed by a hyperlink that brings you to the stage in the codebase
from where the snippet or demo was taken.

{% include youtube_embed.html id="k7zHMiv_YtY" %}
([Browse code](https://github.com/ekiefl/maple/tree/d923c6689f1bafc9ef7e071a6d4674983a8f8d34))

## Better event detection

As mentioned in the video, there are a lot of false-positives for the ends of events. In other
words, many of my spoken sentences were being split up into multiple events, even when there was
little or no break in my speaking rhythm. This was happening because the criterion for events ending
was too simple, and based on a single audio frame (if the mean audio signal of the frame drops below
\$\mu + 2\sigma\$, the event ends). This is problematic because each frame is only a couple of
milliseconds. To more accurately depict the start and stop of events, I wanted to create criteria
that spanned multiple frames.

In the above video, the program has just 1 state variable called `in_event`, and its possible values
are either `True` or `False`. Here is a flowchart of the transitions possible:

[![flow1]({{images}}/state_flow_1.jpg)]({{images}}/state_flow_1.jpg){:.center-img .width-70}

### Event start criterion

Before, transitioning from `in_event == False` to `in_event == True` occurred whenever a frame had a
mean signal 3 standard deviations above the mean. Let's call this threshold value \$X\$ for
convenience. My new criterion is that there must be \$N\$ consecutive frames that are all above
\$X\$. If \$N\$ consecutive frames all meet this threshold, then the event start is attributed to
the first frame in this frame sequence. This effectively guards against false-positives when loud
but short (~ millisecond) sounds are made, which trigger an event. The stringency is thus controlled
by \$N\$: the lower \$N\$ is, the more false-positives in event starts you allow.

Programatically, whenever a frame's mean signal exceeds \$X\$ while `in_event == False`, a second
state variable `in_on_transition` is set to `True`.  Whenever `in_on_transition == True`, it
basically means, "*Ok, we're not for sure in an event, but things are starting to get loud, and if
we stay in this state for long enough, we'll for sure know we are in an event*". If
`in_on_transition == True` for \$N\$ consecutive frames, then the program is convinced it is
actually an event, so `in_event` is set to `True` and `in_on_transition` is returned to `False`. On
the other hand, if any frame fails to exceed \$X\$, `in_on_transition` is set to `False` and the
potential event is deemed not an event. Note that whenever `in_on_transition == True`, the audio
frames are stored in a buffer and retroactively added to the event, in the case that it ends up
*being* an event.

### Event end criterion

Before, an event ended whenever a frame had a mean signal that dipped below 2 standard deviations
above the mean (\$\mu + 2\sigma\$). Call this threshold \$Y\$ for convenience. My new method uses
the same criterion, but rather than ending the event when this occurs, a countdown of $\T\$ seconds
starts. If \$T\$ reaches 0, the event ends.  But it is possible to "save" the event, if any frame
during the countdown has a mean signal exceeding \$X\$ (the event start threshold). In this case,
the event will continue until the next time the mean signal dips below \$Y\$.  The countdown
safeguards against against false-positives that end events because there was a momentary lapse in
sound amplitude. The stringency is thus controlled by \$T\$: the lower \$T\$ is, the more
false-positives in event ends you allow.

Programatically, whenever a frame's mean signal dips below \$Y\$ while `in_event == True`, a second
state variable `in_off_transition` is set to `True`. This starts a countdown. If any frame during
the countdown exceeds \$X\$, `in_off_transition` is set to `False`, and the event is given life
anew. But if no frames exceed $\X\$ during the countdown, the event is deemed to have finished, so
`in_event` is set to `False` and `in_off_transition` is returned to `False`.

### The code

This is how the new state logic is visualized as a flow chart:

[![flow1]({{images}}/state_flow_2.jpg)]({{images}}/state_flow_2.jpg){:.center-img .width-70}

More complex, and more robust. The implementation of this new design is captured by a class called
`Detector` which handles these state variables and updates them each audio frame:

```python
```

