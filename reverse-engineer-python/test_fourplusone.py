#!/usr/bin/env python3
"""
Test script for 4+1 architecture document generation.
"""

import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from reverse_engineer.analyzer import ProjectAnalyzer
from reverse_engineer.generators import FourPlusOneDocGenerator


def test_fourplusone_generation():
    """Test the 4+1 architecture document generation."""
    print("🧪 Testing 4+1 Architecture Document Generator\n")
    
    # Use the current project as test subject
    repo_root = Path(__file__).parent.parent.parent
    print(f"📁 Analyzing project: {repo_root}\n")
    
    # Create analyzer
    analyzer = ProjectAnalyzer(repo_root, verbose=True)
    
    # Run basic discovery
    print("🔍 Running discovery...\n")
    analyzer.discover_endpoints()
    analyzer.discover_models()
    analyzer.discover_views()
    analyzer.discover_services()
    analyzer.extract_features()
    analyzer.discover_actors()
    analyzer.discover_system_boundaries()
    analyzer.map_relationships()
    analyzer.extract_use_cases()
    
    print("\n📊 Discovery Results:")
    print(f"   • Endpoints: {analyzer.endpoint_count}")
    print(f"   • Models: {analyzer.model_count}")
    print(f"   • Views: {analyzer.view_count}")
    print(f"   • Services: {analyzer.service_count}")
    print(f"   • Actors: {analyzer.actor_count}")
    print(f"   • System Boundaries: {analyzer.system_boundary_count}")
    print(f"   • Use Cases: {analyzer.use_case_count}")
    
    # Generate 4+1 document
    print("\n📝 Generating 4+1 Architecture Document...\n")
    generator = FourPlusOneDocGenerator(analyzer)
    content = generator.generate()
    
    # Save to test file
    output_file = Path(__file__).parent / "test-fourplusone-output.md"
    with open(output_file, 'w') as f:
        f.write(content)
    
    print(f"✅ Document generated: {output_file}")
    print(f"📏 Document size: {len(content)} characters")
    print(f"📄 Line count: {len(content.splitlines())} lines")
    
    # Show first few lines
    print("\n📖 First 20 lines of generated document:")
    print("=" * 70)
    for i, line in enumerate(content.splitlines()[:20], 1):
        print(f"{i:3d}: {line}")
    print("=" * 70)
    
    print(f"\n✅ Test complete! Review the full document at: {output_file}")

if __name__ == "__main__":
    try:
        test_fourplusone_generation()
    except Exception as e:
        print(f"\n❌ Test failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
