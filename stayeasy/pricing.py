from stayeasy.database import get_completed_stays
from datetime import timedelta
def calculate_base_charge(booking):
    room_rate = booking._room.get_base_rate()
    number_of_nights = (booking._check_out_date - booking._check_in_date).days
    base_charge = room_rate * number_of_nights
    return base_charge
def calculate_weekend_surcharge(booking):
    room_rate = booking._room.get_base_rate()
    number_of_nights = (booking._check_out_date - booking._check_in_date).days
    weekend_surcharge = 0
    for day in range(number_of_nights):
        current_date = booking._check_in_date + timedelta(days=day)
        day_number = current_date.weekday()
        if day_number in (4, 5):
            weekend_surcharge += room_rate * 0.2
    return weekend_surcharge
def calculate_extra_guest_charge(booking):
    extra_guest_charge = 0    
    number_of_nights = (booking._check_out_date - booking._check_in_date).days
    if booking._number_of_guests > 2:
        extra_guests = booking._number_of_guests - 2
        extra_guest_rate = booking._room.get_extra_guest_rate()
        extra_guest_charge = extra_guests * extra_guest_rate * number_of_nights
    return extra_guest_charge
def calculate_breakfast_charge(booking, breakfast_selected):
    breakfast_charge = 0
    if not booking._room.has_breakfast_included() and breakfast_selected:
        breakfast_rate = booking._room.get_breakfast_charge()
        number_of_nights = (booking._check_out_date - booking._check_in_date).days
        breakfast_charge = breakfast_rate * booking._number_of_guests * number_of_nights
    return breakfast_charge
def calculate_long_stay_discount(booking):
    number_of_nights = (booking._check_out_date - booking._check_in_date).days
    discount_amount = 0
    if number_of_nights >= 7:
        base_charge = calculate_base_charge(booking)
        discount_amount = base_charge * 0.10
    return discount_amount
def calculate_loyalty_discount(booking, connection):
    completed_stays = get_completed_stays(connection, booking._guest._mobile)
    if completed_stays >= 3:
        base_charge = calculate_base_charge(booking)
        discount_amount = base_charge * 0.05
        return discount_amount
    return 0
def calculate_gst(booking, taxable_amount):
    gst_amount = 0
    number_of_nights = (booking._check_out_date - booking._check_in_date).days
    for day in range(number_of_nights):
        current_date = booking._check_in_date + timedelta(days=day)
        daily_rate = booking._room.get_base_rate()
        if current_date.weekday() in (4, 5):
            daily_rate = daily_rate * 1.20
        if daily_rate > 7500:
            gst_amount += daily_rate * 0.18
        else:
            gst_amount += daily_rate * 0.12
    return gst_amount                
       
def calculate_total_amount(booking, breakfast_selected, connection):
    base_charge = calculate_base_charge(booking)
    weekend_surcharge = calculate_weekend_surcharge(booking)
    extra_guest_charge = calculate_extra_guest_charge(booking)
    breakfast_charge = calculate_breakfast_charge(booking, breakfast_selected)
    long_stay_discount = calculate_long_stay_discount(booking) 
    loyalty_discount = calculate_loyalty_discount(booking, connection) 
    subtotal = (base_charge + weekend_surcharge + extra_guest_charge + breakfast_charge)
    amount_after_long_stay = subtotal - long_stay_discount - loyalty_discount
    gst_amount = calculate_gst(booking, amount_after_long_stay)
    final_amount = amount_after_long_stay + gst_amount
    return final_amount 

def calculate_price_breakdown(booking, breakfast_selected, connection):
    base_charge = calculate_base_charge(booking)
    weekend_surcharge = calculate_weekend_surcharge(booking)
    extra_guest_charge = calculate_extra_guest_charge(booking)
    breakfast_charge = calculate_breakfast_charge(booking, breakfast_selected)
    long_stay_discount = calculate_long_stay_discount(booking)
    loyalty_discount = calculate_loyalty_discount(booking, connection)
    subtotal = (
        base_charge
        + weekend_surcharge
        + extra_guest_charge
        + breakfast_charge
    )
    taxable_amount = subtotal - long_stay_discount - loyalty_discount
    gst_amount = calculate_gst(booking, taxable_amount)
    final_amount = taxable_amount + gst_amount
    return {
        "base_charge": base_charge,
        "weekend_surcharge": weekend_surcharge,
        "extra_guest_charge": extra_guest_charge,
        "breakfast_charge": breakfast_charge,
        "long_stay_discount": long_stay_discount,
        "loyalty_discount": loyalty_discount,
        "gst_amount": gst_amount,
        "final_amount": final_amount
    }              