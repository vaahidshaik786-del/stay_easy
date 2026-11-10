from datetime import datetime
from stayeasy.models import Guest, Booking, load_rooms
from stayeasy.exceptions import InvalidGuestError, InvalidBookingError
from stayeasy.database import check_room_availability, insert_guest, insert_booking
from stayeasy.pricing import calculate_total_amount
from stayeasy.database import check_in_booking
from stayeasy.database import check_out_booking
from stayeasy.database import cancel_booking
from stayeasy.database import view_booking_details
from stayeasy.database import get_guest_history
from stayeasy.reports import occupancy_report
from stayeasy.reports import revenue_report
from stayeasy.reports import export_bookings
def show_menu():
    print("\n===== STAY EASY HOTEL =====")
    print("1. Search Room Availability")
    print("2. Create Booking")
    print("3. Check In")
    print("4. Check Out")
    print("5. Cancel Booking")
    print("6. View Booking Details")
    print("7. Guest Stay History")
    print("8. Occupancy Report")
    print("9. Revenue Report")
    print("10. Export Bookings to CSV")
    print("11. Exit")

def run_menu(connection):
    while True:
        show_menu()

        choice = input("Enter your choice: ")

        if choice == "1":
            while True:
                try:
                    room_no = int(input("Enter Room Number: "))
                    if room_no > 0:
                        break
                    else:
                        print("Room number must be positive")
                except ValueError:
                    print("Enter numbers only") 
            while True:
                check_in = input("Enter Check-in Date: ")
                try:
                    check_in_date = datetime.strptime(check_in, "%d-%m-%Y").date()
                    if check_in_date < datetime.today().date():
                        print("Check-in date cannot be in the past")
                        continue
                    break
                except ValueError:
                    print("Invalid date")
            while True:
                check_out = input("Enter check_out Date: ")
                try:
                    check_out_date = datetime.strptime(check_out, "%d-%m-%Y").date()
                    if check_out_date > check_in_date:
                        break
                    else:
                        print("Check-out date must be after check-in date")
                except ValueError:
                    print("Invalid date") 
            availability = check_room_availability(connection, room_no, str(check_in_date), str(check_out_date))
            if availability:
                print("Room is Available")
            else:
                print("Room is not Available")                                        

        elif choice == "2":
            print("Create Booking")
            while True:
                name = input("Enter Guest Name: ").strip()
                if name:
                    break
                else:
                    print("Guest Name cannot be empty")
            while True:        
                mobile = input("Enter Mobile Number: ")
                if len(mobile) == 10 and mobile.isdigit() and mobile.startswith(("6", "7", "8", "9")):
                    break
                else:
                    print("Invalid Mobile Number")
            while True:
                email = input("Enter Email: ").strip()
                if "@" in email and "." in email:
                    break
                else:
                    print("Enter a Valid email address")
            try:
                guest = Guest(name, mobile, email)
            except InvalidGuestError as e:
                print(e)
                continue
            while True:
                room_type = input("Enter Room Type: ").strip().capitalize()
                if room_type in ("Standard", "Deluxe", "Suite"):
                    break
                else:
                    print("Invalid Room type")
                
            while True:
                try:
                    number_of_guests = int(input("Enter Number og Guests: "))
                    if number_of_guests > 0:
                        break
                    else:
                        print("Minimum one guest is required")
                except ValueError:
                    print("Enter numbers only")  
            if room_type == "Standard":
                max_guests = 2
            elif room_type == "Deluxe":
                max_guests = 3
            else:
                max_guests = 4
            if number_of_guests > max_guests:
                print("Guest count exceeds room capacity")
                continue 
            while True:
                check_in = input("Enter Check-in Date: ")
                try:
                    check_in_date = datetime.strptime(check_in, "%d-%m-%Y").date()
                    if check_in_date < datetime.today().date():
                        print("Check-in date cannot be in the past")
                    elif (check_in_date - datetime.today().date()).days > 180:
                        print("Maximum advance booking is 180 days")
                    else:
                        break
                except ValueError:
                    print("Enter a valid date")   
            while True:
                check_out = input("Enter check-out Date: ")
                try:
                    check_out_date = datetime.strptime(check_out, "%d-%m-%Y").date()
                    nights = (check_out_date - check_in_date).days
                    if nights <= 0:
                        print("check-out must be after check-in")
                    elif nights > 30:
                        print("Maximum Stay allowed is 30 nights")
                    else:
                        break
                except ValueError:
                    print("Enter a valid date")  

            rooms = load_rooms()
            available_room = None
            for i in range(len(rooms)):
                for j in range(i + 1, len(rooms)):
                    if rooms[i]._room_no > rooms[j]._room_no:
                        rooms[i], rooms[j] = rooms[j], rooms[i]          
            for room in rooms:
                if room._room_type == room_type:
                    if number_of_guests <= room.get_max_guests():
                        availability = check_room_availability(connection, room._room_no, str(check_in_date), str(check_out_date))
                        if availability:
                            available_room = room
                            break 
            if available_room is None:
                print("Requested room type is not available")
                print("Available alternative room types: ")
                alternative_found = False
                for alternative_room in rooms:
                    if alternative_room._room_type != room_type:
                        if number_of_guests <= alternative_room.get_max_guests():
                            is_available = check_room_availability(connection, alternative_room._room_no, str(check_in_date), str(check_out_date))
                            if is_available:
                                print(alternative_room._room_type, "- Room Number:", alternative_room._room_no)
                                alternative_found = True
                if not alternative_found:
                    print("No alternative rooms available")            
                continue  

            breakfast_selected = False
            if not available_room.has_breakfast_included():
                print("1. Add Breakfast")
                print("2. Skip Breakfast")
                while True:
                    breakfast_choice = input("Enter your choice: ")
                    if breakfast_choice == "1":
                        breakfast_selected = True
                        break
                    elif breakfast_choice == "2":
                        breakfast_selected = False
                        break
                    else:
                        print("Invalid choice. Enter 1 or 2")
            else:
                print("Breakfast is included in this room")  
            try:
                booking = Booking(guest, available_room, str(check_in_date), str(check_out_date), number_of_guests)
                booking_amount = calculate_total_amount(booking, breakfast_selected, connection)
                print("Total Booking Amount: Rs.", round(booking_amount, 2))
            except InvalidBookingError as e:
                print(e)
                continue 
            cursor = connection.cursor()
            cursor.execute(
                "select guest_id from guests where mobile = ?",
                (guest._mobile,)
            )                 
            existing_guest = cursor.fetchone()
            if existing_guest is None:
                insert_guest(connection, guest)
            booking_id = insert_booking(connection, booking, booking_amount, breakfast_selected)
            if booking_id:
                print("\nBooking Successful")
                print("Booking ID:", booking_id)
                print("Room Number:", available_room._room_no)
                print("Total Amount: Rs.", round(booking_amount, 2))    


        elif choice == "3":
            print("Check In")
            booking_id = input("Enter Booking ID: ").strip()
            check_in_booking(connection, booking_id)

        elif choice == "4":
            print("Check Out")
            booking_id = input("Enter Booking ID: ").strip()
            check_out_booking(connection, booking_id)

        elif choice == "5":
            print("Cancel Booking")
            booking_id = input("Enter Booking ID: ").strip()
            cancel_booking(connection, booking_id)

        elif choice == "6":
            print("View Booking Details")
            booking_id = input("Enter Booking ID: ").strip()
            view_booking_details(connection, booking_id)

        elif choice == "7":
            print("Guest Stay History")
            mobile = input("Enter Guest Mobile Number: ").strip()
            get_guest_history(connection, mobile)

        elif choice == "8":
            print("Occupancy Report")
            start_date = input("Enter Start Date: ")
            end_date = input("Enter End Date: ")
            try:
                start_date = datetime.strptime(start_date, "%d-%m-%Y").date()
                end_date = datetime.strptime(end_date, "%d-%m-%Y").date()
                if end_date <= start_date:
                    print("End date must be after start date")
                    continue
                occupancy_report(connection, start_date, end_date)
            except ValueError:
                print("Enter valid dates")    

        elif choice == "9":
            print("Revenue Report")
            revenue_report(connection)

        elif choice == "10":
            print("Export Bookings")
            export_bookings(connection)

        elif choice == "11":
            print("Thank you for using Stay Easy Hotel!")
            break

        else:
            print("Invalid choice. Try again.")    