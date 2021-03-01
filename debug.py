from dymond_game import game


class Main:
    def __init__(self):
        super(Main, self).__init__()


if __name__ == '__main__':
    game_test = game.Game("test", {
        "resolucion": [1600, 900],
        "sfx_volume": 0.5,
        "mus_volume": 0.09
    })
    game_test.run()
