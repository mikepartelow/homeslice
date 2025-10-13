from core.tidal import track
from core import model

def test_track_score():
    assert track.score(
        model.Track(id=1, name="foo", artist="bar", album="baz",),
        model.Track(id=2, name="zip", artist="zap", album="zorp")
    ) == 0

    assert track.score(
        model.Track(id=1, name="foo", artist="bar", album="baz",),
        model.Track(id=2, name="foo", artist="zap", album="zorp")
    ) == 10

    assert track.score(
        model.Track(id=1, name="foo", artist="bar", album="baz",),
        model.Track(id=2, name="foo", artist="bar", album="zorp")
    ) == 20

    assert track.score(
        model.Track(id=1, name="foo", artist="bar", album="baz",),
        model.Track(id=2, name="foo", artist="bar", album="baz")
    ) == 30
