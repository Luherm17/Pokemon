import asyncio
import random
from poke_env import LocalhostServerConfiguration, AccountConfiguration
from poke_env.player import RandomPlayer

async def main():
    # We generate a random ID so the names are always unique
    suffix = random.randint(0, 9999)
    
    # Define unique accounts for both bots
    student_acct = AccountConfiguration(f"Student_{suffix}", None)
    dummy_acct = AccountConfiguration(f"Dummy_{suffix}", None)

    # Initialize players with their unique names
    student = RandomPlayer(
        server_configuration=LocalhostServerConfiguration,
        account_configuration=student_acct,
        battle_format="gen9randombattle",
    )
    dummy = RandomPlayer(
        server_configuration=LocalhostServerConfiguration,
        account_configuration=dummy_acct,
        battle_format="gen9randombattle",
    )

    print(f"--- {student.username} vs {dummy.username} ---")

    # Start the fight
    await student.battle_against(dummy, n_battles=1)

    # Results
    for battle_id, battle in student.battles.items():
        print(f"\n[Battle Results: {battle_id}]")
        print(f"Student Active: {battle.active_pokemon.species} ({battle.active_pokemon.current_hp_fraction*100:.1f}%)")
        print(f"Dummy Active: {battle.opponent_active_pokemon.species} ({battle.opponent_active_pokemon.current_hp_fraction*100:.1f}%)")
        print(f"Winner: {'Student' if battle.won else 'Dummy'}")

if __name__ == "__main__":
    asyncio.run(main())