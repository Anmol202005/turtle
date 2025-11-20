import os
import sys
import json
from pathlib import Path
from typing import Dict, Any


class SetupWizard:

    def __init__(self):
        self.config = {}
        self.env_file = Path(".env")
        self.config_dir = Path(".turtle")
        self.config_file = self.config_dir / "config.json"

    def is_first_run(self) -> bool:
        return not self.env_file.exists() and not self.config_file.exists()

    def show_welcome(self):
        print("\n" + "="*50)
        print("Welcome to Turtle CLI Setup")
        print("="*50)
        print("Multi-API AI coding assistant")
        print("Let's configure your assistant!\n")

    def get_provider_choice(self) -> str:
        providers = {
            "1": "openai",
            "2": "anthropic",
            "3": "gemini"
        }

        while True:
            print("Step 1/3: Choose your AI provider")
            print("-" * 30)
            for key, value in providers.items():
                print(f"{key}. {value.title()}")

            choice = input("\nEnter your choice (1-3): ").strip()
            if choice in providers:
                return providers[choice]
            print("Invalid choice. Please select 1-3.\n")

    def get_model_choice(self, provider: str) -> str:
        models = {
            "openai": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
            "anthropic": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
            "gemini": ["gemini-1.5-flash", "gemini-1.5-pro"]
        }

        provider_models = models.get(provider, [f"{provider}-default"])

        while True:
            print(f"\nStep 2/3: Choose your model for {provider}")
            print("-" * 40)
            for i, model in enumerate(provider_models, 1):
                print(f"{i}. {model}")

            try:
                choice = int(input(f"\nEnter your choice (1-{len(provider_models)}): "))
                if 1 <= choice <= len(provider_models):
                    return provider_models[choice - 1]
            except ValueError:
                pass
            print(f"Invalid choice. Please select 1-{len(provider_models)}.\n")

    def get_api_key(self, provider: str) -> str:
        print(f"\nStep 3/3: Enter your {provider.title()} API key")
        print("-" * 40)

        while True:
            api_key = input(f"Enter your {provider} API key: ").strip()
            if api_key:
                return api_key
            print("API key cannot be empty. Please try again.\n")

    def validate_config(self, provider: str, model: str, api_key: str) -> bool:
        if not provider or not model:
            return False
        if not api_key:
            return False
        return True

    def save_configuration(self, provider: str, model: str, api_key: str):
        env_content = f"""# Turtle CLI Configuration
TURTLE_PROVIDER={provider}
TURTLE_MODEL={model}
TURTLE_API_KEY={api_key}
"""

        with open(self.env_file, "w") as f:
            f.write(env_content)

        self.config_dir.mkdir(exist_ok=True)
        config_data = {
            "provider": provider,
            "model": model,
            "setup_completed": True
        }

        with open(self.config_file, "w") as f:
            json.dump(config_data, f, indent=2)

    def show_success(self):
        print("\n" + "="*50)
        print("🎉 Setup completed successfully!")
        print("="*50)
        print("Your Turtle CLI is now configured and ready to use.")
        print("Configuration saved to .env and .turtle/config.json")
        print("\nYou can start using Turtle CLI now!")
        print("-" * 50)

    def handle_cancellation(self):
        print("\n\nSetup cancelled by user.")
        print("You can run setup again with: turtle --setup")
        sys.exit(0)

    def run_setup(self):
        try:
            if not self.is_first_run():
                print("Setup already completed. Use --setup to reconfigure.")
                return False

            self.show_welcome()

            provider = self.get_provider_choice()
            model = self.get_model_choice(provider)
            api_key = self.get_api_key(provider)

            if not self.validate_config(provider, model, api_key):
                print("Invalid configuration. Please try again.")
                return False

            self.save_configuration(provider, model, api_key)
            self.show_success()
            return True

        except KeyboardInterrupt:
            self.handle_cancellation()
        except Exception as e:
            print(f"Setup failed: {e}")
            return False

    def force_setup(self):
        try:
            self.show_welcome()
            print("Reconfiguring Turtle CLI...\n")

            provider = self.get_provider_choice()
            model = self.get_model_choice(provider)
            api_key = self.get_api_key(provider)

            if not self.validate_config(provider, model, api_key):
                print("Invalid configuration. Please try again.")
                return False

            self.save_configuration(provider, model, api_key)
            self.show_success()
            return True

        except KeyboardInterrupt:
            self.handle_cancellation()
        except Exception as e:
            print(f"Setup failed: {e}")
            return False


def run_first_time_setup():
    wizard = SetupWizard()
    return wizard.run_setup()


def run_forced_setup():
    wizard = SetupWizard()
    return wizard.force_setup()


__all__ = ["SetupWizard", "run_first_time_setup", "run_forced_setup"]