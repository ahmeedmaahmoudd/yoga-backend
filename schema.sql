-- Create tables

-- Teachers table
CREATE TABLE teachers (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    position_title VARCHAR(100) NOT NULL,
    bio TEXT NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL
);

-- Activities table
CREATE TABLE activities (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    image_url VARCHAR(255),
    activity_type VARCHAR(50) NOT NULL,  -- Changed to direct string
    capacity INTEGER NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    schedule VARCHAR(200) NOT NULL,
    expertise_level INTEGER NOT NULL CHECK (expertise_level >= 0 AND expertise_level <= 3),
    is_highlighted BOOLEAN DEFAULT FALSE,
    location VARCHAR(200) NOT NULL,
    CONSTRAINT validate_expertise_level CHECK (
        (activity_type = 'Yoga' AND expertise_level IN (1, 2, 3))
        OR
        (activity_type != 'Yoga' AND expertise_level = 0)
    )
);

-- Teacher responsible for activity (many-to-many)
CREATE TABLE activity_responsible_teachers (
    activity_id INTEGER NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
    teacher_id INTEGER NOT NULL REFERENCES teachers(id) ON DELETE CASCADE,
    PRIMARY KEY (activity_id, teacher_id)
);

-- Teacher teaching an activity (many-to-many)
CREATE TABLE activity_teaching_teachers (
    activity_id INTEGER NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
    teacher_id INTEGER NOT NULL REFERENCES teachers(id) ON DELETE CASCADE,
    PRIMARY KEY (activity_id, teacher_id)
);-- Create tables

-- Teachers table
CREATE TABLE teachers (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    position_title VARCHAR(100) NOT NULL,
    bio TEXT NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL
);

-- Activities table
CREATE TABLE activities (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    image_url VARCHAR(255),
    activity_type VARCHAR(50) NOT NULL,  -- Changed to direct string
    capacity INTEGER NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    schedule VARCHAR(200) NOT NULL,
    expertise_level INTEGER NOT NULL CHECK (expertise_level >= 0 AND expertise_level <= 3),
    is_highlighted BOOLEAN DEFAULT FALSE,
    location VARCHAR(200) NOT NULL,
    CONSTRAINT validate_expertise_level CHECK (
        (activity_type = 'Yoga' AND expertise_level IN (1, 2, 3))
        OR
        (activity_type != 'Yoga' AND expertise_level = 0)
    )
);

-- Teacher responsible for activity (many-to-many)
CREATE TABLE activity_responsible_teachers (
    activity_id INTEGER NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
    teacher_id INTEGER NOT NULL REFERENCES teachers(id) ON DELETE CASCADE,
    PRIMARY KEY (activity_id, teacher_id)
);

-- Teacher teaching an activity (many-to-many)
CREATE TABLE activity_teaching_teachers (
    activity_id INTEGER NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
    teacher_id INTEGER NOT NULL REFERENCES teachers(id) ON DELETE CASCADE,
    PRIMARY KEY (activity_id, teacher_id)
);