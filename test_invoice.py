from stayeasy.database import create_connection, generate_invoice

connection = create_connection()

generate_invoice(connection, "B005")

connection.close()