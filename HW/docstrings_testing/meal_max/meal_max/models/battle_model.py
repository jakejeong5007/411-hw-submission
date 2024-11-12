import logging
from typing import List

from meal_max.models.kitchen_model import Meal, update_meal_stats
from meal_max.utils.logger import configure_logger
from meal_max.utils.random_utils import get_random


logger = logging.getLogger(__name__)
configure_logger(logger)


class BattleModel:
    """
    Manages battles between meals, determining a winner based on specific scoring criteria.

    Methods:
        battle() -> str: Conducts a battle between two meals and returns the winner.
        clear_combatants() -> None: Clears the list of current combatants.
        get_battle_score(combatant: Meal) -> float: Calculates a battle score for a given meal based on price, cuisine, and difficulty.
        get_combatants() -> List[Meal]: Retrieves the current list of combatants.
        prep_combatant(combatant_data: Meal) -> None: Adds a meal as a combatant for battle.

    Raises:
        ValueError: If there are not enough combatants to start a battle or if the combatants list is full.
    """
    def __init__(self):
        self.combatants: List[Meal] = []

    def battle(self) -> str:
        """
        Conducts a battle beteween two meals and returns the name of the winner.

        Returns:
            str: The name of he winning meal.
            
        Rasises:
            ValueError: If there are fewer than two combatants for the battle.
        """ 
                
        logger.info("Two meals enter, one meal leaves!")

        if len(self.combatants) < 2:
            logger.error("Not enough combatants to start a battle.")
            raise ValueError("Two combatants must be prepped for a battle.")

        combatant_1 = self.combatants[0]
        combatant_2 = self.combatants[1]

        # Log the start of the battle
        logger.info("Battle started between %s and %s", combatant_1.meal, combatant_2.meal)

        # Get battle scores for both combatants
        score_1 = self.get_battle_score(combatant_1)
        score_2 = self.get_battle_score(combatant_2)

        # Log the scores for both combatants
        logger.info("Score for %s: %.3f", combatant_1.meal, score_1)
        logger.info("Score for %s: %.3f", combatant_2.meal, score_2)

        # Compute the delta and normalize between 0 and 1
        delta = abs(score_1 - score_2) / 100

        # Log the delta and normalized delta
        logger.info("Delta between scores: %.3f", delta)

        # Get random number from random.org
        random_number = get_random()

        # Log the random number
        logger.info("Random number from random.org: %.3f", random_number)

        # Determine the winner based on the normalized delta
        if delta > random_number:
            winner = combatant_1
            loser = combatant_2
        else:
            winner = combatant_2
            loser = combatant_1

        # Log the winner
        logger.info("The winner is: %s", winner.meal)

        # Update stats for both combatants
        update_meal_stats(winner.id, 'win')
        update_meal_stats(loser.id, 'loss')

        # Remove the losing combatant from combatants
        self.combatants.remove(loser)

        return winner.meal

    def clear_combatants(self):
        """
        Clears the list of current combatants, removing all entries.
        """
        
        logger.info("Clearing the combatants list.")
        self.combatants.clear()

    def get_battle_score(self, combatant: Meal) -> float:
        """
        Calculates a battle score for a given meal based on its price, cuisine, and difficulty.

        Args:
            combatant (Meal): The meal object for which to calculate the battle score.

        Returns:
            float: The calculated score based on the meal's attributes.
        """
        
        difficulty_modifier = {"HIGH": 1, "MED": 2, "LOW": 3}

        # Log the calculation process
        logger.info("Calculating battle score for %s: price=%.3f, cuisine=%s, difficulty=%s",
                    combatant.meal, combatant.price, combatant.cuisine, combatant.difficulty)

        # Calculate score
        score = (combatant.price * len(combatant.cuisine)) - difficulty_modifier[combatant.difficulty]

        # Log the calculated score
        logger.info("Battle score for %s: %.3f", combatant.meal, score)

        return score

    def get_combatants(self) -> List[Meal]:
        """
        Retrieves the current list of combatants.

        Returns:
            List[Meal]: A list of meal objects currently in the combatants list.
        """
        
        logger.info("Retrieving current list of combatants.")
        return self.combatants

    def prep_combatant(self, combatant_data: Meal):
        """
        Adds a meal to the list of combatants.

        Args:
            combatant_data (Meal): The meal object to add as a combatant.

        Raises:
            ValueError: If the combatants list already contains two entries.
        """
        
        if len(self.combatants) >= 2:
            logger.error("Attempted to add combatant '%s' but combatants list is full", combatant_data.meal)
            raise ValueError("Combatant list is full, cannot add more combatants.")

        # Log the addition of the combatant
        logger.info("Adding combatant '%s' to combatants list", combatant_data.meal)

        self.combatants.append(combatant_data)

        # Log the current state of combatants
        logger.info("Current combatants list: %s", [combatant.meal for combatant in self.combatants])
