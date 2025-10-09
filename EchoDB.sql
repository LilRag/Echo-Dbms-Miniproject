show databases;
create database ECHO;
use ECHO;

-- Drop tables in reverse order of creation to avoid foreign key errors
DROP TABLE IF EXISTS `post_views`, `post_categories`, `post_likes`, `bookmarks`, `collections`, `follows`, `comments`, `categories`, `posts`, `users`;

-- =================================================================
--                              TABLES
-- =================================================================

-- Users Table
CREATE TABLE `users` (
  `user_id` INT AUTO_INCREMENT PRIMARY KEY,
  `username` VARCHAR(50) NOT NULL UNIQUE,
  `email` VARCHAR(255) NOT NULL UNIQUE,
  `hashed_password` VARCHAR(255) NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Posts Table
CREATE TABLE `posts` (
  `post_id` INT AUTO_INCREMENT PRIMARY KEY,
  `title` VARCHAR(255) NOT NULL,
  `content` TEXT NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `user_id` INT NOT NULL,
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

-- Bookmarks Table (Ternary Relationship)
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

-- Post Categories Table (Junction Table)
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


show tables;

INSERT INTO `users` (`username`, `email`, `hashed_password`) VALUES
('alice', 'alice@example.com', 'hashed_password_1'),
('bob', 'bob@example.com', 'hashed_password_2'),
('charlie', 'charlie@example.com', 'hashed_password_3');

-- Insert Posts
INSERT INTO `posts` (`title`, `content`, `user_id`) VALUES
('Introduction to FastAPI', 'FastAPI is a modern, fast web framework for building APIs with Python 3.7+ based on standard Python type hints.', 1),
('MySQL Best Practices', 'When designing a MySQL database, it is crucial to normalize your data and use appropriate indexes.', 2),
('A Guide to REST APIs', 'REST is an architectural style that defines a set of constraints for creating web services.', 1);

-- Insert Comments
INSERT INTO `comments` (`content`, `user_id`, `post_id`) VALUES
('Great article, very helpful!', 2, 1),
('Thanks for sharing, Alice!', 3, 1),
('I have a question about indexing.', 1, 2);

-- Insert a threaded comment (replying to comment_id 1)
INSERT INTO `comments` (`content`, `user_id`, `post_id`, `parent_id`) VALUES
('You are welcome!', 1, 1, 1);

-- Insert Post Likes
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

DELIMITER //
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

show triggers;

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

DELIMITER ;





