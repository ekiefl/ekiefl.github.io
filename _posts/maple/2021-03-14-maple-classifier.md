---
layout: post
title: "Virtual dog-sitter II: creating an audio classifier"
categories: [maple]
excerpt: "Classifying dog barks to buff automated owner reponses"
comments: true
authors: [evan]
image:
  feature: maple/maple_banner.jpg
  display: true
---

{% capture images %}{{site.url}}/images/maple/maple-classifier{% endcapture %}
{% include _toc.html %}


## Where I left off

In the [first post]({{ site.url }}/2020/07/20/maple-intro/) of this series, I made a virtual dog-sitter that detects audio events, responds to them, and stores them in a database that can be visualized to make plots like this:

FIXME

Using the dog-sitter ([github here](https://github.com/ekiefl/maple)), I can track the behavior of my girlfriend's dog (Maple) when we leave her alone in the apartment.

I ended that post saying I would report back after acquiring a lot more data and there are a few **logistical updates** on that front.

First, it is no longer just Maple we are tracking. We decided that Kourtney's other dog, **Dexter**, should also be in the room. Originally we separated them based on anecdotal evidence that they barked more when together than when separated. As the data in this post will tell us, keeping them together is a **very good idea**.

Second, we don't lock Maple in the crate anymore. This way she can interact with Dexter and maybe even play with Dexter. Instead, they are both now confined to our bedroom.

Finally, there were some complications, which means **I don't have as much data as I wanted**. Highlights include: I accidentally deleted about a month of data, the volume knob on my microphone changed and went unnoticed for a month, and my calibration system for event detection kept event rates inconsistent across sessions. All of this is sorted out now.

So there isn't enough data to do a comprehensive analysis on the dogs' improvement over time, and whether or not praising/scolding has an effect on their behavior. Not yet anyways.

## Creating an audio classifier

While I wait another couple months for the data to pour in, I decided that being able to classify audio events could greatly increase the accuracy and capabilities of the dog-sitter.

In the last post I developed [complicated flowcharts]({{ site.url }}/2020/07/20/maple-intro/#praise) to determine when the dog-sitter should intervene with pre-recorded audio that either praises or scolds the dog. The logic relied on the assumption that **loud is bad and quiet is good**. Yet if I could classify each audio event, I could step away from this one dimensional paradigm and begin developing more nuanced respones that understand the sentiment of the audio.

For example, whining could trigger a console response. Playing could trigger an encouragement response. Implementing this with the old paradigm would be impossible, because whining and playing produce similar levels of noise.

So that's one thing an audio classifier would enable: **nuanced response**.

Another thing it would enable is **protection against non-dog audio**. The dog-sitter may detect undesirable noise from nondescript sources, like a nearby lawnmower, a person talking in the alley, a dump truck beeping. If I train a good classifier, I could filter out non-dog audio from ever entering my databases. This would filter bad data out of downstream analyses, and prevent any mishaps like scolding a dog because of a lawnmower.
And finally, creating a classifier would greatly improve the ability to understand what happens when I leave. After returning home, I would be able to immediately assess in a highly-resolved manner how well the dogs behaved while I was gone.

## Deciding on a classifier algorithm

<blockquote>
Don't make anything more complicated than it needs to be.
</blockquote>

In my opinion, this quote should be attributed to the [random forest algorithm](https://en.wikipedia.org/wiki/Random_forest). There is really no point starting with any other classifying algorithm. If the classifier is bad, I'll try something more complicated.

Moving on.

## Data transformation

Unfortunately, I can't just throw the audio data into a random forest and be done with it. The data needs to be wrangled and transformed in a suitable format that's consistent across samples and pronounces distinguishable features.

Moving forward, I'll use these two events as examples.

The first is a door scratch:

[![door_scratch]({{images}}/door_scratch.png)]({{images}}/door_scratch.png){:.center-img .width-90}
{% include audio_embed.html id="images/maple/maple-classifier/door_scratch.wav"%}
[\[click for raw text data\]]({{ site.url }}/images/maple/maple-classifier/door_scratch.txt)

The second is a whine:

[![whine]({{images}}/whine.png)]({{images}}/whine.png){:.center-img .width-90}
{% include audio_embed.html id="images/maple/maple-classifier/whine.wav"%}
[\[click for raw text data\]]({{ site.url }}/images/maple/maple-classifier/whine.txt)

<div class="extra-info" markdown="1">
<span class="extra-info-header">USING THE MAPLE API</span>

I found these events using an interactive plot generated with

```
./main.py analyze --session 2021_02_13_19_19_33
```

Once I found these two events, I plotted and exported the audio/text files using maple's API:

```python
from maple.data import SessionAnalysis
session = SessionAnalysis(path='data/sessions/2021_02_13_19_19_33/events.db')

session.plot_audio_event(160)
session.save_event_as_wav(event_id=160, path='door_scratch.wav')
session.save_event_as_txt(event_id=160, path='door_scratch.txt')

session.plot_audio_event(160, xlim=(0, 4.53))
session.save_event_as_wav(event_id=689, path='whine.wav')
session.save_event_as_txt(event_id=689, path='whine.txt')
session.disconnect()
```

</div>

For anyone who doesn't work with audio files, the data is simple. Audio signal is just a 1D array, where the value of each point is proportional to the amplitude of the sound. As you move through the array, you're moving through time at a specified sampling rate. In my recordings I chose a standard sampling rate of 44100 Hz.

{:.notice}
Why 44100 Hz? The human ear can perceive sound waves up to around 20,000 Hz. But resolving a sinusoidal wave requires sampling frequency that is [at least double](https://en.wikipedia.org/wiki/Nyquist_rate) the wave's frequency. Hence we have 44100 Hz.

### The data should be chunked

The first problem I identified is that each audio event (sample) has a unique length (dimension), yet most classifiers demand that **every sample must have the same dimension**.

To deal with this, I decided each audio event would be split into **equal sized chunks** and the classifier would classify chunk-by-chunk.

What length of time should each chunk be? I didn't want to exclude any events that were shorter than the chunk size, so I took a look at the distribution of event lengths for some random session.

```python
import matplotlib.pyplot as plt
from maple.data import SessionAnalysis
session = SessionAnalysis(path='data/sessions/2021_02_13_19_19_33/events.db')
plt.hist(session.dog['t_len'], bins=300)
plt.yscale('log')
plt.xlabel('event length [s]')
plt.show()
```

[![event_lengths]({{images}}/event_lengths.png)]({{images}}/event_lengths.png){:.center-img .width-90}

It seems most event times are less than 2.5 seconds, and we most frequently see events between 0.3s and 0.5s. To make sure events are composed of at least one chunk, **I opted to use a chunk size of 0.25s**. Alternatively I could have picked a larger chunksize and zero-padded shorter events such that they contained at least one chunk.

<div class="extra-info" markdown="1">
<span class="extra-info-header">THE MINIMUM EVENT LENGTH TIME</span>

If you're wondering why there are no events lower than 0.33s, it has to do with the event detection heuristics. If I used different values, by editing the `config` file, the minimum event length would have been different. Here are the settings I used for this session (and all sessions):

```
[detector]
# Standard deviations above background noise to consider start an event
event_start_threshold = 4
# The number of chunks in a row that must exceed event_start_threshold in order to start an event
num_consecutive = 4
# Standard deviations above background noise to end an event
event_end_threshold = 4
# The number of seconds after a chunk dips below event_end_threshold that must pass for the event to
# end. If during this period a chunk exceeds event_start_threshold, the event is sustained
seconds = 0.25
# If an event lasts longer than this many seconds, everything is recalibrated
hang_time = 180
```

</div>


### Frequency or time? Answer: both

I want to represent the data so that distinguishable features are accentuated for the classifier. Thinking in these terms, audio has two really important features: time and frequency.

[![door_scratch]({{images}}/door_scratch.png)]({{images}}/door_scratch.png){:.center-img .width-90}

Above is the 1D audio signal for the door scratching event. This plot basically illustrates how **energy is spread along the axis of time**. And there is clearly distingushing information in this view. For example, we can see that my door is being destroyed in discrete pulses that are roughly equally spaced through time.

But frequency-space also holds critical information. We can visualize how **energy is spread across the axis of frequency** by calculating a Fourier transform of both events:

```python
from maple.data import SessionAnalysis
session = SessionAnalysis(path='data/sessions/2021_02_13_19_19_33/events.db')
session.plot_audio_event_freq(160)
session.plot_audio_event_freq(689)
```

[![door_scratch_freq]({{images}}/door_scratch_freq.png)]({{images}}/door_scratch_freq.png){:.center-img .width-90}
{% include audio_embed.html id="images/maple/maple-classifier/door_scratch.wav"%}

[![whine_freq]({{images}}/whine_freq.png)]({{images}}/whine_freq.png){:.center-img .width-90}
{% include audio_embed.html id="images/maple/maple-classifier/whine.wav"%}

You can really see how my door is being destroyed over a wide range of frequencies. If you listen carefully to the audio, you can hear the bassline and the high hat. In comparison, Maple's whine is much more concentrated in frequency space, localized to a range of about 500-2500 Hz. This is reflected in the relative pureness of the audio, giving that whistley sort of sound.

Clearly, time and frequency are giving complementary information that the classifier should use both of. To accomplish this, I decided to transform the data into **spectrograms**, where the $x-$axis is time and the $y-$axis is frequency. This shows how **energy is spread across time and frequency space**.

```python
from maple.data import SessionAnalysis
session = SessionAnalysis(path='data/sessions/2021_02_13_19_19_33/events.db')
session.plot_audio_event_spectrogram(160)
session.plot_audio_event_spectrogram(689)
```

[![door_scratch_spectrogram]({{images}}/door_scratch_spectrogram.png)]({{images}}/door_scratch_spectrogram.png){:.center-img .width-90}
{% include audio_embed.html id="images/maple/maple-classifier/door_scratch.wav"%}

[![whine_spectrogram]({{images}}/whine_spectrogram.png)]({{images}}/whine_spectrogram.png){:.center-img .width-90}
{% include audio_embed.html id="images/maple/maple-classifier/whine.wav"%}

TODO

- explain log
- talk about flattening
- summarize
    - flattened 0.25s spectrograms


