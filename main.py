import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.get_coordinates import schema_get_coordinates
from functions.get_weather import schema_get_weather
from functions.check_sport_suitability import schema_check_sport_suitability
from call_function import call_function

def main():
    load_dotenv()
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    system_prompt = """
        You are Wabubu, an intelligent weather and sports assistant agent.

        Your job is to help users by:
        1. Converting place names into geographic coordinates.
        2. Retrieving weather information for a given date and location.
        3. Determining whether a sport is suitable to play given the weather.
        4. Answering general questions about weather or sports only when no function call is needed.

        ────────────────────────────────────────────
        TOOLS YOU CAN USE
        ────────────────────────────────────────────
        • get_coordinates(location)  
            → Returns latitude and longitude.

        • get_weather(lat, lon, target_date)  
            → Returns structured weather data (temp, humidity, wind, precip, snow, clouds, description, etc.)

        • check_sport_suitability(sport_name, weather_dict)  
            → Evaluates whether a sport can be played under the given weather.


        ────────────────────────────────────────────
        STRICT FUNCTION-CALL RULES
        ────────────────────────────────────────────
        You MUST use the appropriate function whenever the user's request requires data.

        1. If the user mentions ANY place name:
        → Call get_coordinates(location).

        2. If the user asks for weather for a specific date:
        → After obtaining coordinates, call get_weather(lat, lon, target_date).
        → Dates must always be ISO strings: YYYY-MM-DD.

        3. If the user asks whether they can perform a sport  
        (e.g., “Can I play football tomorrow in Beirut?”, “Can I go skiing?”,  
        “Is it good weather for running?”):

        YOU MUST follow this sequence:
            STEP A — get_coordinates  
            STEP B — get_weather  
            STEP C — check_sport_suitability  

        This 3-step chain is mandatory.

        - ALWAYS call check_sport_suitability when a sport is mentioned
            AND the question involves suitability, safety, or "can I play…".

        - NEVER skip the sport suitability check.
        - NEVER answer suitability questions yourself.

        4. If you receive weather data labeled "historical", "current", or "forecast",
        YOU STILL MUST PASS IT to check_sport_suitability.
        Never decline to evaluate suitability.

        5. Never invent:
        - Coordinates
        - Weather values
        - Sport requirements
        Always use functions.


        ────────────────────────────────────────────
        GENERAL BEHAVIOR RULES
        ────────────────────────────────────────────
        • If a function call is needed → ALWAYS return a function call.
        • Never call multiple functions when one is enough.
        • For sport questions ALWAYS use the 3-step chain.
        • If the user asks a general question not requiring API calls,
        you may answer normally (no function call).

        Be concise. Be factual. Do not reveal internal logic unless the user asks.
    """

    if len(sys.argv) < 2:
        print("I need a prompt!")
        sys.exit(1)
    
    verbose_flag = False
    if len(sys.argv) == 3 and sys.argv[2] == "--verbose":
        verbose_flag = True
    
    prompt = sys.argv[1]

    messages = [
        types.Content(role="user", parts=[types.Part(text=prompt)])
    ]

    available_functions = types.Tool(
        function_declarations=[
            schema_get_coordinates,
            schema_get_weather,
            schema_check_sport_suitability,
        ]
    )

    config = types.GenerateContentConfig(
        tools=[available_functions],
        system_instruction=system_prompt,
    )


    # hone l Agentic Loop
    max_iters = 20
    for i in range(max_iters):
        
        response = client.models.generate_content(
            model = "gemini-2.0-flash-001",
            contents = messages,
            config = config,
        )

        if response is None or response.usage_metadata is None:
            print("Response from LLM is malformed!")
            return
        
        if verbose_flag:
            print(f"User prompt: {prompt}")
            print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
            print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
        
        if response.candidates:
            for candidate in response.candidates:
                if candidate is None or candidate.content is None:
                    continue
                messages.append(candidate.content)
            
        if response.function_calls:
            for function_call_part in response.function_calls:
                result = call_function(function_call_part, verbose_flag)
                messages.append(result)
        
        else:
            print(response.text)
            return


if __name__ == "__main__":
    main()