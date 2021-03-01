from bin.maps.layer_obj import *
import pygame


class Parallax:
    """
    A simple parallax object that holds a static background, and a undefined amount of dynamic parallax layers.

    It will use the LayerObj class to describe each layer.
    """

    def __init__(self, data: {}):
        """

        """
        self.static_bckgnd = pygame.image.load(data["static"]).convert()
        self.layers = []
        for layer_data in data["layers"]:
            self.layers.append(LayerObj(layer_data["path"], layer_data["ratio"], layer_data["offset"],
                                        layer_data["vertical"], layer_data["movement"]))

    def render(self, frame: pygame.Surface, scroll):
        """
        Draws the layers.

        :param frame: Pygame Surface in which the layer is going to be drawn
        :param scroll: The scroll (or camera position) to draw relative to
        :return: None
        """
        frame.blit(self.static_bckgnd, (0, 0))
        for layer in self.layers:
            layer.draw(frame, scroll)
