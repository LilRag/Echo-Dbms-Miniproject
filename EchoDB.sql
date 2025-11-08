-- Create and use the database
CREATE DATABASE IF NOT EXISTS ECHO;
USE ECHO;

-- Drop tables in reverse order of creation
DROP TABLE IF EXISTS `post_views`, `post_categories`, `post_likes`, `bookmarks`, `collections`, `follows`, `comments`, `categories`, `posts`, `users`;

-- =================================================================
--                          TABLES
-- =================================================================

-- Users Table
CREATE TABLE `users` (
  `user_id` INT AUTO_INCREMENT PRIMARY KEY,
  `username` VARCHAR(50) NOT NULL UNIQUE,
  `email` VARCHAR(255) NOT NULL UNIQUE,
  `hashed_password` VARCHAR(255) NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Posts Table (CORRECTED: Added count columns directly)
CREATE TABLE `posts` (
  `post_id` INT AUTO_INCREMENT PRIMARY KEY,
  `title` VARCHAR(255) NOT NULL,
  `content` TEXT NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `user_id` INT NOT NULL,
  `likes_count` INT NOT NULL DEFAULT 0,
  `views_count` INT NOT NULL DEFAULT 0,
  `comments_count` INT NOT NULL DEFAULT 0,
  INDEX `idx_user_id` (`user_id`),
  FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Comments Table
CREATE TABLE `comments` (
  `comment_id` INT AUTO_INCREMENT PRIMARY KEY,
  `content` TEXT NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `user_id` INT NOT NULL,
  `post_id` INT NOT NULL,
  `parent_id` INT DEFAULT NULL,
  INDEX `idx_user_id` (`user_id`),
  INDEX `idx_post_id` (`post_id`),
  FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`) ON DELETE CASCADE,
  FOREIGN KEY (`post_id`) REFERENCES `posts`(`post_id`) ON DELETE CASCADE,
  FOREIGN KEY (`parent_id`) REFERENCES `comments`(`comment_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Categories Table
CREATE TABLE `categories` (
  `category_id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Collections Table (for Bookmarks)
CREATE TABLE `collections` (
  `collection_id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(100) NOT NULL,
  `user_id` INT NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY `unique_user_collection` (`user_id`, `name`),
  FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Bookmarks Table
CREATE TABLE `bookmarks` (
  `user_id` INT NOT NULL,
  `post_id` INT NOT NULL,
  `collection_id` INT NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`, `post_id`, `collection_id`),
  FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`) ON DELETE CASCADE,
  FOREIGN KEY (`post_id`) REFERENCES `posts`(`post_id`) ON DELETE CASCADE,
  FOREIGN KEY (`collection_id`) REFERENCES `collections`(`collection_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Follows Table
CREATE TABLE `follows` (
  `follower_id` INT NOT NULL,
  `followed_id` INT NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`follower_id`, `followed_id`),
  FOREIGN KEY (`follower_id`) REFERENCES `users`(`user_id`) ON DELETE CASCADE,
  FOREIGN KEY (`followed_id`) REFERENCES `users`(`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Post Likes Table
CREATE TABLE `post_likes` (
  `user_id` INT NOT NULL,
  `post_id` INT NOT NULL,
  PRIMARY KEY (`user_id`, `post_id`),
  FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`) ON DELETE CASCADE,
  FOREIGN KEY (`post_id`) REFERENCES `posts`(`post_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Post Categories Table
CREATE TABLE `post_categories` (
  `post_id` INT NOT NULL,
  `category_id` INT NOT NULL,
  PRIMARY KEY (`post_id`, `category_id`),
  FOREIGN KEY (`post_id`) REFERENCES `posts`(`post_id`) ON DELETE CASCADE,
  FOREIGN KEY (`category_id`) REFERENCES `categories`(`category_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Post Views Table
CREATE TABLE `post_views` (
  `view_id` INT AUTO_INCREMENT PRIMARY KEY,
  `viewed_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `user_id` INT DEFAULT NULL,
  `post_id` INT NOT NULL,
  INDEX `idx_user_id` (`user_id`),
  INDEX `idx_post_id` (`post_id`),
  FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`) ON DELETE SET NULL,
  FOREIGN KEY (`post_id`) REFERENCES `posts`(`post_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =================================================================
--                          TRIGGERS
-- =================================================================

DELIMITER //

-- Triggers for Post Likes Count
CREATE TRIGGER `trg_after_like_insert`
AFTER INSERT ON `post_likes`
FOR EACH ROW
BEGIN
    UPDATE `posts` SET `likes_count` = `likes_count` + 1 WHERE `post_id` = NEW.post_id;
END;
//

CREATE TRIGGER `trg_after_like_delete`
AFTER DELETE ON `post_likes`
FOR EACH ROW
BEGIN
    UPDATE `posts` SET `likes_count` = `likes_count` - 1 WHERE `post_id` = OLD.post_id;
END; //

-- Triggers for Post Comments Count
CREATE TRIGGER `trg_after_comment_insert`
AFTER INSERT ON `comments`
FOR EACH ROW
BEGIN
    UPDATE `posts` SET `comments_count` = `comments_count` + 1 WHERE `post_id` = NEW.post_id;
END; //

CREATE TRIGGER `trg_after_comment_delete`
AFTER DELETE ON `comments`
FOR EACH ROW
BEGIN
    UPDATE `posts` SET `comments_count` = `comments_count` - 1 WHERE `post_id` = OLD.post_id;
END; //

DELIMITER ;

-- =================================================================
--                          INSERT DATA
-- =================================================================

-- Insert Users
INSERT INTO `users` (`username`, `email`, `hashed_password`) VALUES
('alice', 'alice@example.com', 'hashed_password_1'),
('bob', 'bob@example.com', 'hashed_password_2'),
('charlie', 'charlie@example.com', 'hashed_password_3');

-- Insert Posts
INSERT INTO `posts` (`title`, `content`, `user_id`) VALUES
('Introduction to FastAPI', 'FastAPI is a modern, fast web framework for building APIs with Python 3.7+ based on standard Python type hints.', 1),
('MySQL Best Practices', 'When designing a MySQL database, it is crucial to normalize your data and use appropriate indexes.', 2),
('A Guide to REST APIs', 'REST is an architectural style that defines a set of constraints for creating web services.', 1);

-- Insert Comments (Triggers will fire)
INSERT INTO `comments` (`content`, `user_id`, `post_id`) VALUES
('Great article, very helpful!', 2, 1),
('Thanks for sharing, Alice!', 3, 1),
('I have a question about indexing.', 1, 2);

-- Insert a threaded comment (Triggers will fire)
INSERT INTO `comments` (`content`, `user_id`, `post_id`, `parent_id`) VALUES
('You are welcome!', 1, 1, 1);

-- Insert Post Likes (Triggers will fire)
INSERT INTO `post_likes` (`user_id`, `post_id`) VALUES
(1, 2), -- Alice likes Bob's post
(2, 1), -- Bob likes Alice's first post
(3, 1), -- Charlie also likes Alice's first post
(3, 2); -- Charlie also likes Bob's post

-- Insert Follows
INSERT INTO `follows` (`follower_id`, `followed_id`) VALUES
(1, 2), -- Alice follows Bob
(2, 1), -- Bob follows Alice
(3, 1); -- Charlie follows Alice

-- Insert Categories
INSERT INTO `categories` (`name`) VALUES
('Python'),
('Web Development'),
('Databases'),
('Tutorials');

-- Link Posts to Categories
INSERT INTO `post_categories` (`post_id`, `category_id`) VALUES
(1, 1), -- FastAPI post is in 'Python'
(1, 2), -- FastAPI post is also in 'Web Development'
(2, 3), -- MySQL post is in 'Databases'
(3, 2), -- REST API post is in 'Web Development'
(3, 4); -- REST API post is also in 'Tutorials'

-- =================================================================
--                          PROCEDURES
-- =================================================================

DELIMITER //

-- Procedure to get a list of posts
CREATE PROCEDURE `get_all_posts`(IN p_limit INT, IN p_offset INT)
BEGIN
    SELECT
        p.post_id, p.title, p.content, p.created_at,
        p.user_id, p.likes_count, p.views_count, p.comments_count,
        u.username, u.email AS user_email, u.created_at AS user_created_at
    FROM `posts` p
    JOIN `users` u ON p.user_id = u.user_id
    ORDER BY p.created_at DESC
    LIMIT p_limit
    OFFSET p_offset;
END; //

-- Procedure to get details for a single post
CREATE PROCEDURE `get_post_details`(IN p_post_id INT, IN p_requesting_user_id INT)
BEGIN
    -- Increment the view count for this post
    -- (We'll also log this in the post_views table for analytics)
    INSERT INTO `post_views` (post_id, user_id) VALUES (p_post_id, p_requesting_user_id);
    UPDATE `posts` SET `views_count` = `views_count` + 1 WHERE `post_id` = p_post_id;

    -- Return the detailed post data
    SELECT
        p.post_id, p.title, p.content, p.created_at,
        p.user_id, p.likes_count, p.views_count, p.comments_count,
        u.username, u.email AS user_email,
        (SELECT COUNT(1) FROM `post_likes` pl WHERE pl.post_id = p.post_id AND pl.user_id = p_requesting_user_id) > 0 AS is_liked_by_user
    FROM `posts` p
    JOIN `users` u ON p.user_id = u.user_id
    WHERE p.post_id = p_post_id;
END; //

-- =================================================================
--                          FUNCTIONS
-- =================================================================

-- function to get users follower count 
CREATE FUNCTION `get_user_follower_count`(p_user_id INT)
RETURNS INT
NOT DETERMINISTIC READS SQL DATA
BEGIN
    DECLARE follower_count INT;
    SELECT COUNT(*)
    INTO follower_count
    FROM `follows`
    WHERE `followed_id` = p_user_id;
    RETURN follower_count;
END //

-- function to get users following count 
CREATE FUNCTION `get_user_following_count`(p_user_id INT)
RETURNS INT
NOT DETERMINISTIC READS SQL DATA
BEGIN
    DECLARE following_count INT;
    SELECT COUNT(*)
    INTO following_count
    FROM `follows`
    WHERE `follower_id` = p_user_id;
    RETURN following_count;
END //

-- function to get Users total post count 
CREATE FUNCTION `get_user_post_count`(p_user_id INT)
RETURNS INT
NOT DETERMINISTIC READS SQL DATA
BEGIN
    DECLARE post_count INT;
    SELECT COUNT(*)
    INTO post_count
    FROM `posts`
    WHERE `user_id` = p_user_id;
    RETURN post_count;
END //

DELIMITER ;


DELIMITER //

-- NEW: Procedure to get all comments for a post
CREATE PROCEDURE `sp_get_post_comments`(IN p_post_id INT)
BEGIN
    SELECT
        c.comment_id, c.content, c.created_at, c.parent_id,
        u.user_id, u.username
    FROM `comments` c
    JOIN `users` u ON c.user_id = u.user_id
    WHERE c.post_id = p_post_id
    ORDER BY c.created_at ASC;
END; //


-- NEW: Procedure to add a new comment
CREATE PROCEDURE `sp_create_comment`(
    IN p_user_id INT, 
    IN p_post_id INT, 
    IN p_content TEXT
)
BEGIN
    INSERT INTO `comments` (user_id, post_id, content)
    VALUES (p_user_id, p_post_id, p_content);
    
    -- Return the newly created comment (useful for the frontend)
    SELECT
        c.comment_id, c.content, c.created_at, c.parent_id,
        u.user_id, u.username
    FROM `comments` c
    JOIN `users` u ON c.user_id = u.user_id
    WHERE c.comment_id = LAST_INSERT_ID();
END; //


-- NEW: Procedure to toggle a like and return the new state
CREATE PROCEDURE `sp_toggle_like`(IN p_user_id INT, IN p_post_id INT)
BEGIN
    DECLARE v_liked_exists INT;
    DECLARE o_liked BOOLEAN;
    DECLARE o_likes_count INT;

    -- Check if the like already exists
    SELECT COUNT(1)
    INTO v_liked_exists
    FROM `post_likes`
    WHERE `user_id` = p_user_id AND `post_id` = p_post_id;

    IF v_liked_exists > 0 THEN
        -- Like exists, so delete it (unlike)
        DELETE FROM `post_likes`
        WHERE `user_id` = p_user_id AND `post_id` = p_post_id;
        SET o_liked = FALSE;
    ELSE
        -- Like does not exist, so insert it (like)
        INSERT INTO `post_likes` (user_id, post_id)
        VALUES (p_user_id, p_post_id);
        SET o_liked = TRUE;
    END IF;

    -- Get the new total likes count from the posts table
    SELECT `likes_count`
    INTO o_likes_count
    FROM `posts`
    WHERE `post_id` = p_post_id;

    -- Return the new state
    SELECT o_liked AS liked, o_likes_count AS new_count;
END; //

DELIMITER ;

DELIMITER //
-- Procedure 1: Get all profile details for a user
CREATE PROCEDURE `sp_get_user_profile`(IN p_user_id INT)
BEGIN
    SELECT
        u.user_id,
        u.username,
        u.email,
        u.created_at,
        get_user_post_count(p_user_id) AS post_count,
        get_user_follower_count(p_user_id) AS follower_count,
        get_user_following_count(p_user_id) AS following_count
    FROM `users` u
    WHERE u.user_id = p_user_id;
END; //

-- Procedure 2: Get all posts for a specific user
CREATE PROCEDURE `sp_get_user_posts`(
    IN p_user_id INT, 
    IN p_limit INT, 
    IN p_offset INT
)
BEGIN
    SELECT
        p.post_id, p.title, p.content, p.created_at,
        p.user_id, p.likes_count, p.views_count, p.comments_count
    FROM `posts` p
    WHERE p.user_id = p_user_id
    ORDER BY p.created_at DESC
    LIMIT p_limit
    OFFSET p_offset;
END; //

DELIMITER ;


DELIMITER //

-- Procedure 1: Check if a follow relationship exists
CREATE PROCEDURE `sp_check_follow`(
    IN p_follower_id INT,
    IN p_followed_id INT
)
BEGIN
    SELECT EXISTS(
        SELECT 1
        FROM `follows`
        WHERE `follower_id` = p_follower_id AND `followed_id` = p_followed_id
    ) AS is_following;
END; //

-- Procedure 2: Toggle a follow relationship
CREATE PROCEDURE `sp_toggle_follow`(
    IN p_follower_id INT,
    IN p_followed_id INT
)
BEGIN
    DECLARE v_following BOOLEAN;

    -- Check if the relationship already exists
    IF EXISTS(SELECT 1 FROM `follows` WHERE `follower_id` = p_follower_id AND `followed_id` = p_followed_id) THEN
        -- Unfollow
        DELETE FROM `follows`
        WHERE `follower_id` = p_follower_id AND `followed_id` = p_followed_id;
        SET v_following = FALSE;
    ELSE
        -- Follow
        INSERT INTO `follows` (follower_id, followed_id)
        VALUES (p_follower_id, p_followed_id);
        SET v_following = TRUE;
    END IF;

    -- Return the new state and the new follower count
    SELECT
        v_following AS is_following,
        get_user_follower_count(p_followed_id) AS new_follower_count;
END; //

DELIMITER ;


DELIMITER //

-- Procedure 1: Check if a follow relationship exists
CREATE PROCEDURE `sp_check_follow`(
    IN p_follower_id INT,
    IN p_followed_id INT
)
BEGIN
    SELECT EXISTS(
        SELECT 1
        FROM `follows`
        WHERE `follower_id` = p_follower_id AND `followed_id` = p_followed_id
    ) AS is_following;
END; //

-- Procedure 2: Toggle a follow relationship
CREATE PROCEDURE `sp_toggle_follow`(
    IN p_follower_id INT,
    IN p_followed_id INT
)
BEGIN
    DECLARE v_following BOOLEAN;

    -- Check if the relationship already exists
    IF EXISTS(SELECT 1 FROM `follows` WHERE `follower_id` = p_follower_id AND `followed_id` = p_followed_id) THEN
        -- Unfollow
        DELETE FROM `follows`
        WHERE `follower_id` = p_follower_id AND `followed_id` = p_followed_id;
        SET v_following = FALSE;
    ELSE
        -- Follow
        INSERT INTO `follows` (follower_id, followed_id)
        VALUES (p_follower_id, p_followed_id);
        SET v_following = TRUE;
    END IF;

    -- Return the new state and the new follower count
    SELECT
        v_following AS is_following,
        get_user_follower_count(p_followed_id) AS new_follower_count;
END; //

DELIMITER ;


DELIMITER //

-- Procedure 1: Check if a follow relationship exists
CREATE PROCEDURE `sp_check_follow`(
    IN p_follower_id INT,
    IN p_followed_id INT
)
BEGIN
    SELECT EXISTS(
        SELECT 1
        FROM `follows`
        WHERE `follower_id` = p_follower_id AND `followed_id` = p_followed_id
    ) AS is_following;
END; //

-- Procedure 2: Toggle a follow relationship
CREATE PROCEDURE `sp_toggle_follow`(
    IN p_follower_id INT,
    IN p_followed_id INT
)
BEGIN
    DECLARE v_following BOOLEAN;

    -- Check if the relationship already exists
    IF EXISTS(SELECT 1 FROM `follows` WHERE `follower_id` = p_follower_id AND `followed_id` = p_followed_id) THEN
        -- Unfollow
        DELETE FROM `follows`
        WHERE `follower_id` = p_follower_id AND `followed_id` = p_followed_id;
        SET v_following = FALSE;
    ELSE
        -- Follow
        INSERT INTO `follows` (follower_id, followed_id)
        VALUES (p_follower_id, p_followed_id);
        SET v_following = TRUE;
    END IF;

    -- Return the new state and the new follower count
    SELECT
        v_following AS is_following,
        get_user_follower_count(p_followed_id) AS new_follower_count;
END; //

DELIMITER ;


DELIMITER //

CREATE PROCEDURE `sp_get_home_feed`(IN p_user_id INT, IN p_limit INT, IN p_offset INT)
BEGIN
    SELECT
        p.post_id, p.title, p.content, p.created_at,
        p.user_id, p.likes_count, p.views_count, p.comments_count,
        u.username, u.email AS user_email, u.created_at AS user_created_at
    FROM `posts` p
    JOIN `users` u ON p.user_id = u.user_id
    WHERE p.user_id IN (
        -- Get all users that p_user_id is following
        SELECT `followed_id` FROM `follows` WHERE `follower_id` = p_user_id
    )
    ORDER BY p.created_at DESC
    LIMIT p_limit
    OFFSET p_offset;
END; //

DELIMITER ;

DELIMITER //

-- Procedure 1: Search Posts by title or content
CREATE PROCEDURE `sp_search_posts`(IN p_search_term VARCHAR(255))
BEGIN
    SET @search_like = CONCAT('%', p_search_term, '%');
    
    SELECT
        p.post_id, p.title, p.content, p.created_at,
        p.user_id, p.likes_count, p.views_count, p.comments_count,
        u.username
    FROM `posts` p
    JOIN `users` u ON p.user_id = u.user_id
    WHERE p.title LIKE @search_like OR p.content LIKE @search_like
    ORDER BY p.created_at DESC
    LIMIT 10;
END; //

-- Procedure 2: Search Users by username
CREATE PROCEDURE `sp_search_users`(IN p_search_term VARCHAR(255))
BEGIN
    SET @search_like = CONCAT('%', p_search_term, '%');
    
    SELECT
        user_id,
        username,
        email,
        created_at
    FROM `users`
    WHERE username LIKE @search_like
    LIMIT 10;
END; //

-- Procedure 3: Search Tags (Categories) by name
CREATE PROCEDURE `sp_search_tags`(IN p_search_term VARCHAR(255))
BEGIN
    SET @search_like = CONCAT('%', p_search_term, '%');
    
    SELECT
        category_id,
        name,
        (SELECT COUNT(*) FROM post_categories pc WHERE pc.category_id = c.category_id) AS post_count
    FROM `categories` c
    WHERE name LIKE @search_like
    ORDER BY post_count DESC
    LIMIT 10;
END; //

DELIMITER ; 

DELIMITER //

CREATE PROCEDURE `sp_create_post`(
    IN p_user_id INT,
    IN p_title VARCHAR(255),
    IN p_content TEXT,
    IN p_categories_csv TEXT
)
BEGIN
    DECLARE v_post_id INT;
    DECLARE v_category_name VARCHAR(100);
    DECLARE v_category_id INT;
    DECLARE v_index INT DEFAULT 1;
    DECLARE v_comma_pos INT;
    DECLARE v_csv_len INT;

    -- 1. Create the post
    INSERT INTO `posts` (user_id, title, content)
    VALUES (p_user_id, p_title, p_content);
    
    SET v_post_id = LAST_INSERT_ID();

    -- 2. Process and link categories
    IF p_categories_csv IS NOT NULL AND LENGTH(p_categories_csv) > 0 THEN
        -- Add a trailing comma to make the loop simpler
        SET p_categories_csv = CONCAT(p_categories_csv, ',');
        SET v_csv_len = LENGTH(p_categories_csv);

        WHILE v_index <= v_csv_len DO
            -- Find the next comma
            SET v_comma_pos = INSTR(SUBSTRING(p_categories_csv, v_index), ',');
            
            IF v_comma_pos > 0 THEN
                -- Extract the tag name
                SET v_category_name = LTRIM(RTRIM(SUBSTRING(p_categories_csv, v_index, v_comma_pos - 1)));
                
                -- Only process non-empty tags
                IF LENGTH(v_category_name) > 0 THEN
                    
                    -- 3. Find or create the category
                    -- Use INSERT IGNORE to safely add the tag if it's new
                    INSERT IGNORE INTO `categories` (`name`) VALUES (v_category_name);
                    
                    -- Get the ID of that category
                    SELECT `category_id` INTO v_category_id FROM `categories` WHERE `name` = v_category_name;
                    
                    -- 4. Link the post to the category
                    IF v_category_id IS NOT NULL THEN
                        -- Use INSERT IGNORE to avoid duplicate links
                        INSERT IGNORE INTO `post_categories` (`post_id`, `category_id`)
                        VALUES (v_post_id, v_category_id);
                    END IF;
                END IF;
                
                -- Move the index to the character after the comma
                SET v_index = v_index + v_comma_pos;
            ELSE
                -- No more commas, exit the loop
                SET v_index = v_csv_len + 1;
            END IF;
        END WHILE;
    END IF;

    -- 5. Return the newly created post
    SELECT
        p.*,
        u.username,
        u.email AS user_email
    FROM `posts` p
    JOIN `users` u ON p.user_id = u.user_id
    WHERE p.post_id = v_post_id;
END; //
DELIMITER ;


DELIMITER //

-- Procedure 1: Get all collections for a user
CREATE PROCEDURE `sp_get_user_collections`(IN p_user_id INT)
BEGIN
    SELECT 
        collection_id,
        name,
        user_id,
        created_at,
        (SELECT COUNT(*) FROM bookmarks b WHERE b.collection_id = c.collection_id) AS post_count
    FROM `collections` c
    WHERE user_id = p_user_id
    ORDER BY name ASC;
END; //

-- Procedure 2: Create a new collection for a user
-- (Replaces the old crud.py function)
CREATE PROCEDURE `sp_create_collection`(
    IN p_user_id INT,
    IN p_name VARCHAR(100)
)
BEGIN
    -- The UNIQUE KEY in your table will prevent duplicates
    INSERT INTO `collections` (user_id, name)
    VALUES (p_user_id, p_name);
    
    -- Return the new collection
    SELECT * FROM `collections` WHERE collection_id = LAST_INSERT_ID();
END; //

-- Procedure 3: Add a bookmark (save a post to a collection)
-- (Replaces the old crud.py function)
CREATE PROCEDURE `sp_add_bookmark`(
    IN p_user_id INT,
    IN p_post_id INT,
    IN p_collection_id INT
)
BEGIN
    -- The PRIMARY KEY in your table will prevent duplicates
    INSERT IGNORE INTO `bookmarks` (user_id, post_id, collection_id)
    VALUES (p_user_id, p_post_id, p_collection_id);
    
    -- Return the new bookmark
    SELECT * FROM `bookmarks`
    WHERE user_id = p_user_id AND post_id = p_post_id AND collection_id = p_collection_id;
END; //

-- Procedure 4: Remove a bookmark
CREATE PROCEDURE `sp_remove_bookmark`(
    IN p_user_id INT,
    IN p_post_id INT,
    IN p_collection_id INT
)
BEGIN
    DELETE FROM `bookmarks`
    WHERE user_id = p_user_id AND post_id = p_post_id AND collection_id = p_collection_id;
    
    SELECT 'bookmark_removed' AS status;
END; //

-- Procedure 5: Check which collections a post is saved in
CREATE PROCEDURE `sp_check_bookmark_status`(
    IN p_user_id INT,
    IN p_post_id INT
)
BEGIN
    -- Returns a list of collection IDs this post is bookmarked in
    SELECT collection_id
    FROM `bookmarks`
    WHERE user_id = p_user_id AND post_id = p_post_id;
END; //

-- Procedure 6: Get all posts saved in a specific collection
CREATE PROCEDURE `sp_get_posts_in_collection`(
    IN p_user_id INT,
    IN p_collection_id INT
)
BEGIN
    SELECT
        p.post_id, p.title, p.content, p.created_at,
        p.user_id, p.likes_count, p.views_count, p.comments_count,
        u.username
    FROM `posts` p
    JOIN `users` u ON p.user_id = u.user_id
    JOIN `bookmarks` b ON p.post_id = b.post_id
    WHERE b.user_id = p_user_id AND b.collection_id = p_collection_id
    ORDER BY b.created_at DESC;
END; //

DELIMITER ;

