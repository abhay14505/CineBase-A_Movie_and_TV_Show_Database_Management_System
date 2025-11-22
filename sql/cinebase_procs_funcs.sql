USE cinebase;

DELIMITER //
CREATE PROCEDURE AddMovieWithGenre (
    IN movieTitle VARCHAR(200),
    IN releaseDate DATE,
    IN runtime INT,
    IN languageName VARCHAR(50),
    IN countryName VARCHAR(50),
    IN genreName VARCHAR(50)
)
BEGIN
    DECLARE newMovieID INT;
    DECLARE genreID INT;

    INSERT INTO Movie (Title, ReleaseDate, Runtime, Language, Country)
    VALUES (movieTitle, releaseDate, runtime, languageName, countryName);
    SET newMovieID = LAST_INSERT_ID();

    SELECT GenreID INTO genreID FROM Genre WHERE Name = genreName LIMIT 1;

    IF genreID IS NOT NULL THEN
        INSERT INTO Movie_Genre (MovieID, GenreID) VALUES (newMovieID, genreID);
    ELSE
        INSERT INTO Genre (Name) VALUES (genreName);
        INSERT INTO Movie_Genre (MovieID, GenreID) VALUES (newMovieID, LAST_INSERT_ID());
    END IF;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE GetAverageRating (
    IN movieID INT,
    IN showID INT
)
BEGIN
    IF movieID IS NOT NULL THEN
        SELECT AVG(Rating) AS AvgRating FROM Review WHERE MovieID = movieID;
    ELSEIF showID IS NOT NULL THEN
        SELECT AVG(Rating) AS AvgRating FROM Review WHERE ShowID = showID;
    ELSE
        SELECT 'Provide either movieID or showID' AS Message;
    END IF;
END //
DELIMITER ;

DELIMITER //
CREATE FUNCTION GetUserReviewCount(user_id INT)
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE total INT;
    SELECT COUNT(*) INTO total FROM Review WHERE UserID = user_id;
    RETURN total;
END //
DELIMITER ;

DELIMITER //
CREATE FUNCTION CalculateAge(birth_date DATE)
RETURNS INT
DETERMINISTIC
BEGIN
    RETURN TIMESTAMPDIFF(YEAR, birth_date, CURDATE());
END //
DELIMITER ;
