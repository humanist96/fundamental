import sqlite3
import streamlit as st
import pandas as pd
import os


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Exception as e:
        st.write(e)

    return conn


def create_database():
    st.markdown("# Create Database")

    st.write("""A database in SQLite is just a file on same server. 
    By convention their names always end in .db""")


    db_filename = st.text_input("DB Filename")
    create_db = st.button('Create Database')

    if create_db:
        if db_filename.endswith('.db'):
            conn = create_connection(db_filename)
            st.write(conn) # success message?
        else: 
            st.write('DB filename must end with .db, please retry.')


def upload_data():
    st.markdown("# Upload Data")
    # https://discuss.streamlit.io/t/uploading-csv-and-excel-files/10866/2
    #sqlite_dbs = [file for file in os.listdir('.') if file.endswith('.db')]
    #db_filename = st.selectbox('DB Filename', sqlite_dbs)
    db_filename = './files/test.db'
    table_name = st.text_input('Table Name to Insert')
    conn = create_connection(db_filename)
    uploaded_file = st.file_uploader('Choose a XLSX file')
    if uploaded_file is not None:
        #read csv
        try:
            df = pd.read_excel(uploaded_file)
            df.to_sql(name=table_name, con=conn)
            st.write('Data uploaded successfully. These are the first 5 rows.')
            st.dataframe(df.head(5))
            conn.commit()
            conn.close()
        except Exception as e:
            st.write(e)
    else:
        st.warning("you need to upload excel file.")
def run_query():
    st.markdown("# Run Query")
    # sqlite_dbs = [file for file in os.listdir('.') if file.endswith('.db')]
    db_filename = './files/rebuild_house.db'
    conn = create_connection(db_filename)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    table_list = []
    for row in cursor:
        table_list.append(row[0])


    table_name = st.selectbox('DB Table name', table_list)

    query = st.text_area("SQL Query", height=100)
    
    # conn = create_connection("./files/usfinance.db")

    submitted = st.button('Run Query')

    if submitted:
        try:
            query = conn.execute(query)
            cols = [column[0] for column in query.description]
            results_df= pd.DataFrame.from_records(
                data = query.fetchall(), 
                columns = cols
            )
            st.dataframe(results_df)
        except Exception as e:
            st.write(e)
       
        # conn.close()

    st.sidebar.markdown("# Run Query")

page_names_to_funcs = {
    "Create Database": create_database,
    "Upload Data": upload_data,
    "Run Query": run_query,
}

selected_page = st.sidebar.selectbox("Select a page", page_names_to_funcs.keys())
page_names_to_funcs[selected_page]()