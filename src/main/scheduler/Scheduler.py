from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime


'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None


def create_patient(tokens):
    # create_patient <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_patient(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the patient
    patient = Patient(username, salt=salt, hash=hash)

    # save patient information to the database
    try:
        patient.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)


def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patients WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False
    


def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    caregiver = Caregiver(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)


def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def login_patient(tokens):
    # login_patient <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_patient
    if current_patient is not None or current_caregiver is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    patient = None
    try:
        patient = Patient(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if patient is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_patient = patient


def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if caregiver is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_caregiver = caregiver


def search_caregiver_schedule(tokens):
    # search_caregiver_schedule <date>

    # Output the username for the caregivers that are available for the date, along with the number of available doses 
    # left for each vaccine. Order by the username of the caregiver. Separate each attribute with a space.

    # check 1: if no user is logged in, print "Please login first!"
    # both caregiver and patient can search for caregiver schedules

    global current_caregiver
    global current_patient

    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    cm = ConnectionManager()
    conn = cm.create_connection()
    date = tokens[1]
    select_caregiver = "SELECT * FROM Caregivers WHERE Username NOT IN (SELECT Caregiver_name FROM Availabilities WHERE Date = %s) ORDER BY Username ASC"
    cursor = conn.cursor(as_dict=True)
    cursor.execute(select_caregiver, date)
    caregivers = cursor.fetchall()
    if len(caregivers) == 0:
        print("No Caregiver is available on {}!".format(date))
    else: 
        print("Available caregivers:")
        for row in caregivers:
            print(row['Username'])
    print("######################")
    select_vaccine = "SELECT * FROM Vaccines ORDER BY Name ASC"
    cursor.execute(select_vaccine)
    print("Available vaccines in doses:")
    for row in cursor:
        print(row['Name'], row['Doses'])
    return


def reserve(tokens):
    # reserve <date> <vaccine>
    
    # Patients perform this operation to reserve an appointment.
    # Caregivers can only see a maximum of one patient per day, meaning that if the reservation went through, the caregiver is no longer available for that date.
    # If there are available caregivers, choose the caregiver by alphabetical order and print “Appointment ID: {appointment_id}, Caregiver username: {username}” for the reservation.
    # If there’s no available caregiver, print “No Caregiver is available!”. If not enough vaccine doses are available, print "Not enough available doses!".
    # If no user is logged in, print “Please login first!”. If the current user logged in is not a patient, print “Please login as a patient!”.
    # For all other errors, print "Please try again!".
    
    global current_patient
    global current_caregiver
    
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return

    if current_patient is None:
        print("Please login as a patient!")
        return
    
    if len(tokens) != 3:
        print("Please try again!")
        return
    
    date = tokens[1]
    vaccine = tokens[2]
    
    cm = ConnectionManager()
    conn = cm.create_connection()
    
    # Check if there are available caregivers for the given date
    select_caregiver = "SELECT * FROM Caregivers WHERE Username NOT IN (SELECT Caregiver_name FROM Availabilities WHERE Date = %s) ORDER BY Username ASC"
    cursor = conn.cursor(as_dict=True)
    cursor.execute(select_caregiver, date)
    caregivers = cursor.fetchall()
    
    if len(caregivers) == 0:
        print("No Caregiver is available!")
        return
    
    # Check if there are enough vaccine doses available
    select_vaccine = "SELECT * FROM Vaccines WHERE Name = %s"
    cursor.execute(select_vaccine, vaccine)
    vaccine_info = cursor.fetchone()
    
    if vaccine_info['Doses'] == 0:
        print("Not enough available doses!")
        return
    
    # Reserve the appointment
    caregiver_username = caregivers[0]['Username']
    appointment_id = str(int(int(datetime.datetime.now().timestamp()*1e6)%1e8)).zfill(8)
    
    insert_appointment = "INSERT INTO Appointments (Appointment_id, Date, Patient_name, Caregiver_name, Vaccine_name) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(insert_appointment, (appointment_id, date, current_patient.username, caregiver_username, vaccine))
    conn.commit()
    
    Caregiver(caregiver_username).upload_availability(date)
    Vaccine(vaccine, vaccine_info['Doses']).decrease_available_doses(1)
    
    print(f"Appointment ID: {appointment_id}, Caregiver username: {caregiver_username}")


def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)
        current_caregiver.upload_availability(d)
    except pymssql.Error as e:
        print("Upload Availability Failed")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please enter a valid date!")
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        print("Error:", e)
        return
    print("Availability uploaded!")


def cancel(tokens):
    # cancel <appointment_id>
    
    # Both caregivers and patients can cancel an existing appointment.
    # The appointment ID is used to identify the appointment to be canceled.
    # When an appointment is canceled, it should be removed from both the patient's and caregiver's schedules.
    # If no user is logged in, print "Please login first!".
    # For all other errors, print "Please try again!".
    
    global current_caregiver
    global current_patient

    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return

    if len(tokens) != 2:
        print("Please try again!")
        return

    appointment_id = tokens[1]
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()

    # add one dose back to the vaccine
    select_appointment = "SELECT * FROM Appointments WHERE Appointment_id = %s"
    cursor.execute(select_appointment, appointment_id)
    vaccine_name = cursor.fetchone()[-1]
    select_vaccine = "SELECT * FROM Vaccines WHERE Name = %s"
    cursor.execute(select_vaccine, vaccine_name)
    vaccine_info = cursor.fetchone()
    Vaccine(vaccine_name, vaccine_info[-1]).increase_available_doses(1)

    delete_availability = "DELETE FROM Availabilities WHERE Date = (SELECT Date FROM Appointments WHERE Appointment_id = %s)"
    cursor.execute(delete_availability, appointment_id)
    delete_appointment = "DELETE FROM Appointments WHERE Appointment_id = %s"
    cursor.execute(delete_appointment, appointment_id)
    
    conn.commit()
    
    print("Appointment canceled!")
    return


def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error as e:
        print("Error occurred when adding doses")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when adding doses")
        print("Error:", e)
        return

    # if the vaccine is not found in the database, add a new (vaccine, doses) entry.
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    print("Doses updated!")


def show_appointments(tokens):
    # show_appointments

    # Output the scheduled appointments for the current user (both patients and caregivers). 
    # For caregivers, you should print the appointment ID, vaccine name, date, and patient name. Order by the appointment ID. Separate each attribute with a space.
    # For patients, you should print the appointment ID, vaccine name, date, and caregiver name. Order by the appointment ID. Separate each attribute with a space.
    # If no user is logged in, print “Please login first!”.
    # For all other errors, print "Please try again!".
    
    global current_caregiver
    global current_patient

    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return
    
    if len(tokens) != 1:
        print("Please try again!")
        return

    if current_caregiver is None:
        # Show appointments for patients
        select_appointments = "SELECT * FROM Appointments WHERE Patient_name = %s ORDER BY Appointment_id ASC"
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_appointments, current_patient.username)
        appointments = cursor.fetchall()
        if len(appointments) == 0:
            print("No appointments found!")
            return
        else:
            print("Appointment ID | Vaccine Name | Date | Caregiver Name")
            for row in appointments:
                print(f"{row['Appointment_id']} {row['Vaccine_name']} {row['Date']} {row['Caregiver_name']}")
    else:
        # Show appointments for caregivers
        select_appointments = "SELECT * FROM Appointments WHERE Caregiver_name = %s ORDER BY Appointment_id ASC"
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_appointments, current_caregiver.username)
        appointments = cursor.fetchall()
        if len(appointments) == 0:
            print("No appointments found!")
            return
        else:
            print("Appointment ID | Vaccine Name | Date | Patient Name")
            for row in appointments:
                print(f"{row['Appointment_id']} {row['Vaccine_name']} {row['Date']} {row['Patient_name']}")


def logout(tokens):
    # logout

    global current_caregiver
    global current_patient

    if current_caregiver is None and current_patient is None:
        print("Please login first.")
        return

    if len(tokens) != 1:
        print("Please try again!")
        return

    current_caregiver = None
    current_patient = None
    print("Successfully logged out!")


def start():
    stop = False
    print()
    print(" *** Please enter one of the following commands *** ")
    print("> create_patient <username> <password>")  # //TODO: implement create_patient (Part 1)
    print("> create_caregiver <username> <password>")
    print("> login_patient <username> <password>")  # // TODO: implement login_patient (Part 1)
    print("> login_caregiver <username> <password>")
    print("> search_caregiver_schedule <date>")  # // TODO: implement search_caregiver_schedule (Part 2)
    print("> reserve <date> <vaccine>")  # // TODO: implement reserve (Part 2)
    print("> upload_availability <date>")
    print("> cancel <appointment_id>")  # // TODO: implement cancel (extra credit)
    print("> add_doses <vaccine> <number>")
    print("> show_appointments")  # // TODO: implement show_appointments (Part 2)
    print("> logout")  # // TODO: implement logout (Part 2)
    print("> Quit")
    print()
    while not stop:
        response = ""
        print("> ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Please try again!")
            break

        response = response.lower()
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Please try again!")
            continue
        operation = tokens[0]
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == "cancel":
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Bye!")
            stop = True
        else:
            print("Invalid operation name!")


if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()
