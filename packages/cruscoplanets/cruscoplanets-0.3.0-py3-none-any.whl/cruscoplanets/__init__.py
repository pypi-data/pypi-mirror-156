#    This file is part of Cruscoplanets.
#
#    Cruscoplanets is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Cruscoplanets is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Cruscoplanets.  If not, see <http://www.gnu.org/licenses/>.

import os

libvipspath = os.path.join(os.path.irname(os.path.abspath(__file__)), "c_libraries", "vips-dev-w64-web-8.12.1", "vips-dev-8.12", "bin")
if libvipspath not in os.environ['PATH']:
	os.environ['PATH'] = os.environ['PATH'] + os.pathsep + libvipspath

import cruscoplanets.cmdline as cmdline
