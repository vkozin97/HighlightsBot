CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE,
    username TEXT,
    nickname TEXT NOT NULL UNIQUE,
    current_state INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS timecodes (
    timecode_id INTEGER PRIMARY KEY,
    base_video_address TEXT NOT NULL,
    seconds_from_start INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS timecode_author_heros (
    timecode_id INTEGER,
    author_id INTEGER NOT NULL,
    hero_id INTEGER,
    anti_hero_id INTEGER,
    comment TEXT,
    FOREIGN KEY (timecode_id)
        REFERENCES timecodes (timecode_id)
            ON UPDATE CASCADE
            ON DELETE CASCADE,
    FOREIGN KEY (author_id)
        REFERENCES users (id)
            ON UPDATE CASCADE
            ON DELETE CASCADE,
    FOREIGN KEY (hero_id)
        REFERENCES users (id)
            ON UPDATE CASCADE
            ON DELETE CASCADE
    FOREIGN KEY (anti_hero_id)
        REFERENCES users (id)
            ON UPDATE CASCADE
            ON DELETE CASCADE
)