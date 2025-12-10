"""
Test configuration settings
"""
from app.config import Config
import json

def test_config():
    print("="*60)
    print("🔧 Testing Configuration")
    print("="*60)
    
    try:
        # Validate config
        Config.validate_config()
        print("✅ Configuration validation passed")
        
        # Print config summary
        summary = Config.get_config_summary()
        print("\n📋 Configuration Summary:")
        print(json.dumps(summary, indent=2))
        
        print("\n✅ All configuration tests passed!")
        return True
        
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        return False

if __name__ == "__main__":
    test_config()
