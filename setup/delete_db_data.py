from mysql import connector


mydb = connector.connect(user='DeviceControl', host='localhost', database='device_control', password='&Bioarineo1')
cursor = mydb.cursor()

tables = ['`values`', '`events`', '`experiments`', '`devices`']

for table in tables:
    query = 'delete from ' + table + ';'
    print(query)
    cursor.execute(query)

mydb.commit()
mydb.close()
