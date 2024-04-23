#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#  Copyright (C) 2023. HCAT-Project-Team
#  _
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#  _
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#  _
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
@File       : main.py

@Author     : hsn

@Date       : 3/31/24 10:07 AM
"""
import dataclasses
import math

import svgwrite


@dataclasses.dataclass
class Station:
    name: str
    pos: tuple[int, int]
    airport: str | None = None
    railway: str | None = None
    lines_count: int = dataclasses.field(default=0, init=False)

    def count(self):
        self.lines_count += 1


@dataclasses.dataclass
class Line:
    name: str
    color: tuple[int, int, int] = (0, 0, 0)
    under_construction: bool = False
    start_v: tuple[int, int] = (0, 0)
    end_v: tuple[int, int] = (0, 0)
    stations: list[Station] = dataclasses.field(default_factory=list)

    def add_station(self, station: Station):
        station.count()
        self.stations.append(station)

    def add_stations(self, stations: list[Station]):
        for station in stations:
            station.count()
            self.stations.append(station)


@dataclasses.dataclass
class Map:
    name: str
    lines: list[Line] = dataclasses.field(default_factory=list)
    constructing_lines: list[Line] = dataclasses.field(default_factory=list)

    def add_line(self, line: Line):
        if line.under_construction:
            self.constructing_lines.append(line)
        else:
            self.lines.append(line)

    def asdict(self):
        return dataclasses.asdict(self)

    def gen_img(self, generator):
        return generator(self)


class PosConverter:
    def __init__(self, map_size=(2048, 2048), starting_pos=(0, 0), ratio=1 / 10000):
        self.map_size = map_size
        self.starting_pos = starting_pos
        self.ratio = ratio

    def __call__(self, pos):
        x, y = pos
        start_x, start_y = self.starting_pos
        map_x, map_y = self.map_size
        return x * self.ratio * map_x + start_x, y * self.ratio * map_y + start_y


def gen(_map: Map, size=(2048, 2048), padding=15):
    # backgraound
    draw = svgwrite.Drawing(profile='tiny', size=size)
    draw.add(draw.rect((0, 0), size, fill=svgwrite.rgb(255, 255, 255)))
    converter = PosConverter(map_size=size, ratio=1 / 2800)

    def draw_lines(lines: list[Line]):
        for line in lines:
            last_station = None
            for i, station in enumerate(line.stations):
                x, y = converter(station.pos)
                if last_station:
                    last_x, last_y = converter(last_station.pos)

                    # start vector
                    # print(f'M {last_x} {last_y} C {x+a_x} {y+a_y} L {x} {y}')
                    # draw.add(draw.path(d=f'M {last_x} {last_y} C {last_x+a_x} {last_y+a_y},{last_x+2*a_x} {last_y+2*a_y},{x} {y}', stroke=svgwrite.rgb(*line.color)))
                    draw.add(draw.line((last_x, last_y), (x, y), stroke=svgwrite.rgb(*line.color), stroke_width=15))
                    # draw.line((last_x, last_y, x, y), fill=line.color, width=5)
                last_station = station

    def draw_stations(lines: list[Line]):
        for line in lines:
            for station in line.stations:
                x, y = converter(station.pos)
                draw.add(draw.ellipse((x, y), (padding, padding), stroke=svgwrite.rgb(0, 0, 0),
                                      fill=svgwrite.rgb(255, 255, 255)))
                # draw.ellipse((x - padding, y - padding, x + padding, y + padding), fill=(0, 0, 0))

    draw_lines(_map.constructing_lines)
    draw_lines(_map.lines)
    draw_stations(_map.constructing_lines)
    draw_stations(_map.lines)

    return draw


@dataclasses.dataclass
class Point:
    x: float
    y: float

    def __add__(self, other):
        assert isinstance(other, Point)
        return StraightLine(a=self.y - other.y, b=other.x - self.x, c=self.x * other.y - other.x * self.y)

    def __sub__(self, other):
        assert isinstance(other, Point)
        return Vector(x=self.x - other.x, y=self.y - other.y)


@dataclasses.dataclass
class Vector:
    x: float
    y: float

    def angle(self, other):
        assert isinstance(other, Vector)
        print(self * other)
        print(math.sqrt(self.x ** 2 + self.y ** 2) * math.sqrt(other.x ** 2 + other.y ** 2))
        print(math.acos(1/2))
        return math.acos(self * other / (math.sqrt(self.x ** 2 + self.y ** 2) * math.sqrt(other.x ** 2 + other.y ** 2)))

    def __add__(self, other):
        assert isinstance(other, Vector)
        return Point(x=self.x + other.x, y=self.y + other.y)

    def __sub__(self, other):
        assert isinstance(other, Vector)
        return Vector(x=self.x - other.x, y=self.y - other.y)

    def __mul__(self, other):
        if isinstance(other, Vector):
            return self.x * other.x + self.y * other.y
        else:
            return Vector(x=self.x * other, y=self.y * other)


@dataclasses.dataclass
class StraightLine:
    a: float
    b: float
    c: float


if __name__ == '__main__':
    l3x, l3y = 1400, 100
    st_airport_north = Station('Airport North', (l3x, l3y), airport='CAN')
    st_airport_south = Station('Airport South', (l3x, l3y + 100), airport='CAN')
    st_gaozeng = Station('Gaozeng', (l3x, l3y + 200))
    st_renhe = Station('Renhe', (l3x, l3y + 300))
    st_longgui = Station('Longgui', (l3x, l3y + 400))
    st_jiahewanggang = Station('Jiahewanggang', (l3x, l3y + 500))
    st_baiyundadaobei = Station('Baiyundadaobei', (l3x + 100, l3y + 700))
    st_yongtai = Station('Yongtai', (l3x + 200, l3y + 800))
    st_tonghe = Station('Tonghe', (l3x + 300, l3y + 900))
    st_jingxi_nanfang_hospital = Station('Jingxi Nanfang Hospital', (l3x + 400, l3y + 1000))
    st_meihuayuan = Station('Meihuayuan', (l3x + 500, l3y + 1100))
    st_yantang = Station('Yantang', (l3x + 500, l3y + 1200))
    st_guangzhou_east_railway_station = Station('Guangzhou East Railway Station', (l3x + 500, l3y + 1300),
                                                railway='GZD')
    st_linhexi = Station('Linhexi', (l3x + 500, l3y + 1400))
    st_tiyuxilu = Station('Tiyuxilu', (l3x + 500, l3y + 1400))
    st_zhujiang_new_town = Station('Zhujiang New Town', (l3x + 500, l3y + 1500))
    st_canton_tower = Station('Canton Tower', (l3x + 500, l3y + 1600))
    st_kecun = Station('Kecun', (l3x + 500, l3y + 1700))
    st_datang = Station('Datang', (l3x + 500, l3y + 1800))
    st_lijiao = Station('Lijiao', (l3x + 500, l3y + 1900))
    st_xiajiao = Station('Xiajiao', (l3x + 500, l3y + 2000))
    st_dashi = Station('Dashi', (l3x + 500, l3y + 2100))
    st_hanxi_changlong = Station('Hanxi Changlong', (l3x + 500, l3y + 2200))
    st_shiqiao = Station('Shiqiao', (l3x + 500, l3y + 2300))
    st_panyu_square = Station('Panyu Square', (l3x + 700, l3y + 2400))

    l3 = Line('Line 3', color=(232, 158, 71), start_v=(0, 10))
    l3.add_station(st_airport_north)

    map = Map('Guangzhou Metro')
    map.add_line(l3)
    svgwrite.Drawing()
    gen(map, (7520, 6600)).saveas('guangzhou_metro.svg')

    p0=Point(0,0)
    p1 = Point(1, 0)
    p2 = Point(1, math.sqrt(3))
    print((p1-p0).angle(p2-p0))
