import base64

# REPLACE 'your-key-file.json' with the actual name of the file you just downloaded
file_path = 'C:\\Users\\Btrin\\Downloads\\key.json' 

try:
    with open(file_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
        print("\n✅ COPY THE TEXT BELOW (between the lines):\n")
        print("-" * 20)
        print(encoded)
        print("-" * 20)
        print("\n✅ Paste this LONG string into your Secrets!")
except FileNotFoundError:
    print(f"❌ Error: Could not find file '{file_path}'. Check the name!")