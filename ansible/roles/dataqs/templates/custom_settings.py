# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2012 OpenPlans
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

# Custom BSVE settings and apps for GeoNode/dataqs.
from settings import INSTALLED_APPS

LANDSCAN_FILEPATH = \
    "http://web.ornl.gov/sci/landscan/landscan2011/LS11sample_Cyprus.zip"

CUSTOM_APPS = (
    # Insert any custom/additional Django apps here
)

INSTALLED_APPS += CUSTOM_APPS