#!/usr/bin/env python3
"""
Test script to verify the n8n to Python converter installation
"""

import sys
from pathlib import Path


def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")

    try:
        from backend.parser import WorkflowParser, N8nWorkflow
        from backend.generator import PythonCodeGenerator, NodeGeneratorRegistry
        print("✅ Core modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\nMake sure you've installed dependencies:")
        print("  cd backend")
        print("  pip install -r requirements.txt")
        return False


def test_parser():
    """Test the workflow parser"""
    print("\n🔍 Testing workflow parser...")

    try:
        from backend.parser import WorkflowParser

        # Test with simple workflow
        sample_file = Path("samples/simple-http.json")

        if not sample_file.exists():
            print(f"⚠️  Sample file not found: {sample_file}")
            return False

        workflow = WorkflowParser.parse_file(sample_file)
        print(f"✅ Parser working - loaded workflow: {workflow.name}")
        print(f"   Nodes: {len(workflow.nodes)}")
        return True

    except Exception as e:
        print(f"❌ Parser test failed: {e}")
        return False


def test_generator():
    """Test the code generator"""
    print("\n🔍 Testing code generator...")

    try:
        from backend.parser import WorkflowParser
        from backend.generator import PythonCodeGenerator

        # Parse sample workflow
        sample_file = Path("samples/simple-http.json")

        if not sample_file.exists():
            print(f"⚠️  Sample file not found: {sample_file}")
            return False

        workflow = WorkflowParser.parse_file(sample_file)

        # Generate code
        generator = PythonCodeGenerator(workflow)
        code = generator.generate()

        if len(code) > 0 and "async def main():" in code:
            print("✅ Code generator working")
            print(f"   Generated {len(code)} characters of Python code")
            return True
        else:
            print("❌ Generated code seems invalid")
            return False

    except Exception as e:
        print(f"❌ Generator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cli():
    """Test the CLI module"""
    print("\n🔍 Testing CLI...")

    try:
        from backend.cli import cli
        print("✅ CLI module loaded successfully")
        return True
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False


def test_api():
    """Test the API module"""
    print("\n🔍 Testing API...")

    try:
        from backend.api.main import app
        print("✅ API module loaded successfully")
        print("   You can start the server with:")
        print("   uvicorn backend.api.main:app --reload")
        return True
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False


def test_node_generators():
    """Test node generators"""
    print("\n🔍 Testing node generators...")

    try:
        from backend.generator import NodeGeneratorRegistry

        supported = NodeGeneratorRegistry.get_supported_types()

        if len(supported) > 0:
            print(f"✅ Node generators working")
            print(f"   Supported node types: {len(supported)}")
            print(f"   Examples: {', '.join(supported[:3])}")
            return True
        else:
            print("❌ No node generators registered")
            return False

    except Exception as e:
        print(f"❌ Node generator test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 70)
    print("n8n to Python Converter - Installation Test")
    print("=" * 70)

    tests = [
        ("Imports", test_imports),
        ("Parser", test_parser),
        ("Generator", test_generator),
        ("Node Generators", test_node_generators),
        ("CLI", test_cli),
        ("API", test_api),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Unexpected error in {test_name}: {e}")
            results.append((test_name, False))

    # Print summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Your installation is working correctly.")
        print("\nNext steps:")
        print("  1. Try the CLI: python -m backend.cli convert samples/simple-http.json -o test.py")
        print("  2. Start the API: uvicorn backend.api.main:app --reload")
        print("  3. Open frontend/index.html in your browser")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("\nMake sure you have:")
        print("  1. Installed dependencies: cd backend && pip install -r requirements.txt")
        print("  2. Run from the project root directory")
        return 1


if __name__ == "__main__":
    sys.exit(main())
