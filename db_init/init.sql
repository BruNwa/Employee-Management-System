-- DROP DATABASE IF EXISTS employee_management_system;
CREATE DATABASE IF NOT EXISTS employee_management_system;

CREATE USER IF NOT EXISTS 'admin'@'%' IDENTIFIED BY 'mthree';
GRANT ALL PRIVILEGES ON employee_management_system.* TO 'admin'@'%';

CREATE USER IF NOT EXISTS 'employee'@'%' IDENTIFIED BY 'employee';
GRANT SELECT, UPDATE ON employee_management_system.* TO 'employee'@'%';
GRANT INSERT ON employee_management_system.leave TO 'employee'@'%';
GRANT INSERT ON employee_management_system.attendance TO 'employee'@'%';
FLUSH PRIVILEGES; 

USE employee_management_system;

CREATE TABLE IF NOT EXISTS `department` (
	department_id INT AUTO_INCREMENT PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS `role` (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(100) NOT NULL
);
CREATE TABLE IF NOT EXISTS `employee` (
    employee_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(15),
    hire_date DATE,
    employee_status ENUM('full_time', 'part_time','contractor'),
    department_id INT NULL,
    role_id INT NULL,
	contract_start_date DATE NOT NULL,
    contract_end_date DATE NULL,
    contract_status ENUM('active', 'expired', 'terminated') NOT NULL,
    FOREIGN KEY (department_id) REFERENCES department(department_id) ON DELETE SET NULL,
    FOREIGN KEY (role_id) REFERENCES role(role_id) ON DELETE SET NULL
);



CREATE TABLE IF NOT EXISTS `attendance` (
	attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT,
    date DATE NOT NULL,
    time_in TIME NULL,
    time_out TIME NULL,
    work_hours DECIMAL(4, 2) NOT NULL,
    overtime_hours DECIMAL(4, 2) NOT NULL,
    employee_status ENUM('present', 'absent', 'leave', 'remote'),
    FOREIGN KEY (employee_id) REFERENCES employee(employee_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS `performance` (
	performance_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    review_score DECIMAL(3,1) CHECK (review_score BETWEEN 1 AND 10),
    reviewer_id INT NULL,
    review_date DATE,
	FOREIGN KEY (employee_id) REFERENCES employee(employee_id) ON DELETE CASCADE,
    FOREIGN KEY (reviewer_id) REFERENCES employee(employee_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS `kpi` (
	kpi_id INT AUTO_INCREMENT PRIMARY KEY,
    performance_id INT NOT NULL,
    kpi_description VARCHAR(255) NOT NULL,
    kpi_score  DECIMAL(2,1) CHECK (kpi_score BETWEEN 1 AND 5),
    FOREIGN KEY (performance_id) REFERENCES performance(performance_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS `goal` (
	goal_id INT AUTO_INCREMENT PRIMARY KEY,
    performance_id INT NOT NULL,
    goal_description VARCHAR(255) NOT NULL,
    goal_status ENUM('not started','in progress','achieved'),
    FOREIGN KEY (performance_id) REFERENCES performance(performance_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS `achievement` (
	achievement_id INT AUTO_INCREMENT PRIMARY KEY,
    performance_id INT NOT NULL,
    achievement_description VARCHAR(255) NOT NULL,
    achievement_date DATE,
	FOREIGN KEY (performance_id) REFERENCES performance(performance_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS `payroll` (
	payroll_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    base_salary DECIMAL(10,2) NOT NULL,
	bonus DECIMAL(10,2) DEFAULT 0 CHECK (bonus >= 0),
	tax DECIMAL(10,2) NOT NULL CHECK (tax >= 0),
	deduction DECIMAL(10,2) DEFAULT 0 CHECK (deduction >= 0),
    FOREIGN KEY (employee_id) REFERENCES employee(employee_id) ON DELETE CASCADE 
);


CREATE TABLE IF NOT EXISTS `payment` (
	payment_id INT AUTO_INCREMENT PRIMARY KEY,
    payroll_id INT NOT NULL,
    payment_method ENUM('bank transfer','cash', 'check'),
    payment_status ENUM('paid','failed','pending'),
    payment_date DATE,
    amount_paid DECIMAL(10,2),
	FOREIGN KEY (payroll_id) REFERENCES payroll(payroll_id) ON DELETE CASCADE

);

CREATE TABLE IF NOT EXISTS `leave_type` (
	leave_type_id INT AUTO_INCREMENT PRIMARY KEY,
	leave_type_name VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS `leave_balance`(
	balance_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT,
    leave_type_id INT NULL,
	leave_balance INT NOT NULL DEFAULT 0,
    FOREIGN KEY (employee_id) REFERENCES employee(employee_id) ON DELETE CASCADE,
    FOREIGN KEY (leave_type_id) REFERENCES leave_type(leave_type_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS `leave` (
	leave_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    leave_type_id INT NULL,
    leave_start DATE,
    leave_end DATE,
    leave_status ENUM('pending','approved','rejected') DEFAULT 'pending',
    approver_id INT NULL,
	FOREIGN KEY (employee_id) REFERENCES employee(employee_id) ON DELETE CASCADE,
    FOREIGN KEY (leave_type_id) REFERENCES leave_type(leave_type_id) ON DELETE SET NULL,
	FOREIGN KEY (approver_id) REFERENCES employee(employee_id) ON DELETE SET NULL
);

-- Insert departments
INSERT INTO `department` (department_name) VALUES
('Human Resources'),
('Finance'),
('IT'),
('Marketing'),
('Sales');

-- Insert roles
INSERT INTO `role` (role_name) VALUES
('Manager'),
('Team Lead'),
('Senior Developer'),
('Junior Developer'),
('Intern');

-- Insert employees
INSERT INTO `employee` (first_name, last_name, email, phone, hire_date, employee_status, department_id, role_id, contract_start_date, contract_end_date, contract_status) VALUES
('John', 'Doe', 'john.doe@example.com', '123-456-7890', '2020-01-15', 'full_time', 1, 1, '2020-01-15', NULL, 'active'),
('Jane', 'Smith', 'jane.smith@example.com', '123-456-7891', '2019-05-20', 'full_time', 2, 2, '2019-05-20', NULL, 'active'),
('Emily', 'Jones', 'emily.jones@example.com', '123-456-7892', '2021-03-10', 'contractor', 3, 3, '2021-03-10', '2024-03-10', 'terminated'),
('Michael', 'Brown', 'michael.brown@example.com', '123-456-7893', '2022-07-22', 'part_time', 4, 4, '2022-07-22', NULL, 'active'),
('Lisa', 'Davis', 'lisa.davis@example.com', '123-456-7894', '2023-08-30', 'full_time', 5, 5, '2023-08-30', NULL, 'active'),
('Alice', 'Williams', 'alice.williams@example.com', '123-456-7895', '2020-04-18', 'full_time', 1, 2, '2020-04-18', NULL, 'active'),
('David', 'Garcia', 'david.garcia@example.com', '123-456-7896', '2018-02-12', 'full_time', 2, 1, '2018-02-12', NULL, 'active'),
('Sophia', 'Martinez', 'sophia.martinez@example.com', '123-456-7897', '2021-09-05', 'contractor', 3, 3, '2021-09-05', '2022-09-05', 'expired'),
('James', 'Hernandez', 'james.hernandez@example.com', '123-456-7898', '2019-12-15', 'part_time', 4, 4, '2019-12-15', NULL, 'active'),
('Mia', 'Lopez', 'mia.lopez@example.com', '123-456-7899', '2022-08-01', 'part_time', 5, 5, '2022-08-01', NULL, 'active');

-- Insert attendance records
INSERT INTO `attendance` (employee_id, date, time_in, time_out, work_hours, overtime_hours, employee_status) VALUES
(1, '2024-10-01', '09:00:00', '17:00:00', 8.00, 0.00, 'present'),
(1, '2024-10-02', '09:00:00', '17:00:00', 8.00, 0.00, 'present'),
(1, '2024-10-03', '09:00:00', '17:00:00', 8.00, 0.00, 'present'),
(1, '2024-10-04', '09:00:00', '17:00:00', 8.00, 0.00, 'present'),
(1, '2024-10-05', '09:00:00', '17:00:00', 8.00, 0.00, 'present'),
(1, '2024-10-06', '09:00:00', '17:00:00', 8.00, 0.00, 'present'),
(1, '2024-10-07', '09:00:00', '17:00:00', 8.00, 0.00, 'present'),
(1, '2024-10-08', '09:00:00', '17:00:00', 8.00, 0.00, 'present'),
(1, '2024-10-09', '09:00:00', '17:00:00', 8.00, 0.00, 'present'),
(1, '2024-10-10', '09:00:00', '17:00:00', 8.00, 0.00, 'present'),

(2, '2024-10-01', '09:00:00', '17:00:00', 8.00, 0.00, 'present'),
(2, '2024-10-02', '09:00:00', '17:00:00', 8.00, 0.00, 'present'),
(2, '2024-10-03', '09:00:00', '17:00:00', 8.00, 0.00, 'present'),
(2, '2024-10-04', '09:00:00', '17:00:00', 8.00, 0.00, 'present'),
(2, '2024-10-05', '09:00:00', '17:00:00', 8.00, 0.00, 'present'),
(2, '2024-10-06', '09:00:00', '17:00:00', 8.00, 0.00, 'present'),
(2, '2024-10-07', '09:00:00', '17:00:00', 8.00, 0.00, 'present'),
(2, '2024-10-08', '09:00:00', '17:00:00', 8.00, 0.00, 'present'),
(2, '2024-10-09', '09:00:00', '17:00:00', 8.00, 0.00, 'present'),
(2, '2024-10-10', '09:00:00', '17:00:00', 8.00, 0.00, 'present'),

(3, '2024-10-01', NULL, NULL, 0.00, 0.00, 'absent'),
(3, '2024-10-02', NULL, NULL, 0.00, 0.00, 'absent'),
(3, '2024-10-03', NULL, NULL, 0.00, 0.00, 'absent'),

(4, '2024-10-01', '09:00:00', '17:00:00', 8.00, 0.00, 'remote'),
(4, '2024-10-02', '09:00:00', '17:00:00', 8.00, 0.00, 'remote'),
(4, '2024-10-03', '09:00:00', '17:00:00', 8.00, 0.00, 'remote'),
(4, '2024-10-04', '09:00:00', '17:00:00', 8.00, 0.00, 'remote'),
(4, '2024-10-05', '09:00:00', '17:00:00', 8.00, 0.00, 'remote'),
(4, '2024-10-06', '09:00:00', '19:00:00', 8.00, 2.00, 'remote'),
(4, '2024-10-07', '09:00:00', '19:00:00', 8.00, 2.00, 'present'),
(4, '2024-10-08', '09:00:00', '19:00:00', 8.00, 2.00, 'present'),
(4, '2024-10-09', '09:00:00', '17:00:00', 8.00, 0.00, 'present'),
(4, '2024-10-10', '09:00:00', '17:00:00', 8.00, 0.00, 'present'),

(5, '2024-10-01', NULL, NULL, 0.00, 0.00, 'leave'),
(5, '2024-10-02', NULL, NULL, 0.00, 0.00, 'leave'),
(5, '2024-10-03', NULL, NULL, 0.00, 0.00, 'leave'),
(5, '2024-10-04', NULL, NULL, 0.00, 0.00, 'leave'),
(5, '2024-10-05', NULL, NULL, 0.00, 0.00, 'leave'),
(5, '2024-10-06', NULL, NULL, 0.00, 0.00, 'leave'),
(5, '2024-10-07', NULL, NULL, 0.00, 0.00, 'leave'),
(5, '2024-10-08', NULL, NULL, 0.00, 0.00, 'leave'),
(5, '2024-10-09', NULL, NULL, 0.00, 0.00, 'leave'),
(5, '2024-10-10', NULL, NULL, 0.00, 0.00, 'leave'),

(6, '2024-10-01', '09:00:00', '17:30:00', 8.50, 0.50, 'present'),
(6, '2024-10-02', '09:00:00', '17:30:00', 8.50, 0.50, 'present'),
(6, '2024-10-03', '09:00:00', '17:30:00', 8.50, 0.50, 'present'),
(6, '2024-10-04', '09:00:00', '17:30:00', 8.50, 0.50, 'present'),
(6, '2024-10-05', '09:00:00', '17:30:00', 8.50, 0.50, 'present'),
(6, '2024-10-06', '09:00:00', '17:30:00', 8.50, 0.50, 'present'),
(6, '2024-10-07', '09:00:00', '17:30:00', 8.50, 0.50, 'present'),
(6, '2024-10-08', '09:00:00', '17:30:00', 8.50, 0.50, 'present'),
(6, '2024-10-09', '09:00:00', '17:30:00', 8.50, 0.50, 'present'),
(6, '2024-10-10', '09:00:00', '17:30:00', 8.50, 0.50, 'present'),

(7, '2024-10-01', '09:00:00', '17:00:00', 8.00, 0.00, 'present'),
(7, '2024-10-02', '09:00:00', '17:00:00', 8.00, 0.00, 'present'),
(7, '2024-10-03', '09:00:00', '17:00:00', 8.00, 0.00, 'present'),
(7, '2024-10-04', '09:00:00', '17:00:00', 8.00, 0.00, 'present'),
(7, '2024-10-05', '09:00:00', '17:00:00', 8.00, 0.00, 'present'),
(7, '2024-10-06', '09:00:00', '17:00:00', 8.00, 0.00, 'present'),
(7, '2024-10-07', '09:00:00', '17:00:00', 8.00, 0.00, 'present'),
(7, '2024-10-08', '09:00:00', '17:00:00', 8.00, 0.00, 'present'),
(7, '2024-10-09', '09:00:00', '17:00:00', 8.00, 0.00, 'present'),
(7, '2024-10-10', '09:00:00', '17:00:00', 8.00, 0.00, 'present'),

(9, '2024-10-01', '09:00:00', '17:00:00', 8.00, 0.00, 'present'),
(9, '2024-10-02', '09:00:00', '17:00:00', 8.00, 0.00, 'present'),
(9, '2024-10-03', '09:00:00', '15:00:00', 6.00, 0.00, 'present'),
(9, '2024-10-04', NULL, NULL, 0.00, 0.00, 'absent'),
(9, '2024-10-05', '09:00:00', '17:00:00', 8.00, 0.00, 'present'),
(9, '2024-10-06', '09:00:00', '17:00:00', 8.00, 0.00, 'present'),
(9, '2024-10-07', '09:00:00', '17:00:00', 8.00, 0.00, 'present'),
(9, '2024-10-08', '09:00:00', '17:00:00', 8.00, 0.00, 'present'),
(9, '2024-10-09', '09:00:00', '17:00:00', 8.00, 0.00, 'present'),
(9, '2024-10-10', '09:00:00', '13:00:00', 4.00, 0.00, 'present'),

(10, '2024-10-01', NULL, NULL, 0.00, 0.00, 'leave'),
(10, '2024-10-02', NULL, NULL, 0.00, 0.00, 'leave'),
(10, '2024-10-03', NULL, NULL, 0.00, 0.00, 'leave'),
(10, '2024-10-04', '09:00:00', '17:00:00', 8.00, 0.00, 'remote'),
(10, '2024-10-05', '09:00:00', '17:00:00', 8.00, 0.00, 'remote'),
(10, '2024-10-06', '09:00:00', '17:00:00', 8.00, 0.00, 'remote'),
(10, '2024-10-07', '09:00:00', '17:00:00', 8.00, 0.00, 'remote'),
(10, '2024-10-08', '09:00:00', '17:00:00', 8.00, 0.00, 'remote'),
(10, '2024-10-09', '09:00:00', '17:00:00', 8.00, 0.00, 'remote'),
(10, '2024-10-10', '09:00:00', '17:00:00', 8.00, 0.00, 'remote');

-- Insert performance records
INSERT INTO `performance` (employee_id, review_score, reviewer_id, review_date) VALUES
(10, 9.0, 2, '2024-10-15'),
(2, 8.5, 1, '2024-10-15'),
(3, 7.0, 1, '2024-10-10'),
(4, 8.0, 2, '2024-10-20'),
(5, 9.5, 1, '2024-10-22'),
(6, 8.0, 1, '2024-10-15'),
(7, 8.5, 6, '2024-10-16'),
(8, 7.5, 2, '2024-10-17'),
(9, 9.0, 6, '2024-10-18');

-- Insert KPI records
INSERT INTO `kpi` (performance_id, kpi_description, kpi_score) VALUES
(1, 'Meeting project deadlines', 4.5),
(2, 'Customer satisfaction score', 4.0),
(3, 'Code quality metrics', 3.5),
(4, 'Team collaboration', 4.0),
(5, 'Learning new technologies', 5.0),
(6, 'Meeting deadlines for tasks', 4.0),
(7, 'Quality of code produced', 4.5),
(8, 'Collaboration with team', 3.5),
(9, 'Innovative contributions to projects', 5.0),
(1, 'Timely completion of all assigned tasks', 5.0),
(1, 'Effective communication with stakeholders', 4.8),
(1, 'Proactive problem solving', 4.7),
(7, 'Ability to work under pressure', 4.6),
(5, 'Adoption of new tools and technologies', 5.0),
(5, 'Mentoring team members', 4.9),
(5, 'Sharing knowledge in team meetings', 5.0),
(5, 'Continuous improvement in skills', 5.0),
(9, 'Creating innovative solutions', 5.0),
(9, 'Driving project success', 4.9),
(9, 'Exceptional client feedback', 5.0),
(9, 'Leading team brainstorming sessions', 4.8);

-- Insert goal records
INSERT INTO `goal` (performance_id, goal_description, goal_status) VALUES
(1, 'Achieve a customer satisfaction score of 90% or higher', 'in progress'),
(1, 'Implement feedback from last performance review', 'not started'),
(1, 'Attend a leadership workshop', 'not started'),
(2, 'Develop a marketing strategy for new product launch', 'not started'),
(2, 'Increase client engagement through social media', 'in progress'),
(2, 'Improve response time to customer inquiries', 'in progress'),
(3, 'Enhance product quality through better testing', 'in progress'),
(3, 'Reduce delivery time for new features', 'in progress'),
(3, 'Train team members on best practices', 'not started'),
(4, 'Establish regular team check-ins', 'in progress'),
(4, 'Facilitate conflict resolution workshops', 'not started'),
(5, 'Present internship findings to the team', 'not started'),
(5, 'Create a project timeline for internship tasks', 'in progress'),
(6, 'Attend a public speaking course', 'not started'),
(6, 'Practice communication in team settings', 'in progress'),
(7, 'Complete all modules of certification', 'in progress'),
(7, 'Apply learnings from training in daily tasks', 'not started'),
(8, 'Encourage feedback during meetings', 'achieved'),
(8, 'Share meeting notes with the team', 'achieved'),
(9, 'Prepare a project proposal', 'in progress'),
(9, 'Define project scope and objectives', 'not started'),
(9, 'Mentor junior team members during the project', 'in progress');

-- Insert achievement records
INSERT INTO `achievement` (performance_id, achievement_description, achievement_date) VALUES
(1, 'Completed all project milestones ahead of schedule', '2024-01-10'),
(1, 'Developed an innovative solution for client needs', '2024-02-15'),
(2, 'Increased customer retention by 15%', '2024-03-01'),
(2, 'Successfully launched a marketing campaign', '2024-03-20'),
(3, 'Achieved a 30% reduction in bug reports', '2024-04-05'),
(3, 'Successfully integrated feedback from user testing', '2024-04-20'),
(4, 'Facilitated a successful team workshop', '2024-05-01'),
(4, 'Developed a training program for new hires', '2024-05-15'),
(5, 'Presented at a tech conference', '2024-06-10'),
(5, 'Achieved recognition in an industry publication', '2024-06-25'),
(6, 'Organized a charity event for team bonding', '2024-07-15'),
(6, 'Created a positive work environment through initiatives', '2024-07-30'),
(7, 'Earned a professional certification in a relevant field', '2024-08-20'),
(7, 'Contributed to a significant team project that was praised', '2024-08-25'),
(8, 'Developed a comprehensive onboarding process', '2024-09-10'),
(8, 'Played a key role in team collaboration initiatives', '2024-09-20'),
(9, 'Received a company-wide innovation award', '2024-10-01'),
(9, 'Promoted to a team lead position', '2024-10-15');

-- Insert leave type records
INSERT INTO `leave_type` (leave_type_name) VALUES
('Sick Leave'),
('Casual Leave'),
('Annual Leave'),
('Maternity Leave'),
('Paternity Leave');

-- Insert leave balance records
INSERT INTO `leave_balance` (employee_id, leave_type_id, leave_balance) VALUES

(1, 1, 10),  -- Employee 1: Sick Leave
(1, 2, 2),   -- Employee 1: Casual Leave
(1, 3, 26),  -- Employee 1: Annual Leave

(2, 1, 10),  -- Employee 2: Sick Leave
(2, 2, 2),   -- Employee 2: Casual Leave
(2, 3, 26),  -- Employee 2: Annual Leave

(3, 1, 10),  -- Employee 3: Sick Leave
(3, 2, 2),   -- Employee 3: Casual Leave
(3, 3, 20),  -- Employee 3: Annual Leave

(4, 1, 10),  -- Employee 4: Sick Leave
(4, 2, 1),   -- Employee 4: Casual Leave
(4, 3, 20),  -- Employee 4: Annual Leave

(5, 1, 8),  -- Employee 5: Sick Leave
(5, 2, 0),   -- Employee 5: Casual Leave
(5, 3, 16),  -- Employee 5: Annual Leave
(5, 4, 30), -- Maternity leave

(6, 1, 10),  -- Employee 6: Sick Leave
(6, 2, 1),   -- Employee 6: Casual Leave
(6, 3, 20),  -- Employee 6: Annual Leave

(7, 1, 2),  -- Employee 7: Sick Leave
(7, 2, 0),   -- Employee 7: Casual Leave
(7, 3, 15),  -- Employee 7: Annual Leave

(8, 1, 8),  -- Employee 8: Sick Leave
(8, 2, 2),   -- Employee 8: Casual Leave
(8, 3, 26),  -- Employee 8: Annual Leave

(9, 1, 5),  -- Employee 9: Sick Leave
(9, 2, 2),   -- Employee 9: Casual Leave
(9, 3, 13);  -- Employee 9: Annual Leave


-- Insert leave records
INSERT INTO `leave` (employee_id, leave_type_id, leave_start, leave_end, leave_status, approver_id) VALUES
(1, 1, '2023-10-10', '2023-10-11', 'approved', 2),
(2, 3, '2023-10-05', '2023-10-07', 'pending', 1),
(3, 2, '2023-10-15', '2023-10-16', 'approved', 1),
(4, 4, '2023-10-20', '2023-10-25', 'pending', 1),
(5, 4, '2024-10-01', '2023-10-30', 'approved', 2),
(6, 2, '2023-10-10', '2023-10-11', 'approved', 1),
(7, 3, '2023-10-15', '2023-10-17', 'pending', 2),
(8, 1, '2023-10-20', '2023-10-22', 'approved', 2),
(9, 4, '2023-10-28', '2023-10-30', 'pending', 1),
(10, 1, '2024-09-28', '2024-10-03', 'approved', 1);



