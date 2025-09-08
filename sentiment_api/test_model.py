print("Attempting to import libraries...")
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

print("Libraries imported successfully.")
print("Now loading a smaller sentiment model... (This may take a moment)")

try:
    # Use a more memory-efficient model
    model_name = "cardiffnlp/twitter-roberta-base-sentiment"
    
    # The pipeline will automatically download and cache it the first time
    sent_pipe = pipeline(
        "sentiment-analysis",
        model=model_name,
        tokenizer=model_name,
        device=-1, # Force CPU
    )
    print("✅ SUCCESS: Model loaded successfully!")
    
    # Let's test it
    test_text = "This is a great library."
    result = sent_pipe(test_text)
    print(f"Test analysis successful. Result for '{test_text}': {result}")

except Exception as e:
    print(f"❌ ERROR: Failed to load or run the model. Error: {e}")