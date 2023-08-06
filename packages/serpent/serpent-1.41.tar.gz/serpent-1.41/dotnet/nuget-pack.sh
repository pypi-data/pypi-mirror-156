#!/bin/sh
set -e
echo "Building and testing..."
dotnet test -c Release Serpent/Tests

echo "\n\nCreating nuget release package..."
dotnet pack -c Release -o $(pwd)/dist Serpent

echo "\n\nPackage available in dist/ directory:"
ls -l dist

echo "\nIf this is allright, publish to nuget.org with:"
echo "dotnet nuget push dist/Razorvine.Serpent.xxxxx.nupkg -s https://www.nuget.org -k api_key_from_nuget_org"
