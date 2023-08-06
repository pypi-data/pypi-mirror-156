import argparse
import os

from . import api, model

__version__ = "0.8.1"


def board_list_handler(api_credentials, _args):
    return api.Boards(**api_credentials).list()


def list_handler(api_credentials, args):
    list_ids = api.Lists(**api_credentials)
    list_ids.board_id = args.board_id
    return list_ids.list()


def card_create_handler(api_credentials, args):
    if args.cards_csv:
        cards_list = model.cards_from_csv(args.cards_csv)
    else:
        cards_list = [model.card_from_dict(args.__dict__)]

    return [api.Cards(**api_credentials).create(card) for card in cards_list]


def main():
    parser = argparse.ArgumentParser(description="Interacts with Trello Restful API")
    parser.add_argument("--api_key", default=os.environ.get("TRELLO_API_KEY"))
    parser.add_argument("--api_token", default=os.environ.get("TRELLO_API_TOKEN"))

    subparsers = parser.add_subparsers(help="service help")

    boards = subparsers.add_parser("boards")
    board_actions = boards.add_subparsers()

    board_list = board_actions.add_parser("list")
    board_list.set_defaults(func=board_list_handler)

    lists = subparsers.add_parser("lists")
    lists.add_argument("--board_id", dest="board_id")
    lists.set_defaults(func=list_handler)

    cards = subparsers.add_parser("cards")
    card_actions = cards.add_subparsers()

    card_create = card_actions.add_parser("create")
    card_csv = card_create.add_argument_group("create from csv")
    card_csv.add_argument(
        "-f", "--from-csv", dest="cards_csv", type=argparse.FileType("r")
    )

    card_model = card_create.add_argument_group("create from cli")
    card_model.add_argument("--name", dest="name", type=str)
    card_model.add_argument("--desc", dest="desc", type=str)
    card_model.add_argument("--idList", dest="idList", type=str)

    card_create.set_defaults(func=card_create_handler)
    args = parser.parse_args(
        "cards create --name test --desc test --idList abc123".split()
    )

    args = parser.parse_args()

    api_credentials = {"api_key": args.api_key, "api_token": args.api_token}

    try:
        print(args.func(api_credentials, args))
    except AttributeError:
        parser.print_help()
