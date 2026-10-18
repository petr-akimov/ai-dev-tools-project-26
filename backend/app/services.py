import os
from gigachat import GigaChat

from .schemas import MatchCreate


def generate_recap_service_sync(match: MatchCreate) -> tuple[str, str]:
    # Retrieve GigaChat configuration from environment variables
    auth_key = os.getenv("GIGACHAT_AUTH_KEY")
    model_name = os.getenv("GIGACHAT_MODEL", "GigaChat-2")

    if not auth_key:
        # Fallback if authorization key is missing
        fallback_recap = (
            f"Match played between {match.home_team} and {match.away_team} "
            f"ended with a score of {match.home_score}-{match.away_score}."
        )
        return fallback_recap, "fallback-local"

    home_goals = [f"{s.player} {s.minute}'" for s in match.scorers if s.team == match.home_team]
    away_goals = [f"{s.player} {s.minute}'" for s in match.scorers if s.team == match.away_team]

    context = (
        f"Match: {match.home_team} vs {match.away_team} ({match.match_date}). "
        f"Final Score: {match.home_score}-{match.away_score}. "
        f"{match.home_team} goals: {', '.join(home_goals) if home_goals else 'None'}. "
        f"{match.away_team} goals: {', '.join(away_goals) if away_goals else 'None'}. "
        f"Key details: {match.summary_notes or 'Standard match flow.'}"
    )

    try:
        # Initialize GigaChat client with self-signed SSL verification disabled
        with GigaChat(
            credentials=auth_key,
            scope="GIGACHAT_API_PERS",
            model=model_name,
            verify_ssl_certs=False
        ) as client:
            system_prompt = (
                "An expert sports journalist. "
                "Write a 2-3 sentence match recap strictly based ONLY on the provided match stats."
            )
            
            # Send completion request
            response = client.chat(f"{system_prompt}\n\n{context}")
            recap_text = response.choices[0].message.content if response.choices else ""
            return recap_text, model_name

    except Exception as e:
        # Fallback mode if GigaChat API is unreachable or fails
        print(f"GigaChat service error: {e}")
        fallback_recap = (
            f"Match played between {match.home_team} and {match.away_team} "
            f"ended with a score of {match.home_score}-{match.away_score}."
        )
        return fallback_recap, "fallback-local"


async def generate_recap_service(match: MatchCreate) -> tuple[str, str]:
    # Wrapper function for asynchronous service execution
    return generate_recap_service_sync(match)