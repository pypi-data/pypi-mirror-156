from os import path

from IPython.display import Image


def image(checkmark: bool, size: int = 32):
    filename = f'{"checkmark" if checkmark else "cross"}_{size}.png'
    return Image(filename=path.join(path.dirname(__file__), filename))
