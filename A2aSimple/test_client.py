import uuid
import httpx
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import (
    AgentCard,
    Message,
    MessageSendParams,
    Part,
    Role,
    SendMessageRequest,
    TextPart,
)
import json
from datetime import datetime




# CHANGE THIS LINE: Use HTTP instead of HTTPS
PUBLIC_AGENT_CARD_PATH = "/.well-known/agent.json"
BASE_URL = "http://localhost:9999"  # Changed from https:// to http://

async def main() -> None:
    async with httpx.AsyncClient() as httpx_client:
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=BASE_URL,
        )


        final_agent_card_to_use: AgentCard | None = None

        try:
            print(f"Fetching public agent card from: {BASE_URL}{PUBLIC_AGENT_CARD_PATH}")

            _public_card = await resolver.get_agent_card()
            print("Fetched public agent card")
            print(_public_card.model_dump_json(indent=2))

            final_agent_card_to_use = _public_card

        except Exception as e:
            print(f"Error fetching public agent card: {e}")
            raise RuntimeError("Failed to fetch public agent card")
        
        client = A2AClient(
            httpx_client=httpx_client, agent_card=final_agent_card_to_use
        )
        print("A2AClient initalized")

        message_payload = Message(
            role=Role.user,
            messageId=str(uuid.uuid4()),
            parts=[Part(root=TextPart(text="Hello, how are you?"))],
        )
        request = SendMessageRequest(
            id=str(uuid.uuid4()),
            params=MessageSendParams(
                message=message_payload,
            ),
        )
        print("Sending message")

        response = await client.send_message(request)

        response_dict = response.model_dump()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"resposne_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(response_dict, f, indent=2, ensure_ascii=False)

        print(f"Response saved to {filename}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())