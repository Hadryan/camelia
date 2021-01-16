# %%

# We need it to import sunflower

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

raw_audio, extension = load_from_disk("../assets/boombap.mp3")

song = Song(raw_audio, extension)

# Video setup

vdo = MusicVideo(
    song,
    "../assets/chillhop_mix/mpc_vid_89bpm.mp4",
    "NUMERO 13",
    "Boom bap!",
    music_bpm=91,
    drop_beats=14,
    watermark=False,
)

# Main Loop

vdo.main_clip = vdo.sync_bpm_clip(vdo.main_clip, bpm_video=87.4)

vdo.main_clip = moviepy.editor.vfx.mask_color(
    vdo.main_clip, color=[235, 238, 231], thr=20, s=10
)
vdo.main_clip = vdo.loop_clip(vdo.main_clip, bpm_video=87.4, crossfadein=1)

# Text
vdo.text_assets.generate_clips()
vdo.text_assets.set_timing(mode="before_drop")

# Intro
vdo.add_background_clip("../assets/loops/boreal_static.gif", sync=True)
video_gen = vdo.generate_video(cut=30)

# %%

video_gen.write_videofile(
    "../results/numero13_test2.mp4",
    temp_audiofile="../results/temp-audio.m4a",
    remove_temp=True,
    codec="libx264",
    audio_codec="aac",
)

# %%
