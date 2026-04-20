CREATE DATABASE IF NOT EXISTS huskybites;
USE huskybites;

DROP TABLE IF EXISTS Restaurant_Dietary_Tag;
DROP TABLE IF EXISTS Activity_Metric;
DROP TABLE IF EXISTS Admin_Action;
DROP TABLE IF EXISTS Leaderboard_Entry;
DROP TABLE IF EXISTS Wait_Time_Record;
DROP TABLE IF EXISTS Crowd_Level_Record;
DROP TABLE IF EXISTS Favorite;
DROP TABLE IF EXISTS Review;
DROP TABLE IF EXISTS Restaurant;
DROP TABLE IF EXISTS Dietary_Tag;
DROP TABLE IF EXISTS Neighborhood;
DROP TABLE IF EXISTS Cuisine;
DROP TABLE IF EXISTS User;

CREATE TABLE User (
                      user_id INT AUTO_INCREMENT PRIMARY KEY,
                      username VARCHAR(100) NOT NULL,
                      role VARCHAR(50),
                      allergy_preference VARCHAR(255),
                      dietary_preference VARCHAR(255)
);

CREATE TABLE Cuisine (
                         cuisine_id INT AUTO_INCREMENT PRIMARY KEY,
                         cuisine_name VARCHAR(100) NOT NULL
);

CREATE TABLE Neighborhood (
                              neighborhood_id INT AUTO_INCREMENT PRIMARY KEY,
                              neighborhood_name VARCHAR(100) NOT NULL
);

CREATE TABLE Dietary_Tag (
                             dietary_tag_id INT AUTO_INCREMENT PRIMARY KEY,
                             dietary_tag_name VARCHAR(100) NOT NULL,
                             dietary_tag_category VARCHAR(100)
);

CREATE TABLE Restaurant (
                            restaurant_id INT AUTO_INCREMENT PRIMARY KEY,
                            cuisine_id INT,
                            neighborhood_id INT,
                            name VARCHAR(150) NOT NULL,
                            location VARCHAR(255),
                            status VARCHAR(50),
                            hours VARCHAR(100),
                            date DATE,
                            last_updated DATE,
                            halal_certified BOOLEAN DEFAULT FALSE,
                            price_range FLOAT,
                            avg_rating FLOAT,
                            dist_from_campus FLOAT,
                            atmosphere VARCHAR(100),
                            local_fav_tag VARCHAR(100),
                            student_fav_tag VARCHAR(100),
                            dietary_options VARCHAR(255),
                            working_hours VARCHAR(100),
                            FOREIGN KEY (cuisine_id) REFERENCES Cuisine(cuisine_id),
                            FOREIGN KEY (neighborhood_id) REFERENCES Neighborhood(neighborhood_id)
);

CREATE TABLE Review (
                        review_id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT,
                        restaurant_id INT,
                        rating FLOAT,
                        review_text TEXT,
                        review_date DATE,
                        review_status VARCHAR(50),
                        FOREIGN KEY (user_id) REFERENCES User(user_id),
                        FOREIGN KEY (restaurant_id) REFERENCES Restaurant(restaurant_id)
);

CREATE TABLE Favorite (
                          favorite_id INT AUTO_INCREMENT PRIMARY KEY,
                          user_id INT,
                          restaurant_id INT,
                          saved_date DATE,
                          FOREIGN KEY (user_id) REFERENCES User(user_id),
                          FOREIGN KEY (restaurant_id) REFERENCES Restaurant(restaurant_id)
);

CREATE TABLE Crowd_Level_Record (
                                    crowd_record_id INT AUTO_INCREMENT PRIMARY KEY,
                                    restaurant_id INT,
                                    crowd_level VARCHAR(50),
                                    recorded_at DATETIME,
                                    FOREIGN KEY (restaurant_id) REFERENCES Restaurant(restaurant_id)
);

CREATE TABLE Wait_Time_Record (
                                  wait_time_id INT AUTO_INCREMENT PRIMARY KEY,
                                  restaurant_id INT,
                                  estimated_wait_time INT,
                                  wait_minutes INT,
                                  recorded_at DATETIME,
                                  updated_time DATETIME,
                                  day_type VARCHAR(50),
                                  FOREIGN KEY (restaurant_id) REFERENCES Restaurant(restaurant_id)
);

CREATE TABLE Leaderboard_Entry (
                                   entry_id INT AUTO_INCREMENT PRIMARY KEY,
                                   restaurant_id INT,
                                   rank_num INT,
                                   score_avg FLOAT,
                                   FOREIGN KEY (restaurant_id) REFERENCES Restaurant(restaurant_id)
);

CREATE TABLE Admin_Action (
                              action_id INT AUTO_INCREMENT PRIMARY KEY,
                              user_id INT,
                              target_id INT,
                              action_type VARCHAR(100),
                              action_timestamp DATETIME,
                              target_entity VARCHAR(100),
                              FOREIGN KEY (user_id) REFERENCES User(user_id)
);

CREATE TABLE Activity_Metric (
                                 metric_id INT AUTO_INCREMENT PRIMARY KEY,
                                 metric_date DATE,
                                 reviews_count INT,
                                 active_users_count INT,
                                 restaurant_count INT
);

CREATE TABLE Restaurant_Dietary_Tag (
                                        restaurant_id INT,
                                        dietary_tag_id INT,
                                        UNIQUE (restaurant_id, dietary_tag_id),
                                        FOREIGN KEY (restaurant_id) REFERENCES Restaurant(restaurant_id),
                                        FOREIGN KEY (dietary_tag_id) REFERENCES Dietary_Tag(dietary_tag_id)
);