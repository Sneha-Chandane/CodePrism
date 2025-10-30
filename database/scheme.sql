CREATE DATABASE IF NOT EXISTS codeprism_db;
USE codeprism_db;

CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(100),
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE analyses (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    repo_url VARCHAR(500),
    repo_name VARCHAR(200),
    efficiency_score FLOAT,
    total_commits INT,
    total_prs INT,
    total_issues INT,
    analysis_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Insert default users
INSERT INTO users (username, password, name, email) VALUES
('admin', 'admin123', 'Admin User', 'admin@codeprism.com'),
('sneha', 'sneha0306@', 'Sneha Chandane', 'sneha@codeprism.com');
