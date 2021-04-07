import os
import random
from math import *

from kivy_garden.mapview.utils import clamp
# from kivy.garden.mapview.mapview.utils import clamp

from kivy.graphics import Color, Line, SmoothLine, MatrixInstruction
from kivy.clock import Clock
from kivy.graphics.context_instructions import Translate, Scale
from kivy.garden.mapview import MapView, MapLayer, MapSource

# Use the legacy package to enable this
from kivy.garden.mapview.mapview import (
    MIN_LONGITUDE,
    MIN_LATITUDE,
    MAX_LATITUDE,
    MAX_LONGITUDE,
)
# MIN_LONGITUDE = -180
# MIN_LATITUDE = -90
# MAX_LATITUDE = 90
# MAX_LONGITUDE = 180

# amnonn122 commented on May 5, 2019
# lucifermorn commented on Nov 25, 2020
# https://github.com/kivy-garden/mapview/issues/4

class LineMapLayer(MapLayer):
    def __init__(self, **kwargs):
        """Customizing Screen Initializing"""
        super(LineMapLayer, self).__init__(**kwargs)
        self._coordinates = list()
        self._line_points = None
        self._line_points_offset = (0, 0)
        self.zoom = 0
        self.lon = 0
        self.lat = 0
        self.ms = 0

    @property
    def coordinates(self):
        return self._coordinates

    @coordinates.setter
    def coordinates(self, coordinates):
        self._coordinates = coordinates
        self.invalidate_line_points()
        self.clear_and_redraw()

    @property
    def line_points(self):
        if self._line_points is None:
            self.calc_line_points()
        return self._line_points

    @property
    def line_points_offset(self):
        if self._line_points is None:
            self.calc_line_points()
        return self._line_points_offset

    def calc_line_points(self):
        # Offset all points by the coordinates of the first point, to keep coordinates closer to zero.
        # (and therefore avoid some float precision issues when drawing lines)
        self._line_points_offset = (
            self.get_x(self.coordinates[0][1]),
            self.get_y(self.coordinates[0][0]),
        )
        # Since lat is not a linear transform we must compute manually
        self._line_points = [
            (
                self.get_x(lon) - self._line_points_offset[0],
                self.get_y(lat) - self._line_points_offset[1],
            )
            for lat, lon in self.coordinates
        ]

    def invalidate_line_points(self):
        self._line_points = None
        self._line_points_offset = (0, 0)

    def get_x(self, lon):
        """Get the x position on the map using this map source's projection
        (0, 0) is located at the top left.
        """
        return clamp(lon, MIN_LONGITUDE, MAX_LONGITUDE) * self.ms / 360.0

    def get_y(self, lat):
        """Get the y position on the map using this map source's projection
        (0, 0) is located at the top left.
        """
        lat = radians(clamp(-lat, MIN_LATITUDE, MAX_LATITUDE))
        # print(log((tan(lat) + 1.0) / cos(lat))) # Return Here
        # if tan(lat) + 1.0 / cos(lat) <= 0:
        #     return (1.0 - (tan(lat) + 1.0 / cos(lat)) / pi) * self.ms / 2.0
        return (1.0 - log(tan(lat) + 1.0 / cos(lat)) / pi) * self.ms / 2.0

    def reposition(self):
        map_view = self.parent

        # Must redraw when the zoom changes
        # as the scatter transform resets for the new tiles

        if (
            self.zoom != map_view.zoom
            or self.lon != round(map_view.lon, 7)
            or self.lat != round(map_view.lat, 7)
        ):
            map_source = map_view.map_source
            self.ms = pow(2.0, map_view.zoom) * map_source.dp_tile_size
            self.invalidate_line_points()
            self.clear_and_redraw()

    def clear_and_redraw(self, *args):
        with self.canvas:
            # Clear old line
            self.canvas.clear()

        # FIXME: Why is 0.05 a good value here? Why does 0 leave us with weird offsets?
        Clock.schedule_once(self._draw_line, 0.05)
        # Clock.schedule_interval(self._draw_line, 0.05)

    def _draw_line(self, *args):
        map_view = self.parent
        self.zoom = map_view.zoom
        self.lon = map_view.lon
        self.lat = map_view.lat

        # When zooming we must undo the current scatter transform
        # or the animation distorts it
        scatter = map_view._scatter
        sx, sy, ss = scatter.x, scatter.y, scatter.scale

        # Account for map source tile size and map view zoom
        vx, vy, vs = map_view.viewport_pos[0], map_view.viewport_pos[1], map_view.scale

        with self.canvas:
            # Clear old line
            self.canvas.clear()

            # Offset by the MapView's position in the window
            Translate(*map_view.pos)

            # Undo the scatter animation transform
            # The fix for the after load bug was to undo the scatter animation (March 22)
            # Scale(1 / ss, 1 / ss, 1)
            # Translate(-sx, -sy)

            # Apply the get window xy from transforms
            Scale(vs, vs, 1)
            Translate(-vx, -vy)

            # Apply the what we can factor out of the mapsource long, lat to x, y conversion
            Translate(self.ms / 2, 0)

            # Translate by the offset of the line points (this keeps the points closer to the origin)
            Translate(*self.line_points_offset)

            Color(0, 0.3, 1, 1)
            Line(points=self.line_points, width=2)


# MapViewApp().run()
