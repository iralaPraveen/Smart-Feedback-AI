"""
Application entry point
"""
from app import create_app
from app.config import Config
import logging

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    try:
        # Validate configuration
        Config.validate_config()
        
        # Log configuration summary (without secrets)
        logger.info("🚀 Starting Feedback Analyzer Backend")
        logger.info(f"Configuration: {Config.get_config_summary()}")
        
        # Create and run app
        app = create_app()
        app.run(
            host=Config.HOST,
            port=Config.PORT,
            debug=Config.DEBUG
        )
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        exit(1)
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        exit(1)
