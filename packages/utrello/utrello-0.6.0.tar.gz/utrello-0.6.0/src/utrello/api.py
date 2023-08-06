import typing

import requests


class TrelloApi:
    """
    Base class to interact with Trello API.
    Ideally this should not be used directly
    """

    base_url: str = "https://api.trello.com/1"
    service_endpoint: typing.Optional[str] = None
    url: str
    params: typing.Dict[str, typing.Any] = {}

    def __init__(self, api_key, api_token):
        self.params["key"] = api_key
        self.params["token"] = api_token
        self.url = f"{self.base_url.strip('/')}/{self.service_endpoint.strip('/')}"


class Boards(TrelloApi):
    base_url = "https://api.trello.com/1/members/me"
    service_endpoint = "/boards"

    def list(self):
        params = self.params.copy()
        params["fields"] = "name"
        req = requests.get(self.url, params=params)
        return req.json()


class Lists(TrelloApi):
    service_endpoint = "/boards/{board_id}/lists"
    board_id = None

    def list(self):
        req = requests.get(self.url.format(board_id=self.board_id), params=self.params)
        return req.json()


class Cards(TrelloApi):
    service_endpoint = "/cards"

    def create(self, card):
        headers = {"Accept": "application/json"}
        print(self.url)

        query = self.params.copy()
        query.update(card.__dict__)
        print(query)

        response = requests.post(self.url, headers=headers, params=query)
        print(response)
        return response.json()
