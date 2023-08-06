# Copyright (C) 2022 Ben Elliston
#
# This file is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.

"""Simulated loads for the NEMO simulation framework."""


class Load():
    """Base load class (ha ha)."""
    def __init__(self, label):
        self.label = label


class NoLoad(Load):
    """No load class that always returns zero."""
    def __init__(self, timesteps=8760, label=None):
        Load.__init__(self, label)
        self.timesteps = timesteps

    def total_demand(self):
        """Return total demand."""
        return 0

    def step(self, hour):
        """Demand in given timestep."""
        assert hour < self.timesteps
        return 0

    def __str__(self):
        return 'Noload'


class FlatBlock(Load):
    """A flat load block."""
    def __init__(self, load, timesteps=8760, label=None):
        Load.__init__(self, label)
        self.timesteps = timesteps
        self.load = load

    def total_demand(self):
        """Return total demand."""
        return self.timesteps * self.load

    def step(self, hour):
        """Demand in given timestep."""
        assert hour < self.timesteps
        return self.load

    def __str__(self):
        return f'Flat block load ({self.load} MW)'
