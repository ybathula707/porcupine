#!/bin/sh
set -eu
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
  CREATE TABLE teams (
      id SERIAL PRIMARY KEY,
      name VARCHAR(100) NOT NULL,
      team_function VARCHAR(255)
  );

  CREATE TABLE "users" (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(100),
    team_id INT NOT NULL,
    CONSTRAINT fk_team
        FOREIGN KEY (team_id)
        REFERENCES teams (id)
        ON DELETE CASCADE
  );

  INSERT INTO teams (name, team_function)
  VALUES
  ('Frontend Engineering', 'Builds and maintains user interfaces and client-side logic'),
  ('Backend Engineering', 'Develops server-side logic, APIs, and data processing services'),
  ('DevOps', 'Manages infrastructure, CI/CD pipelines, and deployment automation'),
  ('QA Engineering', 'Ensures software quality through automated and manual testing'),
  ('Data Engineering', 'Designs and builds data pipelines and data warehouses'),
  ('Machine Learning Engineering', 'Builds ML models and integrates them into production systems'),
  ('Security Engineering', 'Implements security measures, monitors threats, and ensures compliance'),
  ('Mobile Engineering', 'Develops native and cross-platform mobile applications'),
  ('Platform Engineering', 'Builds core services and tools used by other engineering teams'),
  ('Site Reliability Engineering', 'Improves system reliability, scalability, and performance'),
  ('Identity Services', 'Builds and maintains authentication, authorization, and user identity management systems');


  INSERT INTO "users" (name, role, team_id)
  VALUES
  ('Alice Johnson', 'PM', 1),
  ('Bob Carter', 'Dev', 1),
  ('Charlie Nguyen', 'Dev', 1),
  ('Diana Brooks', 'Dev', 1),
  ('Evan Foster', 'QA', 1),

  ('Fiona Turner', 'PM', 2),
  ('George Patel', 'Dev', 2),
  ('Hannah Kim', 'Dev', 2),
  ('Ian Romero', 'Dev', 2),
  ('Jack Simmons', 'QA', 2),

  ('Karen Blake', 'PM', 3),
  ('Liam Chen', 'Dev', 3),
  ('Mona Castillo', 'Dev', 3),
  ('Nate Holland', 'Dev', 3),
  ('Oscar Silva', 'Dev', 3),

  ('Paula Mitchell', 'PM', 4),
  ('Quinn Hayes', 'Dev', 4),
  ('Riley Zhang', 'Dev', 4),
  ('Sam Watts', 'QA', 4),
  ('Tina Lawrence', 'QA', 4),

  ('Uma Richards', 'PM', 5),
  ('Victor Delgado', 'Dev', 5),
  ('Wendy Park', 'Dev', 5),
  ('Xavier Morgan', 'Dev', 5),
  ('Yara Bennett', 'QA', 5),

  ('Zack Hughes', 'PM', 6),
  ('Amy Crawford', 'Dev', 6),
  ('Brian Ortiz', 'Dev', 6),
  ('Clara Walsh', 'Dev', 6),
  ('Derek Abbott', 'Dev', 6),

  ('Ella Daniels', 'PM', 7),
  ('Frank Rivera', 'Dev', 7),
  ('Grace Armstrong', 'Dev', 7),
  ('Harry Cohen', 'Dev', 7),
  ('Ivy Barker', 'QA', 7),

  ('Jon Ellis', 'PM', 8),
  ('Kara Phillips', 'Dev', 8),
  ('Leo Watson', 'Dev', 8),
  ('Mila Stone', 'Dev', 8),
  ('Nora Burns', 'QA', 8),

  ('Owen Ford', 'PM', 9),
  ('Pia Chavez', 'Dev', 9),
  ('Quincy Shaw', 'Dev', 9),
  ('Rosa Nichols', 'Dev', 9),
  ('Steve Harper', 'Dev', 9),

  ('Tara Lowe', 'PM', 10),
  ('Umair Dawson', 'Dev', 10),
  ('Vik Matthews', 'Dev', 10),
  ('Will Greene', 'Dev', 10),
  ('Xena Fuller', 'QA', 10),

  ('Yvonne Sullivan', 'PM', 11),
  ('Zane Carr', 'Dev', 11),
  ('Aaron West', 'Dev', 11),
  ('Bella Knight', 'Dev', 11),
  ('Caleb Ford', 'QA', 11);
EOSQL
