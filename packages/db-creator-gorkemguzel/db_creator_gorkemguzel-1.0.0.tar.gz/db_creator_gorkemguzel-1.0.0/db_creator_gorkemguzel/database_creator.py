import sqlite3
import csv
import logging

def create_database(text_file_path):
    x = (input("Please enter the desired database name including the extension.\t"))
    table_name = input("Please enter desired table name.\t")
    logging.basicConfig(format='%(asctime)s | %(levelname)s: %(message)s', level=logging.NOTSET)
    logging.info("Process has been started.")
    logging.info("Please wait, take less than 5 seconds.\n")
    #Importing txt file into list of lists
    with open(text_file_path, newline='') as f:
        reader = csv.reader(f)
        DataArray = list(reader)

    #Creating database on memory
    conn = sqlite3.connect(x)

    # In SQLite, constraints doesn't affect the amount of space the string takes up on disk. Therefore varchar calculation is unneccessary.
    # It will only cause to slow down the code for little to no benefit.
    # If you really want it, it can be done with creating loops to count the length of every element with index (i,1), (i,2)....(i,n) then defining limits for every single column one by one.

    #CREATING THE TABLE

    #First we need to create a table with a dummy column to be able to automatically fill the remaining columns.
    c = conn.cursor()
    command_line = f"CREATE TABLE {table_name} (dummy text)"
    c.execute(command_line)

    #We can see record id for each row by default if we want by rowid function, so, we don't need that column.
    for x in DataArray:
        del x[0]

    #Adding every remaining element of first row of the text file as columns.
    for i in DataArray[0]:
        command_line = f"ALTER TABLE {table_name} ADD COLUMN {i}"
        c.execute(command_line)

    #Deleting the dummy column
    command_line = f"ALTER TABLE {table_name} DROP COLUMN dummy"
    c.execute(command_line)

    #Adding rows. We need to disregard the first row since it forms from names of columns.
    for i in range(1,len(DataArray)):
        command_line = f"INSERT INTO {table_name} VALUES {tuple(DataArray[i])}"
        c.execute(command_line)

    logging.info("Database is ready to use.")

    conn.commit()
    conn.close