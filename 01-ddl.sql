-- Table: contacts
CREATE TABLE contacts (
						  contact_email VARCHAR(255) NOT NULL PRIMARY KEY,
						  contact_first_name VARCHAR(255),
						  contact_last_name VARCHAR(500),
						  contact_address VARCHAR(700),
						  contact_city VARCHAR(255),
						  contact_country VARCHAR(255),
						  contact_birthdate DATE
) COMMENT='contains information about contacts';

-- Table: populations
CREATE TABLE populations (
							 population_code VARCHAR(10) NOT NULL,
							 population_year INTEGER NOT NULL,
							 population_period VARCHAR(10) NOT NULL,
							 PRIMARY KEY (population_code, population_year, population_period)
) COMMENT='Different populations over time';

-- Table: students
CREATE TABLE students (
						  student_epita_email VARCHAR(255) NOT NULL PRIMARY KEY,
						  student_contact_ref VARCHAR(255) NOT NULL,
						  student_enrollment_status VARCHAR(50) NOT NULL,
						  student_population_period_ref VARCHAR(10) NOT NULL,
						  student_population_year_ref INTEGER NOT NULL,
						  student_population_code_ref VARCHAR(5) NOT NULL,
						  FOREIGN KEY (student_contact_ref) REFERENCES contacts(contact_email)
);

-- Table: teachers
CREATE TABLE teachers (
						  teacher_contact_ref VARCHAR(255),
						  teacher_epita_email VARCHAR(255) NOT NULL PRIMARY KEY,
						  teacher_study_level INTEGER
);

-- Table: courses
CREATE TABLE courses (
						 course_code VARCHAR(255) NOT NULL,
						 course_rev INTEGER NOT NULL,
						 duration INTEGER,
						 course_last_rev INTEGER,
						 course_name VARCHAR(255),
						 course_description VARCHAR(255),
						 PRIMARY KEY (course_code, course_rev)
);

-- Table: exams
CREATE TABLE exams (
					   exam_course_code VARCHAR(255) NOT NULL,
					   exam_course_rev INTEGER NOT NULL,
					   exam_weight INTEGER,
					   exam_type VARCHAR(255) NOT NULL,
					   PRIMARY KEY (exam_course_code, exam_course_rev, exam_type)
);

-- Table: sessions
CREATE TABLE sessions (
						  session_course_ref VARCHAR(255) NOT NULL,
						  session_course_rev_ref INTEGER NOT NULL,
						  session_prof_ref VARCHAR(255),
						  session_date DATE NOT NULL,
						  session_start_time VARCHAR(255) NOT NULL,
						  session_end_time VARCHAR(255) NOT NULL,
						  session_type VARCHAR(255),
						  session_population_year INTEGER,
						  session_population_period VARCHAR(255),
						  session_room VARCHAR(255),
						  PRIMARY KEY (session_course_ref, session_date, session_start_time, session_end_time)
);

-- Table: attendance
CREATE TABLE attendance (
							attendance_student_ref VARCHAR(255),
							attendance_population_year_ref INTEGER,
							attendance_course_ref VARCHAR(255),
							attendance_course_rev INTEGER,
							attendance_session_date_ref VARCHAR(255),
							attendance_session_start_time VARCHAR(255),
							attendance_session_end_time VARCHAR(255),
							attendance_presence INTEGER
);

-- Table: programs
CREATE TABLE programs (
						  program_course_code_ref VARCHAR(255) NOT NULL,
						  program_course_rev_ref INTEGER NOT NULL,
						  program_assignment VARCHAR(255) NOT NULL,
						  PRIMARY KEY (program_course_code_ref, program_course_rev_ref, program_assignment),
						  FOREIGN KEY (program_course_code_ref, program_course_rev_ref) REFERENCES courses(course_code, course_rev)
);

-- Table: grades
CREATE TABLE grades (
						grade_student_epita_email_ref VARCHAR(255) NOT NULL,
						grade_course_code_ref VARCHAR(255) NOT NULL,
						grade_course_rev_ref INTEGER NOT NULL,
						grade_exam_type_ref VARCHAR(255) NOT NULL,
						grade_score INTEGER,
						PRIMARY KEY (grade_student_epita_email_ref, grade_course_rev_ref, grade_course_code_ref, grade_exam_type_ref),
						FOREIGN KEY (grade_student_epita_email_ref) REFERENCES students(student_epita_email)
);
