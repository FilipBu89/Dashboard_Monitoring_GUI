import re
import sqlite3
from typing import Set, Tuple, List
import datetime

def get_filter_results(date_from=None, date_to=None, configuration=None,
                        identifier=None, filename=None, data_type=None,description_ignore=None) -> str:
    if any((date_from,date_to)):
        try:
            for date in (date_from,date_to):
                datetime.datetime.strptime(date,"%Y-%m-%d")
        except Exception as err:
            return "DateError"

    if "*" in filename:
        filename = re.sub("\*","%",filename)

    description_in: str = ""
    for item in description_ignore:
        description_in += f"'{item}',"
    description_in = description_in.strip(",")
    
    args = (date_from,date_to,configuration,identifier,filename)
     
    query_string = """
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
        AND e.Filename IS NOT NULL
    """
    data_type_nav_filter = """    AND e.ConfigurationName LIKE '%NAV %'
    """
    description_ignore_filter = f"""    AND e.Description NOT IN ({description_in})
    """
    data_type_excl_nav_filter = """    AND e.ConfigurationName NOT LIKE '%NAV %'
    """
    configuration_filter = f"""    AND e.ConfigurationName = '{configuration}'
    """
    identifier_filter = f"""    AND e.Identifier = {identifier}
    """
    filename_filter = f"""    AND e.Filename LIKE '{filename}'
    """
    date_range = f"""    AND DATE(e.Date) BETWEEN '{date_from}' AND '{date_to}'
    """

    query_string+= description_ignore_filter if description_in != "" else ""
    query_string+= data_type_nav_filter if data_type == "NAVs" else ""
    query_string+= data_type_excl_nav_filter if data_type == "Excluding NAVs" else ""
    query_string+= configuration_filter if configuration != "" else ""
    query_string+= identifier_filter if identifier != "" else ""
    query_string+= filename_filter if filename != "" else ""
    query_string+= date_range if all((date_from,date_to)) else ""
    query_string+= """  ) t
    GROUP BY t.ConfigurationName,t.Filename,t.Identifier,t.Date
    ORDER BY t.Date DESC"""

    return query_string

def get_identifier_items(identifier: int,description_ignore: List[str]) -> str:

    description_in: str = ""
    for item in description_ignore:
        description_in += f"'{item}',"
    description_in = description_in.strip(",")

    query_string = f"""
    SELECT DISTINCT
    CASE WHEN e.CompanyName IS NULL THEN '' ELSE e.CompanyName END,
    CASE WHEN e.ConnectionName IS NULL THEN '' ELSE e.ConnectionName END,
    CASE WHEN e.ConfigurationName IS NULL THEN '' ELSE e.ConfigurationName END,
    CASE WHEN e.Filename IS NULL THEN '' ELSE e.Filename END,
    CASE WHEN e.Identifier IS NULL THEN '' ELSE e.Identifier END,
    CASE WHEN e.Worker IS NULL THEN '' ELSE e.Worker END,
    CASE WHEN e.Type IS NULL THEN '' ELSE e.Type END,
    CASE WHEN e.Description IS NULL THEN '' ELSE e.Description END,
    CASE WHEN e.DescriptionBusiness IS NULL THEN '' ELSE e.DescriptionBusiness END,
    CASE WHEN e.Date IS NULL THEN '' ELSE e.Date END,
    CASE WHEN e.DataOwner IS NULL THEN '' ELSE e.DataOwner END
    FROM tblErrorsMonitoring AS e
    LEFT JOIN tblValidationStatus AS v ON v.Identifier = e.Identifier AND v.Description = e.Description
    WHERE e.Identifier = {identifier}
    AND e.Identifier IS NOT NULL
    AND e.Description NOT IN ({description_in})
    AND v.StatusID IS NULL
    """

    return query_string

def validate_identifier_items_pernament(identifier: int, configuration: str, company_name: Set[str], 
                                        description: Set[str], action_type: int, comment: str="") -> str:

    description_in: str = ""
    for item in description:
        description_in += f"'{item}',"
    description_in = description_in.strip(",")

    company_in: str = ""
    for item in company_name:
        company_in += f"'{item}',"
    company_in = company_in.strip(",")

    query_string = f"""
    INSERT INTO tblValidationStatus
    ('Identifier',
    'CompanyName',
    'ConfigurationName',
    'Description',
    'Comment',
    'StatusID',
    'ValidationDate')
    SELECT DISTINCT
    e.Identifier,
    e.CompanyName,
    e.ConfigurationName,
    e.Description,
    '{comment}',
    {action_type},
    DATETIME('now','localtime')
    FROM tblErrorsMonitoring AS e
    WHERE e.Identifier IS NOT NULL
    AND e.Identifier = {identifier}
    AND e.ConfigurationName = '{configuration}'
    AND e.Description IN ({description_in})
    AND e.CompanyName IN ({company_in})
    """

    return query_string

def validate_identifier_items(identifier: int, description: Set[str], action_type: int, comment: str="") -> str:

    description_in: str = ""
    for item in description:
        description_in += f"'{item}',"
    description_in = description_in.strip(",")

    query_string = f"""
    INSERT INTO tblValidationStatus
    ('Identifier',
    'CompanyName',
    'ConfigurationName',
    'Description',
    'Comment',
    'StatusID',
    'ValidationDate')
    SELECT DISTINCT
    e.Identifier,
    e.CompanyName,
    e.ConfigurationName,
    e.Description,
    '{comment}',
    {action_type},
    DATETIME('now','localtime')
    FROM tblErrorsMonitoring AS e
    WHERE e.Identifier IS NOT NULL
    AND e.Identifier = {identifier}
    AND e.Description IN ({description_in})
    """

    return query_string

def validate_escalation_items(identifier_description_item: Tuple[int,str], action_type: int, comment: str = "") -> str:

    query_string = f"""
    UPDATE  tblValidationStatus
    SET 
    StatusID = {action_type},
    Comment = '{comment}'
    WHERE Identifier = {identifier_description_item[0]} AND 
    Description = '{identifier_description_item[1]}'
    """
    return query_string

def get_escalated_items(status_id: int) -> str:

    query_string = f"""
    SELECT DISTINCT
    CASE WHEN Identifier IS NULL THEN '' ELSE Identifier END,
    CASE WHEN CompanyName IS NULL THEN '' ELSE CompanyName END,
    CASE WHEN ConfigurationName IS NULL THEN '' ELSE ConfigurationName END,
    CASE WHEN Description IS NULL THEN '' ELSE Description END,
    CASE WHEN Comment IS NULL THEN '' ELSE Comment END,
    CASE WHEN ValidationDate IS NULL THEN '' ELSE ValidationDate END
    FROM tblValidationStatus
    WHERE StatusID = {status_id}
    """
    return query_string
