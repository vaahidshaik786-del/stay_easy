from datetime import timedelta
import csv

def occupancy_report(connection, start_date, end_date):
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM rooms")
    total_rooms = cursor.fetchone()[0]
    if total_rooms == 0:
        print("No rooms available in the hotel")
        return

    current_date = start_date
    total_occupancy = 0
    total_nights = 0

    while current_date < end_date:

        cursor.execute("""
            SELECT COUNT(DISTINCT room_no)
            FROM bookings
            WHERE status IN ('CONFIRMED', 'CHECKED_IN')
            AND check_in_date <= ?
            AND check_out_date > ?
        """, (str(current_date), str(current_date)))

        occupied_rooms = cursor.fetchone()[0]

        occupancy_percentage = (occupied_rooms / total_rooms) * 100

        print("Date:", current_date)
        print("Occupied Rooms:", occupied_rooms)
        print("Total Rooms:", total_rooms)
        print("Occupancy:", round(occupancy_percentage, 2), "%")

        total_occupancy += occupancy_percentage
        total_nights += 1

        current_date += timedelta(days=1)

    if total_nights > 0:
        average_occupancy = total_occupancy / total_nights
        print("Average Occupancy:", round(average_occupancy, 2), "%")

def revenue_report(connection):
    cursor = connection.cursor()

    room_types = ["Standard", "Deluxe", "Suite"]

    for room_type in room_types:

        cursor.execute("""
            SELECT COUNT(*), SUM(booking_amount)
            FROM bookings
            JOIN rooms ON bookings.room_no = rooms.room_no
            WHERE rooms.room_type = ?
            AND bookings.status = 'CHECKED_OUT'
        """, (room_type,))

        data = cursor.fetchone()

        completed_stays = data[0]
        room_revenue = data[1] or 0

        print("Room Type:", room_type)
        print("Completed Stays:", completed_stays)
        print("Room Revenue:", room_revenue)

        print("----------------------")   

def export_bookings(connection):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT bookings.booking_id,
               guests.name,
               guests.mobile,
               rooms.room_no,
               rooms.room_type,
               bookings.check_in_date,
               bookings.check_out_date,
               bookings.number_of_guests,
               bookings.booking_amount,
               bookings.status
        FROM bookings
        JOIN guests ON bookings.guest_id = guests.guest_id
        JOIN rooms ON bookings.room_no = rooms.room_no
    """)

    booking_data = cursor.fetchall()

    with open("bookings_export.csv", "w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            "Booking ID", "Guest Name", "Mobile", "Room Number",
            "Room Type", "Check-in", "Check-out", "Guests",
            "Amount", "Status"
        ])

        writer.writerows(booking_data)

    print("Bookings exported successfully")             