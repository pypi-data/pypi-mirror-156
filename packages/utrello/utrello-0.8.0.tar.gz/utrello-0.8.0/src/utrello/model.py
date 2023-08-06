import pandas


class Card:
    """
    Simple class used to map Trello's Card.
    """

    name = None
    desc = None
    idList = None  # noqa Since this is mapping a Trello field, it does not follow PEP8

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def __repr__(self) -> str:
        return f"{self.name}/{self.desc}/{self.idList}"

    def __eq__(self, other_card: object) -> bool:
        comparable_attrs = list(
            filter(lambda m: not (m.startswith("__")), Card.__dict__)
        )
        comparisson = [
            getattr(self, attr) == getattr(other_card, attr)
            for attr in comparable_attrs
        ]
        return all(comparisson)


def card_from_dict(attrs):
    """
    Creates a new Card object from a dict as input.
    This is used to create Card from both CLI and CSV inputs.
    The keys used will only be the keys that have exactly the same name
    as the attributes in Card class.
    """

    acceptable_params = list(filter(lambda m: not (m.startswith("__")), Card.__dict__))
    new_card_params = {param: attrs.get(param, None) for param in acceptable_params}
    return Card(**new_card_params)


def cards_from_csv(cards_csv):
    """
    Returns a list of Card objects for a CSV input.
    The CSV column headers must coincide with Card's attributes in name, not in order.
    """
    df = pandas.read_csv(cards_csv)
    return [Card(**row.to_dict()) for _idx, row in df.iterrows()]
