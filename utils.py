import json


def build_JSON(list_of_objects):
    """
    Converts a list of objects into a JSON string with a structured format.

    Args:
        list_of_objects (list): A list of Python dictionaries representing objects.

    Returns:
        str: A formatted JSON string containing the objects under the 'data' key.
    """
    json_data = {"data": list_of_objects}
    return json.dumps(json_data, indent=4)


def json_to_dict(json_data):
    """
    Parses a JSON string and converts it into a list of Python dictionaries.

    This function ensures that:
    - If objects are stored as JSON strings within the 'data' array, they are properly decoded.
    - String representations of lists (e.g., 'strongest_skills' and 'challenges') are converted into actual lists.

    Args:
        json_data (str): A JSON string containing a 'data' key with a list of objects.

    Returns:
        list: A list of Python dictionaries, each representing an object from the JSON data.
    """
    parsed_data = json.loads(json_data)
    objects = parsed_data.get("data", [])

    # If objects are stored as JSON-encoded strings, convert them to dictionaries
    if all(isinstance(obj, str) for obj in objects):
        objects = [json.loads(obj) for obj in objects]

    for obj in objects:
        if isinstance(obj.get("strongest_skills"), str):
            obj["strongest_skills"] = obj["strongest_skills"].split(", ")
        if isinstance(obj.get("challenges"), str):
            obj["challenges"] = obj["challenges"].split(", ")

    return objects


if __name__ == '__main__':
    # Open the example.json file and read its contents
    with open("example.json", "r", encoding="utf-8") as file:
        json_content = file.read()

    # Convert the JSON string into a list of Python objects
    python_objects = json_to_dict(json_content)

    # Print the result
    print(python_objects)
