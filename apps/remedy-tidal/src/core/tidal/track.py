"""Tidal track helpers."""

import tidalapi  # type: ignore[import-untyped]

from .. import model


def scrub(ot: model.Track) -> model.Track:
    """Remove attribute string fragments that inhibit matching, e.g. '(Remastered)'."""
    return model.Track(
        id=ot.id,
        name=ot.name,
        artist=ot.artist,
        album=ot.album.replace(" (Remastered)", ""),
        artists=[],
        available=ot.available,
    )


def score(candidate: model.Track, target: model.Track) -> int:
    """Return a match score representing alikeness of two Tracks. Higher score = more alike."""
    if candidate.name != target.name:
        return 0

    s = 10

    if candidate.artist == target.artist:
        s += 10

    if candidate.album == target.album:
        s += 10

    return s


def find(session: tidalapi.Session, target: model.Track) -> model.Track | None:
    """Query Tidal to find the closest matching track to the target.

    Use simple weighted comparison of selected track attributes.
    """
    target = scrub(target)

    search_terms = [f"{target.artist} {target.name}", target.name]

    candidates = []

    for search_term in search_terms:
        results = session.search(search_term, models=[tidalapi.media.Track])

        for result in results["tracks"]:
            candidate = scrub(model.Track.from_tidal(result))

            if cscore := score(candidate, target) > 0:
                candidates.append((candidate, cscore))

    if len(candidates) == 0:
        return None

    return sorted(candidates, key=lambda c: -c[1])[0][0]
