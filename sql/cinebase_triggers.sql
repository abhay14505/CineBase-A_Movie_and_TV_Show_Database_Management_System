USE cinebase;

CREATE TABLE Review_Log (
    LogID INT AUTO_INCREMENT PRIMARY KEY,
    ReviewID INT,
    UserID INT,
    MovieID INT,
    ShowID INT,
    Action VARCHAR(50),
    ActionTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DELIMITER //
CREATE TRIGGER after_review_insert
AFTER INSERT ON Review
FOR EACH ROW
BEGIN
    INSERT INTO Review_Log (ReviewID, UserID, MovieID, ShowID, Action)
    VALUES (NEW.ReviewID, NEW.UserID, NEW.MovieID, NEW.ShowID, 'Review Added');
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER before_user_delete
BEFORE DELETE ON Users
FOR EACH ROW
BEGIN
    IF (SELECT COUNT(*) FROM Review WHERE UserID = OLD.UserID) > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Cannot delete user with existing reviews';
    END IF;
END //
DELIMITER ;
