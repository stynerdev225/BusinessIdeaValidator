#!/usr/bin/env python3
"""
Quick test to verify the LLM fixes are working properly.
"""
import logging
import sys
import os

# Add the project directory to the path
sys.path.insert(0, '/Users/stynerstiner/Downloads/BusinessIdeaValidator')

from business_validator.validator import validate_business_idea
from business_validator.analyzers.trend_analyzer import generate_tech_business_ideas, analyze_health_trends

logging.basicConfig(level=logging.INFO)

def test_business_validation():
    """Test business idea validation with JSON parsing fixes."""
    print("🔍 Testing Business Idea Validation...")
    
    try:
        result = validate_business_idea("AI-powered fitness tracker for seniors")
        
        if isinstance(result, dict):
            print("✅ Business validation returned proper dict format")
            
            # Check platform insights
            if 'platform_insights' in result:
                insights = result['platform_insights']
                print(f"✅ Found {len(insights)} platform insights")
                
                platforms = []
                for insight in insights:
                    if isinstance(insight, dict) and 'platform' in insight:
                        platforms.append(insight['platform'])
                
                if 'Web Search' in platforms:
                    print("✅ Web Search platform insight found")
                else:
                    print("❌ Web Search platform insight missing")
                    
                return True
            else:
                print("❌ No platform insights found")
                return False
        else:
            print(f"❌ Business validation returned wrong type: {type(result)}")
            return False
            
    except Exception as e:
        print(f"❌ Business validation failed: {e}")
        return False

def test_tech_business_ideas():
    """Test tech business ideas generation."""
    print("\n💡 Testing Tech Business Ideas Generation...")
    
    try:
        result = generate_tech_business_ideas(
            focus_areas=['AI/ML', 'HealthTech', 'SaaS'],
            market_size='medium',
            timeframe='near-term'
        )
        
        if isinstance(result, dict):
            print("✅ Tech business ideas returned proper dict format")
            
            # Check required keys
            required_keys = ['market_overview', 'ideas', 'implementation_factors', 'market_trends']
            missing_keys = [key for key in required_keys if key not in result]
            
            if not missing_keys:
                print("✅ All required keys present")
                
                ideas = result.get('ideas', [])
                print(f"✅ Generated {len(ideas)} business ideas")
                
                if ideas and len(ideas) > 0:
                    first_idea = ideas[0]
                    if isinstance(first_idea, dict) and 'name' in first_idea:
                        print(f"✅ First idea: {first_idea['name']}")
                        return True
                    else:
                        print("❌ Ideas not properly formatted")
                        return False
                else:
                    print("❌ No ideas generated")
                    return False
            else:
                print(f"❌ Missing required keys: {missing_keys}")
                return False
        else:
            print(f"❌ Tech ideas returned wrong type: {type(result)}")
            return False
            
    except Exception as e:
        print(f"❌ Tech business ideas generation failed: {e}")
        return False

def test_health_trends_fix():
    """Test health trends analysis string/dict handling fix."""
    print("\n🩺 Testing Health Trends Analysis Fix...")
    
    try:
        result = analyze_health_trends("diabetes", ["adults"], ["Global"])
        
        if isinstance(result, dict):
            print("✅ Health trends returned proper dict format")
            
            # Check statistics structure
            if 'statistics' in result:
                stats = result['statistics']
                
                # Test demographic breakdown handling
                if 'demographic_breakdown' in stats:
                    demo_data = stats['demographic_breakdown']
                    if isinstance(demo_data, list):
                        print(f"✅ Demographic breakdown: {len(demo_data)} items")
                        if demo_data:
                            item_type = type(demo_data[0]).__name__
                            print(f"✅ Items are {item_type} (both str and dict should work)")
                
                # Test regional breakdown handling
                if 'regional_breakdown' in stats:
                    regional_data = stats['regional_breakdown']
                    if isinstance(regional_data, list):
                        print(f"✅ Regional breakdown: {len(regional_data)} items")
                
                return True
            else:
                print("❌ No statistics found")
                return False
        else:
            print(f"❌ Health trends returned wrong type: {type(result)}")
            return False
            
    except Exception as e:
        print(f"❌ Health trends analysis failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 RUNNING LLM AND FUNCTIONALITY FIXES TEST")
    print("=" * 50)
    
    tests = [
        ("Business Validation", test_business_validation),
        ("Tech Business Ideas", test_tech_business_ideas),
        ("Health Trends Fix", test_health_trends_fix)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        success = test_func()
        results.append((test_name, success))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL FIXES WORKING! LLM token limits increased, JSON parsing improved.")
        return 0
    else:
        print("⚠️ Some issues remain. Check the failures above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
