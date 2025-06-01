from typing import List, Dict
from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..models import Pokemon, Team
import logging
from datetime import datetime
import random

logger = logging.getLogger(__name__)

# Define team roles and their associated stats
TEAM_ROLES = {
    "attacker": ["attack", "special-attack"],
    "defender": ["defense", "special-defense", "hp"],
    "speedster": ["speed"],
    "balanced": ["attack", "defense", "special-attack", "special-defense", "hp", "speed"]
}

async def generate_team(description: str, db: Session) -> Dict:
    """Generate a team of Pokémon based on a natural language description."""
    try:
        # Get all Pokémon from the database
        all_pokemon = db.query(Pokemon).all()
        if not all_pokemon:
            raise HTTPException(status_code=404, detail="No Pokémon found in database")

        # Parse description for requirements
        requirements = parse_team_requirements(description)
        
        # Initialize team
        team = []
        used_types = set()
        
        # Add Pokémon based on requirements
        for role in requirements["roles"]:
            candidates = filter_pokemon_by_role(all_pokemon, role, used_types)
            if not candidates:
                continue
                
            # Select best candidate
            selected = select_best_candidate(candidates, role, requirements)
            team.append(selected)
            used_types.update(selected.types)

        # Fill remaining slots with balanced Pokémon
        while len(team) < 6:
            candidates = [p for p in all_pokemon if p not in team]
            if not candidates:
                break
                
            selected = random.choice(candidates)
            team.append(selected)

        # Create team record
        team_record = Team(
            description=description,
            pokemon_ids=[p.id for p in team],
            created_at=datetime.now().isoformat()
        )
        db.add(team_record)
        db.commit()

        return {
            "description": description,
            "team": [
                {
                    "name": p.name,
                    "types": p.types,
                    "stats": p.stats,
                    "abilities": p.abilities[:3]  # Limit to 3 abilities
                }
                for p in team
            ],
            "team_id": team_record.id
        }

    except Exception as e:
        logger.error(f"Error generating team: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating team")

def parse_team_requirements(description: str) -> Dict:
    """Parse natural language description into team requirements."""
    description = description.lower()
    requirements = {
        "roles": [],
        "types": [],
        "balance": "balanced"
    }

    # Check for roles
    for role in TEAM_ROLES.keys():
        if role in description:
            requirements["roles"].append(role)

    # Check for type requirements
    type_keywords = {
        "fire": "fire",
        "water": "water",
        "grass": "grass",
        "electric": "electric",
        "ice": "ice",
        "fighting": "fighting",
        "poison": "poison",
        "ground": "ground",
        "flying": "flying",
        "psychic": "psychic",
        "bug": "bug",
        "rock": "rock",
        "ghost": "ghost",
        "dragon": "dragon",
        "dark": "dark",
        "steel": "steel",
        "fairy": "fairy"
    }

    for keyword, type_name in type_keywords.items():
        if keyword in description:
            requirements["types"].append(type_name)

    # If no specific roles mentioned, default to balanced
    if not requirements["roles"]:
        requirements["roles"] = ["balanced"]

    return requirements

def filter_pokemon_by_role(pokemon_list: List[Pokemon], role: str, used_types: set) -> List[Pokemon]:
    """Filter Pokémon based on role and type diversity."""
    candidates = []
    for pokemon in pokemon_list:
        # Skip if too many of the same type
        if len(used_types & set(pokemon.types)) >= 2:
            continue

        # Calculate role score
        score = 0
        for stat in TEAM_ROLES[role]:
            if stat in pokemon.stats:
                score += pokemon.stats[stat]

        if score > 0:
            candidates.append((pokemon, score))

    # Sort by score and return top candidates
    candidates.sort(key=lambda x: x[1], reverse=True)
    return [p[0] for p in candidates[:10]]

def select_best_candidate(candidates: List[Pokemon], role: str, requirements: Dict) -> Pokemon:
    """Select the best Pokémon candidate based on role and requirements."""
    if not candidates:
        return None

    # If type requirements exist, prioritize matching types
    if requirements["types"]:
        for pokemon in candidates:
            if any(t in requirements["types"] for t in pokemon.types):
                return pokemon

    # Otherwise, return the first candidate
    return candidates[0] 