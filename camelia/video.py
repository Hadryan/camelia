from moviepy.editor import *
import moviepy
from moviepy.audio.AudioClip import AudioArrayClip
from .text_assets import TextAssets
import math

OPTIMIZED_PARAMS = {
    "square_preview": {
        "width": 400,
        "height": 400,
    },
    "square_instagram": {
        "width": 1080,
        "height": 1080,
    },
}


class MusicVideo:
    def __init__(
        self,
        song,
        path_video: str,
        artist_name: str,
        track_name: str,
        music_bpm: float,
        drop_beats=None,
        watermark=False,
    ):
        """Generic video object.
        This class contains all parameters common to all styles of videos to be generated.

        :param song: Song
        :param path_video: Path to the video
        :param artist_name: Artist name
        :param track_name: Track name
        :param music_bpm: BPM of the music
        :param drop_beats: Number of beats before drop
        :param watermark: If set to True: adds a watermark on the corner of the video
        """

        # Size

        self.width = None
        self.height = None

        self.set_params()

        # Video

        self.main_clip = VideoFileClip(path_video, fps_source="fps")
        self.bpm_video = None
        self.drop_beats = drop_beats

        self.main_clip = self.process_size_clip(self.main_clip, prop=0.8)

        self.background_clips = []

        # Song

        self.song = song
        self.audioclip = AudioArrayClip(
            self.song.waveform.reshape(-1, 2), fps=self.song.sr
        )

        # Rhythm

        self.music_bpm = music_bpm
        self.duration = 60 / self.music_bpm

        # Informations to display

        self.artist_name = artist_name
        self.track_name = track_name

        self.text_assets = TextAssets(
            self.width,
            self.height,
            self.artist_name,
            self.track_name,
            self.duration,
            self.drop_beats,
        )

        # Watermark

        self.watermark = None

        if watermark:

            self.watermark = self.add_watermark()

    def set_params(self, platform: str = "square_preview") -> None:
        """Set optimized params for platforms.

        :param platform: Platform for the video (instagram, twitter etc.)
        :return: None
        """

        width = OPTIMIZED_PARAMS.get(platform).get("width")
        height = OPTIMIZED_PARAMS.get(platform).get("height")

        self.width = width
        self.height = height

    def process_size_clip(self, clip, prop: float = 1):
        """Process size of the clip."""

        # Square size
        if self.width == self.height:
            clip = transform_square_size(clip)

        clip = clip.resize((self.width, self.height)).resize(prop)

        return clip

    def loop_clip(self, clip, bpm_video: float = None, crossfadein: float = None):
        """Loop main clip.

        So far the clip is looped for the whole video and then starts late

        :param bpm_video: BPM of the video
        :param crossfade: Duration of the crossfadein (in % of loops), if negative then the clip starts before the drop
        :param early_crossfadein:"""

        clip_duration = clip.duration
        start_offset = 0

        # Fadein

        if crossfadein:

            # We only want an offset when it's negative
            start_offset = min(crossfadein * clip_duration, 0)

        # Loop the clip
        nb_loops = (self.audioclip.duration // clip.duration) + 1

        clip = clip.loop(n=nb_loops).crossfadein(abs(crossfadein))

        # Drop

        if self.drop_beats:

            start = max((self.drop_beats) * self.duration - start_offset, 0)

            clip = clip.set_start(start, change_end=False)

        return clip

    def add_background_clip(self, path, sync=False):
        """Add background clips.

        :param path: Path to the background clip
        """

        clip = VideoFileClip(path, fps_source="fps")

        clip = self.process_size_clip(clip)

        if sync:

            clip = self.sync_bpm_clip(clip)

        # Loop the clip
        nb_loops = (self.audioclip.duration // clip.duration) + 1

        clip = clip.loop(n=nb_loops).set_position("center")

        self.background_clips.append(clip)

    def add_watermark(
        self, path="../design_assets/logo_transparent.gif", sync=True, prop_screen=0.22
    ):
        """Add background clips.

        :param path: Path to the background clip
        :param sync: Sync the watermark
        :param prop_screen: Proportion of the screen.
        """

        clip = VideoFileClip(path, fps_source="fps", has_mask=True)

        # The GIF is too large, we crop it
        # TO-DO: Generate a better GIF
        clip = clip.crop(
            x_center=int(clip.w / 2),
            y_center=int(clip.h / 2),
            width=clip.w * 0.45,
            height=clip.h * 0.55,
        )

        clip = clip.resize(width=prop_screen * self.width)

        # Removing black background

        # clip = moviepy.editor.vfx.mask_color(clip, color=[0, 0, 0], thr=20, s=10)

        if sync:

            clip = self.sync_bpm_clip(clip)

        # Loop the clip
        nb_loops = (self.audioclip.duration // clip.duration) + 1

        clip = clip.loop(n=nb_loops).set_position(
            (
                self.width - clip.w - self.width * 0.005,
                self.height - clip.h - self.height * 0.005,
            )
        )

        return clip

    def sync_bpm_clip(self, clip, bpm_video=None, optimize_loop=True):
        """Sync the video with the music.
        
        :param optimize_loop: Use the video as 1 loop each measure (False) or optimize it (True)"""

        # If the BPM of the video is known we might have to truncate it
        if bpm_video:
            video_loop_duration = 60 / bpm_video

        # Otherwise we assume it's a perfect loop
        else:
            bpm_video = round(60 / clip.duration, 0)
            video_loop_duration = clip.duration

        # limit duration = video_loop_duration when the bpm is not specified
        limit_duration = (clip.duration // video_loop_duration) * video_loop_duration
        clip = clip.set_duration(limit_duration)

        # Number of loops to fit with the smallest BPM unity of the music

        if optimize_loop:
            loops = self.music_bpm // bpm_video
        else:
            loops = 1

        # Factor to adjust speed
        factor = self.music_bpm / (bpm_video * loops)

        clip = clip.speedx(factor=factor)

        return clip

    def generate_video(self, cut=None):
        """Generate final video.

        :param cut: Truncate the video (in seconds)
        """

        clips = []

        # Background clips

        for clip in self.background_clips:

            clips.append(clip)

        # Main clip

        clips.append(self.main_clip.set_position("center"))

        # Text

        if self.text_assets.text_clips:

            for txt_clip in self.text_assets.text_clips:
                clips.append(txt_clip)

        # Watermark

        if self.watermark:

            clips.append(self.watermark)

        video = CompositeVideoClip(clips)

        video = video.set_audio(self.audioclip)

        # Cut de la video

        if cut:

            video = video.subclip(0, cut)

        return video


def transform_square_size(clip):
    """Resize the video to fit in a square.

    TO DO: not only square size

    :param clip: Clip to resize"""

    # Resize
    clip = clip.crop(
        x_center=int(clip.w / 2),
        y_center=int(clip.h / 2),
        width=min(clip.w, clip.h),
        height=min(clip.w, clip.h),
    )

    return clip
