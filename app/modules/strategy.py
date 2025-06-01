import requests
from typing import List, Dict
from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..models import Pokemon
import logging

logger = logging.getLogger(__name__)

POKE_API_BASE_URL = "https://pokeapi.co/api/v2"

# Cache for type effectiveness
type_effectiveness_cache = {}

async def get_type_effectiveness(attacking_type: str, defending_type: str) -> float:
    """Get the effectiveness multiplier between two types."""
    try:
        if (attacking_type, defending_type) in type_effectiveness_cache:
            return type_effectiveness_cache[(attacking_type, defending_type)]

        response = requests.get(f"{POKE_API_BASE_URL}/type/{attacking_type}")
        response.raise_for_status()
        data = response.json()

        # Find the effectiveness against the defending type
        for relation in data["damage_relations"]["double_damage_to"]:
            if relation["name"] == defending_type:
                type_effectiveness_cache[(attacking_type, defending_type)] = 2.0
                return 2.0

        for relation in data["damage_relations"]["half_damage_to"]:
            if relation["name"] == defending_type:
                type_effectiveness_cache[(attacking_type, defending_type)] = 0.5
                return 0.5

        for relation in data["damage_relations"]["no_damage_to"]:
            if relation["name"] == defending_type:
                type_effectiveness_cache[(attacking_type, defending_type)] = 0.0
                return 0.0

        type_effectiveness_cache[(attacking_type, defending_type)] = 1.0
        return 1.0

    except Exception as e:
        logger.error(f"Error getting type effectiveness: {str(e)}")
        raise HTTPException(status_code=500, detail="Error calculating type effectiveness")

async def find_counters(pokemon_name: str, db: Session) -> List[Dict]:
    """Find effective counters for a given Pokémon."""
    try:
        # Get the target Pokémon
        target = db.query(Pokemon).filter(Pokemon.name == pokemon_name.lower()).first()
        if not target:
            raise HTTPException(status_code=404, detail="Pokémon not found")

        # Get all Pokémon from the database
        all_pokemon = db.query(Pokemon).all()
        
        # Calculate effectiveness scores for each Pokémon
        counter_scores = []
        for pokemon in all_pokemon:
            if pokemon.name == target.name:
                continue

            # Calculate type effectiveness
            effectiveness_score = 1.0
            for attacker_type in pokemon.types:
                for defender_type in target.types:
                    effectiveness = await get_type_effectiveness(attacker_type, defender_type)
                    effectiveness_score *= effectiveness

            # Consider stats
            stat_score = sum(pokemon.stats.values()) / sum(target.stats.values())

            # Calculate final score
            final_score = effectiveness_score * stat_score

            counter_scores.append({
                "pokemon": pokemon,
                "score": final_score,
                "effectiveness": effectiveness_score,
                "stat_ratio": stat_score
            })

        # Sort by score and return top 5 counters
        counter_scores.sort(key=lambda x: x["score"], reverse=True)
        return counter_scores[:5]

    except Exception as e:
        logger.error(f"Error finding counters: {str(e)}")
        raise HTTPException(status_code=500, detail="Error finding counters")

async def get_type_matchup(pokemon_name: str, db: Session) -> Dict:
    """Get type matchup information for a Pokémon."""
    try:
        pokemon = db.query(Pokemon).filter(Pokemon.name == pokemon_name.lower()).first()
        if not pokemon:
            raise HTTPException(status_code=404, detail="Pokémon not found")

        matchup_info = {
            "pokemon": pokemon.name,
            "types": pokemon.types,
            "strong_against": [],
            "weak_against": [],
            "immune_to": []
        }

        # Get type information for each of the Pokémon's types
        for type_name in pokemon.types:
            response = requests.get(f"{POKE_API_BASE_URL}/type/{type_name}")
            response.raise_for_status()
            type_data = response.json()

            # Add strong matchups
            for relation in type_data["damage_relations"]["double_damage_to"]:
                if relation["name"] not in matchup_info["strong_against"]:
                    matchup_info["strong_against"].append(relation["name"])

            # Add weak matchups
            for relation in type_data["damage_relations"]["half_damage_to"]:
                if relation["name"] not in matchup_info["weak_against"]:
                    matchup_info["weak_against"].append(relation["name"])

            # Add immunities
            for relation in type_data["damage_relations"]["no_damage_to"]:
                if relation["name"] not in matchup_info["immune_to"]:
                    matchup_info["immune_to"].append(relation["name"])

        return matchup_info

    except Exception as e:
        logger.error(f"Error getting type matchup: {str(e)}")
        raise HTTPException(status_code=500, detail="Error getting type matchup") 