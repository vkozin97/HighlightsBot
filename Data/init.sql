CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    nickname TEXT NOT NULL UNIQUE,
    current_state INTEGER NOT NULL DEFAULT 1,
    current_video TEXT NOT NULL DEFAULT '',
    current_timecode TEXT NOT NULL DEFAULT '',
    current_heroes TEXT NOT NULL DEFAULT '',
    current_antiheroes TEXT NOT NULL DEFAULT '',
    current_comment TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS original_videos (
    video_id INTEGER PRIMARY KEY,
    video_path TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS timecodes (
    timecode_id INTEGER PRIMARY KEY,
    original_video_id INTEGER NOT NULL,
    timecode TEXT NOT NULL,  -- FORMAT '11:43'
    FOREIGN KEY (original_video_id)
        REFERENCES original_videos (video_id)
            ON UPDATE CASCADE
            ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS timecode_author_heros (
    timecode_id INTEGER PRIMARY KEY,
    author_id INTEGER NOT NULL,
    hero_id INTEGER,
    anti_hero_id INTEGER,
    comment TEXT,
    FOREIGN KEY (timecode_id)
        REFERENCES timecodes (timecode_id)
            ON UPDATE CASCADE
            ON DELETE CASCADE,
    FOREIGN KEY (author_id)
        REFERENCES users (user_id)
            ON UPDATE CASCADE
            ON DELETE CASCADE,
    FOREIGN KEY (hero_id)
        REFERENCES users (user_id)
            ON UPDATE CASCADE
            ON DELETE CASCADE,
    FOREIGN KEY (anti_hero_id)
        REFERENCES users (user_id)
            ON UPDATE CASCADE
            ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS highlights (
    highlight_id INTEGER PRIMARY KEY,
    original_video_id INTEGER NOT NULL,
    start_second INTEGER NOT NULL,
    end_second INTEGER NOT NULL,
    highlight_local_path TEXT,
    highlight_server_path TEXT,
    public_link TEXT,
    FOREIGN KEY (original_video_id)
        REFERENCES original_videos (video_id)
            ON UPDATE CASCADE
            ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS highlight2timecodes (
    relation_id INTEGER PRIMARY KEY,
    highlight_id INTEGER NOT NULL,
    timecode_id INTEGER NOT NULL UNIQUE,
    FOREIGN KEY (highlight_id)
        REFERENCES highlights (highlight_id)
            ON UPDATE CASCADE
            ON DELETE CASCADE,
    FOREIGN KEY (timecode_id)
        REFERENCES timecodes (timecode_id)
            ON UPDATE CASCADE
            ON DELETE CASCADE
);