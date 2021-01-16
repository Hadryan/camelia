# %%

import sys

sys.path.insert(0, "..")
sys.path.insert(0, "../..")

# General
import numpy
import pandas

# Audio
from sunflower.sunflower.song_loader import Song, load_from_disk
from sunflower.sunflower.song_analyzer import SongAnalyzer
from sunflower.sunflower.utils import export_wav
from sunflower.sunflower.song_visualizer import visualize_waveform
import plotly.graph_objects as go
import numpy as np
import librosa
import soundfile as sf

# Video
import moviepy
import pygame

from camelia.video import MusicVideo

# %%
# Loading song

raw_audio, extension = load_from_disk("../assets/chiptune.mp3")

song = Song(raw_audio, extension)

# Video setup

vdo = MusicVideo(
    song,
    "../assets/loops/loop.mp4",
    "Tices",
    "Chiptune",
    music_bpm=95.5,
    drop_beats=4,
    watermark=False,
)

# Main Loop

vdo.main_clip = vdo.sync_bpm_clip(vdo.main_clip, optimize_loop=False)
vdo.main_clip = vdo.loop_clip(vdo.main_clip, crossfadein=0.5)

# Text
vdo.text_assets.generate_clips()
vdo.text_assets.set_timing(mode="before_drop")

# Intro
vdo.add_background_clip("../assets/loops/boreal_static.gif", sync=True)
video_gen = vdo.generate_video(cut=10)

# %%
video_gen.write_videofile(
    "../results/test2.mp4",
    temp_audiofile="../results/temp-audio.m4a",
    remove_temp=True,
    codec="libx264",
    audio_codec="aac",
)
