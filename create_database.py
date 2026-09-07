from database import connect, create_schema

connection, cursor = connect()
create_schema(cursor)
connection.commit()
connection.close()

print("Database Ready.")
