from transformers import pipeline
from scripts.processing import categorize_article


# Let's test the classifier directly to see raw outputs
def debug_classifier():
    print("Debugging Zero-Shot Classifier...")
    print("=" * 50)

    test_cases = [
        "Meta to Debut Smart Glasses at September's Connect Event - AI technology",
        "Stock market reaches all time high as investors celebrate economic growth",
        "New cancer drug shows promising results in clinical trials at Harvard Medical",
        "President Biden signs new law on immigration reform and border security"
    ]

    for i, text in enumerate(test_cases, 1):
        print(f"\n{i}. Text: '{text}'")

        # Test the classifier directly
        try:
            from scripts.processing import classifier
            if classifier is not None:
                result = classifier(text,
                                    candidate_labels=["technology", "politics", "business", "science", "entertainment",
                                                      "health", "sports", "art"],
                                    multi_label=False)
                print(f"   Raw result: {result}")
                print(f"   Top label: {result['labels'][0]} (confidence: {result['scores'][0]:.3f})")
            else:
                print("   Classifier is None - using fallback")
        except Exception as e:
            print(f"   Error: {e}")

        # Test our categorize function
        category = categorize_article(text, "")
        print(f"   Final category: {category}")


if __name__ == "__main__":
    debug_classifier()