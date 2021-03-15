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

{% capture images %}{{site.url}}/images/maple/maple-intro{% endcapture %}
{% include _toc.html %}

- what classes should we include?

1. whine
2. howl
3. bark
4. play
5. scratch

- we needed to transform the audio data into something more intuitive: spectrograms

- lets just start looking at individual events to see what the spectrograms look like

- the spectrograms show an extreme range of amplitudes, and so logged values can retain resolution of small/intermediate amplitudes (example: event 348 for data/sessions/2021_03_03_12_47_56/events.db)

- we need to chop up the spectrogram into equal sized segments. looking at spectrograms by hand, it seems like any given dog sound presents itself in 0.25 seconds, and the smallest event is 0.33 seconds. So maybe 0.25s or lower is a good starting point for data chunking

- listening to the audio reveals that many of the events multi-classed, meaning they contain bark and howl characteristics (for example) in the same event. Because we are going to chop up the spectrogram, this can allow us to classify each chunk. 
