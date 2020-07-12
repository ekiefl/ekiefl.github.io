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

{% capture images %}{{site.url}}/images/psim/psim-intro{% endcapture %}
{% include _toc.html %}

## Why?

I recently moved in with my girlfriend who has a 6-month old puppy named Maple. She's a sweet girl
(the puppy), however she was born in the COVID era, and that comes with some behavioral challenges.
The biggest problem is that she's developed an unrealistic assumption that she can be with us 100%
of the time. And when that unrealistic expectation is challenged by us leaving the apartment, she
barks. **Loudly**. I wanted to create a program that monitors this barking, and potentially even scolds
her outbursts and praises her silences.

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
focus on detecting events. The this is to focus post-processing on only the interesting
stuff (barks, etc) and to not store large audio files that are mostly background noise.

Events are basically anomalies in the background noise, and so to detect events, we need to
properly distinguish background from signal. To do this, I wrote a calibration method that runs at
the start of the program. The premise is to wait until the audio signal reaches an equilibrium, and
then measures the mean and standard deviation of signal strength. Equilibrium is established by demanding
that the coefficient of variation (the standard deviation divided by the mean, \$\sigma/\mu\$) is
less than some threshold value. The background mean and standard deviation that satisfied this
constrant for equilibrium can then be used to
distinguish signal from noise.

We can do some back of the envelope calculations to show that if the signal is drawn from a Normal
distribution, there is a ~33% chance that any given datapoint in the signal will exceed 1 standard
deviation about the mean (\$\mu + \sigma\$). That probability becomes ~5% that it will exceed 2
standard deviations (\$\mu + 2\sigma\$) and ~1% that it exceeds 3 standard deviations (\$\mu +
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

