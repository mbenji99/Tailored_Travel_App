-- Create users table (since MySQL does not have auth.users like Supabase)
CREATE TABLE users (
  id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create profiles table
CREATE TABLE profiles (
  id CHAR(36) PRIMARY KEY,
  username VARCHAR(255) UNIQUE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create trips table
CREATE TABLE trips (
  id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  user_id CHAR(36) NOT NULL,
  budget DECIMAL(10,2) NOT NULL CHECK (budget > 0),
  remaining_budget DECIMAL(10,2) NOT NULL,
  destination VARCHAR(255),
  weather_preference VARCHAR(255),
  environment_preference VARCHAR(255),
  activity_preference VARCHAR(255),
  status ENUM('planning', 'booked', 'completed', 'cancelled') DEFAULT 'planning',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create itineraries table
CREATE TABLE itineraries (
  id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  trip_id CHAR(36) NOT NULL,
  day_number INT NOT NULL,
  activity VARCHAR(255) NOT NULL,
  cost DECIMAL(10,2) NOT NULL DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE
);

-- Create trigger to update updated_at timestamp
DELIMITER //
CREATE TRIGGER update_profiles_updated_at
BEFORE UPDATE ON profiles
FOR EACH ROW
BEGIN
  SET NEW.updated_at = CURRENT_TIMESTAMP;
END;
//

CREATE TRIGGER update_trips_updated_at
BEFORE UPDATE ON trips
FOR EACH ROW
BEGIN
  SET NEW.updated_at = CURRENT_TIMESTAMP;
END;
//

CREATE TRIGGER update_itineraries_updated_at
BEFORE UPDATE ON itineraries
FOR EACH ROW
BEGIN
  SET NEW.updated_at = CURRENT_TIMESTAMP;
END;
//
DELIMITER ;
