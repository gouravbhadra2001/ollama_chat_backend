from flask import Flask, request, jsonify
import subprocess
import time
import sys
import ollama  # Ensure you have the Ollama Python package installed

app = Flask(__name__)

def check_ollama_installed():
    """Check if Ollama is installed by checking its version."""
    try:
        subprocess.run(['ollama', '--version'], check=True)
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        return False

def install_ollama():
    """Install Ollama using the provided installation script."""
    print("Ollama is not installed. Installing now...")
    try:
        subprocess.run(['bash', '-c', 'curl -fsSL https://ollama.com/install.sh | sh'], check=True)
        print("Ollama installation complete.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install Ollama: {e}")
        sys.exit(1)

def is_ollama_running():
    """Check if the Ollama server is running."""
    try:
        result = subprocess.run(['pgrep', '-f', 'ollama serve'], stdout=subprocess.PIPE)
        return result.stdout != b''  # If output is not empty, the process is running
    except Exception as e:
        print(f"Error checking Ollama status: {e}")
        return False

def start_ollama_server():
    """Start the Ollama server in a new terminal window."""
    subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', 'ollama serve; exec bash'])

def pull_model(model_name):
    """Pull the specified model using Ollama CLI and display output in real-time."""
    process = subprocess.Popen(['ollama', 'pull', model_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Stream output from the model pulling process in real-time
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            # Print progress output directly to console
            sys.stdout.write(output)
            sys.stdout.flush()

@app.route('/get_response', methods=['POST'])
def get_response():
    data = request.json
    prompt = data.get("prompt", "")
    
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400
    
    # Use Ollama to get a response based on the prompt
    response = ollama.chat(model="llama3.2", messages=[{"role": "user", "content": prompt}])
    
    return jsonify({"response": response['message']['content']})

if __name__ == "__main__":
    # Check if Ollama is installed
    if not check_ollama_installed():
        install_ollama()

    # Check if the Ollama server is already running
    if not is_ollama_running():
        print("Starting Ollama server...")
        start_ollama_server()
        
        # Give the server some time to start
        time.sleep(5)  # Adjust time as necessary for your system

    print("Pulling model 'llama3.2'...")
    pull_model('llama3.2')

    # Start the Flask app
    app.run(host='0.0.0.0', port=5000)
