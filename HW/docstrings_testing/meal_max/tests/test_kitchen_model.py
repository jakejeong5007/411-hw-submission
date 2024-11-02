from contextlib import contextmanager

import pytest
import re
import sqlite3


from meal_max.models.kitchen_model import (
    Meal,
    get_meal_by_id,
    clear_meals,
    get_meal_by_name,
    create_meal,
    delete_meal,
    update_meal_stats,
    get_leaderboard
)

def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

#  Mocking the database connection for tests
@pytest.fixture
def mock_db_connection(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()
    
    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_vale = None
    mock_cursor.fetchall.return_value = []
    mock_conn.commit.return_vale = None
    
    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn # Yield the mocked connection object
    
    mocker.patch("kitchen_model.get_db_connection", mock_get_db_connection)
    
    return mock_cursor  # Return the mock cursor so we can set expectations per test
    
######################################################
#
#    Add and delete
#
######################################################

def test_create_meal(mock_cursor):
    """Test creating a new meal successfully."""
    
    # Call the function to create a new meal
    create_meal("Pizza", "Italian", 10.99, "MED")
    
    expected_query = """
        INSERT INTO meals (meal, cuisine, price, difficulty)
        VALUES (?, ?, ?, ?)
    """
    actual_query = normalize_whitespace(mock_db_connection.execute.call_args[0][0])
    
    # Assert that the SQL query was correct
    assert actual_query == normalize_whitespace(expected_query), "The SQL query did not match the expected structure."
    
    # Extrach the arguments used in the SQL caa (second element of call_args)
    actual_arguments = mock_db_connection.execute.call_args[0][1]
    
    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = ("Pizza", "Italian", 10.99, "MED")
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}"
    
def test_create_meal_invalid_price():
    """Test creating a meal with an invalid price"""
    
    # Attempt to create a meal with a negative price
    with pytest.raises(ValueError, match="Invalid price: -5. Price must be a positive number"):
        create_meal("Pasta", "Italian", -5, "LOW")
        
def test_create_meal_invalid_diffculty():
    """Test creating a meal with an invalid difficulty"""
    
    # Attempt to create a meal with a difficulty that does not exists
    with pytest.raises(ValueError, match="Invalid difficulty level."):
        create_meal("Burger", "American", 8.5, "EXPERT")

def test_create_meal_duplicate(mock_cursor):
    """Test creating a meal with a duplicate name (Should raise an error).""" 
    
    # Simulate that the database will raise an IntegrityError due to a duplicate entry
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: meals.meal")
    
    # Expect the function to raise a ValueError with a specific message when handling the IntegrityError
    with pytest.raises(ValueError, match="Meal with name 'Pizza' already exists"):
        create_meal("Pizza", "Italian", 10.99, "MED")

def test_delete_meal(mock_cursor):
    """Test soft deleting meal by meal ID"""
    
    # Simulate that the song exists (id = 1)
    mock_cursor.fetchone.return_value = ([False])

    # Call the delete_meal function
    delete_meal(1)

    # Normalize the SQL for both queries (SELECT and UPDATE)
    expected_select_sql = normalize_whitespace("SELECT deleted FROM meal WHERE id = ?")
    expected_update_sql = normalize_whitespace("UPDATE meals SET deleted = TRUE WHERE id = ?")
   
    # Access both calls to 'execute()' using 'call_args_list'
    actual_select_sql = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_update_sql = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])
   
    # Ensure the correct SQL queries were executed
    assert actual_select_sql == expected_select_sql, "The SELECT query did not match the expected structure."
    assert actual_update_sql == expected_update_sql, "The UPDATE query did not match the expected structure."
    
    # Ensure the correct arguments were used in both SQL queries
    expected_select_sql = (1,)
    expected_update_sql = (1,)
    
    actual_select_sql = mock_cursor.execute.call_args_list[0][0][1]
    actual_update_sql = mock_cursor.execute.call_args_list[1][0][1]
    
    assert actual_select_sql == expected_select_sql, f"The SELECT query arguments did not match. Expected {expected_select_sql}, got {actual_select_sql}."
    assert actual_update_sql == expected_update_sql, f"The UPDATE query arguments did not match. Expected {expected_update_sql}, got {actual_update_sql}."

def test_delete_meal_bad_id(mock_cursor):
    """Test error when trying to delete a non-existent song."""
    
    # Simulate that no meal exists with the given ID
    mock_cursor.fetchone.return_value = None
    
    # Expect ValueError when attempting to delete a non-existent meal
    with pytest.raises(ValueError, match="Meal with ID 1 not found"):
        delete_meal(1)


def test_delete_meal_already_deleted(mock_cursor):
    """Test error when trying to delte a meal already deleted"""
    
    # Simulate that the meal exists but already marked as deleted
    mock_cursor.fetchone.return_value = ([True])
    
    # Expect ValueError when attempting to delete a meal that's already been
    with pytest.raises(ValueError, match="Meal with ID 1 has already been deleted"):
        delete_meal(1)
    
def test_clear_meal(mock_cursor, mocker):
    """Test clearing entire meals (remove all meals)"""

    # Mock the file reading
    mocker.patch.dict('os.environ', {'SQL_CREATE_TABLE_PATH': 'sql/create_meal_table.sql'})
    mock_open = mocker.patch('builtins.open', mocker.mock_open(read_data="The body of the create statement"))
    
    # Call the clear_database function
    clear_meals()
    
    # Ensure the file was opened using the environment variable's path
    mock_open.assert_called_once_with('sql/create_meal_table.sql', 'r')
    
    # Verify that the correct SQL script was executed
    mock_cursor.executescript.assert_called_once()
    
######################################################
#
#    Get Meal
#
######################################################

def test_get_leaderboard_empty_leaderboard(mock_cursor):
    """Test that retrieving leaderboard returns an empty list when the catalog is empty."""
    
    # Simulate that the leaderboard is empty (no meals)
    mock_cursor.fetchall.return_value = []
    
    result = get_leaderboard()
    assert result == [], f"Expected empty list, but got {result}"
    
def test_get_leaderboard_ordered_by_wins(mock_cursor):
    """Test retrieving the leaderboard ordered by wins."""
    # Simulate leaderboard sorted by wins
    mock_cursor.fetchall.return_value = [
        (1, "Pizza", 10, 8),
        (2, "Burger", 8, 6),
        (3, "Pasta", 6, 4)
    ]

    result = get_leaderboard(sort_by="wins")
    assert len(result) == 3
    assert result[0]["meal"] == "Pizza"
    assert result[1]["meal"] == "Burger"
    assert result[2]["meal"] == "Pasta"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("""
        SELECT id, meal, wins, losses
        FROM meals
        WHERE deleted = FALSE
        ORDER BY wins DESC
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

def test_get_leaderboard_ordered_by_win_pct(mock_cursor):
    """Test retrieving the leaderboard ordered by win percentage."""
    # Simulate leaderboard sorted by win percentage
    mock_cursor.fetchall.return_value = [
        (1, "Pizza", 10, 8),
        (2, "Burger", 8, 5),
        (3, "Pasta", 5, 2)
    ]

    result = get_leaderboard(sort_by="win_pct")
    assert len(result) == 3
    assert result[0]["meal"] == "Pizza"
    assert result[1]["meal"] == "Burger"
    assert result[2]["meal"] == "Pasta"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("""
        SELECT id, meal, wins, losses, (CAST(wins AS FLOAT) / (wins + losses)) AS win_pct
        FROM meals
        WHERE deleted = FALSE
        ORDER BY win_pct DESC
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    assert actual_query == expected_query, "The SQL query did not match the expected structure."    
    
def test_get_leaderboard_invalid_sort_parameter(mock_cursor):
    """Test retrieving the leaderboard with an invalid sort by parameter"""

    with pytest.raises(ValueError, match="Invalid sort parameter: rating"):
        get_leaderboard(sort_by="rating")

def test_get_meal_by_id(mock_cursor):
   
    """Test retrieving a meal by a given ID"""
    # Simulate that the meal exists (id = 1)
    mock_cursor.fetchone.return_value = (1, "Sushi", "Japanese", 15.5, "HIGH")

    # Call the function and check the result
    result = get_meal_by_id(1)
    
    # Expected result based on the simulated fetchone return value
    expected_result = Meal(1, "Sushi", "Japanese", 15.5, "HIGH")
   
    # Ensure the result matches the expected output
    assert result == expected_result, f"Expected {expected_result}, got {result}."
    
    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, meal ,cuisine, price, difficutly, deleted FROM meals WHERE meal = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    
    # Assert that the SQL query was correct
    assert expected_query == actual_query, "The SQL query did not match the expected structure"
    
    # Extract the arguments used in the SQl call
    actual_arguments = mock_cursor.execute.call_args[0][1]
    
    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = (1,)
    assert expected_arguments == actual_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."
    
def test_get_meal_by_id_bad_id(mock_cursor):
    """Test retrieving a meal with an invalid ID"""
   
    # Simulate that the meal does not exists for the given ID
    mock_cursor.execute.return_value = None
    
    # Expect a ValueError when the meal is not found
    with pytest.raises(ValueError, match="Meal with ID 1 not found"):
        get_meal_by_id(1)
        
def test_get_meal_by_id_deleted_meal(mock_cursor):
    """Test retrieving meal that is deleted by given ID"""
   
    # Simulate that the meal was deleted for the given ID
    mock_cursor.execute.return_value = (1, "Ramen", "Japanese", 10.5, "MED", True)
    
    # Expect a ValueError when the meal with the given ID is marked deleted
    with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
        get_meal_by_id(1)
    
def test_get_meal_by_name(mock_cursor):
    """Test retrieving meal by a given name"""
    
    # Simulate that the meal exists (name = Cheeesecake)
    mock_cursor.execute.return_value = (1, "Cheesecake", "Greece", 8.5, "MED")
    
    # Call the function and check the result
    result = get_meal_by_name("Cheesecake")
    
    # Expected result based on the simulated fetchone return value
    expected_result = Meal(1, "Cheesecake", "Greece", 8.5, "MED")
    
    # Ensure the result matches the expected output
    assert result == expected_result, f"Expected {expected_result}, got {result}"
    
    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE meal = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    
    # Assert that the SQL query was correct
    assert expected_query == actual_query, "The SQL query did not match the expected structure"
    
    # Extrach the arguments from the SQL call
    actual_arguments = mock_cursor.execute.call_args[0][1]
    
    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = ("Cheesecake",)
    assert expected_arguments == actual_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}"
    

def test_get_meal_by_name_bad_name(mock_cursor):
    """Test retrieving a meal by an invalid name"""
    
    # Simulate that the meal does not exists for the given name
    mock_cursor.execute.return_value = None
    
    # Expect a ValueError when the meal is not found
    with pytest.raises(ValueError, match="Meal with name 'French Fries' not found"):
        get_meal_by_name("French Fries")
       
def test_get_meal_by_name_deleted_meal(mock_cursor):
    """Test retrieving a deleted meal by a given name"""
    
    # Simulate that the meal was deleted for the given name
    mock_cursor.execute.return_value = (1, "Kimchi", "Korean", 6.5, "MED", True)
    
    # Expect a ValueError when the meal with the given name is marked deleted
    with pytest.raises(ValueError, match="Meal with name 'Kimhchi' has been deleted"):
        get_meal_by_name(1)
        
def test_update_meal_status_win(mock_cursor):
    """Test updating the statistics for a given meal based on the result of a battle"""
  
    # Simulate that the meal with ID = 1 wins a battle
    mock_cursor.fetchone.return_value = [False]
    update_meal_stats(1, "win")
    
    # Ensure the SQL query was executed correctly 
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])
    expected_query = "UPDTAE meals SET battles + 1, wins = wins + 1 where id = ?"
    
    # Assert that the SQL query was correct
    assert expected_query == actual_query, "The SQL query did not match the expected structure"
    
    # Extract the arguments used in the SQL call
    actual_arguments = mock_db_connection.execute.call_args_list[1][0][1]
    expected_arguments = (1,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_update_meal_status_lose(mock_cursor):
    """Test updating meal stats for a loss."""
    
    # Simulate that the meal with ID = 1 loses a battle
    mock_db_connection.fetchone.return_value = [False] 
    update_meal_stats(1, "loss")
    
    # Ensure the SQL query was executed correctly
    expected_query = "UPDATE meals SET battles = battles + 1, losses = losses + 1 WHERE id = ?"
    actual_query = normalize_whitespace(mock_db_connection.execute.call_args_list[1][0][0])

    # Assert that the SQL query was correct
    assert actual_query == normalize_whitespace(expected_query), "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_db_connection.execute.call_args_list[1][0][1]
    expected_arguments = (1,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

   
def test_update_meal_status_deleted_meal(mock_cursor):
    """Test updating meal status for a deleted meal.""" 
    
    # Simulate that the meal was deleted for the given ID
    mock_cursor.execute.return_value = (1, "Ramen", "Japanese", 10.5, "MED", True)
    
    # Expect a ValueError when the meal with the given ID is marked deleted
    with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
        update_meal_stats(1, "win")
    
    
def test_update_meal_status_invalid_ID(mock_cursor):
    """Test updating meal status for an invalid meal ID"""
    
    # Simulate that the meal does not exists for the given ID
    mock_cursor.execute.return_value = None
    
    # Expect a ValueError when the meal is not found
    with pytest.raises(ValueError, match="Meal with ID 1 not found"):
        update_meal_stats(1)
    
def test_update_meal_status_invalid_result(mock_cursor):
    """Test updating meal status with an invalid result"""
   
    # Simulate that the result in invalid (neither win or lose)
    mock_cursor.execute.return_value = [False]
    
    with pytest.raises(ValueError, match="Invalid result: draw. Expected 'win' or 'loss'."):
        update_meal_stats(1, "draw") 
       