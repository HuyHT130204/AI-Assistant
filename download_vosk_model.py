import os
import requests
import zipfile
import shutil

def download_vosk_model():
    # Create models directory if it doesn't exist
    models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
    
    # Vosk model URL
    model_url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
    model_path = os.path.join(models_dir, "vosk-model-small-en-us-0.15.zip")
    
    print("Downloading Vosk model...")
    try:
        # Download the model
        response = requests.get(model_url, stream=True)
        response.raise_for_status()
        
        # Save the model
        with open(model_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print("Extracting model...")
        # Extract the model
        with zipfile.ZipFile(model_path, 'r') as zip_ref:
            zip_ref.extractall(models_dir)
        
        # Remove the zip file
        os.remove(model_path)
        
        print("Vosk model downloaded and extracted successfully!")
    except Exception as e:
        print(f"Error downloading Vosk model: {e}")
        if os.path.exists(model_path):
            os.remove(model_path)

if __name__ == "__main__":
    download_vosk_model() 