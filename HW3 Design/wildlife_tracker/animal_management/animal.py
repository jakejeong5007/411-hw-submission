from typing import Any, Optional

class Animal:

    def __init__(self,
                animal_id: int,
                species: str,
                habitat_id: int,
                health_status: Optional[str] = None,
                age: Optional[int] = None,) -> None:
        self.age = age
        self.animal_id = animal_id
        self.habitat_id = habitat_id
        self.species = species
        self.health_status = health_status

    def update_animal_details(self, animal_id: int, **kwargs: Any) -> None:
        pass

    def get_animal_details(self, animal_id) -> dict[str, Any]:
        pass
