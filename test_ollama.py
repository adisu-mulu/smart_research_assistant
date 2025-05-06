from langchain_community.llms import Ollama

def test_ollama():
    try:
        print("\nTesting connection to Ollama...")
        llm = Ollama(
            model="llama3.2:latest",
            base_url="http://localhost:11434",
            temperature=0.1
        )
        
        print("Sending test prompt to Ollama...")
        response = llm.invoke("discuss the latest trends in AI agent building")
        print(f"Ollama response: {response}")
        return True
    except Exception as e:
        print(f"Failed to connect to Ollama: {str(e)}")
        return False

if __name__ == "__main__":
    test_ollama()