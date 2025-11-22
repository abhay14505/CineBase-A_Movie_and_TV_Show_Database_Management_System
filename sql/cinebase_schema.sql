CREATE DATABASE cinebase;
USE cinebase;

-- USER entity
CREATE TABLE Users (
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    Username VARCHAR(50) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    Password VARCHAR(100) NOT NULL,
    DateOfBirth DATE,
    Country VARCHAR(50) DEFAULT 'Unknown',
    JoinDate DATE DEFAULT (CURRENT_DATE)
);

-- MOVIE entity
CREATE TABLE Movie (
    MovieID INT AUTO_INCREMENT PRIMARY KEY,
    Title VARCHAR(200) NOT NULL,
    ReleaseDate DATE,
    Runtime INT,
    Language VARCHAR(50) DEFAULT 'English',
    Country VARCHAR(50) DEFAULT 'Unknown'
);

-- TV_SHOW entity
CREATE TABLE TV_Show (
    ShowID INT AUTO_INCREMENT PRIMARY KEY,
    Title VARCHAR(200) NOT NULL,
    StartDate DATE,
    EndDate DATE
);

-- SEASON entity
CREATE TABLE Season (
    SeasonID INT AUTO_INCREMENT PRIMARY KEY,
    ShowID INT NOT NULL,
    SeasonNumber INT NOT NULL,
    FOREIGN KEY (ShowID) REFERENCES TV_Show(ShowID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- EPISODE entity
CREATE TABLE Episode (
    EpisodeID INT AUTO_INCREMENT PRIMARY KEY,
    SeasonID INT NOT NULL,
    Title VARCHAR(200) NOT NULL,
    FOREIGN KEY (SeasonID) REFERENCES Season(SeasonID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- PERSON entity
CREATE TABLE Person (
    PersonID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Birthdate DATE
);

-- GENRE entity
CREATE TABLE Genre (
    GenreID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(50) NOT NULL
);

-- AWARD entity
CREATE TABLE Award (
    AwardID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL
);

-- ROLE (Associative Entity: Person–Movie/Show)
CREATE TABLE Role (
    RoleID INT AUTO_INCREMENT PRIMARY KEY,
    RoleType VARCHAR(50) NOT NULL,
    PersonID INT NOT NULL,
    MovieID INT NULL,
    ShowID INT NULL,
    FOREIGN KEY (PersonID) REFERENCES Person(PersonID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (MovieID) REFERENCES Movie(MovieID)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    FOREIGN KEY (ShowID) REFERENCES TV_Show(ShowID)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

-- REVIEW entity (User–Movie/Show)
CREATE TABLE Review (
    ReviewID INT AUTO_INCREMENT PRIMARY KEY,
    Rating INT CHECK (Rating BETWEEN 1 AND 10),
    UserID INT NOT NULL,
    MovieID INT NULL,
    ShowID INT NULL,
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (MovieID) REFERENCES Movie(MovieID)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    FOREIGN KEY (ShowID) REFERENCES TV_Show(ShowID)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

-- AWARD_WINNER (Associative Entity)
CREATE TABLE Award_Winner (
    WinnerID INT AUTO_INCREMENT PRIMARY KEY,
    AwardID INT NOT NULL,
    PersonID INT NULL,
    MovieID INT NULL,
    ShowID INT NULL,
    FOREIGN KEY (AwardID) REFERENCES Award(AwardID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (PersonID) REFERENCES Person(PersonID)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    FOREIGN KEY (MovieID) REFERENCES Movie(MovieID)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    FOREIGN KEY (ShowID) REFERENCES TV_Show(ShowID)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

-- MOVIE_GENRE (Associative Entity)
CREATE TABLE Movie_Genre (
    MovieGenreID INT AUTO_INCREMENT PRIMARY KEY,
    MovieID INT NOT NULL,
    GenreID INT NOT NULL,
    FOREIGN KEY (MovieID) REFERENCES Movie(MovieID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (GenreID) REFERENCES Genre(GenreID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    UNIQUE (MovieID, GenreID)
);

-- SHOW_GENRE (Associative Entity)
CREATE TABLE Show_Genre (
    ShowGenreID INT AUTO_INCREMENT PRIMARY KEY,
    ShowID INT NOT NULL,
    GenreID INT NOT NULL,
    FOREIGN KEY (ShowID) REFERENCES TV_Show(ShowID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (GenreID) REFERENCES Genre(GenreID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    UNIQUE (ShowID, GenreID)
);

-- INSERT DATA
INSERT INTO Users (Username, Email, Password, DateOfBirth, Country, JoinDate) VALUES
('john_doe', 'john@example.com', 'pass123', '1990-05-14', 'USA', '2024-01-01'),
('alice_smith', 'alice@example.com', 'alicepass', '1995-08-20', 'UK', '2024-02-15'),
('mark_taylor', 'mark@example.com', 'markpass', '1988-03-10', 'Canada', '2024-03-01'),
('emma_wilson', 'emma@example.com', 'emmapass', '2000-07-25', 'Australia', '2024-03-20'),
('david_lee', 'david@example.com', 'davidpass', '1992-09-12', 'USA', '2024-04-10');

INSERT INTO Movie (Title, ReleaseDate, Runtime, Language, Country) VALUES
('Inception', '2010-07-16', 148, 'English', 'USA'),
('Parasite', '2019-05-30', 132, 'Korean', 'South Korea'),
('Interstellar', '2014-11-07', 169, 'English', 'USA'),
('The Dark Knight', '2008-07-18', 152, 'English', 'USA'),
('Spirited Away', '2001-07-20', 125, 'Japanese', 'Japan');

INSERT INTO TV_Show (Title, StartDate, EndDate) VALUES
('Breaking Bad', '2008-01-20', '2013-09-29'),
('Stranger Things', '2016-07-15', NULL),
('Game of Thrones', '2011-04-17', '2019-05-19'),
('The Crown', '2016-11-04', NULL),
('Friends', '1994-09-22', '2004-05-06');

INSERT INTO Season (ShowID, SeasonNumber) VALUES
(1, 1), (1, 2), (2, 1), (3, 1), (5, 1);

INSERT INTO Episode (SeasonID, Title) VALUES
(1, 'Pilot'),
(1, 'Cat’s in the Bag...'),
(2, 'Seven Thirty-Seven'),
(3, 'Chapter One: The Vanishing of Will Byers'),
(5, 'The One Where Monica Gets a Roommate');

INSERT INTO Person (Name, Birthdate) VALUES
('Leonardo DiCaprio', '1974-11-11'),
('Bong Joon-ho', '1969-09-14'),
('Bryan Cranston', '1956-03-07'),
('Millie Bobby Brown', '2004-02-19'),
('Emma Watson', '1990-04-15');

INSERT INTO Genre (Name) VALUES
('Action'), ('Thriller'), ('Drama'), ('Sci-Fi'), ('Fantasy');

INSERT INTO Award (Name) VALUES
('Academy Award'), ('Golden Globe'), ('Emmy Award'), ('BAFTA'), ('Cannes Palm d’Or');

INSERT INTO Role (RoleType, PersonID, MovieID, ShowID) VALUES
('Actor', 1, 1, NULL),
('Director', 2, 2, NULL),
('Actor', 3, NULL, 1),
('Actor', 4, NULL, 2),
('Actor', 5, NULL, 5);

INSERT INTO Review (Rating, UserID, MovieID, ShowID) VALUES
(9, 1, 1, NULL),
(10, 2, 2, NULL),
(8, 3, NULL, 1),
(9, 4, NULL, 2),
(7, 5, NULL, 5);

INSERT INTO Award_Winner (AwardID, PersonID, MovieID, ShowID) VALUES
(1, 2, 2, NULL),
(3, 3, NULL, 1),
(2, 1, 1, NULL),
(4, 5, NULL, 5),
(5, NULL, 5, NULL);

INSERT INTO Movie_Genre (MovieID, GenreID) VALUES
(1, 1), (1, 4),
(2, 3),
(3, 4), (3, 5),
(5, 5);

INSERT INTO Show_Genre (ShowID, GenreID) VALUES
(1, 3),
(2, 2), (2, 4),
(3, 5),
(5, 3);
