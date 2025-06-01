const API_BASE_URL = 'http://localhost:8000';
const POKE_API_URL = 'https://pokeapi.co/api/v2';

// Initialize agents
const comparisonAgent = new PokemonAgents.ComparisonAgent();
const counterAgent = new PokemonAgents.CounterAgent();
const teamBuilderAgent = new PokemonAgents.TeamBuilderAgent();

// Cache for Pokémon list
let pokemonList = [];

// Fetch Pokémon list on page load
async function fetchPokemonList() {
    try {
        const response = await fetch(`${POKE_API_URL}/pokemon?limit=1000`);
        const data = await response.json();
        pokemonList = data.results.map(pokemon => pokemon.name);
        populateDropdowns();
    } catch (error) {
        console.error('Error fetching Pokémon list:', error);
    }
}

// Populate all dropdowns with Pokémon names
function populateDropdowns() {
    const dropdowns = [
        'pokemonSearch',
        'pokemon1',
        'pokemon2',
        'targetPokemon'
    ];

    dropdowns.forEach(id => {
        const select = document.getElementById(id);
        if (select) {
            // Clear existing options
            select.innerHTML = '<option value="">Select a Pokémon</option>';
            
            // Add Pokémon options
            pokemonList.forEach(name => {
                const option = document.createElement('option');
                option.value = name;
                option.textContent = name.charAt(0).toUpperCase() + name.slice(1);
                select.appendChild(option);
            });
        }
    });
}

// Utility functions
function showLoading(element) {
    element.innerHTML = '<div class="loading"></div>';
}

function showError(element, message) {
    element.innerHTML = `<div class="error">${message}</div>`;
}

function createPokemonCard(pokemon) {
    return `
        <div class="pokemon-card">
            <img src="${pokemon.sprite_url}" alt="${pokemon.name}">
            <h3>${pokemon.name}</h3>
            <p>Types: ${pokemon.types.join(', ')}</p>
            <div class="stats">
                ${Object.entries(pokemon.stats).map(([stat, value]) => 
                    `<p>${stat}: ${value}</p>`
                ).join('')}
            </div>
        </div>
    `;
}

// Search functionality
async function searchPokemon() {
    const searchInput = document.getElementById('pokemonSearch');
    const resultsDiv = document.getElementById('searchResults');
    const query = searchInput.value.trim();

    if (!query) {
        showError(resultsDiv, 'Please select a Pokémon');
        return;
    }

    showLoading(resultsDiv);

    try {
        const response = await fetch(`${API_BASE_URL}/pokemon/search/${query}`);
        if (!response.ok) throw new Error('Pokémon not found');
        
        const data = await response.json();
        resultsDiv.innerHTML = data.map(pokemon => createPokemonCard(pokemon)).join('');
    } catch (error) {
        showError(resultsDiv, error.message);
    }
}

// Comparison functionality
async function comparePokemon() {
    const pokemon1Input = document.getElementById('pokemon1');
    const pokemon2Input = document.getElementById('pokemon2');
    const resultsDiv = document.getElementById('comparisonResults');
    const pokemon1 = pokemon1Input.value.trim();
    const pokemon2 = pokemon2Input.value.trim();

    if (!pokemon1 || !pokemon2) {
        showError(resultsDiv, 'Please select both Pokémon');
        return;
    }

    showLoading(resultsDiv);

    try {
        const comparison = await comparisonAgent.compare(pokemon1, pokemon2);
        
        let html = '<div class="comparison-details">';
        
        // Create comparison table
        html += `
            <table class="comparison-table">
                <thead>
                    <tr>
                        <th>Stat</th>
                        <th>${comparison.pokemon1.name}</th>
                        <th>${comparison.pokemon2.name}</th>
                        <th>Difference</th>
                    </tr>
                </thead>
                <tbody>
        `;

        // Stats comparison
        for (const [stat, values] of Object.entries(comparison.stats)) {
            const diff = values.difference;
            const diffClass = diff > 0 ? 'positive' : diff < 0 ? 'negative' : '';
            html += `
                <tr class="${diffClass}">
                    <td>${stat}</td>
                    <td>${values.pokemon1}</td>
                    <td>${values.pokemon2}</td>
                    <td>
                        <span class="stat-diff">
                            ${diff > 0 ? '+' : ''}${diff}
                        </span>
                    </td>
                </tr>
            `;
        }

        html += '</tbody></table>';

        // Type comparison
        html += '<h3>Type Comparison</h3>';
        html += `
            <div class="types-comparison">
                <div class="pokemon-types">
                    <h4>${comparison.pokemon1.name}</h4>
                    <div class="types">
                        ${comparison.types.pokemon1_types.map(type => 
                            `<span class="type-badge">${type}</span>`
                        ).join('')}
                    </div>
                </div>
                <div class="pokemon-types">
                    <h4>${comparison.pokemon2.name}</h4>
                    <div class="types">
                        ${comparison.types.pokemon2_types.map(type => 
                            `<span class="type-badge">${type}</span>`
                        ).join('')}
                    </div>
                </div>
            </div>
        `;

        if (comparison.types.common_types.length > 0) {
            html += `
                <div class="common-types">
                    <h4>Common Types</h4>
                    <div class="types">
                        ${comparison.types.common_types.map(type => 
                            `<span class="type-badge">${type}</span>`
                        ).join('')}
                    </div>
                </div>
            `;
        }

        // Abilities comparison
        html += '<h3>Abilities</h3>';
        html += `
            <div class="abilities-comparison">
                <div class="pokemon-abilities">
                    <h4>${comparison.pokemon1.name}</h4>
                    <div class="abilities">
                        ${comparison.abilities.pokemon1_abilities.map(ability => 
                            `<span class="ability-badge">${ability}</span>`
                        ).join('')}
                    </div>
                </div>
                <div class="pokemon-abilities">
                    <h4>${comparison.pokemon2.name}</h4>
                    <div class="abilities">
                        ${comparison.abilities.pokemon2_abilities.map(ability => 
                            `<span class="ability-badge">${ability}</span>`
                        ).join('')}
                    </div>
                </div>
            </div>
        `;

        if (comparison.abilities.common_abilities.length > 0) {
            html += `
                <div class="common-abilities">
                    <h4>Common Abilities</h4>
                    <div class="abilities">
                        ${comparison.abilities.common_abilities.map(ability => 
                            `<span class="ability-badge">${ability}</span>`
                        ).join('')}
                    </div>
                </div>
            `;
        }

        html += '</div>';
        resultsDiv.innerHTML = html;
    } catch (error) {
        showError(resultsDiv, error.message);
    }
}

// Counter functionality
async function findCounters() {
    const targetInput = document.getElementById('targetPokemon');
    const resultsDiv = document.getElementById('counterResults');
    const target = targetInput.value.trim();

    if (!target) {
        showError(resultsDiv, 'Please select a Pokémon');
        return;
    }

    showLoading(resultsDiv);

    try {
        const counters = await counterAgent.findCounters(target);
        resultsDiv.innerHTML = counters.map(counter => createPokemonCard(counter.pokemon)).join('');
    } catch (error) {
        showError(resultsDiv, error.message);
    }
}

// Team generation functionality
async function generateTeam() {
    const descriptionInput = document.getElementById('teamDescription');
    const resultsDiv = document.getElementById('teamResults');
    const description = descriptionInput.value.trim();

    if (!description) {
        showError(resultsDiv, 'Please enter a team description');
        return;
    }

    showLoading(resultsDiv);

    try {
        const team = await teamBuilderAgent.generateTeam(description);
        resultsDiv.innerHTML = `<div class="results-grid">${team.map(pokemon => createPokemonCard(pokemon)).join('')}</div>`;
    } catch (error) {
        showError(resultsDiv, error.message);
    }
}

// Initialize the page
document.addEventListener('DOMContentLoaded', () => {
    fetchPokemonList();
}); 