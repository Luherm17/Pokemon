import asyncio
import torch
import torch.nn as nn
import random
from poke_env.player import Player, RandomPlayer
from poke_env import LocalhostServerConfiguration, AccountConfiguration

print("DEBUG: Script is starting")

# --- THE BRAIN (22 inputs, 32 hidden neurons) ---
class SimpleBrain(nn.Module):
    def __init__(self):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(22, 32), 
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 4)
        )

    def forward(self, x):
        return self.network(x)

# --- THE BOT ---
class NeuralBot(Player):
    def __init__(self, brain, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.brain = brain

    def choose_move(self, battle):
        # 1. HP & TEAM SENSES (4 features)
        my_hp = battle.active_pokemon.current_hp_fraction or 0
        opp_hp = 1.0
        if battle.opponent_active_pokemon:
            opp_hp = battle.opponent_active_pokemon.current_hp_fraction or 0
        my_rem = len([p for p in battle.team.values() if not p.fainted]) / 6
        opp_rem = len([p for p in battle.opponent_team.values() if not p.fainted]) / 6

        # 2. BOOST SENSES (7 features)
        b = battle.active_pokemon.boosts
        boosts = [
            b.get('atk', 0)/6, b.get('def', 0)/6, b.get('spa', 0)/6,
            b.get('spd', 0)/6, b.get('spe', 0)/6, b.get('accuracy', 0)/6, b.get('evasion', 0)/6
        ]

        # 3. STATUS SENSES (4 features)
        s = battle.active_pokemon.status
        status_feats = [1.0 if s == st else 0.0 for st in ["BRN", "PAR", "SLP"]] + \
                       [1.0 if s in ["PSN", "TOX"] else 0.0]

        # 4. SPEED & TERA SENSES (3 features)
        my_spe = battle.active_pokemon.stats.get('spe', 100) or 100
        opp_spe = 100
        if battle.opponent_active_pokemon and battle.opponent_active_pokemon.stats:
            opp_spe = battle.opponent_active_pokemon.stats.get('spe', 100) or 100
        
        is_faster = 1.0 if my_spe > opp_spe else 0.0
        
        # Safe Tera check
        can_tera = 1.0 if getattr(battle, 'can_terastallize', False) else 0.0
        opp_tera = 0.0 if getattr(battle, 'opponent_can_terastallize', True) else 1.0

        # 5. TYPE ADVANTAGE SENSES (4 features)
        type_scores = [0.0, 0.0, 0.0, 0.0]
        if battle.opponent_active_pokemon:
            for i, move in enumerate(battle.available_moves):
                if i < 4:
                    type_scores[i] = battle.opponent_active_pokemon.damage_multiplier(move)

        # 6. COMBINE ALL (22 features total)
        features = [my_hp, opp_hp, my_rem, opp_rem] + boosts + status_feats + \
                   [is_faster, can_tera, opp_tera] + type_scores
        
        # 7. THINK
        state_tensor = torch.tensor(features, dtype=torch.float32)
        with torch.no_grad():
            action_scores = self.brain(state_tensor)

        # 8. ACT (With an "Immunity" filter)
        with torch.no_grad():
            action_scores = self.brain(state_tensor)

        # Let's manually tank the score of any move that has a 0.0 multiplier
        for i in range(len(type_scores)):
            if type_scores[i] == 0:
                action_scores[i] -= 100.0 # Make this move look terrible

# --- THE MAIN EXECUTION BLOCK ---
async def main():
    suffix = random.randint(0, 9999)
    print(f"DEBUG: Initializing battle for AlphaBot_{suffix}...")
    
    bot = NeuralBot(
        brain=SimpleBrain(),
        server_configuration=LocalhostServerConfiguration,
        account_configuration=AccountConfiguration(f"AlphaBot_{suffix}", None)
    )
    
    dummy = RandomPlayer(
        server_configuration=LocalhostServerConfiguration,
        account_configuration=AccountConfiguration(f"Dummy_{suffix}", None)
    )
    
    print("DEBUG: Fighting...")
    await bot.battle_against(dummy, n_battles=1)
    print(f"DEBUG: Battle finished. Winner: {'Bot' if bot.n_won_battles > 0 else 'Dummy'}")

if __name__ == "__main__":
    asyncio.run(main())