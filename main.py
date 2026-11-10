# from stayeasy.models import *
# from stayeasy.pricing import calculate_base_charge
# print(calculate_base_charge(book1))

# from stayeasy.models import Guest, StandardRoom, Booking
# from stayeasy.pricing import calculate_total_amount

# guest = Guest("Vaahid", "9876543210", "vaahid@gmail.com")

# room = StandardRoom(101, "standard", 1)

# booking = Booking(guest, room, "2026-11-12", "2026-11-15", 2)
# total_amount = calculate_total_amount(booking, True)
# print("Final Booking Amount:", total_amount)

# from stayeasy.database import create_connection
# connection = create_connection()
# print("Database connected successfully")
# connection.close()

# from stayeasy.database import create_connection, create_rooms_table, create_guests_table
# connection = create_connection()
# create_rooms_table(connection)
# create_guests_table(connection)
# print("Rooms and Guests tables created successfully")
# connection.close()

# from stayeasy.models import load_rooms
# from stayeasy.database import create_connection, insert_rooms
# connection = create_connection()
# rooms = load_rooms()
# insert_rooms(connection, rooms)
# print("Rooms inserted successfully")
# connection.close()

# cursor = connection.cursor()
# cursor.execute("SELECT * FROM rooms")
# rooms_data = cursor.fetchall()
# for room in rooms_data:
#     print(room)

# from stayeasy.models import Guest
# from stayeasy.database import create_connection, insert_guest
# connection = create_connection()
# guest = Guest("Vaahid", "9876543210", "vaahid@gmail.com")
# insert_guest(connection, guest)
# print("Guest registered successfully!")
# connection.close()

# cursor = connection.cursor()
# cursor.execute("SELECT * FROM guests")
# guest_data = cursor.fetchall()
# for guest in guest_data:
#     print(guest)

# from stayeasy.models import Guest, StandardRoom, Booking
# from stayeasy.database import (create_connection, create_rooms_table, create_guests_table, create_bookings_table, create_payments_table, insert_rooms, insert_guest, insert_booking)
# from stayeasy.pricing import calculate_total_amount

# connection = create_connection()
# create_rooms_table(connection)
# create_guests_table(connection)
# create_bookings_table(connection)
# create_payments_table(connection)

# guest = Guest("Vaahid", "9876543210", "vaahid@gmail.com")
# room = StandardRoom(101, "Standard", 1)

# booking = Booking(
#     guest,
#     room,
#     "2026-11-12",
#     "2026-11-15",
#     2
# )
# booking_amount = calculate_total_amount(booking, True, connection)
# # insert_booking(connection, booking, booking_amount)
# print("Booking registered successfully!")

# cursor = connection.cursor()
# cursor.execute("SELECT * FROM bookings")
# booking_data = cursor.fetchall()
# for booking in booking_data:
#     print(booking)
# connection.close()    

# from stayeasy.database import check_room_availability

# availability = check_room_availability(
#     connection,
#     101,
#     "2026-11-14",
#     "2026-11-17"
# )

# if availability:
#     print("Room is Available")
# else:
#     print("Room is Not Available")

# from stayeasy.database import(check_room_availability, check_in_booking, check_out_booking, cancel_booking, get_guest_history)
# from stayeasy.reports import(occupancy_report, revenue_report, export_bookings)

from stayeasy.database import create_connection
from stayeasy.menu import run_menu

connection = create_connection()

run_menu(connection)

connection.close()

# from stayeasy.database import create_connection

# connection = create_connection()

# cursor = connection.cursor()
# cursor.execute("PRAGMA table_info(payments)")

# columns = cursor.fetchall()

# for column in columns:
#     print(column)

# connection.close()

# cursor = connection.cursor()

# cursor.execute("""
#     ALTER TABLE bookings
#     ADD COLUMN breakfast_selected INTEGER NOT NULL DEFAULT 0
# """)

# connection.commit()

# from stayeasy.database import create_connection

# connection = create_connection()
# cursor = connection.cursor()

# cursor.execute("""
#     SELECT booking_id, breakfast_selected
#     FROM bookings
# """)

# data = cursor.fetchall()

# for row in data:
#     print(row)

# connection.close()

# from stayeasy.database import create_connection, generate_invoice

# connection = create_connection()

# generate_invoice(connection, "B004")

# connection.close()

# from stayeasy.models import load_rooms

# rooms = load_rooms()

# print("Total valid rooms loaded:", len(rooms))
# print("Check app.log file for invalid records.")

# from stayeasy.database import create_connection

# connection = create_connection()
# cursor = connection.cursor()

# cursor.execute("""
#     SELECT booking_id, payments_status, refund_amount
#     FROM payments
#     WHERE booking_id = ?
# """, ("B013",))

# print(cursor.fetchone())

# connection.close()

# from stayeasy.models import Guest, load_rooms

# guest = Guest("Rahul", "9876543210", "rahul@gmail.com")
# rooms = load_rooms()

# print(guest)
# print(rooms[0])