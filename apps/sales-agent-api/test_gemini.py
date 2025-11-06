import os
import google.generativeai as genai
from dotenv import load_dotenv

print("Attempting to load .env file...")
load_dotenv()  # This line loads your .env file

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if GEMINI_API_KEY is None:
    print("-----------------------------------------------------------------")
    print("ERROR: Could not find GEMINI_API_KEY in your .env file.")
    print("Please check that your .env file is in the same folder as this script")
    print("and that the variable name is spelled exactly 'GEMINI_API_KEY'.")
    print("-----------------------------------------------------------------")
else:
    print("API Key found! Configuring Gemini...")
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        
        print("Checking models...")
        # This loop will list the models your key can actually see
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f" - Found usable model: {m.name}")

        print("\nAttempting to create a generative model...")
        # Try to connect to the gemini-pro model
        model = genai.GenerativeModel('gemini-pro-latest') 
        
        print("Sending a test message to Gemini...")
        response = model.generate_content("Hello, world!")
        
        print("---------------------------------")
        print("✅ SUCCESS! Gemini responded:")
        print(response.text)
        print("---------------------------------")

    except Exception as e:
        print("---------------------------------")
        print(f"❌ AN ERROR OCCURRED:")
        print(e)
        print("---------------------------------")
        print("TIP: If you see an 'API_KEY_INVALID' error,")
        print("your key is wrong or not from aistudio.google.com.")
        print("If you see a 'permission' error, your key might be")
        print("from the wrong project (Google Cloud instead of AI Studio).")