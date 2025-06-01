import requests
from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..models import Pokemon
import logging

logger = logging.getLogger(__name__)

POKE_API_BASE_URL = "https://pokeapi.co/api/v2"

async def fetch_pokemon_data(pokemon_id_or_name: str, db: Session):
    """Fetch Pokémon data from PokeAPI or cache."""
    try:
        # Check cache first
        cached_pokemon = db.query(Pokemon).filter(
            Pokemon.name == pokemon_id_or_name.lower()
        ).first()
        
        if cached_pokemon:
            logger.info(f"Retrieved {pokemon_id_or_name} from cache")
            return cached_pokemon

        # Fetch from API
        response = requests.get(f"{POKE_API_BASE_URL}/pokemon/{pokemon_id_or_name.lower()}")
        response.raise_for_status()
        data = response.json()

        # Create new Pokemon record
        pokemon = Pokemon(
            id=data["id"],
            name=data["name"],
            types=[t["type"]["name"] for t in data["types"]],
            stats={s["stat"]["name"]: s["base_stat"] for s in data["stats"]},
            abilities=[a["ability"]["name"] for a in data["abilities"]],
            moves=[m["move"]["name"] for m in data["moves"]],
            height=data["height"] / 10,  # Convert to meters
            weight=data["weight"] / 10,  # Convert to kg
            sprite_url=data["sprites"]["front_default"]
        )

        # Save to cache
        db.add(pokemon)
        db.commit()
        db.refresh(pokemon)
        
        logger.info(f"Cached new Pokémon data for {pokemon_id_or_name}")
        return pokemon

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching Pokémon data: {str(e)}")
        raise HTTPException(status_code=404, detail="Pokémon not found")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def search_pokemon(query: str, db: Session):
    """Search for Pokémon by name."""
    try:
        # Search in cache
        pokemon = db.query(Pokemon).filter(
            Pokemon.name.contains(query.lower())
        ).all()
        
        if pokemon:
            return pokemon

        # If not in cache, fetch from API
        response = requests.get(f"{POKE_API_BASE_URL}/pokemon?limit=1000")
        response.raise_for_status()
        data = response.json()

        # Filter results
        matches = [
            p["name"] for p in data["results"]
            if query.lower() in p["name"].lower()
        ]

        # Fetch and cache matching Pokémon
        results = []
        for name in matches[:10]:  # Limit to 10 results
            pokemon = await fetch_pokemon_data(name, db)
            results.append(pokemon)

        return results

    except Exception as e:
        logger.error(f"Error searching Pokémon: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error") 