# Employee-Management-System Database structure 

## Table of Tables

1. [Employee table](#1-employee-table)
2. [Department table](#2-department-table)
3. [Role table](#3-role-table)
4. [Attendance table](#4-attendance-table)
5. [Performance table](#5-performance-table)
6. [KPI table](#6-kpi-table)
7. [Goal table](#7-goal-table)
8. [Achievement table](#8-achievement-table)
9. [Payroll table](#9-payroll-table)
10. [Payment table](#10-payment-table)
11. [Leave table](#11-leave-table)
12. [Leave type table](#12-leave-type-table)
13. [Leave balance table](#13-leave-balance-table)

## Overwiew
Before describing stucture of database let us have a look at the visualisation of it to better comprehend the idea behind it, notice that all the names are in lowercase and singular:
![Alt Text](database_structure.png)
## Database employee_management_system - table structure

It is important to note that all primary keys have the `AUTO_INCREMENT` attribute enabled. When these keys are used as foreign keys in other tables, they are associated with either `ON DELETE SET NULL` or `ON DELETE CASCADE` constraints, depending on whether the foreign key is critical to the integrity of the referencing table.
| Term                | Meaning                                                        | Usage in this database                                |
|---------------------|----------------------------------------------------------------|---------------------------------------|
| `ON DELETE SET NULL`  | Sets the foreign key field to `NULL` when the referenced row is deleted.  | Used when the deletion does not render the other table useless (your menager is no longer in our database but your leave still can be there|
| `ON DELETE CASCADE`   | Automatically deletes rows in the child table when the referenced row is deleted. | Used when deleting table makes other useless, why you need to keep reviews for employee 44 if there no loger exist person with such ID          |

This will clarify the meaning and when to use each constraint, and it will stand out with inline code 
### 1. Employee table 
 This table is heart and soul of our database:
 | Field              | Type                                           | Comment          |
|--------------------|------------------------------------------------|------------------|
| `employee_id`      | `INT `                                          | `PRIMARY KEY` |
| `first_name`       | `VARCHAR(50)`                                  |  |
| `last_name`        | `VARCHAR(50)`                                  |       |
| `email`            | `VARCHAR(100)`                                 |      |
| `phone`            | `VARCHAR(15)`                                  | hopefully this will be enough characters      |
| `hire_date`        | `DATE`                                         | The first day of work of emplyee       |
| `employee_status`  | `ENUM('full_time', 'part_time', 'contractor')`  | Employment Status within our company|
| `department_id`    | `INT `                                          | `FOREIGN KEY` linking to [`department`](#2-department-table)   |
| `role_id`          | `INT `                                          | `FOREIGN KEY` linking to [`role`](#3-role-table)       |
| `contract_start_date`| `DATE`                                       | The start date of current contract, the idea behaind it is if we have employees who continue to work after first contract to have this field changed - change from part to full time i.e.  |
| `contract_end_date`| `DATE`                                         | it should be `NULL` unless the contract already ended |
| `contract_status`  | `ENUM('active', 'expired', 'terminated')`      | Contract Status in case we want to keep records of employees that are not longer working with us  |

The `contract_` entries are the result of my not inplemented ide of contract table, now it looks a bit redundant, but the functionality can be expaded for employees who start 

### 2. Department table
Here whe hold simply name of department, scope of project does not require any more data, but this approach make us flexible and expanding database will be easier.
 | Field              | Type                                           | Comment          |
|--------------------|------------------------------------------------|------------------|
| `department_id` | `INT` | `PRIMARY KEY` |
| `department_name` | `VARCHAR(100)` | just a simle name is enough for our needs |

### 3. Role table
Here we have the same idea as with the previous table, just to keep data more flexivle and easy to edit or expand in the future.
 | Field              | Type                                           | Comment          |
|--------------------|------------------------------------------------|------------------|
| `role_id` | `INT` | `PRIMARY KEY` |
| `role_name` | `VARCHAR(100)` | just a simle name is enough for our needs |

### 4. Attendance table 


### 5. Performance table

### 6. KPI table

### 7. Goal table

### 8. Achievement table 

### 9. Payroll table

### 10. Payment table

### 11. Leave table 

### 12. Leave type table

### 13. Leave balance table
