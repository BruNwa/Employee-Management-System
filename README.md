# Employee-Management-System Database structure 

## Overwiew
Before describing stucture of database let us have a look at the visualisation of it to better comprehend the idea behind it:
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
| `employee_id`      | `int`                                          | `PRIMARY KEY` |
| `first_name`       | `varchar(50)`                                  | |
| `last_name`        | `varchar(50)`                                  |       |
| `email`            | `varchar(100)`                                 |      |
| `phone`            | `varchar(15)`                                  |       |
| `hire_date`        | `date`                                         | The first day of work of emplyee       |
| `employee_status`  | `enum('full_time', 'part_time', 'contractor')`  | Employment Status within our company|
| `department_id`    | `int`                                          | `FOREIGN KEY` linking us to [`department`](#2-department-table)  table   |
| `role_id`          | `int`                                          | `FOREIGN KEY`         |
| `contract_start_date`| `date`                                       | Contract Start Date|
| `contract_end_date`| `date`                                         | it should be `NULL` unless the contract already ended |
| `contract_status`  | `enum('active', 'expired', 'terminated')`      | Contract Status in case we want to keep records of employees that are not longer working with us  |

### 2. Department table
