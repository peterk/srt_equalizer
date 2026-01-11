import argparse
import srt_equalizer



def main():
    parser = argparse.ArgumentParser(description="Equalize SRT file line lengths.")
    parser.add_argument("input_file", type=str, help="Path to the input SRT file.")
    parser.add_argument("output_file", type=str, help="Path to the output SRT file.")
    parser.add_argument("--max-line-length", type=int, default=42, help="Maximum line length in characters.")
    parser.add_argument(
        "--method",
        type=str,
        choices=["greedy", "halving", "punctuation"],
        default="greedy",
        help="Method for equalizing line lengths: 'greedy', 'halving', or 'punctuation'."
    )

    args = parser.parse_args()

    srt_equalizer.equalize_srt_file(args.input_file, args.output_file, args.max_line_length, args.method)
