"""
Test Hybrid AI System
Run: python tests/test_hybrid.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app.services.ai_service import FeedbackSummarizer

def test_hybrid_analysis():
    """Test the hybrid analysis pipeline"""
    
    test_feedback = [
        "Outstanding presentation! The speaker covered all key points effectively",
        "Sound system needs improvement, echo was very distracting",
        "Loved the interactive polls during the session",
        "The slides were well-designed and easy to understand",
        "Speaker seemed nervous at the beginning but improved over time",
        "Lighting in the room was too dim to take proper notes",
        "Excellent use of case studies and practical examples",
        "The presentation went over the allocated time",
        "Very informative content, will definitely apply these concepts",
        "Microphone feedback was annoying throughout the session",
        "Speaker's expertise was evident in the depth of knowledge shared",
        "Room was too small for the number of attendees",
        "Great storytelling approach made complex topics easier to grasp"
    ]
    
    print("\n" + "="*70)
    print("TESTING HYBRID AI FEEDBACK ANALYZER (WITHOUT SENTIMENT)")
    print("="*70 + "\n")
    
    try:
        summarizer = FeedbackSummarizer()
        print("✅ AI Service initialized\n")
        
        result = summarizer.get_structured_analysis(test_feedback)
        
        print(f"✅ Analysis Success: {result['success']}")
        print(f"📊 Total Feedback: {result['total_feedback']}")
        print(f"🔢 Clusters Found: {result['statistics']['clusters_found']}")
        print(f"🏷️  Themes Identified: {result['statistics']['themes_identified']}")
        
        print(f"\n🏷️  Top Themes:")
        for theme, count in list(result['key_themes'].items())[:5]:
            print(f"   • {theme}: {count} mentions")
        
        print(f"\n💡 Suggestions:")
        for i, suggestion in enumerate(result['suggestions'], 1):
            print(f"   {i}. {suggestion}")
        
        print(f"\n📝 Summary Preview:")
        summary_lines = result['summary'].split('\n')[:10]
        for line in summary_lines:
            if line.strip():
                print(f"   {line}")
        
        print("\n" + "="*70)
        print("✅ TEST COMPLETED SUCCESSFULLY!")
        print("="*70 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_hybrid_analysis()
    sys.exit(0 if success else 1)
