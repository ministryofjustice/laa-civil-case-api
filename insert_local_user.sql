-- add_user.sql
INSERT INTO "users" (username, hashed_password, email, full_name, disabled)
VALUES ('johndoe', '$2b$12$niIeexAn3B2ASvQ6T3xJ3OJqsFkeGXj.hImNhiHxTwnxJoUezZy4m', 'johndoe@example.com', 'John Doe', false);