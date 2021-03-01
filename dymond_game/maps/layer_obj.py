import pygame

from dymond_game import game_data


class LayerObj(object):
    """
    This class is, as for now, only really useful for side scrolling backgrounds. Other classes may inherit from this
    one and override the draw function to allow proper continuous vertical scrolling.
    """

    def __init__(self, path: str, ratio: float, offset: [int, int], vertical: int, movement: float):
        """
        LayerObj contains the data necessary to define the behaviour of a background layer to be handled properly by a
        background class. This allows for simple backgrounds and more complex parallax backgrounds.

        :param ratio: Ratio from the original scroll at which the layer will scroll, set to a value between 0 and 1 to
        avoid weird layer movement
        :param path: Where the image of the layer is
        :param offset: Default [0, 0], if not None sets the offset of the layer
        :param vertical: Vertical scrolling multiplier
        :param movement: Default 0, continuous movement of a layer
        """
        self.x = 0  # Position of the layer on the x axis
        self.y = 0  # Position of the layer on the y axis
        self.offset = offset  # Offset of the layer from the origin (0, 0)
        self.ratio = ratio  # Ratio of scroll compared to the original scroll
        self.vertical = vertical  # If scrolling is vertical
        self.movement = movement  # Continuous x axis movement
        self.moved_offset = 0
        self.stage_x = 0  # Stage (chunk) of the background on the x axis
        self.image = pygame.image.load(path).convert()  # Loads the image from the path and converts it to improve
        # performance
        self.image.set_colorkey(game_data.COLOR_KEY)  # Color key for alpha transformation, set to pure green

    def draw(self, frame: pygame.Surface, scroll):
        """
        Draws 3 images, one to the left and another one on the right. This allows for continuous x axis scrolling
        backgrounds. Maybe not the most efficient measure. Other types of LayerObj may override this function to allow
        for continuous vertical scrolling or to ignore horizontal scrolling.

        :param frame: Pygame Surface in which the layer is going to be drawn
        :param scroll: The scroll (or camera position) to draw relative to
        :return None:
        """
        self.moved_offset += self.movement
        self.stage_x = round(((scroll[0] + self.moved_offset) * self.ratio) / game_data.FRAME_SIZE[0])
        self.x = self.stage_x * game_data.FRAME_SIZE[0]
        to_scroll = [(self.x - (scroll[0] + self.moved_offset) * self.ratio + self.offset[0]),
                     ((scroll[1] * self.ratio)*self.vertical + self.offset[1])]
        # Draws the main image, plus one to the left and another one to the right
        frame.blit(self.image, to_scroll)
        frame.blit(self.image,
                   (to_scroll[0] + game_data.FRAME_SIZE[0], to_scroll[1]))
        frame.blit(self.image,
                   (to_scroll[0] - game_data.FRAME_SIZE[0], to_scroll[1]))
