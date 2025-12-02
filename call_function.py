# hone mna3mil call lal function le be2elna 3ana l agent ma3 l parameters le bya3tina hene
from google.genai import types
from functions.get_coordinates import get_coordinates
from functions.get_weather import get_weather
from functions.check_sport_suitability import check_sport_suitability

def call_function(function_call_part, verbose=False):
    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")
    
    result = ""
    if function_call_part.name == "get_coordinates":
        result = get_coordinates(**function_call_part.args)
    if function_call_part.name == "get_weather":
        result = get_weather(**function_call_part.args)
    if function_call_part.name == "check_sport_suitability":
        result = check_sport_suitability(**function_call_part.args)
    
    if result == "":
        return types.Content(
            role="tool",
            parts = [
                types.Part.from_function_response(
                    name = function_call_part.name,
                    response = {"error": f"Unknown function: {function_call_part.name}"}
                )
            ]
        )

    return types.Content(
        role = "tool",
        parts = [
            types.Part.from_function_response(
                name = function_call_part.name,
                response = {"result": result}
            )
        ]
    )