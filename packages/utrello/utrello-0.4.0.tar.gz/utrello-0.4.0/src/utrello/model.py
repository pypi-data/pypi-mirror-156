import pandas


class Card(object):
    name = None
    desc = None
    idList = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    

def card_from_args(args):
    acceptable_params = list(filter(lambda m: not(m.startswith('__')), Card.__dict__))
    new_card_params = {param: getattr(args, param) for param in acceptable_params if hasattr(args, param)}
    return Card(**new_card_params)

def cards_from_csv(cards_csv):
    df = pandas.read_csv(cards_csv)
    return [Card(**row.to_dict()) for _idx, row in df.iterrows()]