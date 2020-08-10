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
turned it into a class structure:

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
the same criterion, but rather than ending the event when this occurs, a countdown of \$T\$ seconds
starts. If \$T\$ reaches 0, the event ends.  But it is possible to "save" the event, if any frame
during the countdown has a mean signal exceeding \$X\$ (the event start threshold). In this case,
the event will continue until the next time the mean signal dips below \$Y\$.  The countdown
safeguards against against false-positives that end events because there was a momentary lapse in
sound amplitude. The stringency is thus controlled by \$T\$: the lower \$T\$ is, the more
false-positives in event ends you allow.

Programatically, whenever a frame's mean signal dips below \$Y\$ while `in_event == True`, a second
state variable `in_off_transition` is set to `True`. This starts a countdown. If any frame during
the countdown exceeds \$X\$, `in_off_transition` is set to `False`, and the event is given life
anew. But if no frames exceed \$X\$ during the countdown, the event is deemed to have finished, so
`in_event` is set to `False` and `in_off_transition` is returned to `False`.

With the implementation of these new criteria, here is the updated state logic visualized as a
flow chart:

[![flow2]({{images}}/state_flow_2.jpg)]({{images}}/state_flow_2.jpg){:.center-img .width-70}


### Results

Here is a demo of the new event detector.

{% include youtube_embed.html id="uQBNo67m85c" %}
([Browse code](https://github.com/ekiefl/maple/tree/cac03c052c399b4eb2365c35892e2156500e4397))

Overall, I am happy with how it works and ready to move on.

### A generic event detector (ready for your use)

I noticed at this point that nothing I have done so far has anything to do with dogs and barking.
Being noncommital is a great quality in a codebase because it creates flexibility. So this may be
useful to anyone with their own applications, I created a well-polished timepoint in the codebase.

```python
#! /usr/bin/env python

import numpy as np
import pyaudio
import argparse

CHUNK = 2**11
RATE = 44100


def calc_power(data):
    """Calculate the power of a discrete time signal"""

    return np.mean(np.abs(data))*2


class Stream(object):
    def __init__(self):
        self.p = pyaudio.PyAudio()

        self._stream = self.p.open(
            format = pyaudio.paInt16,
            channels = 1,
            rate = RATE,
            input = True,
            frames_per_buffer = CHUNK,
            start = False, # To read from stream, self.stream.start_stream must be called
        )


    def __enter__(self):
        if not self._stream.is_active():
            self._stream.start_stream()

        return self


    def __exit__(self, exc_type, exc_val, traceback):
        self._stream.stop_stream()


    def close(self):
        """Close the stream gracefully"""

        if self._stream.is_active():
            self._stream.stop_stream()
        self._stream.close()
        self.p.terminate()


class Monitor(object):
    def __init__(self, args = argparse.Namespace()):
        self.args = args

        self.dt = CHUNK/RATE # Time between each sample

        # Calibration parameters
        self.calibration_time = 3 # How many seconds is calibration window
        self.calibration_threshold = 0.50 # Required ratio of std power to mean power
        self.calibration_tries = 1 # Number of running windows tried until threshold is doubled

        # Event detection parameters
        self.event_start_threshold = 3 # standard deviations above background noise to start an event
        self.event_end_threshold = 2 # standard deviations above background noise to end an event
        self.seconds = 0.5
        self.num_consecutive = 4

        self.stream = None
        self.background = None
        self.background_std = None

        self.detector = None
        self.event_recs = {}
        self.num_events = 0


    def read_chunk(self):
        """Read a chunk from the stream and cast as a numpy array"""

        return np.fromstring(self.stream._stream.read(CHUNK), dtype=np.int16)


    def calibrate_background_noise(self):
        """Establish a background noise
        Calculates moving windows of power. If the ratio between standard deviation and mean is less
        than a threshold, signifying a constant level of noise, the mean power is chosen as the
        background. Otherwise, it is tried again. If it fails too many times, the threshold is
        increased and the process is repeated.
        """

        stable = False
        power_vals = []

        # Number of chunks in running window based on self.calibration time
        running_avg_domain = int(self.calibration_time / self.dt)

        with self.stream:
            tries = 0
            while True:
                for i in range(running_avg_domain):
                    power_vals.append(utils.calc_power(self.read_chunk()))

                # Test if threshold met
                power_vals = np.array(power_vals)
                if np.std(power_vals)/np.mean(power_vals) < self.calibration_threshold:
                    self.background = np.mean(power_vals)
                    self.background_std = np.std(power_vals)
                    return

                # Threshold not met, try again
                power_vals = []
                tries += 1

                if tries == self.calibration_tries:
                    # Max tries met--doubling calibration threshold
                    print(f'Calibration threshold not met after {tries} tries. Increasing threshold ({self.calibration_threshold:.2f} --> {1.5*self.calibration_threshold:.2f})')
                    tries = 0
                    self.calibration_threshold *= 1.5


    def setup(self):
        self.stream = Stream()

        self.calibrate_background_noise()

        self.detector = Detector(
            background_std = self.background_std,
            background = self.background,
            start_thresh = self.event_start_threshold,
            end_thresh = self.event_end_threshold,
            seconds = self.seconds,
            num_consecutive = self.num_consecutive,
            dt = self.dt,
        )

        self.wait_for_event()


    def wait_for_event(self, log=True):
        """Waits for an event, records the event, and returns the event audio as numpy array"""

        self.detector.reset()

        with self.stream:
            while True:
                self.detector.process(self.read_chunk())

                if self.detector.event_finished:
                    break

        return self.detector.get_event_data()


    def stream_power_and_pitch_to_stdout(self, data):
        """Call for every chunk to create a primitive stream plot of power and pitch to stdout
        Pitch is indicated with 'o' bars, amplitude is indicated with '-'
        """

        power = utils.calc_power(data)
        bars = "-"*int(1000*power/2**16)

        print("%05d %s" % (power, bars))

        w = np.fft.fft(data)
        freqs = np.fft.fftfreq(len(data))
        peak = abs(freqs[np.argmax(w)] * RATE)
        bars="o"*int(3000*peak/2**16)

        print("%05d %s" % (peak, bars))


class Detector(object):
    def __init__(self, background_std, background, start_thresh, end_thresh, num_consecutive, seconds, dt, quiet=False):
        """Manages the detection of events
        Parameters
        ==========
        background_std : float
            The standard deviation of the background noise.
        background : float
            The mean of the background noise.
        start_thresh : float
            The number of standard deviations above the background noise that the power must exceed
            for a data point to be considered as the start of an event.
        end_thresh : float
            The number of standard deviations above the background noise that the power dip below
            for a data point to be considered as the end of an event.
        num_consecutive : int
            The number of frames needed that must consecutively be above the threshold to be
            considered the start of an event.
        seconds : float
            The number of seconds that must pass after the `end_thresh` condition is met in order
            for the event to end. If, during this time, the `start_thresh` condition is met, the
            ending of the event will be cancelled.
        dt : float
            The inverse sampling frequency, i.e the time captured by each frame.
        quiet : bool
            If True, nothing is sent to stdout
        """

        self.quiet = quiet

        self.dt = dt
        self.bg_std = background_std
        self.bg_mean = background
        self.seconds = seconds
        self.num_consecutive = num_consecutive

        # Recast the start and end thresholds in terms of power values
        self.start_thresh = self.bg_mean + start_thresh*self.bg_std
        self.end_thresh = self.bg_mean + end_thresh*self.bg_std

        self.reset()


    def update_event_states(self, power):
        """Update event states based on their current states plus the power of the current frame"""

        if self.event_started:
            self.event_started = False

        if self.in_event:
            if self.in_off_transition:
                if self.off_time > self.seconds:
                    self.in_event = False
                    self.in_off_transition = False
                    self.event_finished = True
                elif power > self.start_thresh:
                    self.in_off_transition = False
                else:
                    self.off_time += self.dt
            else:
                if power < self.end_thresh:
                    self.in_off_transition = True
                    self.off_time = 0
                else:
                    pass
        else:
            if self.in_on_transition:
                # Not in event
                if self.on_counter >= self.num_consecutive:
                    self.in_event = True
                    self.in_on_transition = False
                    self.event_started = True
                elif power > self.start_thresh:
                    self.on_counter += 1
                else:
                    self.in_on_transition = False
                    self.frames = []
            else:
                if power > self.start_thresh:
                    self.in_on_transition = True
                    self.on_counter = 0
                else:
                    # Silence
                    pass


    def print_to_stdout(self):
        """Prints to standard out to create a text-based stream of event detection"""

        if self.quiet:
            return

        if self.in_event:
            if self.in_off_transition:
                msg = '         o '
            else:
                msg = '        |||'
        else:
            if self.in_on_transition:
                msg = '         | '
            else:
                msg = ''

        if self.event_started:
            msg = '####### EVENT START #########'
        elif self.event_finished:
            msg = '####### EVENT END #########'
        print(msg)


    def reset(self):
        """Reset event states and storage buffer"""

        self.in_event = False
        self.in_off_transition = False
        self.in_on_transition = False
        self.event_finished = False
        self.event_started = False

        self.frames = []


    def append_to_buffer(self, data):
        if self.in_event or self.in_on_transition:
            self.frames.append(data)


    def process(self, data):
        """Takes in data and updates event transition variables if need be"""

        # Calculate power of frame
        power = utils.calc_power(data)

        self.update_event_states(power)

        # Write to stdout if not self.quiet
        self.print_to_stdout()

        # Append to buffer
        self.append_to_buffer(data)


    def get_event_data(self):
        return np.concatenate(self.frames)


if __name__ == '__main__':
    s = Monitor()
    s.setup()
```
([Browse code](https://github.com/ekiefl/maple/tree/cac03c052c399b4eb2365c35892e2156500e4397))

The implementation of this new event detector is captured by a class called `Detector` which handles these
state variables and updates them each audio frame. The logic is housed in this method:

