import httpx
import asyncio

async def test_api():
    base_url = "http://127.0.0.1:8000/api"
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Create a session
        print("Creating session...")
        session_res = await client.post(f"{base_url}/sessions")
        session_res.raise_for_status()
        session_data = session_res.json()
        session_id = session_data["id"]
        print(f"Session created: {session_id}")
        
        # Ask a question
        question = "tell me about quantum physics"
        print(f"\nAsking question: {question}")
        chat_res = await client.post(
            f"{base_url}/chat",
            json={
                "session_id": session_id,
                "message": question
            }
        )
        try:
            chat_res.raise_for_status()
            chat_data = chat_res.json()
            print("\nResponse:")
            print(chat_data["answer"])
            if chat_data.get("artifact"):
                print("\nArtifact included!")
        except Exception as e:
            print(f"Failed: {e}")
            print(chat_res.text)

if __name__ == "__main__":
    asyncio.run(test_api())
