<p align="center">
  <img src="https://github.com/user-attachments/assets/d206f56e-d0e5-467d-bed4-48f04bf37650" alt="EMS Logo" width="200"/>
</p>

# Employee Management System 🏢

A comprehensive employee management solution built with Python-Flask backend and HTML/CSS/JavaScript frontend, designed to streamline HR operations including employee data management, attendance tracking, performance monitoring, and payroll processing. This project was developed as part of the Mthree Site Reliability Program.

## 🌐 Demo
Check out our live demo: [EMS Landing Page](https://employee-management-syst-55c8d.web.app/home)

## 🌟 Features

### Employee Management
- Complete employee profile management (CRUD operations)
- Role and department-based organization
- Contract and employment status tracking
- Personal information management

### Attendance & Leave Management
- Daily attendance tracking
- Leave request and approval system
- Overtime calculation
- Leave balance monitoring

### Performance Tracking
- KPI management
- Goal setting and achievement tracking
- Performance reviews
- Achievement documentation

### Payroll System
- Automated salary calculation
- Tax and deduction management
- Multiple payment methods support
- Payslip generation
- Bonus management

## 🏗 Architecture

### Backend
- **Framework**: Python-Flask
- **Database**: MySQL 8.0
- **Authentication**: JWT-based authentication
- **API**: RESTful architecture

### Frontend
- **Technology**: HTML5, CSS3, JavaScript
- **Server**: Nginx
- **UI Framework**: Modern responsive design

## 🎯 Application Architecture  
<p align="center">
  <img src="https://github.com/user-attachments/assets/2f186afd-e1a2-47e4-89db-b6e8e7c9a0ea" alt="Application Architecture" width="800"/>
</p>


## 🛠 Infrastructure

The application is containerized using Docker with three main services:

```yaml
Services:
1. Backend (Python-Flask)
   - CPU: 1-2 cores
   - Memory: 4-8GB
   - Port: 2222

2. Database (MySQL 8.0)
   - CPU: 1-1.5 cores
   - Memory: 6-10GB
   - Network: Private subnet (172.20.0.0/16)

3. Frontend (Nginx)
   - CPU: 0.25-0.5 cores
   - Memory: 1-2GB
   - Port: 3000
```

## 📊 Database Schema

The system uses a relational database with the following core entities:
- Employees
- Departments
- Roles
- Attendance
- Leave Management
- Performance
- Payroll
- Payments

![database_structure](https://github.com/user-attachments/assets/4345b257-9a7a-4711-b02c-f95000dec7b7)


[View detailed database schema diagram](https://github.com/BruNwa/Employee-Management-System/tree/sql)

## 🚀 Getting Started

### Prerequisites
- Docker and Docker Compose
- Git

### Installation

1. Clone the repository
```bash
git clone https://github.com/your-username/employee-management-system.git
cd employee-management-system
```

2. Start the application
```bash
docker-compose up -d
```

3. Access the application
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
## 📋 Sprint Progress

Our project follows Agile methodology using GitHub Projects for sprint tracking.
![image](https://github.com/user-attachments/assets/84a0abcd-41a8-41f9-8728-d54c0154c277)


[View Sprint Board](https://github.com/users/BruNwa/projects/4) 📊

Current progress and future sprints can be tracked in the GitHub Projects section of this repository.

## 🔒 Security

- Role-based access control (RBAC)
- Encrypted data transmission
- Secure password handling
- Protected API endpoints

## 🫡 Team

<div align="center">
  <table>
    <tr>
      <td align="center">
        <a href="https://github.com/BruNwa">
          <img src="https://avatars.githubusercontent.com/u/106646716?v=4" width="100px;" alt="Zaim Anwar"/><br />
          <sub><b>Zaim Anwar</b></sub>
        </a>
      </td>
      <td align="center">
        <a href="https://github.com/WojciechSokolowski">
          <img src="https://avatars.githubusercontent.com/u/116203298?v=4" width="100px;" alt="Wojciech Sokołowski"/><br />
          <sub><b>Wojciech Sokołowski</b></sub>
        </a>
      </td>
      <td align="center">
        <a href="https://github.com/Ahmad-Fakhouri">
          <img src="https://avatars.githubusercontent.com/u/116568413?v=4" width="100px;" alt="Ahmad Fakhouri"/><br />
          <sub><b>Ahmad Fakhouri</b></sub>
        </a>
      </td>
    </tr>
  </table>
</div>

 <p align="center">
  <img src="https://github.com/user-attachments/assets/3c9217b2-d7f7-47d1-a183-30c90810c43f" alt="Mthree Logo" width="150"/>
</p>
