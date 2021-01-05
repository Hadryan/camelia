from moviepy.editor import *

TEXT_PRESETS = {
    "fancy": {
        "artist": {"color": "white", "font": "Helvetica"},
        "track": {"color": "Helvetica", "font": "Helvetica-bold"},
    }
}


class TextAssets:
    def __init__(width: float, height: float, artist_name: str, track_name: str):
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

        # Generated clips
        self.text_clips = None

    def generate_clips(self, prop_screen, graphic_chart="fancy"):
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

        self.text_clips = [txtClip_artist, txtClip_track]
