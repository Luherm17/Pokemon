import asyncio
import torch
import random
from neural_bot import SimpleBrain, NeuralBot
from poke_env import LocalhostServerConfiguration, AccountConfiguration

async def main():
    # 1. Create the brain (Must be the 22-input version!)
    my_brain = SimpleBrain()
    
    # 2. Load the weights from your training session
    try:
        my_brain.load_state_dict(torch.load("best_brain.pth"))
        print("Successfully loaded 'best_brain.pth'. The Alpha is ready.")
    except Exception as e:
        print(f"Error loading brain: {e}")
        print("Make sure your SimpleBrain in neural_bot.py is set to 22 inputs!")
        return

    my_brain.eval() # Set to evaluation mode
    
    bot_username = f"The_Alpha_Bot_{random.randint(0, 99)}"
    
    bot = NeuralBot(
        brain=my_brain,
        server_configuration=LocalhostServerConfiguration,
        account_configuration=AccountConfiguration(bot_username, None)
    )
    
    print("\n" + "="*40)
    print(f"  CHALLENGE THE ALPHA")
    print("="*40)
    print(f"1. Go to: http://localhost:8000")
    print(f"2. Pick a username (anything works).")
    print(f"3. Click 'Find a user' and search for: {bot_username}")
    print(f"4. Challenge it to a 'Gen 9 Random Battle'.")
    print("="*40)
    
    # The bot will wait here until it receives 1 challenge, then it will close.
    await bot.accept_challenges(None, 1)

if __name__ == "__main__":
    asyncio.run(main())