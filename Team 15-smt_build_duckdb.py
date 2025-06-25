import pandas as pd
import pyarrow.dataset as pads
import pyarrow as pa
import os
import duckdb as db

"""
INTRO:
This is a supplement to the starter code provided by Billy to read in the data! 
Here you can read all of the .csv files into a local, persistent database called DuckDB.
DuckDB provides incredible flexibility and efficiency for the data storage, access, and 
manipulation processes. The use of SQL allows for speedy analytical queries at scale. 

SETUP:
First, make sure to install the duckdb package along with pandas, pyarrow, and os as in 
Billy's code. Then run this script once to load all of the data into your very own DuckDB 
database called smt_2025.db. Once this database is created, you will have access to each of
the 5 tables (ball_pos, game_events, game_info, player_pos, rosters) anywhere on your local 
machine (i.e. you can load the database in R and then access it in Python and vice versa).

NOTES & SUGGESTIONS:
- With the use of DuckDB comes the natural need to use SQL (Structured Query Language).
If you have never used SQL before, NO WORRIES. It is an awesome skill to pick up, and 
you can do it! Check out this link https://duckdb.org/docs/stable/sql/introduction.html#querying-a-table 
for great documentation on an intro to writing SQL queries. 

- The main function shows an example of how to read in data and convert it to a pandas 
DataFrame. For more comprehensive examples of loading data from the database, visit the 
official DuckDB documentation here: https://duckdb.org/docs/stable/clients/python/dbapi
In particular, look for accessing a persistent database. To reiterate, you only need
to run the script below once, and then you can access the smt_2025.db in your analysis code
as shown in the documentation.

- I manually set the smt_2025.db file to be created in the same folder as where you run this script. 
To ensure you are connecting to the correct database when you begin your analysis in other files, 
you must adjust the file path in the connection string to the absolute path of the smt_2025.db 
file that gets generated with this script. If you do not pass the correct path, then connecting to 
the database will create a new empty database file with the same name but in a different folder which 
can become confusing. If you ran this script, and then try to access the database but get a 
CatalogException error, this likely means your path is not pointing to the correct database.
EX: db.connect("absolute/path/to/your/smt_2025.db")

- The process took 30-45 seconds for the data to be fully loaded into the database. I did
not have issues loading the data into memory temporarily, but if you do, consider batching 
the data when creating the 'temp_df' variable (line 137). However, once the data is loaded in 
the database, your query performance should be lightning fast!

- Feel free to reach out to me on the discord @GabeRiedel with any questions, I am happy to help!

"""

# For the data_path argument, include the full file path to the folder that holds the data!
# The schema is set for every table (other than rosters) to prevent mismatched type issues within columns
def readDataSubset(table_type, data_path="SMT-Data-Challenge-2025"):
    if table_type not in ['ball_pos', 'game_events', 'game_info', 'player_pos', 'rosters']:
        #print("Invalid data subset name. Please try again with a valid data subset.")
        return -1
    
    if table_type == 'rosters':
        return pads.dataset(source = os.path.join(os.path.dirname(__name__), data_path, 'rosters.csv'), format = 'csv')
    else:
        return pads.dataset(source = os.path.join(os.path.dirname(__name__), data_path, table_type), format = 'csv', partitioning = ['home_team', 'away_team', 'year', 'day'])


# Create a new table in your persistent DuckDB
def makeDuckDBTable(table_type):

    df_name = table_type + "_df"

    # Manually setting the smt_2025.db file to populate in the working directory.
    # If you want to read from the database later from a different directory
    # then just make sure to pass the path of where smt_2025.db gets created to the 
    # connection string (db.connect("path/to/your/smt_2025.db"))
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, 'smt_2025.db')

    try:
        # Reads data subset into temporary variable
        temp_df = readDataSubset(table_type).to_table().to_pandas()
        with db.connect(db_path) as con:
            # Registers the temp_df under the alias of the value in 'df_name' with DuckDB
            # (necessary in order to be read in as a table)
            con.register(df_name, temp_df)
            # Creates a new table (if one does not already exist) out of the registered
            # data with the name of the given table type
            con.sql(f"CREATE TABLE IF NOT EXISTS {table_type} AS SELECT * FROM {df_name}")
            print(f"Successfully loaded {table_type} into persistent DuckDB", "\n")

    except Exception as e:
        print(f"Invalid Value in - {table_type}", e, "\n")

def main():
    # Create the 5 tables
    makeDuckDBTable('rosters')
    makeDuckDBTable('ball_pos')
    makeDuckDBTable('game_events')
    makeDuckDBTable('game_info')
    makeDuckDBTable('player_pos')

    # Example SQL queries

    # Set up connection to your local database: smt_2025.db 
    # Manually setting the path to the smt_2025.db file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, 'smt_2025.db')
    with db.connect(db_path) as con:
        # Checks the number of rows in each table to 
        # see if they pass the "sniff test"
        df_rosters_rows = con.sql("SELECT COUNT(*) AS count FROM rosters").df()
        df_game_info_rows = con.sql("SELECT COUNT(*) AS count FROM game_info").df()
        df_game_events_rows = con.sql("SELECT COUNT(*) AS count FROM game_events").df()
        df_ball_pos_rows = con.sql("SELECT COUNT(*) AS count FROM ball_pos").df()
        df_player_pos_rows = con.sql("SELECT COUNT(*) AS count FROM player_pos").df()

    print("rosters Table Row Count:", df_rosters_rows["count"][0])
    print("game_info Table Row Count:", df_game_info_rows["count"][0])
    print("game_events Table Row Count:", df_game_events_rows["count"][0])
    print("ball_pos Table Row Count:", df_ball_pos_rows["count"][0])
    print("player_pos Table Row Count:", df_player_pos_rows["count"][0])

    # Expected output
    # rosters Table Row Count:  143
    # game_info Table Row Count:72566
    # game_events Table Row Count:301314
    # ball_pos Table Row Count:2303558
    # player_pos Table Row Count:76350613

if __name__ == "__main__":
    main()

