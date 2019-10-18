from unicodedata import east_asian_width


WIDTH_DICT = {
	'F':  2,    # Fullwidth
	'H':  1,    # Halfwidth
	'W':  2,    # Wide
	'Na': 1,    # Narrow
	'A':  2,    # Ambiguous
	'N':  1,    # Neutral
}


def char_width(char : str):
	return WIDTH_DICT[east_asian_width(char)]

def text_width(text : str):
	return sum(map(char_width, text))

def ljust(text : str, width : int, fill_char = ' '):
	fill_chars = fill_char * (max(0, width - text_width(text)) // char_width(fill_char))
	return text + fill_chars

def rjust(text : str, width : int, fill_char = ' '):
	fill_chars = fill_char * (max(0, width - text_width(text)) // char_width(fill_char))
	return fill_chars + text

def center(text : str, width : int, fill_char = ' '):
	fill_char_width = char_width(fill_char)
	fill_chars_length = max(0, width - text_width(text)) // fill_char_width
	left_length = fill_chars_length // 2
	right_length = fill_chars_length - left_length
	return (fill_char * left_length) + text + (fill_char * right_length)

def lclip(text : str, width : int):
	total_width = 0
	for i in range(len(text)):
		total_width += char_width(text[i])
		if width < total_width:
			return text[:i]
	return text

def ljust_lclip(text : str, width : int, fill_char = ' '):
	return ljust(lclip(text, width), width, fill_char)

def center_lclip(text : str, width : int, fill_char = ' '):
	return center(lclip(text, width), width, fill_char)

def rjust_lclip(text : str, width : int, fill_char = ' '):
	return rjust(lclip(text, width), width, fill_char)


QUADRANT_THREE_BLOCKS = (
	'\u259B',
	'\u259C',
	'\u259F',
	'\u2599',
)

def quadrant_three_blocks(index : int):
	return QUADRANT_THREE_BLOCKS[index]


class IndexFlapper:
	def __init__(self, interval_frames : int, flapper_size : int):
		self._interval_frames = int(interval_frames)
		self._flapper_size = int(flapper_size)
		self._frame = 0
		self._index = 0
	
	def update(self):
		self._frame += 1
		if self._interval_frames <= self._frame:
			self._frame = 0
			self._index += 1
			if self._flapper_size <= self._index:
				self._index = 0
	
	def index(self):
		return self._index
