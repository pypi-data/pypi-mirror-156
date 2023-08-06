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

from cruscoplanets import utils
import os

class SvgSettings(metaclass=utils.Singleton):
	"""Provides access to the settings for drawing the astrological chart. This class is a Singleton, therefore any call will always return the same instance.
	The instance of this class is programmed to behave like a dictionary where keys are the settings and the items their values. The settings can be got, set and listed with the same methods of
	*dict* objects. Moreover, they are also accessible through the normal access operator '.'.
	The values of the settings are provided as *float* objects if numeric, strings if not.
	"""
	CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "graphic.txt")
	#list of the values read from the config file that are used to calculate other values; if one of them is modified, these other values need to be updated as well
	TRIGGER_UPDATE_VALUES = ('HOUSES_CIRCLE_RADIUS', 'INNER_POINTERS_LENGTH', 'ZODIAC_CIRCLE_RADIUS', 'OUTER_POINTERS_LENGTH')
	#list of the values which are not directly got from the config file
	OTHER_VALUES = ('POINTERS_CIRCLE_RADIUS', 'TRANSIT_POINTERS_RADIUS')
		
	def __init__(self):
		self.reset()

	def reset(self):
		config = utils.parseBanalConfig(self.__class__.CONFIG_FILE)
		for line in config:
			try:
				value = float(line[1])
			except ValueError:
				value = line[1]
			self.__dict__[line[0]] = value

		#here we define other values which are not worth storing directly in the configuration file. Since the class is a Singleton, it makes no sense to define them as properties; moreover,
		#in this way they can be got also by the __getitem__ method
		self.__calculateOtherValues()

	def __calculateOtherValues(self):
		self.POINTERS_CIRCLE_RADIUS = self.HOUSES_CIRCLE_RADIUS - self.INNER_POINTERS_LENGTH
		self.TRANSIT_POINTERS_RADIUS = self.ZODIAC_CIRCLE_RADIUS + self.OUTER_POINTERS_LENGTH
	
	def __repr__(self):
		retlst = []
		for key in sorted(self.__dict__.keys()):
			retlst.append("'%s' = '%s'"%(key, self.__dict__[key]))
		return '\n'.join(retlst)
		
	def __getitem__(self, key):
		return self.__dict__[key]
		
	def __setitem__(self, key, value):
		self.__dict__[key] = value
		if key in self.__class__.TRIGGER_UPDATE_VALUES:
			self.__calculateOtherValues()
			
	def __setattr__(self, attr, value):
		super().__setattr__(attr, value)
		if attr in self.__class__.TRIGGER_UPDATE_VALUES:
			self.__calculateOtherValues()

	def save(self):
		new_config = utils.buildBanalConfig(self.classDict.items())
		with open(self.__class__.CONFIG_FILE, 'w') as save_file:
			save_file.write(new_config)
	
	@property		
	def classDict(self):
		return {setting: self.__dict__[setting] for setting in self.__dict__ if setting not in self.__class__.OTHER_VALUES}

	@property
	def topLeftCoordinates(self):
		x, y = self.IMAGE_VIEWBOX.split()[0:2]
		return float(x), float(y)
		
	def planetsTableCoordinates(self, planet_index: int, transit: bool):
		"""Returns the coordinates where the row for a certain planet in the birth planets table must be placed. Returns three values: the x value of the symbol cell, the x value of the value cell, 
		and the y value of both cells.
		"""
		x0, y0 = self.topLeftCoordinates
		x_symbol = x0 + self.PLANETS_TABLE_X_OFFSET
		y = y0 + self.PLANETS_TABLE_Y_OFFSET

		#we adjust coordinates for transit tables (where tables need to be lowered)
		if transit:
			y += 2*self.PERSONAL_DATA_FONT_SIZE

		y = y+1.5*(planet_index+1)*self.PLANETS_TABLE_FONT_SIZE,#i+1 for not overlapping the first row with the table title
		x_degree = x_symbol + self.PLANETS_TABLE_CELL_LENGTH
		
		return x_symbol, x_degree, y
		
	def housesTableCoordinates(self, house_index: int, transit: bool):
		"""Returns the coordinates where the row for a certain house in the houses table must be placed. Returns three values: the x value of the symbol cell, the x value of the value cell, 
		and the y value of both cells.
		"""
		x0, y0 = self.topLeftCoordinates
		x_symbol = x0 + self.HOUSES_TABLE_X_OFFSET
		y = y0 + self.HOUSES_TABLE_Y_OFFSET

		#we adjust coordinates for transit tables (where tables need to be lowered)
		if transit:
			y += 2*self.PERSONAL_DATA_FONT_SIZE

		y = y+1.5*(house_index+1)*self.HOUSES_TABLE_FONT_SIZE,#i+1 for not overlapping the first row with the table title
		x_degree = x_symbol + self.HOUSES_TABLE_CELL_LENGTH
		
		return x_symbol, x_degree, y
		
	def transitsTableCoordinates(self, planet_index: int, transit: bool):
		"""Returns the coordinates where the row for a certain planet in the transit planets table must be placed. Returns three values: the x value of the symbol cell, the x value of the value cell, 
		and the y value of both cells.
		"""
		x0, y0 = self.topLeftCoordinates
		x_symbol = x0 + self.TRANSITS_TABLE_X_OFFSET
		y = y0 + self.TRANSITS_TABLE_Y_OFFSET

		#we adjust coordinates for transit tables (where tables need to be lowered)
		if transit:
			y += 2*self.PERSONAL_DATA_FONT_SIZE

		y = y+1.5*(planet_index+1)*self.TRANSITS_TABLE_FONT_SIZE,#i+1 for not overlapping the first row with the table title
		x_degree = x_symbol + self.TRANSITS_TABLE_CELL_LENGTH
		
		return x_symbol, x_degree, y

		
if __name__ == '__main__':
	settings = SvgSettings()
	print(settings.POINTERS_CIRCLE_RADIUS)		#getting a value as class attribute
	settings['INNER_POINTERS_LENGTH'] += 10		#setting a value as item of dictionary
	print(settings['POINTERS_CIRCLE_RADIUS'])	#getting a calue as item of dictionary
	settings.INNER_POINTERS_LENGTH -= 10		#setting a value as class attribute
	print(settings['POINTERS_CIRCLE_RADIUS'])	#final result

