from srt_equalizer.srt_equalizer import *
import pytest
import srt
import datetime


def test_load_srt():
    """Test loading of an SRT file and parsing into subtitle items"""
    subs = load_srt("tests/gwb.srt")
    assert len(subs) == 101


def test_load_srt_file_not_found():
    """Test file missing error."""
    with pytest.raises(Exception):
        subs = load_srt("notavailable.srt")


def test_split_subtitle():
    """Test split subtitle."""
    sub = srt.Subtitle(index=1,
                       start=datetime.timedelta(seconds=0, milliseconds=0),
                       end=datetime.timedelta(seconds=1, milliseconds=0),
                       content="A string with more than 40 characters that should be split into several smaller ones.")
    s = split_subtitle(sub, 42)

    # check that the line is split after "characters"
    assert len(s[0].content) == 37

    # assert that fragment two is correct
    assert s[1].content == "that should be split into several smaller"

    # assert that fragment two is correct
    assert s[2].content == "ones."

    # check fragment timing
    assert s[2].end == sub.end


def test_split_subtitle_halving():
    """Test split subtitle."""
    sub = srt.Subtitle(index=1,
                       start=datetime.timedelta(seconds=0, milliseconds=0),
                       end=datetime.timedelta(seconds=1, milliseconds=0),
                       content="A string with more than 40 characters that should be split into several smaller ones.")
    s = split_subtitle(sub, 42, method='halving')

    reconstructed = ' '.join([x.content for x in s])
    assert sub.content == reconstructed

    assert s[0].content == "A string with more than 40 characters that"
    assert s[1].content == "should be split into several smaller ones."

    # check fragment timing
    assert s[1].end == sub.end
