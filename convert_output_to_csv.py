"""Convert Result JSON to csv that can be consumed by Indico IPA"""
import csv
import json
import argparse
from pathlib import Path


def get_args():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "result_json_file",
        metavar="result-json-file",
        type=Path,
        help="Path to final JSON result file from Parhelion",
    )
    parser.add_argument(
        "-o",
        "--output-directory",
        type=Path,
        help="directory to save csv_files",
    )
    parser.add_argument(
        "-p",
        "--output-prefix",
        type=Path,
        help="Prefix to apply to output paths, output will look like <output-prefix>-sentence.csv",
    )

    args = parser.parse_args()
    return args


def main():
    args = get_args()
    result_json = open_result_file(args.result_json_file)
    sentence_rows, header_rows = convert_json_to_csv_rows(result_json)

    if args.output_directory:
        output_dir = args.output_directory
    else:
        output_dir = args.result_json_file.parent

    if args.output_prefix:
        sentence_csv_filepath, header_csv_filepath = create_output_paths(
            output_dir, args.output_prefix
        )
    else:
        sentence_csv_filepath, header_csv_filepath = create_output_paths(
            output_dir, args.result_json_file.stem
        )

    to_csv(sentence_rows, ["Sentences", "Label"], sentence_csv_filepath)
    to_csv(header_rows, ["Headers", "Label"], header_csv_filepath)


def open_result_file(result_json_file):
    with open(result_json_file) as f:
        results = json.load(f)
    return results


def convert_json_to_csv_rows(result_json):
    results = result_json["results"]
    header_rows = []
    sentence_rows = []
    for result in results:
        if result["label_type"] == "Content":
            sentence = result["text"]
            label = result["label"]
            sentence_row = {"Sentences": sentence, "Label": label}
            sentence_rows.append(sentence_row)
        else:
            header = result["text"]
            label = json.dumps([result["label"]])
            header_row = {"Headers": header, "Label": label}
            header_rows.append(header_row)
    return sentence_rows, header_rows


def create_output_paths(output_dir, filepath_prefix):
    sentence_csv_filepath = output_dir / f"{filepath_prefix}-sentences.csv"
    header_csv_filepath = output_dir / f"{filepath_prefix}-headers.csv"
    return sentence_csv_filepath, header_csv_filepath


def to_csv(rows, headers, output_path):
    with open(output_path, "w") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
