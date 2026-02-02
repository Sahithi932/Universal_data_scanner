#!/bin/bash

echo "================================================"
echo "  Universal Data Scanner - Test Suite"
echo "================================================"
echo ""

# Run pytest with verbose output and coverage
echo "Running all 49 test cases..."
echo ""

pytest tests/ -v --tb=short --color=yes

echo ""
echo "================================================"
echo "Test execution completed!"
echo "================================================"
