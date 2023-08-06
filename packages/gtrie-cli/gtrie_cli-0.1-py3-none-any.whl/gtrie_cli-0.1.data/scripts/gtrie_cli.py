#!python

import argparse
import requests


from typing import List

class Consts(object):
    URL="https://green-bedrock-354219.wl.r.appspot.com"
    ADD="add"
    DEL="delete"
    LIST="display"
    GET_PREFIX="autocomplete"
    SEARCH="search"


def send_request(url: str, data=None):
    try:
        response = requests.post(url, data=data)

        if response.ok:
            print(f"{response.content}")
        else:
            print(f"Error response {response}")

    except Exception as e:
        print(f"Error sending request {url}:{e}")



def add_string(word: str):
    print(f"Adding {word}")
    url = f"{Consts.URL}/{Consts.ADD}/{word}"
    send_request(url)


def del_string(word: str):
    print(f"Deleting {word}")
    url = f"{Consts.URL}/{Consts.DEL}/{word}"
    send_request(url)


def list_strings():
    print("Listing all words")
    url = f"{Consts.URL}/{Consts.LIST}"
    send_request(url)


def get_prefix_strings(word: str):
    print(f"Listing all prefixes for {word}")
    url = f"{Consts.URL}/{Consts.GET_PREFIX}/{word}"
    send_request(url)


def search_string(word: str):
    print(f"Searching {word}")
    url = f"{Consts.URL}/{Consts.SEARCH}/{word}"
    send_request(url)


def main():

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        "-a",
        "--add",
        type=str,
        help="Provide a string to add",
        required=False
    )
    group.add_argument(
        "-d",
        "--delete",
        type=str,
        help="Provide a string to delete",
        required=False
    )
    group.add_argument(
        '-l',
        '--list',
        default=False,
        action='store_true',
        help="Print list of strings"
    )
    group.add_argument(
        '-g',
        '--get',
        type=str,
        help="Get string prefix list",
        required=False
    )
    parser.add_argument(
        "-s",
        "--search",
        type=str,
        help="Provide a string to search",
        required=False,
    )


    args = parser.parse_args()

    if args.add is not None:
        add_string(args.add)

    if args.delete is not None:
        del_string(args.delete)

    if args.list:
        list_strings()

    if args.get is not None:
        get_prefix_strings(args.get)

    if args.search is not None:
        search_string(args.search)


if __name__ == "__main__":
    main()
