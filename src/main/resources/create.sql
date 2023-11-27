DROP TABLE IF EXISTS Availabilities;
DROP TABLE IF EXISTS Appointments;
DROP TABLE IF EXISTS Caregivers;
DROP TABLE IF EXISTS Patients;
DROP TABLE IF EXISTS Vaccines;

CREATE TABLE Caregivers (
    username varchar(255),
    salt BINARY(16),
    hash BINARY(16),
    PRIMARY KEY (username)
);

CREATE TABLE Patients (
    username varchar(255),
    salt BINARY(16),
    hash BINARY(16),
    PRIMARY KEY (username)
);

CREATE TABLE Vaccines (
    name varchar(255),
    doses int,
    PRIMARY KEY (name)
);

CREATE TABLE Availabilities (
    date date,
    caregiver_name varchar(255) REFERENCES Caregivers,
    availability int,
    PRIMARY KEY (date, caregiver_name)
);

CREATE TABLE Appointments (
    appointment_id int,
    date date,
    patient_name varchar(255) REFERENCES Patients,
    caregiver_name varchar(255) REFERENCES Caregivers,
    vaccine_name varchar(255) REFERENCES Vaccines,
    PRIMARY KEY (appointment_id)
);