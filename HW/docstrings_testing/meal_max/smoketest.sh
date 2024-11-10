#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5001/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done


###############################################
#
# Health checks
#
###############################################

echo "Health Checks Start"

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}

############################################################
#
# Meals
#
############################################################

clear_meals() {
  echo "Clearing the meal list..."
  curl -s -X DELETE "$BASE_URL/clear-meals" | grep -a '"status": "success"'
}

add_meal() {
  meal=$1
  cuisine=$1
  price=$3
  difficulty=$4

  echo "Adding meal ($meal - $cuisine, $price, $difficulty) to the meal list..."
  curl -s -X POST "$BASE_URL/create-meal" -H "Content-Type: application/json" \
    -d "{\"meal\":\"$meal\", \"cuisine\":\"$cuisine\", \"price\":\"$price\", \"difficulty\":\"$difficulty\"}" | grep -q '"status": "success"'

  if [$? -eq 0]; then
    echo "Meal added successfully."
  else
    echo "Failed to add meal"
    exit 1
  fi 
}

delete_meal() {
  meal_id=$1

  echo "Deleting meal by ID ($meal_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-meal/$meal_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal deleted successfully by ID ($meal_id)."
  else
    echo "Failed to delete meal by ID ($meal_id)."
    exit 1
  fi
}

get_meal_by_id() {
  meal_id=$1

  echo "Getting meal by ID ($meal_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-id/$meal_id")
  if echo "$response" | grep -q '"status": "succeess"'; then
    echo "Meal retrieved succesfully by ID ($meal_id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON (ID $meal_id):"
      echo "$response" |jq .
    fi
  else
    echo "Failed to get meal by ID ($meal_id)."
    exit 1
  fi
}

get_meal_by_name() {
  meal_name=$1

  echo "Getting meal by Name ($meal_name)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-name/$meal_name")
  if echo "$response" | grep -q '"status": "succeess"'; then
    echo "Meal retrieved succesfully by Name ($meal_name)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON (by meal name):"
      echo "$response" |jq .
    fi
  else
    echo "Failed to get meal by Name ($meal_name)."
    exit 1
  fi
}

############################################################
#
# Battle
#
############################################################

battle() {
  echo "Initiating a battle..."
  response=$(curl -s -X GET "$BASE_URL/battle")
  
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Battle done successfully"
  else
    echo "Failed to battle"
    exit 1
  fi
}

clear_combatants() {
  echo "Clearing combatants..."
  response=$(curl -s -X POST "$BASE_URL/clear-combatants")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Combatants cleared successfully."
  else
    echo "Failed to clear combatants"
    exit 1
  fi
}

get_combatants() {
  echo "Getting combatants..."
  response=$(curl -s -X POST "$BASE_URL/get-combatants")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Combatants retrieved successfully."
  else
    echo "Failed to get combatants"
    exit 1
  fi
}

prep_combatant() {
  echo "Preparing combatants..."
  response=$(curl -s -X POST "$BASE_URL/prep-combatants")
  
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Combatants prepared successfully."
  else
    echo "Failed to prepare combatants"
    exit 1
  fi

}



############################################################
#
# Leaderboard
#
############################################################
get_leaderboard() {
  echo "Getting meal leaderboard sorted by wins..."
  response=$(curl -s -X GET "$BASE_URL/meal-leaderboard?sort=wins")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal leaderboard retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Leaderboard JSON (sorted by wins):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal leaderboard."
    exit 1
  fi
}



# Health checks
check_health
check_db

# Clear the meal list
clear_meals


echo "All tests passed succesfully"
