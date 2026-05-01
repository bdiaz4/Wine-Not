"""
Wine matching module for text-based wine name entry.
Matches wine names from user input against WineDataset.csv using keyword scoring.
"""

import pandas as pd
from difflib import SequenceMatcher
import os


def similarity(a, b):
    """Calculate similarity ratio between two strings using SequenceMatcher"""
    return SequenceMatcher(None, a, b).ratio()


def keywordScore(queryWords, name):
    """
    Score based on keyword matches in wine name.
    Returns ratio of matched keywords to total query keywords.
    """
    nameWords = name.lower().split()
    matches = sum(1 for w in queryWords if w in nameWords)
    return matches / max(len(queryWords), 1)


def findBestMatch(query, df, column="Title"):
    """
    Find the best matching wine in dataset for a given query string.
    Uses combination of string similarity and keyword scoring.
    
    Args:
        query: Wine name to search for
        df: Pandas dataframe with wine data
        column: Column name to search in (default: "Title")
    
    Returns:
        Tuple of (matching_row, confidence_score)
    """
    query = query.lower().strip()
    queryWords = query.split()
    bestScore = 0
    bestRow = None
    
    # Clean query for word matching
    queryClean = ''.join(c if c.isalnum() else ' ' for c in query).split()

    for _, row in df.iterrows():
        name = str(row[column]).lower()
        
        # Skip if length difference is too large
        if abs(len(name) - len(query)) > 20:
            continue
        
        # Calculate similarity score
        s1 = similarity(query, name)
        
        # Skip if similarity too low
        if s1 < 0.3:
            continue
        
        # Keyword score
        s2 = keywordScore(queryWords, name)
        
        # Word-level matching
        nameClean = ''.join(c if c.isalnum() else ' ' for c in name).split()
        wordMatches = sum(1 for w in queryClean if any(w in nw for nw in nameClean))
        wordMatchScore = wordMatches / max(len(queryClean), 1)
        
        # Combined score
        score = 0.4 * s1 + 0.3 * s2 + 0.3 * wordMatchScore
        
        if score > bestScore:
            bestScore = score
            bestRow = row

    return bestRow, bestScore


def matchWineNames(wineNames, datasetPath="WineDataset.csv", confidence_threshold=0.35):
    """
    Match multiple wine names from text input against dataset.
    
    Args:
        wineNames: List of wine name strings
        datasetPath: Path to WineDataset.csv
        confidence_threshold: Minimum confidence score to return match
    
    Returns:
        List of dicts with matched wine data and confidence scores
    """
    try:
        df = pd.read_csv(datasetPath)
    except FileNotFoundError:
        return {"error": "Wine dataset file not found"}
    
    # Use first column as wine name column
    column_name = df.columns[0]
    
    results = []
    
    for wine_name in wineNames:
        wine_name = wine_name.strip()
        if not wine_name:  # Skip empty lines
            continue
        
        best_row, score = findBestMatch(wine_name, df, column_name)
        
        if score >= confidence_threshold and best_row is not None:
            # Extract the 6 required fields
            wine_data = {
                "Wine Name": best_row[column_name],
                "Types": best_row.get("Type", "N/A"),
                "Country": best_row.get("Country", "N/A"),
                "Characteristics": best_row.get("Characteristics", "N/A"),
                "ABV": best_row.get("ABV", "N/A"),
                "Region": best_row.get("Region", "N/A") if pd.notna(best_row.get("Region", None)) else "N/A",
                "Style": best_row.get("Style", "N/A") if pd.notna(best_row.get("Style", None)) else "N/A",
                "Confidence": score,
                "Original Input": wine_name
            }
            results.append(wine_data)
        else:
            # Create entry for unmatched wines
            results.append({
                "Wine Name": None,
                "Original Input": wine_name,
                "Confidence": score,
                "matched": False
            })
    
    return results


def processMenuText(textInput, datasetPath="WineDataset.csv"):
    """
    Process menu text input and return matched wines.
    Splits input by newlines and matches each entry.
    
    Args:
        textInput: Multi-line text input from user
        datasetPath: Path to WineDataset.csv
    
    Returns:
        Dict with matched and unmatched wines
    """
    # Split by newline and filter empty lines
    wine_names = [line.strip() for line in textInput.split('\n') if line.strip()]
    
    # Match all wines
    matches = matchWineNames(wine_names, datasetPath)
    
    # Separate matched and unmatched
    matched = [m for m in matches if m.get("Wine Name") is not None]
    unmatched = [m for m in matches if m.get("Wine Name") is None]
    
    return {
        "matched_wines": matched,
        "unmatched_wines": unmatched,
        "total_input": len(wine_names),
        "total_matched": len(matched)
    }



