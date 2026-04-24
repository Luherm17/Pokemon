import asyncio
from poke_env import LocalhostServerConfiguration
from poke_env.player import RandomPlayer
import logging

# This turns on Python's internal logging so we can see the "Handshake"
logging.basicConfig(level=logging.INFO)

async def diagnostic():
    # Use the pre-configured Localhost settings (Port 8000)
    bot = RandomPlayer(
        server_configuration=LocalhostServerConfiguration,
        battle_format="gen9randombattle"
    )

    print("--- Diagnostic Start ---")
    
    try:
        # We'll try to find a game on the local ladder 
        # (This will fail because your server is empty, but it triggers the connection)
        await bot.ladder(1)
    except Exception as e:
        print(f"Connection attempt finished. Result: {e}")
    
    print("--- Diagnostic End ---")

if __name__ == "__main__":
    asyncio.run(diagnostic())