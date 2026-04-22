import cv2 as opencv # image processing to make text more readable
import pandas as pd # read wine dataset and manage collection
from difflib import SequenceMatcher # compare read text to dataset
import easyocr # read text from images
import os # file handling


def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def keywordScore(queryWords, name):
    nameWords = name.lower().split()
    matches = sum(1 for w in queryWords if w in nameWords)
    return matches / max(len(queryWords), 1)

def findBestMatch(query, df, column):
    query = query.lower()
    queryWords = query.split()
    bestScore = 0
    bestRow = None
    queryClean = ''.join(c if c.isalnum() else ' ' for c in query).split()

    for _, row in df.iterrows():
        name = str(row[column]).lower()
        if abs(len(name) - len(query)) > 20:
            continue
        nameClean = ''.join(c if c.isalnum() else ' ' for c in name).split()
        s1 = similarity(query, name)
        if s1 < 0.3:
            continue
        s2 = keywordScore(queryWords, name)
        wordMatches = sum(1 for w in queryClean if any(w in nw for nw in nameClean))
        wordMatchScore = wordMatches / max(len(queryClean), 1)
        score = 0.4 * s1 + 0.3 * s2 + 0.3 * wordMatchScore
        if score > bestScore:
            bestScore = score
            bestRow = row
    return bestRow, bestScore


def wineCollection(wineName, imageName=None, collectionFile="wineCollection.csv"):
    from datetime import datetime
    try:
        dfCollection = pd.read_csv(collectionFile)
    except FileNotFoundError:
        dfCollection = pd.DataFrame(columns=["Wine Name", "Count", "Date Added", "Most Recent", "Image"])
    if wineName in dfCollection["Wine Name"].values:
        dfCollection.loc[dfCollection["Wine Name"] == wineName, "Count"] += 1
        recent =  datetime.now().strftime("%Y-%m-%d")
        dfCollection.loc[dfCollection["Wine Name"] == wineName, "Most Recent"] = recent
        if imageName:
            dfCollection.loc[dfCollection["Wine Name"] == wineName, "Image"] = imageName
        print(f"Updated '{wineName}' - New count: {dfCollection.loc[dfCollection['Wine Name'] == wineName, 'Count'].values[0]}")
    else:
        newEntry = pd.DataFrame({
            "Wine Name": [wineName], 
            "Count": [1], 
            "Date Added": [datetime.now().strftime("%Y-%m-%d")],
            "Most Recent": [datetime.now().strftime("%Y-%m-%d")],
            "Image": [imageName if imageName else ""]
        })
        dfCollection = pd.concat([dfCollection, newEntry], ignore_index=True)
        print(f"Added '{wineName}' to collection")
    dfCollection.to_csv(collectionFile, index=False)
    return dfCollection


def wordPermutations(query, df, column, targetScore=0.50):
    from itertools import permutations, combinations
    words = query.split()
    _, score = findBestMatch(query, df, column)

    if score >= targetScore:
        return query, score
    
    bestScore = score
    bestQuery = query
    tried = set()
    maxPerms = 20
    permCount = 0

    for perm in permutations(words):
        if permCount >= maxPerms:
            break
        permCount += 1
        reordered = " ".join(perm)
        if reordered in tried:
            continue
        tried.add(reordered)
        bestRow, score = findBestMatch(reordered, df, column)
        if score >= targetScore:
            return reordered, score
        if score > bestScore:
            bestScore = score
            bestQuery = reordered

    maxWordsToRemove = min(2, len(words) - 1)
    for numRemove in range(1, maxWordsToRemove + 1):
        maxCombos = 10
        comboCount = 0
        for combo in combinations(range(len(words)), len(words) - numRemove):
            if comboCount >= maxCombos:
                break
            comboCount += 1
            remainingWords = [words[i] for i in combo]
            reducedQuery = " ".join(remainingWords)
            if reducedQuery in tried:
                continue
            tried.add(reducedQuery)
            bestRow, score = findBestMatch(reducedQuery, df, column)
            if score >= targetScore:
                return reducedQuery, score
            if score > bestScore:
                bestScore = score
                bestQuery = reducedQuery

    return bestQuery, bestScore


def enhanceText(label):
    gray = opencv.cvtColor(label, opencv.COLOR_BGR2GRAY)
    gray = opencv.resize(gray, None, fx=2, fy=2, interpolation=opencv.INTER_CUBIC)
    gray = opencv.fastNlMeansDenoising(gray, None, 5, 7, 21)
    clahe = opencv.createCLAHE(clipLimit=2.5, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)

    gamma = 1.2
    table = [((i / 255.0) ** (1.0 / gamma)) * 255 for i in range(256)]
    enhanced = opencv.LUT(enhanced, opencv.UMat(opencv.numpy.array(table, dtype="uint8")))
    enhanced = opencv.add(enhanced, 5)
    blurred = opencv.GaussianBlur(enhanced, (0, 0), 1.0)
    enhanced = opencv.addWeighted(enhanced, 1.1, blurred, -0.1, 0)

    return enhanced

ocrReader = None

def extractTextOcr(label):
    global ocrReader
    try:
        if ocrReader is None:
            ocrReader = easyocr.Reader(['en', 'es', 'fr'])
        results = ocrReader.readtext(label)
        extractedText = []
        totalConfidence = 0
        for detection in results:
            text = detection[1]
            confidence = detection[2]
            if confidence > 0.05:
                extractedText.append(text)
                totalConfidence += confidence
        return " ".join(extractedText)
    except:
        return "", 0


def process_wine_image(image_path):
    try:
        csvPath = "WineDataset.csv"
        df = pd.read_csv(csvPath)
    except FileNotFoundError:
        return {'matched': False, 'error': 'Wine dataset file not found'}
    columnName = df.columns[0]
    imageName = os.path.splitext(os.path.basename(image_path))[0]
    outputFolder = f"results/{imageName}Results"

    os.makedirs(outputFolder, exist_ok=True)
    img = opencv.imread(image_path)
    if img is None:
        return {'matched': False, 'error': 'Could not read image'}

    opencv.imwrite(f"{outputFolder}/enhanced_image.jpg", enhanceText(img))
    opencv.imwrite(f"{outputFolder}/original_image.jpg", img)

    extractedText = extractTextOcr(f"{outputFolder}/enhanced_image.jpg")

    strategies = [
        ("Permutations", extractedText),
        ("Filtered", " ".join([w for w in extractedText.split() if len(w) > 2])),
        ("Capitalized", " ".join(w.capitalize() for w in extractedText.split()))
    ]

    bestScore = 0
    bestWine = None
    bestText = ""
    for name, text in strategies:
        current_best_text, score = wordPermutations(text, df, columnName, targetScore=0.50)
        if score > bestScore:
            bestScore = score
            bestText = current_best_text
            bestMatch, _ = findBestMatch(bestText, df, columnName)
            if bestMatch is not None:
                bestWine = bestMatch[columnName]

    if bestScore >= 0.5:
        return {
            'matched': True,
            'wine_name': bestWine,
            'score': bestScore,
            'extracted_text': extractedText,
            'best_text': bestText
        }
    else:
        return {
            'matched': False,
            'extracted_text': extractedText,
            'best_text': bestText,
            'score': bestScore
        }


def main():
    print("Available wine images:")
    for file in os.listdir("wineImages/"):
        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
            print(f"  {file}")
    print()

    imagePath = "wineImages/" + input("Enter the image file name (e.g., guv.jpg): ").strip()
    if not imagePath:
        print("Error: Image file name cannot be empty.")
        exit(1)
    if not os.path.exists(imagePath):
        print(f"Error: File '{imagePath}' not found.")
        exit(1)

    wine_result = process_wine_image(imagePath)
    if wine_result['matched']:
        print(f"Matched wine: {wine_result['wine_name']}")
        print(f"Score: {wine_result['score']:.2f}")
        print(f"Extracted Text: {wine_result['extracted_text']}")
        print(f"Best Text: {wine_result['best_text']}")
        collection = wineCollection(wine_result['wine_name'], os.path.basename(imagePath))
        print(f"\nCurrent Wine Collection:")
        print(collection.to_string(index=False))
    else:
        print("Could not identify wine from image.")
        print(f"Extracted Text: {wine_result.get('extracted_text', '')}")
        print(f"Best Text: {wine_result.get('best_text', '')}")
        print(f"Score: {wine_result.get('score', 0):.2f}")


if __name__ == "__main__":
    main()
