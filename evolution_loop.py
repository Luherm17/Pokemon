import torch
import copy
import asyncio
import random
from neural_bot import SimpleBrain, NeuralBot
from poke_env import LocalhostServerConfiguration, AccountConfiguration
from poke_env.player import RandomPlayer

# 1. THE MUTATOR (Tiny tweaks to the "Knobs")
def mutate(brain, power=0.1):
    new_brain = copy.deepcopy(brain)
    with torch.no_grad():
        for param in new_brain.parameters():
            param.add_(torch.randn(param.size()) * power)
    return new_brain

# 2. THE REWARD SYSTEM (Fitness Function)
async def evaluate_brain(brain, gen, spec_id):
    # This suffix ensures the server sees them as brand-new people
    suffix = f"G{gen}S{spec_id}_{random.randint(0, 9999)}"
    
    # --- FIXED: Now passing the names correctly ---
    bot = NeuralBot(
        brain=brain, 
        server_configuration=LocalhostServerConfiguration,
        account_configuration=AccountConfiguration(f"Bot_{suffix}", None)
    )
    
    dummy = RandomPlayer(
        server_configuration=LocalhostServerConfiguration,
        account_configuration=AccountConfiguration(f"Dummy_{suffix}", None)
    )
    
    print(f"  -> Specimen {spec_id} is entering for 5 battles as Bot_{suffix}...")
    
    await bot.battle_against(dummy, n_battles=5)
    
    # Using Win Rate as the fitness score
    fitness = (bot.n_won_battles * 100)
    return fitness

async def main():
    best_brain = SimpleBrain()
    best_fitness = -1
    
    print("\n" + "="*40)
    print("  COMMENCING ELITE EVOLUTION (22 SENSES)")
    print("="*40)

    for gen in range(1, 11): # 10 Generations
        print(f"\n[GENERATION {gen}]")
        
        for i in range(4): # 4 Specimens
            # Specimen 0 is always the previous winner (no mutation)
            if i == 0 and gen > 1:
                current_brain = best_brain
            else:
                current_brain = mutate(best_brain) if gen > 1 else SimpleBrain()

            fitness = await evaluate_brain(current_brain, gen, i)
            print(f"Specimen {i}: Fitness Score: {fitness}")

            if fitness >= best_fitness:
                best_fitness = fitness
                best_brain = current_brain
                torch.save(best_brain.state_dict(), "best_brain.pth")
                print(f"  >>> NEW ALPHA FOUND (Fitness: {best_fitness})")

    print("\nTraining Complete. 'best_brain.pth' is ready for the PC.")

if __name__ == "__main__":
    asyncio.run(main())