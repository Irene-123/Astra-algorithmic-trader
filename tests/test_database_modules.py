import pytest
import os
from lib.modules.database.database_manager import Manager
import psycopg2
from unittest.mock import patch
obj= Manager() 
obj.setup_db() 

@pytest.mark.parametrize(
    "credentials",
    [
        {
            "ASTRA_HISTORICAL_DATA": {"DATABASE": "test_historical"},
            "ASTRA_USER_DB": {"DATABASE": "test_user"}
        },
        {
            "ASTRA_HISTORICAL_DATA": {"DATABASE": "another_historical"},
            "ASTRA_USER_DB": {"DATABASE": "another_user"}
        },
        # Add more test cases as needed
    ]
)
def test_setup_db(credentials):
    def connect_db(database):
        conn= psycopg2.connect(f'postgresql://{username}:{password}@localhost:{host}/{database}') 
        return conn
    with patch("setup_db.connect_db", side_effect=connect_db):
        # Call the setup_db function
        result = obj.setup_db(credentials)
        
        # Assert the result is True
        assert result == True
        
        # Check if the databases are created
        conn = connect_db('DEFAULT_DB')
        cursor = conn.cursor()
        
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'astra_historical_data'")
        exists = cursor.fetchone()
        assert exists is not None
        
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'astra_user_db'")
        exists = cursor.fetchone()
        assert exists is not None
        
        cursor.close()
        conn.close()


