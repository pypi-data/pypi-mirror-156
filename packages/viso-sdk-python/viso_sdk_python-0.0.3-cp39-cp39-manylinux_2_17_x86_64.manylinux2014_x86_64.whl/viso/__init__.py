# -*- coding: utf-8 -*-
#
# Copyright (C) 2018-2022 Shane Carlyon <s.carlyon@viso.ai>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Wrapper for the Viso SDK."""

import warnings

from viso._version import (  # noqa: F401
    __author__,
    __copyright__,
    __email__,
    __license__,
    __title__,
    __version__,
)

warnings.filterwarnings("default", category=DeprecationWarning, module="^viso")
