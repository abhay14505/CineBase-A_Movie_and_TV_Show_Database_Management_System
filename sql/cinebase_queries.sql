USE cinebase;


-- 1. NESTED QUERY
-- Find users who have reviewed award-winning movies

-- This query finds all users who have written reviews for movies that have won at least one award
SELECT DISTINCT u.UserID, u.Username, u.Email, u.Country
FROM Users u
WHERE u.UserID IN (
    SELECT r.UserID
    FROM Review r
    WHERE r.MovieID IN (
        SELECT aw.MovieID
        FROM Award_Winner aw
        WHERE aw.MovieID IS NOT NULL
    )
);


-- 2. JOIN QUERY
-- Get detailed movie information with genres and average ratings

-- This query joins Movie, Movie_Genre, Genre, and Review tables to show comprehensive movie details
SELECT 
    m.MovieID,
    m.Title,
    m.ReleaseDate,
    m.Runtime,
    m.Language,
    m.Country,
    GROUP_CONCAT(DISTINCT g.Name ORDER BY g.Name SEPARATOR ', ') AS Genres,
    ROUND(AVG(r.Rating), 2) AS AverageRating,
    COUNT(DISTINCT r.ReviewID) AS TotalReviews
FROM Movie m
LEFT JOIN Movie_Genre mg ON m.MovieID = mg.MovieID
LEFT JOIN Genre g ON mg.GenreID = g.GenreID
LEFT JOIN Review r ON m.MovieID = r.MovieID
GROUP BY m.MovieID, m.Title, m.ReleaseDate, m.Runtime, m.Language, m.Country
ORDER BY AverageRating DESC;


-- 3. AGGREGATE QUERY
-- Get statistics on content by genre

-- This query provides aggregate statistics showing how many movies and shows exist per genre,
-- along with average ratings
SELECT 
    g.Name AS Genre,
    COUNT(DISTINCT mg.MovieID) AS TotalMovies,
    COUNT(DISTINCT sg.ShowID) AS TotalShows,
    COUNT(DISTINCT mg.MovieID) + COUNT(DISTINCT sg.ShowID) AS TotalContent,
    ROUND(AVG(r.Rating), 2) AS AverageRating,
    MAX(r.Rating) AS HighestRating,
    MIN(r.Rating) AS LowestRating
FROM Genre g
LEFT JOIN Movie_Genre mg ON g.GenreID = mg.GenreID
LEFT JOIN Show_Genre sg ON g.GenreID = sg.GenreID
LEFT JOIN Review r ON (r.MovieID = mg.MovieID OR r.ShowID = sg.ShowID)
GROUP BY g.GenreID, g.Name
ORDER BY TotalContent DESC;
