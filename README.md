# SRT Equalizer

A Python module to transform subtitle line lengths, splitting into multiple subtitle
fragments if necessary. Useful to adjust automatic speech recognition outputs from e.g. [Whisper](https://github.com/openai/whisper) to a more convenient size.

This library works for all languages where spaces separate words.

## Installing

`pip install srt_equalizer`

## Example

If the SRT file contains lines over a certain length like this:

```
1
00:00:00,000 --> 00:00:04,000
Good evening. I appreciate you giving me a few minutes of your time tonight

2
00:00:04,000 --> 00:00:11,000
so I can discuss with you a complex and difficult issue, an issue that is one of the most profound of our time.
```

Using this code to shorten the subtitles to a maximum length of 42 chars:

```python

from srt_equalizer import srt_equalizer

srt_equalizer.equalize_srt_file("test.srt", "shortened.srt", 42)
```

...they are split into multiple fragments and time code is adjusted to the
approximate proportional length of each segment while staying inside the time
slot for the fragment.

```
1
00:00:00,000 --> 00:00:02,132
Good evening. I appreciate you giving me

2
00:00:02,132 --> 00:00:04,000
a few minutes of your time tonight

3
00:00:04,000 --> 00:00:06,458
so I can discuss with you a complex and

4
00:00:06,458 --> 00:00:08,979
difficult issue, an issue that is one of

5
00:00:08,979 --> 00:00:11,000
the most profound of our time.
```

## Adjust Whisper subtitle lengths
Is is also possible to work with the subtitle items with the following utility methods:

```python
split_subtitle(sub: srt.Subtitle, target_chars: int=42, start_from_index: int=1) -> list[srt.Subtitle]:

whisper_result_to_srt(segments: list[dict]) -> list[srt.Subtitle]:
```

Here is an example of how to reduce the lingth of subtitles created by Whisper. It assumes you have an audio file to transcribe called gwb.wav.

```python
import whisper
from srt_equalizer import srt_equalizer
import srt
from datetime import timedelta

options_dict = {"task" : "transcribe", "language": "en"}
model = whisper.load_model("small")
result = model.transcribe("gwb.wav", language="en")
segments = result["segments"]
subs = srt_equalizer.whisper_result_to_srt(segments)

# Reduce line lenth in the whisper result to <= 42 chars
equalized = []
for sub in subs:
    equalized.extend(srt_equalizer.split_subtitle(sub, 42))

for i in equalized:
    print(i.content)
```

## Contributing

This library is built with [Poetry](https://python-poetry.org). Checkout this repo and run `poetry install` in the source folder. To run tests use `poetry run pytest tests`.

If you want to explore the library start a `poetry shell`.
