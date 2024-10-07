from typing import Optional

from wildlife_tracker.habitat_management.habitat import Habitat

class MigrationPath:
    def __init__(self,
                 path_id: int,
                 current_location: str,
                 start_location: Habitat,
                 destination: Habitat,
                 ) -> None:
        self.path_id = path_id
        self.current_location = current_location
        self.start_location = start_location
        self.destination = destination

    def update_migration_path_details(path_id: int, **kwargs) -> None:
        pass

    def get_migration_path_details(path_id) -> dict:
        pass