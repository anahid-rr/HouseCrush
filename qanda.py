#!/usr/bin/env python3
"""
Q&A Module for House Crush
Handles answering user questions about rental properties using OpenAI.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv
from config import config

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QandAManager:
    """Manages Q&A functionality for rental property questions."""
    
    def __init__(self):
        """Initialize the Q&A manager."""
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            logger.warning("OpenAI API key not found in environment variables")
    
    def answer_question(self, question: str) -> Dict:
        """
        Answer a user's question about rental properties using OpenAI.
        
        Args:
            question: The user's question string
            
        Returns:
            Dictionary containing:
            - success: Boolean indicating success
            - answer: The answer text
            - sources: List of sources (if any)
            - error: Error message (if failed)
        """
        if not self.api_key:
            return {
                'success': False,
                'answer': '',
                'sources': [],
                'error': 'OpenAI API key not configured. Please set OPENAI_API_KEY environment variable.'
            }
        
        if not question or not question.strip():
            return {
                'success': False,
                'answer': '',
                'sources': [],
                'error': 'No question provided.'
            }
        
        try:
            import openai
            openai.api_key = self.api_key
            
            # Create the prompt
            system_prompt = self._create_system_prompt()
            user_prompt = question.strip()
            
            # Get answer from OpenAI
            answer_data = self._get_openai_answer(system_prompt, user_prompt)
            
            return answer_data
            
        except ImportError:
            return {
                'success': False,
                'answer': '',
                'sources': [],
                'error': 'OpenAI library not installed. Please install with: pip install openai'
            }
        except Exception as e:
            if config.should_log_debug():
                logger.error(f"Error answering question: {e}")
            self._log_error(question, str(e))
            return {
                'success': False,
                'answer': '',
                'sources': [],
                'error': f'Failed to get answer: {str(e)}'
            }
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt for OpenAI."""
        return """You are a helpful rental property expert with extensive knowledge about:
- Rental markets and trends
- Property search strategies
- Rental requirements and applications
- Amenities and property features
- Location analysis and commute considerations
- Rental laws and regulations
- Property management and maintenance

Provide clear, helpful answers based on your knowledge. If you're not sure about something, say so. 
If possible, mention if your answer is based on general knowledge or specific sources.
Keep answers concise but informative (2-4 sentences typically)."""
    
    def _get_openai_answer(self, system_prompt: str, user_prompt: str) -> Dict:
        """Get answer from OpenAI API."""
        import openai
        
        # Try GPT-4o first, fallback to gpt-3.5-turbo
        models_to_try = ["gpt-4o", "gpt-3.5-turbo"]
        
        for model in models_to_try:
            try:
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=600,
                    temperature=0.2
                )
                
                answer_text = response.choices[0].message.content.strip()
                
                # Extract sources if mentioned
                sources = []
                if "Sources:" in answer_text:
                    parts = answer_text.split("Sources:")
                    answer = parts[0].strip()
                    sources_text = parts[1].strip()
                    sources = [s.strip() for s in sources_text.split("\n") if s.strip()]
                else:
                    answer = answer_text
                
                return {
                    'success': True,
                    'answer': answer,
                    'sources': sources,
                    'model_used': model,
                    'error': ''
                }
                
            except Exception as e:
                if config.should_log_debug():
                    logger.warning(f"Failed to use model {model}: {e}")
                continue
        
        # If all models fail
        raise Exception("All OpenAI models failed")
    
    def _log_error(self, question: str, error: str):
        """Log errors for debugging (only in development)."""
        if config.should_save_json_files():
            self._save_debug_data("error", {
                "timestamp": datetime.now().isoformat(),
                "question": question,
                "error": error,
                "error_type": "Q&A Error"
            })
    
    def _save_debug_data(self, data_type: str, data: Dict):
        """Save debug data to files (only in development)."""
        if not config.should_save_json_files():
            return
        
        try:
            # Create debug directory if it doesn't exist
            debug_dir = 'debug'
            if not os.path.exists(debug_dir):
                os.makedirs(debug_dir)
                if config.should_log_debug():
                    logger.info(f"Created debug directory: {debug_dir}")
            
            # Create Q&A debug subdirectory
            qa_debug_dir = os.path.join(debug_dir, 'qa')
            if not os.path.exists(qa_debug_dir):
                os.makedirs(qa_debug_dir)
                if config.should_log_debug():
                    logger.info(f"Created Q&A debug directory: {qa_debug_dir}")
            
            # Generate timestamp for filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create filename
            filename = f"qa_{data_type}_{timestamp}.json"
            filepath = os.path.join(qa_debug_dir, filename)
            
            # Save data to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            if config.should_log_debug():
                logger.info(f"✅ Saved Q&A {data_type} data to: {filepath}")
            
        except Exception as e:
            logger.error(f"❌ Error saving Q&A debug data: {e}")
            # Try to save to current directory as fallback
            if config.should_save_json_files():
                try:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"qa_{data_type}_{timestamp}.json"
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    if config.should_log_debug():
                        logger.info(f"✅ Saved Q&A {data_type} data to current directory: {filename}")
                except Exception as fallback_error:
                    logger.error(f"❌ Failed to save Q&A debug data even to current directory: {fallback_error}")
    
    def get_status(self) -> Dict:
        """Get the status of the Q&A system."""
        return {
            "available": bool(self.api_key),
            "status": "Ready" if self.api_key else "Not configured",
            "message": "Q&A system is ready" if self.api_key else "OpenAI API key not configured"
        }

# Global instance for easy access
qa_manager = QandAManager()

def answer_user_question(question: str) -> Dict:
    """
    Convenience function to answer a user question.
    
    Args:
        question: The user's question
        
    Returns:
        Dictionary with answer data
    """
    return qa_manager.answer_question(question)

def get_qa_status() -> Dict:
    """
    Get Q&A system status.
    
    Returns:
        Dictionary with status information
    """
    return qa_manager.get_status()

if __name__ == "__main__":
    # Test the Q&A system
    test_questions = [
        "What are typical rental requirements?",
        "What amenities should I look for in an apartment?",
        "What's the difference between downtown and suburban properties?"
    ]
    
    print("=== Q&A System Test ===\n")
    
    for question in test_questions:
        print(f"Question: {question}")
        result = answer_user_question(question)
        
        if result['success']:
            print(f"Answer: {result['answer']}")
            if result['sources']:
                print(f"Sources: {', '.join(result['sources'])}")
        else:
            print(f"Error: {result['error']}")
        
        print("-" * 50) 