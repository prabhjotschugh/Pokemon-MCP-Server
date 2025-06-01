// Pokémon Agents for handling different operations

class PokemonAgent {
    constructor() {
        this.API_BASE_URL = 'http://localhost:8000';
        this.POKE_API_URL = 'https://pokeapi.co/api/v2';
        this.cache = new Map();
    }

    async fetchWithCache(url) {
        if (this.cache.has(url)) {
            return this.cache.get(url);
        }
        const response = await fetch(url);
        const data = await response.json();
        this.cache.set(url, data);
        return data;
    }

    async getPokemonData(name) {
        return this.fetchWithCache(`${this.API_BASE_URL}/pokemon/${name}`);
    }
}

class ComparisonAgent extends PokemonAgent {
    async compare(pokemon1, pokemon2) {
        const [data1, data2] = await Promise.all([
            this.getPokemonData(pokemon1),
            this.getPokemonData(pokemon2)
        ]);

        return {
            pokemon1: data1,
            pokemon2: data2,
            stats: this.compareStats(data1.stats, data2.stats),
            types: this.compareTypes(data1.types, data2.types),
            abilities: this.compareAbilities(data1.abilities, data2.abilities)
        };
    }

    compareStats(stats1, stats2) {
        const comparison = {};
        for (const stat in stats1) {
            comparison[stat] = {
                pokemon1: stats1[stat],
                pokemon2: stats2[stat],
                difference: stats1[stat] - stats2[stat]
            };
        }
        return comparison;
    }

    compareTypes(types1, types2) {
        return {
            pokemon1_types: types1,
            pokemon2_types: types2,
            common_types: types1.filter(type => types2.includes(type))
        };
    }

    compareAbilities(abilities1, abilities2) {
        return {
            pokemon1_abilities: abilities1,
            pokemon2_abilities: abilities2,
            common_abilities: abilities1.filter(ability => abilities2.includes(ability))
        };
    }
}

class CounterAgent extends PokemonAgent {
    async findCounters(targetPokemon) {
        const targetData = await this.getPokemonData(targetPokemon);
        const response = await fetch(`${this.POKE_API_URL}/pokemon?limit=1000`);
        const data = await response.json();
        
        const pokemonList = await Promise.all(
            data.results.slice(0, 20).map(p => this.getPokemonData(p.name))
        );

        return this.calculateCounters(targetData, pokemonList);
    }

    calculateCounters(target, pokemonList) {
        return pokemonList
            .filter(p => p.name !== target.name)
            .map(pokemon => ({
                pokemon,
                score: this.calculateEffectivenessScore(pokemon, target)
            }))
            .sort((a, b) => b.score - a.score)
            .slice(0, 5);
    }

    calculateEffectivenessScore(attacker, defender) {
        let typeScore = 1.0;
        for (const attackerType of attacker.types) {
            for (const defenderType of defender.types) {
                if (this.isSuperEffective(attackerType, defenderType)) {
                    typeScore *= 2.0;
                } else if (this.isNotVeryEffective(attackerType, defenderType)) {
                    typeScore *= 0.5;
                }
            }
        }

        const statScore = this.calculateStatScore(attacker, defender);
        return typeScore * statScore;
    }

    isSuperEffective(attackerType, defenderType) {
        // Simplified type effectiveness chart
        const superEffective = {
            'fire': ['grass', 'ice', 'bug'],
            'water': ['fire', 'ground', 'rock'],
            'grass': ['water', 'ground', 'rock'],
            'electric': ['water', 'flying'],
            'ice': ['grass', 'ground', 'flying', 'dragon'],
            'fighting': ['normal', 'ice', 'rock', 'dark', 'steel'],
            'poison': ['grass', 'fairy'],
            'ground': ['fire', 'electric', 'poison', 'rock', 'steel'],
            'flying': ['grass', 'fighting', 'bug'],
            'psychic': ['fighting', 'poison'],
            'bug': ['grass', 'psychic', 'dark'],
            'rock': ['fire', 'ice', 'flying', 'bug'],
            'ghost': ['psychic', 'ghost'],
            'dragon': ['dragon'],
            'dark': ['psychic', 'ghost'],
            'steel': ['ice', 'rock', 'fairy'],
            'fairy': ['fighting', 'dragon', 'dark']
        };

        return superEffective[attackerType]?.includes(defenderType) || false;
    }

    isNotVeryEffective(attackerType, defenderType) {
        // Simplified type resistance chart
        const notVeryEffective = {
            'fire': ['fire', 'water', 'rock', 'dragon'],
            'water': ['water', 'grass', 'dragon'],
            'grass': ['fire', 'grass', 'poison', 'flying', 'bug', 'dragon', 'steel'],
            'electric': ['electric', 'grass', 'dragon'],
            'ice': ['fire', 'water', 'ice', 'steel'],
            'fighting': ['poison', 'flying', 'psychic', 'bug', 'fairy'],
            'poison': ['poison', 'ground', 'rock', 'ghost'],
            'ground': ['grass', 'bug'],
            'flying': ['electric', 'rock', 'steel'],
            'psychic': ['psychic', 'dark'],
            'bug': ['fire', 'fighting', 'poison', 'flying', 'ghost', 'steel', 'fairy'],
            'rock': ['fighting', 'ground', 'steel'],
            'ghost': ['dark'],
            'dragon': ['steel'],
            'dark': ['fighting', 'dark', 'fairy'],
            'steel': ['fire', 'water', 'electric', 'steel'],
            'fairy': ['fire', 'poison', 'steel']
        };

        return notVeryEffective[attackerType]?.includes(defenderType) || false;
    }

    calculateStatScore(attacker, defender) {
        const attackerTotal = Object.values(attacker.stats).reduce((a, b) => a + b, 0);
        const defenderTotal = Object.values(defender.stats).reduce((a, b) => a + b, 0);
        return attackerTotal / defenderTotal;
    }
}

class TeamBuilderAgent extends PokemonAgent {
    async generateTeam(description) {
        const response = await fetch(`${this.POKE_API_URL}/pokemon?limit=1000`);
        const data = await response.json();
        
        const pokemonList = await Promise.all(
            data.results.slice(0, 50).map(p => this.getPokemonData(p.name))
        );

        return this.buildTeam(description, pokemonList);
    }

    buildTeam(description, pokemonList) {
        const team = [];
        const usedTypes = new Set();
        const requirements = this.analyzeDescription(description);

        // Add Pokémon based on requirements
        for (const requirement of requirements) {
            const matchingPokemon = this.findMatchingPokemon(pokemonList, requirement, usedTypes);
            if (matchingPokemon) {
                team.push(matchingPokemon);
                matchingPokemon.types.forEach(t => usedTypes.add(t));
            }
        }

        // Fill remaining slots with balanced Pokémon
        while (team.length < 6) {
            const availablePokemon = pokemonList.filter(p => !team.includes(p));
            if (availablePokemon.length === 0) break;

            const selected = this.selectBalancedPokemon(availablePokemon, usedTypes);
            team.push(selected);
            selected.types.forEach(t => usedTypes.add(t));
        }

        return team;
    }

    analyzeDescription(description) {
        const requirements = [];
        const lowerDesc = description.toLowerCase();

        // Check for type requirements
        const types = ['fire', 'water', 'grass', 'electric', 'ice', 'fighting', 'poison', 
                      'ground', 'flying', 'psychic', 'bug', 'rock', 'ghost', 'dragon', 
                      'dark', 'steel', 'fairy'];
        
        types.forEach(type => {
            if (lowerDesc.includes(type)) {
                requirements.push({ type, role: 'attacker' });
            }
        });

        // Check for role requirements
        if (lowerDesc.includes('defense') || lowerDesc.includes('tank')) {
            requirements.push({ role: 'defender' });
        }
        if (lowerDesc.includes('speed') || lowerDesc.includes('fast')) {
            requirements.push({ role: 'speedster' });
        }
        if (lowerDesc.includes('balanced')) {
            requirements.push({ role: 'balanced' });
        }

        return requirements;
    }

    findMatchingPokemon(pokemonList, requirement, usedTypes) {
        return pokemonList.find(p => {
            if (requirement.type && !p.types.includes(requirement.type)) {
                return false;
            }
            if (requirement.role) {
                switch (requirement.role) {
                    case 'defender':
                        return p.stats.defense > 80 && p.stats['special-defense'] > 80;
                    case 'speedster':
                        return p.stats.speed > 100;
                    case 'balanced':
                        return this.isBalancedPokemon(p);
                }
            }
            return true;
        });
    }

    isBalancedPokemon(pokemon) {
        const stats = Object.values(pokemon.stats);
        const avg = stats.reduce((a, b) => a + b, 0) / stats.length;
        return stats.every(stat => Math.abs(stat - avg) < 20);
    }

    selectBalancedPokemon(pokemonList, usedTypes) {
        // Try to find a Pokémon with different types
        const differentType = pokemonList.find(p => 
            !p.types.some(t => usedTypes.has(t))
        );
        if (differentType) return differentType;

        // If no different type found, return the first available
        return pokemonList[0];
    }
}

// Export the agents
window.PokemonAgents = {
    ComparisonAgent,
    CounterAgent,
    TeamBuilderAgent
}; 