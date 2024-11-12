import pytest
from unittest.mock import patch

from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal

@pytest.fixture()
def battle_model():
    """ Fixture to provide a new instance of BattleModel for each test."""
    return BattleModel()

@pytest.fixture
def sample_meal1():
    return Meal(1, "Meal 1", "Cuisine 1", 1, "LOW")

@pytest.fixture
def sample_meal2():
    return Meal(2, "Meal 2", "Cuisine 2", 2, "HIGH")
    
@pytest.fixture
def sample_battle(sample_meal1, sample_meal2):
    return [sample_meal1, sample_meal2]


def test_battle(battle_model, sample_meal1, sample_meal2):
    """Test a battle between 2 meals"""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    
    assert len(battle_model.combatants) == 2
    assert battle_model.combatants[0].meal == "Meal 1"
    assert battle_model.combatants[1].meal == "Meal 2"
    
    with patch('meal_max.models.battle_model.get_random', return_value=0.1), \
         patch('meal_max.models.battle_model.update_meal_stats') as mock_update_stats:
        
        # Perform the battle
        winner = battle_model.battle()
        
        # Check that the battle method returns the correct winner
        assert winner in ["Meal 1", "Meal 2"]
        
        # Verify that only one combatant remains after the battle
        assert len(battle_model.combatants) == 1
        assert battle_model.combatants[0].meal == winner

        # Verify that update_meal_stats was called correctly
        if winner == "Meal 1":
            mock_update_stats.assert_any_call(1, 'win')
            mock_update_stats.assert_any_call(2, 'loss')
        else:
            mock_update_stats.assert_any_call(2, 'win')
            mock_update_stats.assert_any_call(1, 'loss')
    
def test_battle_not_enough_combatants(battle_model, sample_meal1):
    """Test a battle were there is one or zero combatants"""
    battle_model.prep_combatant(sample_meal1)
    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle."):
        battle_model.battle()

def test_clear_combatants(battle_model, sample_battle):
    """ Test clearing the combatants """
    battle_model.combatants.extend(sample_battle)
    assert len(battle_model.combatants) == 2
    
    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0, "Combatants should be empty after clearing"

def test_get_battle_score(battle_model, sample_meal1):
    """Test getting the score of a meal"""
    expected_score = 6
    calculated_score = battle_model.get_battle_score(sample_meal1)
    assert expected_score == calculated_score

def test_get_combatants(battle_model, sample_battle):
    """Test successfully retrieving all combatants from combatants."""
    battle_model.combatants.extend(sample_battle)
    all_combatants = battle_model.get_combatants()
    assert len(all_combatants) == 2
    assert all_combatants[0].id == 1
    assert all_combatants[1].id == 2

def test_prep_combatant(battle_model, sample_meal1):
    """Test adding a combatant to the combatants."""
    battle_model.prep_combatant(sample_meal1)
    assert len(battle_model.combatants) <= 2
    assert battle_model.combatants[0].meal == 'Meal 1'

def test_add_duplicate_meal_to_combatants(battle_model, sample_meal1):
    """Test error when adding a duplicate meal to the playlist by ID."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal1)
    with pytest.raises(ValueError, match="Combatant list is full, cannot add more combatants."):
        battle_model.prep_combatant(sample_meal1)
