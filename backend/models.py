from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from utils.database import Base

# playlists-tracks table
playlist_tracks = Table(
    "playlist_tracks",
    Base.metadata,
    Column("playlist_id", String, ForeignKey("playlists.id", ondelete="CASCADE")),
    Column("track_id", Integer, ForeignKey("tracks.id", ondelete="CASCADE")),
)


# track table
class Track(Base):
    __tablename__ = "tracks"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    artist = Column(String)
    album = Column(String)
    duration = Column(Integer)
    explicit = Column(Boolean)
    audio_quality = Column(String)
    isrc = Column(String)
    available = Column(Boolean)
    favorite = Column(Boolean, default=False)
    date_added = Column(String)
    first_seen_at = Column(String)
    last_seen_at = Column(String)
    playlists = relationship(
        "Playlist", secondary=playlist_tracks, back_populates="tracks"
    )


# playlists table
class Playlist(Base):
    __tablename__ = "playlists"
    id = Column(String, primary_key=True)
    name = Column(String)
    first_seen_at = Column(String)
    last_seen_at = Column(String)
    tracks = relationship(
        "Track", secondary=playlist_tracks, back_populates="playlists"
    )
