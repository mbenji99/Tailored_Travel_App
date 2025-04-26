-- tailored_travel.sql

-- 1) Create (or recreate) the database
DROP DATABASE IF EXISTS tailored_travel;
CREATE DATABASE tailored_travel
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci;
USE tailored_travel;

-- 2) Users
CREATE TABLE users (
  id            CHAR(36)     NOT NULL PRIMARY KEY
                  DEFAULT (UUID()),
  email         VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    DATETIME     NOT NULL
                 DEFAULT CURRENT_TIMESTAMP
                 ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 3) Profiles (1:1 with users)
CREATE TABLE profiles (
  user_id     CHAR(36)     NOT NULL PRIMARY KEY,
  username    VARCHAR(255) UNIQUE,
  created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at  DATETIME     NOT NULL
                 DEFAULT CURRENT_TIMESTAMP
                 ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_profiles_user
    FOREIGN KEY (user_id) REFERENCES users(id)
    ON DELETE CASCADE
) ENGINE=InnoDB;

-- 4) Trips
CREATE TABLE trips (
  id                   CHAR(36)      NOT NULL PRIMARY KEY
                       DEFAULT (UUID()),
  user_id              CHAR(36)      NOT NULL,
  budget               DECIMAL(10,2) NOT NULL
                       CHECK (budget > 0),
  remaining_budget     DECIMAL(10,2) NOT NULL,
  destination          VARCHAR(255),
  weather_preference   VARCHAR(255),
  environment_preference VARCHAR(255),
  activity_preference  VARCHAR(255),
  status               ENUM('planning','booked','completed','cancelled')
                       NOT NULL DEFAULT 'planning',
  created_at           DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at           DATETIME      NOT NULL
                       DEFAULT CURRENT_TIMESTAMP
                       ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_trips_user
    FOREIGN KEY (user_id) REFERENCES users(id)
    ON DELETE CASCADE
) ENGINE=InnoDB;

-- 5) Itineraries
CREATE TABLE itineraries (
  id          CHAR(36)      NOT NULL PRIMARY KEY
               DEFAULT (UUID()),
  trip_id     CHAR(36)      NOT NULL,
  day_number  INT           NOT NULL,
  activity    VARCHAR(255)  NOT NULL,
  cost        DECIMAL(10,2) NOT NULL DEFAULT 0,
  created_at  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at  DATETIME      NOT NULL
               DEFAULT CURRENT_TIMESTAMP
               ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_itins_trip
    FOREIGN KEY (trip_id) REFERENCES trips(id)
    ON DELETE CASCADE,
  CONSTRAINT uq_itins_trip_day UNIQUE (trip_id, day_number)
) ENGINE=InnoDB;
