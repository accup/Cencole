from typing import Optional

try:
	# Windows
	import msvcrt
	
	def init():
		return
	
	def restore():
		return
	
	def hit_any_key():
		return msvcrt.kbhit()

	
	class KeyInput:
		def __init__(self):
			self._bytes : bytes = msvcrt.getch()
			if self._bytes in (b'\x00', b'\xe0'):
				self._bytes += msvcrt.getch()
		
		def escape(self):
			return self._bytes == b'\x1b'
		
		def enter(self):
			return self._bytes == b'\r'
		
		def ascii(self, c : bytes):
			return self._bytes == c
		
		def up(self):
			return self._bytes == b'\xe0H'
		
		def down(self):
			return self._bytes == b'\xe0P'
		
		def left(self):
			return self._bytes == b'\xe0K'
		
		def right(self):
			return self._bytes == b'\xe0M'
		
	def key_input():
		return KeyInput()
	
except ImportError:
	# UNIX
	import os
	import sys
	import fcntl
	import termios
	
	fno_stdin = None
	stdinbuf = None
	
	attr_old = None
	fcntl_old = None
	
	def init():
		global fno_stdin, stdinbuf, attr_old, fcntl_old
		fno_stdin = sys.stdin.fileno()
		stdinbuf = sys.stdin.buffer
		
		# 端末設定
		attr_old = termios.tcgetattr(fno_stdin)
		fcntl_old = fcntl.fcntl(fno_stdin, fcntl.F_GETFL)
		
		# ノンブロッキングモード設定
		attr = termios.tcgetattr(fno_stdin)
		attr[3] = attr[3] & ~termios.ECHO & ~termios.ICANON
		termios.tcsetattr(fno_stdin, termios.TCSADRAIN, attr)
		fcntl.fcntl(fno_stdin, fcntl.F_SETFL, fcntl_old | os.O_NONBLOCK)
	
	def restore():
		# 端末設定のリストア
		fcntl.fcntl(fno_stdin, fcntl.F_SETFL, fcntl_old)
		termios.tcsetattr(fno_stdin, termios.TCSANOW, attr_old)
	
	
	next_buf : Optional[bytes] = None
	
	def _getch():
		global next_buf
		if next_buf is None:
			return stdinbuf.read(1)
		else:
			buf = next_buf
			next_buf = None
			return buf
	
	def hit_any_key():
		global next_buf
		if next_buf is None:
			next_buf = stdinbuf.read(1)
		return next_buf is not None
	
	def _lookahead():
		hit_any_key()
		return next_buf
	
	class KeyInput:
		def __init__(self):
			self._bytes : bytes = _getch()
			if self._bytes == b'\x1b': # Escape
				c = _lookahead()
				if 0x40 <= ord(c) < 0x60: # Escape sequences
					self._bytes += _getch()
					if c == b'[': # Control Sequence Introducer
						c = _getch()
						while ord(c) < 0x40:
							self._bytes += c
							c = _getch()
						self._bytes += c
		
		def escape(self):
			return self._bytes == b'\x1b'
		
		def enter(self):
			return self._bytes == b'\n'
		
		def ascii(self, c : bytes):
			return self._bytes == c
		
		def up(self):
			return self._bytes == b'\x1b[A'
		
		def down(self):
			return self._bytes == b'\x1b[B'
		
		def left(self):
			return self._bytes == b'\x1b[D'
		
		def right(self):
			return self._bytes == b'\x1b[C'
	
	def key_input():
		return KeyInput()
	