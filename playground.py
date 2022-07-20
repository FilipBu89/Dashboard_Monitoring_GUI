import sqlite3
import os
import Utilities.commands as commands
import Utilities.load_data as load_data
import Utilities.db_tables_queries as db_tables_queries
import Utilities.app_queries as app_queries

def main(connection_name: str) -> None:
    # variable storing text query; below just an example; use SQLite syntax for your query
    select_complex_query = """
    SELECT DISTINCT
    t.ConfigurationName,
    t.Filename,
    t.Identifier,
    t.Date,
    COUNT(t.Identifier) AS Items
    FROM
        (
        SELECT DISTINCT
        e.ConfigurationName,
        CASE WHEN e.Filename IS NULL THEN '' ELSE e.Filename END AS Filename,
        CASE WHEN e.Identifier IS NULL THEN '' ELSE e.Identifier END As Identifier,
        Date(e.Date) As Date,
        e.Description,
        e.DescriptionBusiness
        FROM tblErrorsMonitoring e
        LEFT JOIN tblValidationStatus AS v1 ON v1.Identifier = e.Identifier AND v1.Description = e.Description
        LEFT JOIN tblValidationStatus AS v2 ON v2.CompanyName = e.CompanyName AND v2.ConfigurationName = e.ConfigurationName
        AND v2.Description = e.Description   
        WHERE (v1.StatusID IS NULL AND (v2.StatusID IS NULL OR v2.StatusID < 3))
        AND e.ConfigurationName = '1235 - Ongoing Charges from Schroders by FTP'
        ) t
    GROUP BY t.ConfigurationName,t.Filename,t.Identifier,t.Date
    ORDER BY t.Date DESC
    """
    
    select_simple_query = """
    SELECT ConfigurationName, Identifier, COUNT(*) FROM tblErrorsMonitoring
    GROUP BY ConfigurationName, Identifier
    ORDER BY COUNT(*) DESC
    LIMIT 100
    """
    
    insert_query = """
    INSERT INTO tblValidationStatus(Identifier,CompanyName,ConfigurationName,Description,Comment,ValidationDate,StatusID)
    VALUES
    (1782957,
    'Schroders',
    'EPT V1.1 file from Schroders to publiFund support',
    'MissingMandatoryData',
    'Missing data in the source file.',
    DATETIME('now','localtime'),
    3)
    """

    delete_simple_query = """
    DELETE FROM tblErrorsMonitoring 
    WHERE ConfigurationName = 'EPT V1.1 file from Schroders to publiFund support' and Description = 'MissingMandatoryData'
    """
    select_copy_query = """
    ATTACH DATABASE 'Database/MyDataFeedIN_New' AS new_db;

    INSERT INTO new_db.tblErrorsMonitoring
    SELECT * FROM tblErrorsMonitoring;

    INSERT INTO new_db.tblValidationStatus
    SELECT * FROM tblValidationStatus;

    INSERT INTO new_db.tblStatus
    SELECT * FROM tblStatus;
    """
    #conn_new = sqlite3.connect(connection_name_new)
    #commands.create_table(connection_name_new,db_tables_queries.create_monitoring_table,"tblErrorsMonitoring")
    #commands.create_table(connection_name_new,db_tables_queries.create_validation_table,"tblValidationStatus")
    #commands.create_table(connection_name_new,db_tables_queries.create_status_table,"tblStatus")
    
    conn = sqlite3.connect(connection_name)
    #commands.update_insert_data(conn,delete_simple_query)
    #commands.update_insert_data(conn,select_copy_query,True) #function allowing update/insert data into database
    #commands.get_tables_info(connection_name) #function showing info about all database tables
    result = commands.select_data(
        connection=conn,
        query=select_simple_query)# change argument to query parameter if you want to use different query
    for row in result.fetchall():
        print(row)

if __name__ == "__main__":
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    conn_name = os.path.join(curr_dir,"Database/MyDataFeedIN_Current")# user local database location
    conn_name_backup = "S:\Personal Backups\FilipRemote\Python\PubliFund_DataFeedIN_Monitoring\Database\MyDataFeedIN_2022-07-18"
    main(conn_name_backup)




