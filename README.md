# SRT Equalizer

A Python module to transform subtitle line lengths, splitting into multiple subtitle
fragments if necessary. Useful to adjust automatic speech recognition outputs from e.g. [Whisper](https://github.com/openai/whisper) to a more convenient size.

This library works for all languages where spaces separate words.

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
import srt_equalizer

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
00:00:02,132 --> 00:00:03,944
a few minutes of your time tonight

3
00:00:04,000 --> 00:00:06,458
so I can discuss with you a complex and

4
00:00:06,458 --> 00:00:08,979
difficult issue, an issue that is one of

5
00:00:08,979 --> 00:00:10,870
the most profound of our time.
```

Is is also possible to work with the subtitle items with the following utility methods:

```python
split_subtitle(sub: srt.Subtitle, target_chars: int=42, start_from_index: int=1) -> list[srt.Subtitle]:

whisper_result_to_srt(segments: list[dict]) -> list[srt.Subtitle]:
```
