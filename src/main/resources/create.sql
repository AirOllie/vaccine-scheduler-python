DROP TABLE IF EXISTS Availabilities;
DROP TABLE IF EXISTS Appointments;
DROP TABLE IF EXISTS Caregivers;
DROP TABLE IF EXISTS Patients;
DROP TABLE IF EXISTS Vaccines;

CREATE TABLE Caregivers (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Patients (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Vaccines (
    Name varchar(255),
    Doses int,
    PRIMARY KEY (Name)
);

CREATE TABLE Availabilities (
    Date date,
    Caregiver_name varchar(255) REFERENCES Caregivers
    PRIMARY KEY (date, Caregiver_name)
);

CREATE TABLE Appointments (
    Appointment_id int,
    Date date,
    Patient_name varchar(255) REFERENCES Patients,
    Caregiver_name varchar(255) REFERENCES Caregivers,
    Vaccine_name varchar(255) REFERENCES Vaccines,
    PRIMARY KEY (Appointment_id)
);