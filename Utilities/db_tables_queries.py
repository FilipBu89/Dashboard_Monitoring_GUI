"""Module is only storing SQL queries"""

#SQL Query for creating monitoring table storing list of all errors
create_monitoring_table = """
    DROP TABLE IF EXISTS {table_name};
            
    CREATE TABLE {table_name}
    (
    [ID] INTEGER PRIMARY KEY,
    [CompanyName] TEXT,
    [ConnectionName] TEXT,
    [ConfigurationName] TEXT,
    [Filename] TEXT,
    [Identifier] INTEGER,
    [Worker] TEXT,
    [Type] TEXT,
    [Description] TEXT,
    [DescriptionBusiness] TEXT,
    [Date] TEXT,
    [DataOwner] TEXT
    )
    """

#SQL Query for creating table storing action status of error item
create_validation_table = """
    DROP TABLE IF EXISTS {table_name};
            
    CREATE TABLE {table_name}
    (
    [ID] INTEGER PRIMARY KEY,
    [Identifier] INTEGER,
    [CompanyName] TEXT,
    [ConfigurationName] TEXT,
    [Description] TEXT,
    [Comment] TEXT,
    [StatusID] INTEGER NOT NULL,
    [ValidationDate] TEXT NOT NULL,
    FOREIGN KEY(Identifier)
        REFERENCES Monitoring(Identifier)
    )
    """

#SQL Query for creating table storing action status of error item
# 0 - Junked, 1 - Forced, 2 - Escalated, 3 - Ignored
create_status_table = """
    DROP TABLE IF EXISTS {table_name};
            
    CREATE TABLE {table_name}
    (
    [ID] INTEGER PRIMARY KEY,
    [StatusID] INTEGER NOT NULL,
    [StatusName] TEXT NOT NULL,
    FOREIGN KEY(StatusID)
        REFERENCES tblValidationStatus(StatusID)
    )
    """

#SQL Query for creating table storing action status of error item
get_max_data = """
    SELECT Max(Date)
    FROM tblErrorsMonitoring
    """



