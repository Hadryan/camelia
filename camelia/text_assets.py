from moviepy.editor import *

TEXT_PRESETS = {
    "fancy": {
        "artist": {"color": "white", "font": "Helvetica"},
        "track": {"color": "LightPink", "font": "Helvetica-bold"},
    }
}


class TextAssets:
    def __init__(
        self,
        width: float,
        height: float,
        artist_name: str,
        track_name: str,
        duration: float,
        drop_beats,
    ):
        """Init TextAssets.

        :param width: Width of the video
        :param height: Height of the video
        :param artist_name: Artist name
        :param track_name: Track name
        """

        # Attributes to generate text assets
        self.width = width
        self.height = height
        self.artist_name = artist_name
        self.track_name = track_name
        self.duration = duration
        self.drop_beats = drop_beats

        # Generated clips
        self.text_clips = None

    def generate_clips(self, prop_screen=0.4, graphic_chart="fancy"):
        """Generate text clips."""

        textwidth = prop_screen * self.width

        txtClip_artist = TextClip(
            self.artist_name,
            color=TEXT_PRESETS[graphic_chart]["artist"]["color"],
            font=TEXT_PRESETS[graphic_chart]["artist"]["font"],
            kerning=5,
            size=(textwidth, None),
        )

        txtClip_track = TextClip(
            self.track_name,
            color=TEXT_PRESETS[graphic_chart]["track"]["color"],
            font=TEXT_PRESETS[graphic_chart]["track"]["font"],
            kerning=5,
            size=(textwidth, None),
        )

        txt_artist_pos = (self.width / 2 - txtClip_artist.w / 2, 0.1 * self.height)

        offset_y = txtClip_artist.h + txt_artist_pos[1] + 0.1

        txt_track_pos = (self.width / 2 - txtClip_track.w / 2, offset_y)

        # Position

        txtClip_artist = txtClip_artist.set_position(txt_artist_pos)

        txtClip_track = txtClip_track.set_position(txt_track_pos)

        self.text_clips = [txtClip_artist, txtClip_track]

    def set_timing(self, mode="always"):

        clips_to_replace = []

        if mode == "before_drop":

            start = 0

            txt_duration = self.duration * 4

            if self.drop_beats:
                txt_duration = self.duration * self.drop_beats

            duration = txt_duration

        elif mode == "always":

            start = 0
            duration = self.total_duration

        else:

            raise ValueError(f"The mode {mode} does not exist.")

        for clip in self.text_clips:

            clip = clip.set_start(start).set_duration(duration)
            clips_to_replace.append(clip)

        self.text_clips = clips_to_replace
