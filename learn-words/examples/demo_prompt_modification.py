#!/usr/bin/env python3
"""Demo script showing how easy it is to modify prompts with the new YAML system."""

import asyncio
from src.prompt_manager import prompt_manager


def demo_prompt_modification():
    """Demonstrate how easy it is to modify and reload prompts."""

    print("🎯 YAML Prompt Management Demo")
    print("=" * 50)

    print("\n📋 Current Available Prompt Types:")
    for prompt_type in prompt_manager.list_prompt_types():
        print(f"   • {prompt_type}")

    print("\n🔧 Current OpenAI Configuration:")
    print(f"   • Model: {prompt_manager.openai_config.get('model')}")
    print(f"   • Response Format: {prompt_manager.openai_config.get('response_format')}")

    print("\n🌡️ Temperature Settings by Prompt Type:")
    temperatures = prompt_manager.openai_config.get("temperature", {})
    for prompt_type, temp in temperatures.items():
        print(f"   • {prompt_type}: {temp}")

    print("\n📝 Sample Prompt Template (Language Detection):")
    system_prompt = prompt_manager.get_system_prompt("language_detection")
    print(f"   System: {system_prompt}")

    print("\n🔄 Template Variable Substitution Example:")
    try:
        user_prompt = prompt_manager.get_user_prompt(
            "language_detection",
            text="Bonjour le monde",
            user_native="English",
            user_learning="French",
        )
        print("   ✅ Successfully rendered template with variables:")
        print(f"      - text: 'Bonjour le monde'")
        print(f"      - user_native: 'English'")
        print(f"      - user_learning: 'French'")
    except Exception as e:
        print(f"   ❌ Template rendering failed: {e}")

    print("\n🛠️ Stop Words Configuration:")
    stop_words = prompt_manager.get_stop_words()
    print(f"   • Total stop words: {len(stop_words)}")
    print(f"   • Sample stop words: {stop_words[:10]}")

    print("\n🎉 Benefits of YAML-Based Prompt Management:")
    print("   ✅ Easy to modify prompts without touching code")
    print("   ✅ Version control for prompt changes")
    print("   ✅ Centralized configuration management")
    print("   ✅ Template variables for dynamic content")
    print("   ✅ Different temperatures per prompt type")
    print("   ✅ Hot-reload capability (prompt_manager.reload_config())")
    print("   ✅ Validation and error handling")

    print("\n📁 To modify prompts, simply edit: src/prompts.yaml")
    print("   • Change system prompts")
    print("   • Modify user prompt templates")
    print("   • Adjust OpenAI parameters")
    print("   • Update stop words")
    print("   • Add new prompt types")

    print("\n🚀 The translation service will automatically use the new prompts!")


if __name__ == "__main__":
    demo_prompt_modification()
