import librosa

import threading
import re
from pathlib import Path

from typing import Union, Optional, List, Tuple


RE_AUDIO_FILEEXT = re.compile(r'.*\.(wav|mp3|m4a|ogg)')


class Command:
	RESET  = 0
	RESUME = 0
	PAUSE  = 0


class SoundSelector (object):
	def __init__(
			self,
			base_dir : Union[str, Path],
			sample_rate = 44100):
		self.lock_object = threading.Lock()
		
		self.loaded_data = None
		self.paused = True
		self._setup_paths(Path(base_dir))
		
		self.sample_rate = int(sample_rate)
		self.amplitude_scale_percent = 100
	
	def _setup_paths(self, base_dir : Path):
		self.paths : List[Tuple[Path, str]] = [
			(path, path.with_suffix('').name)
			for path in base_dir.glob('**/*')
			if RE_AUDIO_FILEEXT.fullmatch(path.name)]
		self.path_index = 0
		self.loaded_path_index = -1
	
	def is_empty(self):
		return len(self.paths) == 0
	
	def is_anything_loaded(self):
		return self.loaded_path_index != -1
	
	def is_selected_loaded(self):
		return self.path_index == self.loaded_path_index
	
	def selected_path(self):
		return self.paths[self.path_index][0]
	
	def loaded_path(self):
		return self.paths[self.loaded_path_index][0]
	
	def selected_title(self):
		return self.paths[self.path_index][1]
	
	def loaded_title(self):
		return self.paths[self.loaded_path_index][1]
		
	def load(self):
		with self.lock_object:
			self.data = librosa.load(str(self.selected_path()), sr=self.sample_rate, mono=False)[0]
			if len(self.data.shape) == 1:
				self.data = self.data[None, :]
			self.loaded_path_index = self.path_index
			self.offset_frame = 0
			self.paused = False
	
	def load_next(self):
		with self.lock_object:
			prev_path_index = self.path_index
		self.path_index = self.loaded_path_index
		self.move_next_title()
		self.load()
		with self.lock_object:
			self.path_index = prev_path_index
	
	def unload(self):
		with self.lock_object:
			self.data = None
			self.loaded_path_index = -1
			self.paused = True
	
	def is_paused(self):
		return self.paused
	
	def is_loaded_finished(self):
		return self.offset_frame == self.data.shape[1]
	
	def pause(self):
		with self.lock_object:
			if self.is_anything_loaded():
				self.paused = True
	
	def resume(self):
		with self.lock_object:
			if self.is_anything_loaded():
				self.paused = False
	
	def restart(self):
		with self.lock_object:
			self.offset_frame = 0
	
	def move_next_title(self):
		self.path_index = (self.path_index + 1) % len(self.paths)
	
	def move_previous_title(self):
		self.path_index = (self.path_index - 1) % len(self.paths)
	
	def volume(self, new_volume : Optional[int] = None):
		if new_volume is None:
			return self.amplitude_scale_percent
		else:
			with self.lock_object:
				self.amplitude_scale_percent = max(0, min(new_volume, 100))
	
	def callback_output_data(self, outdata, frames, time, status):
		outdata.fill(0)
		with self.lock_object:
			if not self.is_anything_loaded() or self.is_paused():
				return
			offset = self.offset_frame
			nframes, _ = outdata.shape
			if self.is_anything_loaded():
				update_frames = min(nframes, self.data.shape[1] - offset)
				outdata[:update_frames, :] = self.data[:, offset:offset+update_frames].T
				outdata[:] *= 0.01 * self.amplitude_scale_percent
				self.offset_frame += update_frames
