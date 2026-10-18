import os
from gigachat import GigaChat
from .schemas import StoryCreate


def generate_story_service_sync(story: StoryCreate) -> tuple[str, str]:
    # Retrieve GigaChat configuration from environment variables
    auth_key = os.getenv("GIGACHAT_AUTH_KEY")
    model_name = os.getenv("GIGACHAT_MODEL", "GigaChat-2")

    if not auth_key:
        # Fallback if authorization key is missing
        fallback_story = (
            f"Story '{story.title}'. In {story.when_happens} at {story.where_happens}, "
            f"heroes ({story.heroes}) faced the following events: {story.summary}."
        )
        return fallback_story, "fallback-local"

    # Build context prompt for the model in English
    context = (
        f"Title: {story.title}\n"
        f"When: {story.when_happens}\n"
        f"Where: {story.where_happens}\n"
        f"Heroes: {story.heroes}\n"
        f"Plot summary: {story.summary}"
    )

    try:
        # Initialize GigaChat client
        with GigaChat(
            credentials=auth_key,
            scope="GIGACHAT_API_PERS",
            model=model_name,
            verify_ssl_certs=False
        ) as client:
            system_prompt = (
                "You are an expert sci-fi fiction writer. "
                "Write an engaging, detailed, and immersive science fiction short story "
                "strictly based on the provided input data."
            )

            # Send completion request to GigaChat-2
            response = client.chat(f"{system_prompt}\n\n{context}")
            story_text = response.choices[0].message.content if response.choices else ""
            return story_text, model_name

    except Exception as e:
        # Fallback mode if GigaChat API fails or is unreachable
        print(f"GigaChat service error: {e}")
        fallback_story = (
            f"Story '{story.title}'. In {story.when_happens} at {story.where_happens}, "
            f"heroes ({story.heroes}) faced the following events: {story.summary}."
        )
        return fallback_story, "fallback-local"


async def generate_story_service(story: StoryCreate) -> tuple[str, str]:
    # Asynchronous wrapper for the synchronous GigaChat service call
    return generate_story_service_sync(story)