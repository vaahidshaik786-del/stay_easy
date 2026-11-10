import os
from datetime import datetime
import sqlite3
from stayeasy.models import Guest, Booking, load_rooms

def create_connection():
    connection = sqlite3.connect("stayeasy.db")
    return connection

def create_rooms_table(connection):
    cursor = connection.cursor()
    cursor.execute("""
        create table if not exists rooms(
            room_no integer primary key,
            room_type text not null,
            floor integer not null
        )
    """)
    connection.commit()

def create_guests_table(connection):
    cursor = connection.cursor()

    cursor.execute("""
        create table if not exists guests(
            guest_id integer primary key autoincrement,
            name text not null,
            mobile text unique not null,
            email text not null
        )
    """)
    connection.commit()

def create_bookings_table(connection):
    cursor = connection.cursor()
    cursor.execute("""
        create table if not exists bookings(
            booking_id text primary key,
            guest_id integer not null,
            room_no integer not null,
            check_in_date text not null,
            check_out_date text not null,
            number_of_guests integer not null,
            breakfast_selected integer not null default 0,
            booking_amount decimal(10, 2) not null,
            status text not null,
            foreign key (guest_id) references guests(guest_id),
            foreign key (room_no) references rooms(room_no)
        )
    """) 
    connection.commit()   

def create_payments_table(connection):
    cursor = connection.cursor()
    cursor.execute("""
        create table if not exists payments(
            payment_id integer primary key autoincrement,
            booking_id text not null,
            amount decimal(10, 2) not null,
            payments_status text not null,
            payment_date text, 
            refund_amount decimal(10, 2) default 0,
            foreign key (booking_id) references bookings(booking_id)
        )
    """) 
    connection.commit()  

def insert_rooms(connection, rooms):
    cursor = connection.cursor()
    for room in rooms:
        cursor.execute("""
            insert into rooms(room_no, room_type, floor)
            values(?, ?, ?)
        """, (room._room_no, room._room_type, room._floor))
    connection.commit()

def insert_guest(connection, guest):
    cursor = connection.cursor()
    cursor.execute("""
        insert into guests(name, mobile, email)
        values(?, ?, ?)
    """, (guest._name, guest._mobile, guest._email))
    connection.commit()

def insert_booking(connection, booking, booking_amount, breakfast_selected):
    cursor = connection.cursor()
    cursor.execute(
        "select guest_id from guests where mobile = ?",
        (booking._guest._mobile,)
    )                 
    guest_data = cursor.fetchone()
    if guest_data is None:
        print("Guest not found")
        return None
    guest_id = guest_data[0]
    cursor.execute("select count(*) from bookings")
    booking_count = cursor.fetchone()[0]
    booking_id = f"B{booking_count + 1:03d}"
    while True:
        cursor.execute(
            "select booking_id from bookings where booking_id = ?",
            (booking_id,)
        )
        if cursor.fetchone() is None:
            break
        booking_count += 1
        booking_id = f"B{booking_count + 1:03d}"
    availability = check_room_availability(connection, booking._room._room_no, str(booking._check_in_date), str(booking._check_out_date))
    if not availability:
        print("Room is not available")
        return None
    cursor.execute("""
        insert into bookings(booking_id, guest_id, room_no, check_in_date, check_out_date, number_of_guests, booking_amount,status, breakfast_selected)
        values(?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (booking_id, guest_id, booking._room._room_no, str(booking._check_in_date), str(booking._check_out_date), booking._number_of_guests, booking_amount, booking._status, int(breakfast_selected) ))
    cursor.execute("""
        insert into payments(booking_id, amount, payments_status, payment_date)
        values(?, ?, ?, ?)
    """, (booking_id, booking_amount, "PAID", str(datetime.now())))
    connection.commit()
    return booking_id

def check_room_availability(connection, room_no, check_in_date, check_out_date):
    cursor = connection.cursor()

    cursor.execute("""
        select * from bookings
        where room_no = ?
        and status in ('CONFIRMED', 'CHECKED_IN')
        and check_in_date < ?
        and check_out_date > ?
    """, (room_no, check_out_date, check_in_date))
    booking_data = cursor.fetchone()
    if booking_data is None:
        return True
    else:
        return False 

def get_completed_stays(connection, mobile):
    cursor = connection.cursor()

    cursor.execute("""
        select count(*) from bookings
        join guests
        on bookings.guest_id = guests.guest_id
        where guests.mobile = ?
        and bookings.status = 'CHECKED_OUT'
    """, (mobile,)) 
    data = cursor.fetchone()
    return data[0]

def get_guest_history(connection, mobile):
    cursor = connection.cursor()

    cursor.execute("""
        select bookings.booking_id, rooms.room_no, bookings.check_in_date, bookings.check_out_date, bookings.booking_amount, bookings.status
        from bookings
        join guests
        on bookings.guest_id = guests.guest_id
        join rooms
        on bookings.room_no = rooms.room_no
        where guests.mobile = ?
    """, (mobile,))    
    booking_history = cursor.fetchall()
    if not booking_history:
        print("No booking history found")
        return
    for booking in booking_history:
        print("Booking ID:", booking[0])
        print("Room Number:", booking[1])
        print("Check-in:", booking[2])
        print("Check-out:", booking[3])
        print("Amount:", booking[4])
        print("Status:", booking[5])
        print("-------------------------")

def view_booking_details(connection, booking_id):
    cursor = connection.cursor()

    cursor.execute("""
        select bookings.booking_id, guests.name, guests.mobile, guests.email, rooms.room_no, rooms.room_type,
            bookings.check_in_date, bookings.check_out_date, bookings.number_of_guests, bookings.booking_amount, bookings.status
        from bookings
        join guests
        on bookings.guest_id = guests.guest_id
        join rooms
        on bookings.room_no = rooms.room_no
        where bookings.booking_id = ?
    """, (booking_id,))
    booking = cursor.fetchone()
    if booking is None:
        print("Booking not found")
        return
    print("\n----- BOOKING DETAILS -----")
    print("Booking ID:", booking[0])
    print("Guest Name:", booking[1])
    print("Mobile:", booking[2])
    print("Email:", booking[3])
    print("Room Number:", booking[4])
    print("Room Type:", booking[5])
    print("Check-in:", booking[6])
    print("Check-out:", booking[7])
    print("Number of Guests:", booking[8])
    print("Booking Amount: Rs.", booking[9])
    print("Booking Status:", booking[10])        

def check_in_booking(connection, booking_id):
    cursor = connection.cursor()

    cursor.execute(
        "select status, check_in_date from bookings where booking_id = ?",
        (booking_id,)
    )      
    booking_data = cursor.fetchone()
    if booking_data is None:
        print("Booking not found")
        return
    status = booking_data[0]
    check_in_date = datetime.strptime(booking_data[1], "%Y-%m-%d").date()
    if status != "CONFIRMED":
        print("Invalid booking status")
        return
    today = datetime.today().date()
    if check_in_date != today:
        print("Check-in is allowed only on the booking date")
        return
    cursor.execute("""
        update bookings
        set status = ?
        where booking_id = ?
    """, ("CHECKED_IN", booking_id))
    connection.commit()
    print("Check_in successful")

def check_out_booking(connection, booking_id):
    cursor = connection.cursor()

    cursor.execute(
        "select status, check_out_date from bookings where booking_id = ?",
        (booking_id,)
    )    
    booking_data = cursor.fetchone()
    if booking_data is None:
        print("Booking not found")
        return
    status = booking_data[0]
    if status != "CHECKED_IN":
        print("Guest must check in first")
        return
    try:
        check_out_date = datetime.strptime(booking_data[1], "%Y-%m-%d").date()
    except ValueError:
        print("Invalid check-out date in database")
        return
    today = datetime.today().date()
    if check_out_date != today:
        print("Checkout is allowed only on the booking check-out date")
        return    
    cursor.execute("""
        update bookings
        set status = ?
        where booking_id = ?
    """, ("CHECKED_OUT", booking_id))
    connection.commit()
    generate_invoice(connection, booking_id)
    print("Checkout successful")

def cancel_booking(connection, booking_id):
    cursor = connection.cursor()

    cursor.execute("""
        select booking_amount, check_in_date, status
        from bookings
        where booking_id = ?
    """, (booking_id,))
    booking_data = cursor.fetchone()
    if booking_data is None:
        print("Booking not found")
        return
    booking_amount = booking_data[0]
    check_in_date = datetime.strptime(booking_data[1], "%Y-%m-%d").date()
    status = booking_data[2]
    if status != "CONFIRMED":
        print("This booking cannot be cancelled")
        return
    days_before_checkin = (check_in_date - datetime.today().date()).days
    if days_before_checkin <= 0:
        print("Cannot cancel after check-in date")
        return
    if days_before_checkin >= 7:
        refund_amount = booking_amount
    elif days_before_checkin >= 2:
        refund_amount = booking_amount * 0.50
    else:
        refund_amount = 0

    cursor.execute("""
        update bookings
        set status = ?
        where booking_id = ?
    """, ("CANCELLED", booking_id))  
    if refund_amount == booking_amount:
        payment_status = "REFUNDED"
    elif refund_amount > 0:
        payment_status = "PARTIALLY_REFUNDED"
    else:
        payment_status = "PAID"         

    cursor.execute("""
        update payments
        set payments_status = ?, refund_amount = ?
        where booking_id = ?
    """,(payment_status, refund_amount, booking_id))
    connection.commit()
    print("Booking cancelled successfully")
    print(f"Refund amount: Rs. {refund_amount}")             

def generate_invoice(connection, booking_id):
    from stayeasy.pricing import calculate_price_breakdown
    cursor = connection.cursor()

    cursor.execute("""
        select guests.name, guests.mobile, guests.email, rooms.room_no, bookings.check_in_date, bookings.check_out_date, bookings.number_of_guests, bookings.booking_amount, rooms.room_type, bookings.breakfast_selected
        from bookings
        join guests on bookings.guest_id = guests.guest_id
        join rooms on bookings.room_no = rooms.room_no
        where bookings.booking_id = ?
    """, (booking_id,))
    invoice_data = cursor.fetchone()
    print("Invoice data:", invoice_data)

    for i in range(len(invoice_data)):
        print(i, invoice_data[i], type(invoice_data[i]))
    if invoice_data is None:
        print("Booking not found")
        return
    guest = Guest(invoice_data[0], invoice_data[1], invoice_data[2])
    rooms = load_rooms()
    # print("Searching for room:", invoice_data[3])

    # for item in rooms:
    #     if item._room_no == invoice_data[3]:
    #         print("MATCH FOUND:", item._room_no)
    room = None
    for item in rooms:
        # print("CSV Room:", item._room_no, type(item._room_no))
        # print("DB Room:", invoice_data[3], type(invoice_data[3]))
        if item._room_no == invoice_data[3]:
            room = item
            break
    if room is None:
        print("Room not found")
        return
    booking = Booking(guest, room, invoice_data[4], invoice_data[5], invoice_data[6])
    breakfast_selected = bool(invoice_data[9])
    price = calculate_price_breakdown(booking, breakfast_selected, connection)
    os.makedirs("invoices", exist_ok=True)
    file_path = f"invoices/{booking_id}.txt"
    with open(file_path, "w") as file:
        file.write("STAY EASY HOTEL INVOICE\n")
        file.write("-----------------------\n")
        file.write(f"Booking ID: {booking_id}\n")
        file.write(f"Guest Name: {invoice_data[0]}\n")
        file.write(f"Mobile: {invoice_data[1]}\n")
        file.write(f"Email: {invoice_data[2]}\n")
        file.write(f"Room Number: {invoice_data[3]}\n")
        file.write(f"Room Type: {invoice_data[8]}\n")
        file.write(f"Check-in: {invoice_data[4]}\n")
        file.write(f"Check-out: {invoice_data[5]}\n")
        file.write(f"Guests: {invoice_data[6]}\n")
        file.write(f"Breakfast Selected: {bool(invoice_data[9])}\n")
        file.write(f"Base Charge: Rs. {price['base_charge']:.2f}\n")
        file.write(f"Weekend Surcharge: Rs. {price['weekend_surcharge']:.2f}\n")
        file.write(f"Extra Guest Charge: Rs. {price['extra_guest_charge']:.2f}\n")
        file.write(f"Breakfast Charge: Rs. {price['breakfast_charge']:.2f}\n")
        file.write(f"Long Stay Discount: Rs. {price['long_stay_discount']:.2f}\n")
        file.write(f"Loyalty Discount: Rs. {price['loyalty_discount']:.2f}\n")
        file.write(f"GST: Rs. {price['gst_amount']:.2f}\n")
        file.write(f"Total Amount: Rs. {invoice_data[7]:.2f}\n")
    print(f"Invoice generated: {file_path}") 


