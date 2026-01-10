import re
import os
from datetime import timedelta
from typing import List

import srt



def validate_file_path(file_path: str, must_exist: bool = False) -> str:
    """Validate and normalize file paths to prevent directory traversal."""
    if not file_path:
        raise ValueError("File path cannot be empty")
    
    # Normalize path and convert to absolute
    abs_path = os.path.abspath(os.path.normpath(file_path))
    
    # Security check for path traversal attempts
    if os.path.relpath(abs_path).startswith('..'):
        raise ValueError(f"Invalid path traversal attempt: {file_path}")
    
    if must_exist and not os.path.isfile(abs_path):
        raise FileNotFoundError(f"File does not exist: {abs_path}")
        
    return abs_path


def load_srt(filepath: str) -> List[srt.Subtitle]:
    """Load SRT file with path validation"""
    clean_path = validate_file_path(filepath, must_exist=True)
    with open(clean_path, 'r') as f:
        return list(srt.parse(f.read()))


def write_srt(filepath: str, subs: List[srt.Subtitle]):
    """Write SRT file with path validation"""
    clean_path = validate_file_path(filepath)
    os.makedirs(os.path.dirname(clean_path), exist_ok=True)
    with open(clean_path, "w") as f:
        f.write(srt.compose(subs))


def whisper_result_to_srt(segments: List[dict]) -> List[srt.Subtitle]:
    """Convert Whisper ASR result segments to a list of srt.Subtitle items."""
    subs = []

    for i, segment in enumerate(segments, start=1):
        start_time = timedelta(seconds=float(segment['start']))
        end_time = timedelta(seconds=float(segment['end']))        
        content = segment['text']
        subs.append(srt.Subtitle(index=i, content=content,
                    start=start_time, end=end_time))

    return subs


def split_subtitle(sub: srt.Subtitle, target_chars: int = 42, start_from_index: int = 1, method: str = 'greedy') -> List[srt.Subtitle]:
    """If the subtitle length is > target_chars, split it into a list of subtitles within the same
    time span. If not, return the subtitle as is. The time code is adjusted proportionally
    to the length of the subtitle.

    Args:
        sub: A srt.Subtitle object.
        target_chars: The max number of characters for a subtitle line.
        start_from_index: The start index of the subtitle item.
        method: algorithm for splitting - either "greedy" (default), "halving" or "punctuation".

    Returns:
        An array of one or more subtitle items.
    """

    if len(sub.content) <= target_chars:
        # keep this item as is, only adjust the start index if necessary.
        sub.index = start_from_index + 1
        return [sub]

    elif method == "greedy":
        text_chunks = split_greedy(sub.content, target_chars)
    elif method == "halving":
        text_chunks = split_at_half(sub.content, target_chars)
    else:
        assert method == "punctuation"
        text_chunks = split_by_punctuation(sub.content, target_chars)

    # Create a new subtitle item for each text chunk, proportional to its length.
    split_subs = []
    total_length = len(sub.content)
    current_time = sub.start

    for i, chunk in enumerate(text_chunks):
        chunk_length = len(chunk)
        chunk_duration = chunk_length / total_length * (sub.end - sub.start)
        start_time = current_time

        # set end time to original sub item end time if this is the last chunk.
        if i == len(text_chunks) - 1:
            end_time = sub.end
        else:
            end_time = current_time + chunk_duration

        new_subtitle = srt.Subtitle(
            index=start_from_index + i,
            start=start_time,
            end=end_time,
            content=chunk
        )
        split_subs.append(new_subtitle)
        current_time = end_time

    return split_subs


def equalize_srt_file(srt_path: str, output_srt_path: str, target_chars: int, method='greedy'):
    """Load subs from an SRT file and output equalized subtitles to a new SRT file.
    """
    assert method in {'greedy', 'halving', 'punctuation'}, method
    subs = load_srt(srt_path)

    adjusted_subs = []
    last_index = 0

    # Limit each subtitle to a maximum character length, splitting into
    # multiple subtitle items if necessary.
    for sub in subs:
        new_subs = split_subtitle(
            sub=sub, target_chars=target_chars, start_from_index=last_index, method=method)
        last_index = new_subs[-1].index
        adjusted_subs.extend(new_subs)

    # Write the result to a new file
    write_srt(filepath=output_srt_path, subs=adjusted_subs)


def split_greedy(sentence: str, target_chars: int) -> List[srt.Subtitle]:
    """Split subtitles into chunks of target_chars length as soon as possible.
    """

    text_chunks = []
    current_chunk = ''
    words = sentence.split()
    for word in words:
        if len(current_chunk) + len(word) + 1 > target_chars:
            text_chunks.append(current_chunk.strip())
            current_chunk = word + ' '
        else:
            current_chunk += word + ' '
    if current_chunk:
        text_chunks.append(current_chunk.strip())

    return text_chunks


def split_at_half(sentence, target_chars):
    """Try to split subtitles into similar line lengths takign commas into account."""

    if len(sentence) <= target_chars or ' ' not in sentence:
        return [sentence]

    # find the central space
    center = len(sentence) // 2
    space_indices = []
    for ix, char in enumerate(sentence):
        if char == ' ':
            distance_to_center = abs(ix-center)
            if distance_to_center < target_chars / 4 and ix > 0 and sentence[ix-1] == ',':
                # boost splitting on commas that are not exacly in the middle, but close to
                distance_to_center /= 10

            space_indices.append((ix, distance_to_center))

    closest_space_to_center = sorted(space_indices, key=lambda x: x[1])[0][0]

    # recursively call this function until the length is bellow limit
    left = sentence[:closest_space_to_center]
    right = sentence[closest_space_to_center+1:]
    return split_at_half(left, target_chars) + split_at_half(right, target_chars)


def split_by_punctuation(sentence: str, target_chars: int) -> List[str]:
    """Split subtitles into chunks of target_chars length by punctuation."""

    if len(sentence) <= target_chars:
        return [sentence]

    # use regex to split the sentence by punctuation
    chunks = re.split(r'([.,!?]+[\'"”’]*)', sentence)
    normalized_chunks = []
    for chunk in chunks:
        # strip whitespace
        chunk = chunk.strip()

        # if this chunk is an empty one, skip it
        if not chunk:
            continue

        if len(chunk) > target_chars:
            normalized_chunks.extend(split_greedy(chunk, target_chars))
            continue

        if normalized_chunks:
            if re.fullmatch(r"[.,!?]+[\'\"”’]*", chunk):
                # add pucturation to the last chunk
                chunk = normalized_chunks.pop() + chunk
            elif len(chunk) + len(normalized_chunks[-1]) <= target_chars:
                # add this chunk to the last one since they still under the limit allowed
                chunk = normalized_chunks.pop() + ' ' + chunk

        normalized_chunks.append(chunk)

    return normalized_chunks