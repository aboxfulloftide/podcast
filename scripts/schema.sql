CREATE TABLE `users` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `username` VARCHAR(255) NOT NULL UNIQUE,
  `hashed_password` VARCHAR(255) NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE `podcasts` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `title` VARCHAR(255) NOT NULL,
  `feed_url` VARCHAR(2048) NOT NULL UNIQUE,
  `podcast_index_id` INT UNIQUE,
  `image_url` VARCHAR(2048),
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE `subscriptions` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `podcast_id` INT NOT NULL,
  `episode_retention_count` INT DEFAULT 5,
  `custom_feed_slug` VARCHAR(255) NOT NULL UNIQUE,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`podcast_id`) REFERENCES `podcasts`(`id`) ON DELETE CASCADE,
  UNIQUE(`user_id`, `podcast_id`)
);

CREATE TABLE `episodes` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `podcast_id` INT NOT NULL,
  `guid` VARCHAR(1024) NOT NULL,
  `title` VARCHAR(255),
  `original_audio_url` VARCHAR(2048),
  `download_path` VARCHAR(2048),
  `edited_path` VARCHAR(2048),
  `publication_date` DATETIME,
  `status` ENUM('pending', 'downloaded', 'processed', 'failed') DEFAULT 'pending',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`podcast_id`) REFERENCES `podcasts`(`id`) ON DELETE CASCADE,
  UNIQUE(`podcast_id`, `guid`)
);

CREATE TABLE `ad_removal_rules` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `subscription_id` INT NOT NULL,
    `strategy` ENUM('remove_before', 'remove_after', 'remove_between') NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`subscription_id`) REFERENCES `subscriptions`(`id`) ON DELETE CASCADE
);

CREATE TABLE `ad_removal_markers` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `rule_id` INT NOT NULL,
    `marker_time_ms` INT NOT NULL,
    `marker_order` INT NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`rule_id`) REFERENCES `ad_removal_rules`(`id`) ON DELETE CASCADE
);
