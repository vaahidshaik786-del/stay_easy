from stayeasy.exceptions import InvalidGuestError, InvalidBookingError, InvalidBookingStatusError
from abc import ABC, abstractmethod
from datetime import datetime
import csv
class Room(ABC):
    def __init__(self, room_no, room_type, floor):
        self._room_no = room_no
        self._room_type = room_type
        self._floor = floor
    def __str__(self):
        return f"Room No: {self._room_no}, Type: {self._room_type}, Floor: {self._floor}"    
    @abstractmethod
    def get_base_rate(self):
        pass
    @abstractmethod
    def get_max_guests(self):
        pass
    @abstractmethod
    def has_breakfast_included(self):
        pass
    @abstractmethod
    def get_breakfast_charge(self):
        pass
    @abstractmethod
    def get_extra_guest_rate(self):
        pass
class StandardRoom(Room):
    def __init__(self, room_no, room_type, floor):
        super().__init__(room_no, room_type, floor)  
    def get_base_rate(self):
        return 2500
    def get_max_guests(self):
        return 2
    def has_breakfast_included(self):
        return False
    def get_breakfast_charge(self):
        return 350
    def get_extra_guest_rate(self):
        return 0
class DeluxeRoom(Room):
    def __init__(self, room_no, room_type, floor):
        super().__init__(room_no, room_type, floor)
    def get_base_rate(self):
        return 4000
    def get_max_guests(self):
        return 3
    def has_breakfast_included(self):
        return True
    def get_breakfast_charge(self):
        return 0
    def get_extra_guest_rate(self):
        return 800
class SuiteRoom(Room):
    def __init__(self, room_no, room_type, floor):
        super().__init__(room_no, room_type, floor)
    def get_base_rate(self):
        return 7500
    def get_max_guests(self):
        return 4  
    def has_breakfast_included(self):
        return True
    def get_breakfast_charge(self):
        return 0
    def get_extra_guest_rate(self):
        return 800             
# standard = StandardRoom(101, "Standard", 1)
# deluxe = DeluxeRoom(201, "Deluxe", 2)
# suite = SuiteRoom(301, "Suite", 3)
# print(standard.get_base_rate())
# print(standard.get_max_guests())
# print(standard.has_breakfast_included())
# print(standard.get_breakfast_charge())
# print(deluxe.get_base_rate())
# print(deluxe.get_max_guests())
# print(deluxe.has_breakfast_included())
# print(deluxe.get_breakfast_charge())
# print(suite.get_base_rate())
# print(suite.get_max_guests())
# print(suite.has_breakfast_included())
# print(suite.get_breakfast_charge())
def load_rooms():
    rooms = []
    with open("rooms.csv", "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                room_no = int(row["room_no"])
                floor = int(row["floor"])
            except ValueError:
                with open("app.log", "a") as log_file:
                    log_file.write(f"Invalid room number or floor: {row}\n")
                continue    
            room_type = row["room_type"].strip().capitalize()
            if room_no <= 0:
                with open("app.log", "a") as log_file:
                    log_file.write(f"Invalid room number: {row}\n")
                continue
            if floor <= 0:
                with open("app.log", "a") as log_file:
                    log_file.write(f"Invalid floor number: {row}\n")
                continue
            duplicate = False
            for room in rooms:
                if room._room_no == room_no:
                    duplicate = True
                    break
            if duplicate:
                with open("app.log", "a") as log_file:
                    log_file.write(f"Duplicate room number: {room_no}\n")
                continue  
            if room_type == "Standard":
                room = StandardRoom(room_no, room_type, floor)
            elif room_type == "Deluxe":
                room = DeluxeRoom(room_no, room_type, floor)
            elif room_type == "Suite":
                room = SuiteRoom(room_no, room_type, floor)
            else:
                with open("app.log", "a") as log_file:
                    log_file.write(f"Invalid room type: {row}\n")
                continue
            rooms.append(room)
    return rooms
class Guest:
    def __init__(self, name, mobile_no, email):
        if not name.strip():
            raise InvalidGuestError("Guest Name cannot be empty")
        else:
            self._name = name.strip()
        if "@" not in email or "." not in email:
            raise InvalidGuestError("Enter Valid email Address")
        else:
            self._email = email
        if len(mobile_no) != 10 or not mobile_no.isdigit() or not mobile_no.startswith(("6","7","8","9")):
            raise InvalidGuestError("Enter Valid mobile number")
        self._mobile = mobile_no 
    def __str__(self):
        return f"Guest: {self._name}, Mobile: {self._mobile}, Email: {self._email}"    
# try:
#     guest1 = Guest("Vaahid", "7382327648", "vaahidshaik@gmail.com")
# except InvalidGuestError as e:
#     print(e)
# try:
#     guest2 = Guest("Abdul", "5678912340", "sunny@gmail.com")
# except InvalidGuestError as e:
#     print(e)
# try:        
#     guest3 = Guest("Raju", "987654321", "raju123@gmail.com")
# except InvalidGuestError as e:
#     print(e)      
# print(guest1)
# print(guest2)
# print(guest3)
class Booking():
    booking_count = 0
    def __init__(self, guest, room, check_in_date, check_out_date, number_of_guests):
        self._guest = guest
        self._room = room
        check_in_date = datetime.strptime(check_in_date, "%Y-%m-%d").date()
        check_out_date = datetime.strptime(check_out_date, "%Y-%m-%d").date()
        if check_in_date >= check_out_date:
            raise InvalidBookingError("Enter proper Check-In date")
        number_of_nights = (check_out_date - check_in_date).days
        if number_of_nights > 30:
            raise InvalidBookingError("Maximum stay allowed is 30 nights")
        self._check_in_date = check_in_date
        self._check_out_date = check_out_date
        if number_of_guests <= 0:
            raise InvalidBookingError("Atleast one guest is required")
        if number_of_guests > room.get_max_guests():
            raise InvalidBookingError("Guest count exceeds room capacity")
        self._number_of_guests = number_of_guests
        Booking.booking_count += 1
        self._booking_id = f"B{Booking.booking_count:03d}"
        self._status = "CONFIRMED"
    def check_in(self):
        if self._status == "CONFIRMED":
            self._status = "CHECKED_IN"
        else:
            raise InvalidBookingStatusError("Cannot Check-in in this booking") 
    def check_out(self):
        if self._status == "CHECKED_IN":
            self._status = "CHECKED_OUT"
        else:
            raise InvalidBookingStatusError("Guest must check in first")
    def cancellation(self):
        if self._status != "CONFIRMED":
            raise InvalidBookingStatusError("This Booking cannot be cancelled")
        cancellation_date = datetime.today().date()
        days_before_checkin = (self._check_in_date - cancellation_date).days
        if days_before_checkin <= 0:
            raise InvalidBookingStatusError("Cannot cancel after check-in date")
        if days_before_checkin >= 7:
            refund_rate = 1.0
        elif days_before_checkin >= 2:
            refund_rate = 0.5
        else:
            refund_rate = 0.0  
        self._status = "CANCELLED"     
    def __str__(self):
        return f"Booking ID: {self._booking_id}, Status: {self._status}"                                  
# guest1 = Guest("Vaahid", "7891236540", "vaahid@gmail.com")
# guest2 = Guest("Abdul", "9876543210", "Abdulshaik@gmail.com")
# room1 = StandardRoom(101, "Standard", 1)
# room2 = StandardRoom(102, "Standard", 1)
# book1 = Booking(guest1, room1, "2026-11-10", "2026-11-12", 2)
# book2 = Booking(guest2, room2, "2026-11-08", "2026-11-10", 2) 

# print(book1.booking_id)    
# print(book2.booking_id)  
        

        