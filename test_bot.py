import asyncio
from poke_env import Player, RandomPlayer

async def main():
    # We define two players. 
    # By default, they look for a server at 'localhost:8000' (Your Arena!)
    player_1 = RandomPlayer(battle_format="gen9randombattle")
    player_2 = RandomPlayer(battle_format="gen9randombattle")

    print("Bot 1 is challenging Bot 2...")

    # This command makes them fight 1 match
    await player_1.battle_against(player_2, n_battles=1)

    # Let's see who won!
    print(f"Battle finished!")
    print(f"Bot 1 wins: {player_1.n_won_battles}")
    print(f"Bot 2 wins: {player_2.n_won_battles}")

if __name__ == "__main__":
    asyncio.run(main())