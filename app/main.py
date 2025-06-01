from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import logging
import uvicorn

from .database import engine, get_db
from .models import Base
from .modules import info, comparison, strategy, team

# Create database tables
Base.metadata.create_all(bind=engine)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Pokémon MCP Server",
    description="A Modular Control Platform server for Pokémon data",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Information Retrieval Endpoints
@app.get("/pokemon/{pokemon_id_or_name}")
async def get_pokemon(pokemon_id_or_name: str, db: Session = Depends(get_db)):
    """Get detailed information about a specific Pokémon."""
    return await info.fetch_pokemon_data(pokemon_id_or_name, db)

@app.get("/pokemon/search/{query}")
async def search_pokemon(query: str, db: Session = Depends(get_db)):
    """Search for Pokémon by name."""
    return await info.search_pokemon(query, db)

# Comparison Endpoints
@app.get("/compare/{pokemon1_id}/{pokemon2_id}")
async def compare_pokemon(pokemon1_id: str, pokemon2_id: str, db: Session = Depends(get_db)):
    """Compare two Pokémon and return their differences."""
    return await comparison.compare_pokemon(pokemon1_id, pokemon2_id, db)

# Strategy Endpoints
@app.get("/counters/{pokemon_name}")
async def get_counters(pokemon_name: str, db: Session = Depends(get_db)):
    """Find effective counters for a given Pokémon."""
    return await strategy.find_counters(pokemon_name, db)

@app.get("/matchup/{pokemon_name}")
async def get_type_matchup(pokemon_name: str, db: Session = Depends(get_db)):
    """Get type matchup information for a Pokémon."""
    return await strategy.get_type_matchup(pokemon_name, db)

# Team Composition Endpoints
@app.post("/team/generate")
async def generate_team(description: str, db: Session = Depends(get_db)):
    """Generate a team of Pokémon based on a natural language description."""
    return await team.generate_team(description, db)

# Health Check
@app.get("/health")
async def health_check():
    """Check if the server is running properly."""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 