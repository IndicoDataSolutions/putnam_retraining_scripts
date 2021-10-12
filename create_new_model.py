"""Create an Indico Dataset and Train New Model"""
import csv
import json
import argparse
from pathlib import Path

from indico_toolkit import create_client
from indico_toolkit.indico_wrapper import Datasets
from indico.queries import CreateModelGroup, ModelGroupPredict, GetDataset


def get_args():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--header-csv-path",
        type=Path,
        required=True,
        help="Path to header training data",
    )
    parser.add_argument(
        "--sentence-csv-path",
        type=Path,
        required=True,
        help="Path to sentence training data",
    )
    parser.add_argument(
        "-d",
        "--dataset-suffix",
        type=str,
        default="",
        help="Suffix to apply to Dataset and Model names",
    )

    args = parser.parse_args()
    return args


def main():
    args = get_args()

    host = "putnam.indico.domains"
    api_token_path = "/home/fitz/Documents/customers/putnam/putnam_onboarding_scripts/indico_api_token.txt"
    client = create_client(host, api_token_path)

    header_dataset, sentence_dataset = create_datasets(
        client, args.header_csv_path, args.sentence_csv_path, args.dataset_suffix
    )
    train_models(client, header_dataset, sentence_dataset, args.dataset_suffix)


def create_datasets(client, header_csv_path, sentence_csv_path, dataset_suffix):
    dataset = Datasets(client)
    header_dataset_name = f"Header Dataset {dataset_suffix}"
    header_dataset = dataset.create_dataset([header_csv_path], header_dataset_name)
    print("Uploaded header dataset")

    sentence_dataset_name = f"Sentence Dataset {dataset_suffix}"
    sentence_dataset = dataset.create_dataset(
        [sentence_csv_path], sentence_dataset_name
    )
    print("Uploaded Sentence Dataset")

    return header_dataset, sentence_dataset


def train_models(client, header_dataset, sentence_dataset, dataset_suffix):
    header_model_name = f"Header Model {dataset_suffix}"
    train_model(client, header_dataset, header_model_name, "Headers", "Label")

    sentence_model_name = f"Sentence Model {dataset_suffix}"
    train_model(client, sentence_dataset, sentence_model_name, "Sentences", "Label")


def train_model(client, dataset, model_name, source_col, label_col):
    model_group = client.call(
        CreateModelGroup(
            name=model_name,
            dataset_id=dataset.id,
            source_column_id=dataset.datacolumn_by_name(
                source_col
            ).id,  # csv text column
            labelset_id=dataset.labelset_by_name(
                label_col
            ).id,  # csv target class column
            model_type="FINETUNE",
        )
    )


if __name__ == "__main__":
    main()
