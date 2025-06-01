from typing import List, Dict
from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..models import Pokemon
import logging

logger = logging.getLogger(__name__)

async def compare_pokemon(pokemon1_id: str, pokemon2_id: str, db: Session) -> Dict:
    """Compare two Pokémon and return their differences."""
    try:
        # Fetch both Pokémon
        pokemon1 = db.query(Pokemon).filter(Pokemon.name == pokemon1_id.lower()).first()
        pokemon2 = db.query(Pokemon).filter(Pokemon.name == pokemon2_id.lower()).first()

        if not pokemon1 or not pokemon2:
            raise HTTPException(status_code=404, detail="One or both Pokémon not found")

        # Compare stats
        stats_comparison = {}
        for stat in pokemon1.stats:
            diff = pokemon1.stats[stat] - pokemon2.stats[stat]
            stats_comparison[stat] = {
                "pokemon1": pokemon1.stats[stat],
                "pokemon2": pokemon2.stats[stat],
                "difference": diff
            }

        # Compare types
        type_comparison = {
            "pokemon1_types": pokemon1.types,
            "pokemon2_types": pokemon2.types,
            "common_types": list(set(pokemon1.types) & set(pokemon2.types))
        }

        # Compare abilities
        ability_comparison = {
            "pokemon1_abilities": pokemon1.abilities,
            "pokemon2_abilities": pokemon2.abilities,
            "common_abilities": list(set(pokemon1.abilities) & set(pokemon2.abilities))
        }

        # Compare moves
        move_comparison = {
            "pokemon1_moves": pokemon1.moves,
            "pokemon2_moves": pokemon2.moves,
            "common_moves": list(set(pokemon1.moves) & set(pokemon2.moves))
        }

        return {
            "stats_comparison": stats_comparison,
            "type_comparison": type_comparison,
            "ability_comparison": ability_comparison,
            "move_comparison": move_comparison,
            "summary": {
                "pokemon1": {
                    "name": pokemon1.name,
                    "total_stats": sum(pokemon1.stats.values())
                },
                "pokemon2": {
                    "name": pokemon2.name,
                    "total_stats": sum(pokemon2.stats.values())
                }
            }
        }

    except Exception as e:
        logger.error(f"Error comparing Pokémon: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error") 