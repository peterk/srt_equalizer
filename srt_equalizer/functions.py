from datetime import timedelta
import srt
import sys


def load_srt(filepath: str):
    """Load an SRT subtitle file and return an array of srt.Subtitle items."""
    filedata = ""
    with open(filepath, 'r') as f:
        filedata = f.read()

    return list(srt.parse(filedata))


def write_srt(filepath: str, subs: list[srt.Subtitle]):
    """Write an SRT subtitle file to disk."""
    with open(filepath, "w") as f:
        f.write(srt.compose(subs))


def whisper_result_to_srt(segments: list[dict]) -> list[srt.Subtitle]:
    """Convert Whisper ASR result segments to a list of srt.Subtitle items."""
    subs = []

    for i, segment in enumerate(segments, start=1):
        start_time = timedelta(seconds=int(segment['start']))
        end_time = timedelta(seconds=int(segment['end']))
        content = segment['text']
        subs.append(srt.Subtitle(index=i, content=content, start=start_time, end=end_time))
    
    return subs


def split_subtitle(sub: srt.Subtitle, target_chars: int=42, start_from_index: int=1) -> list[srt.Subtitle]:
    """If the subtitle length is > target_chars, split it into a list of subtitles within the same
    time span. Otherwise return the subtitle as is. The time code is adjusted proportionally
    to the length of the subtitle.
    
    Args:
        sub: A srt.Subtitle object.
        target_chars: The max number of characters for a subtitle line.
        start_from_index: The start index of the subtitle item.

    Returns:
        An array of one or more subtitle items.
    """

    if len(sub.content) <= target_chars:
        # keep this item as is, only adjust the start index if necessary.
        sub.index = start_from_index + 1
        return [sub]
    
    text_chunks = []
    current_chunk = ""
    words = sub.content.split()

    for word in words:
        if len(current_chunk) + len(word) + 1 > target_chars:
            text_chunks.append(current_chunk.strip())
            current_chunk = word + ' '
        else:
            current_chunk += word + ' '
    if current_chunk:
        text_chunks.append(current_chunk.strip())

    # Create a new subtitle item for each text chunk, proportional to its length.
    split_subs = []
    total_length = len(sub.content)
    current_time = sub.start
    for i, chunk in enumerate(text_chunks):
        chunk_length = len(chunk)
        chunk_duration = chunk_length / total_length * (sub.end - sub.start)
        start_time = current_time

        # prevent overlap errors in subtitle editing software
        end_time = current_time + chunk_duration - timedelta(milliseconds=1)
        
        new_subtitle = srt.Subtitle(
            index=start_from_index + i,
            start=start_time,
            end=end_time, 
            content=chunk
        )
        split_subs.append(new_subtitle)
        current_time = end_time

    return split_subs


def equalize_srt_file(srt_path: str, output_srt_path: str, target_chars: int):
    """Load subs from an SRT file and output equalized subtitles to a new SRT file.
    """
    subs = load_srt(srt_path)

    adjusted_subs = []
    last_index = 0

    # Limit each subtitle to a maximum character length, splitting into
    # multiple subtitle items if necessary.
    for sub in subs:
        new_subs = split_subtitle(sub=sub, target_chars=target_chars, start_from_index=last_index)
        last_index = new_subs[-1].index
        adjusted_subs.extend(new_subs)

    # Write the result to a new file
    write_srt(filepath=output_srt_path, subs=adjusted_subs)



if __name__ == '__main__':

    adjusted_subs = []
    last_index = 1

    equalize_srt_file(srt_path="gwb_journo.srt", output_srt_path="gwb42.srt", target_chars=74)
