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
import pyvips


class FormatError(Exception):
	
	def __init__(self, theformat):
		super().__init__()
		self.format = theformat
		
	def __str__(self):
		return "Unrecognized format: %s"%theformat


class ChartPrinter:

	def __init__(self, chart):
		self.chart = chart
		self.image = pyvips.Image.new_from_buffer(self.chart.svgAsString, "")#empty string is a required positional argument
	
	@property
	def filename(self):
		return self.chart.filename

	def makeSvgBuffer(self):
		return self.chart.svgAsString
	
	def makePngBuffer(self):
		pngbuffer = self.image.write_to_buffer('.png')
		return pngbuffer
	
	def makeJpgBuffer(self):
		jpgbuffer = self.image.write_to_buffer('.jpg')
		return jpgbuffer
	
	def makeBufferInFormat(self, theformat: str = 'svg'):
		myformat = '.' + theformat
		if myformat == '.svg':
			return self.makeSvgBuffer()
		elif myformat == '.png':
			return self.makePngBuffer()
		elif myformat == '.jpg':
			return self.makeJpgBuffer()
		else:
			raise FormatError(theformat)

	def deployInFormat(self, fpath: str):
		theformat = fpath.split('.')[-1]
		if theformat not in {'png', 'jpeg', 'jpg', 'svg'}:
			raise FormatError(theformat)
		if theformat == 'svg':
			self.chart.write(fpath)
		else:
			self.image.write_to_file(fpath)
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
