from flask import Flask, request, jsonify, render_template
from openai import OpenAI
import os
import requests
import json
import datetime

app = Flask(__name__)

# Initialize the OpenAI client

client = OpenAI(
  api_key="key1",  # this is also the default, it can be omitted
)

date = datetime.datetime.now()

# The travel API function as provided
def travel_api(departDate, toEntityId, fromEntityId, adults=1, children=0, infants=0):
    url = "https://sky-scanner3.p.rapidapi.com/flights/search-multi-city"
    headers = {
        "Content-Type": "application/json",
        "x-rapidapi-host": "sky-scanner3.p.rapidapi.com",
        "x-rapidapi-key": "key2"  # Make sure to use a valid API key
        }

    #if adults is NA, make it into 1
    if adults == "NA":
        adults = 1
    #if children is NA, make it into 0
    if children == "NA":
        children = 0
    #if infants is NA, make it into 0
    if infants == "NA":
        infants = 0

    # Define the data payload
    data = {
        "market": "US",
        "locale": "en-US",
        "currency": "USD",
        "adults":  adults,
        "children": children,
        "infants": infants,
      #  "cabinClass": "economy",
        "flights": [
            {
                "fromEntityId": fromEntityId,  # Ensure this is the correct code for your departure airport
                "toEntityId": toEntityId,     # Ensure this is the correct code for your arrival airport
                "departDate": departDate
            }
        ],
        #"stops": ["direct", "1stop", "2stops"],  # Consider removing this to see if it affects results
        "sort": "cheapest_first",
        #"airlines": [-32753, -32695]  # Ensure these IDs are correct for your desired airlines
    }

    # Make the POST request
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # Check the response
    if response.status_code == 200:
        result = response.json()
        #only take the first three results if there are more
        if len(result["data"]["itineraries"]) > 3:
            result = result["data"]["itineraries"][:3]
        else:
            result = result["data"]["itineraries"]
    else:
        print("Error:", response.status_code, response.text)

    return result

# Evaluate trip options function
def evaluate_trip_options(options):
    """
    Function assistant agent to evaluate trip options based on user flight API response. Will receive a list of JSON objects from the response from the API. This
    This function should look throught them and summarize the options from the response.
    It should return a list of the options ordered by number.
    It should say (Recommended Option) for the best one to fit the criteria.
    """
    
   
    gpt_prompt = f"""
    Act as an assistant agent to show the user the flight options returned. 
    look through the response options and summarize the options from the response.
    It should return a list of the options ordered by number.
    It should say (Recommended Option) for the best one to fit the criteria.
    In every option outline, give the url to the booking site (the airline website) and the flight number.
    List the options like:
    Option 1, info...
    Option 2, info...
    Option 3 (Recommended), info...
    etc.
    IMPORTANT: Include line breaks between each option and make it easy to read. ONCE ONE OPTION ENDS, END THE LINE AND START THE NEXT OPTION ON THE NEXT LINE.
    Don't format it in JSON format at all, make it all natural language and easy to read.
    Don't include tags or overall scores in the response
    Here are the options returned by the API:
    {options}
    Here is today's date:
    {date}
    """
    
     # Call GPT API to process the conversation
    completion = client.completions.create(model="gpt-3.5-turbo-instruct", prompt=gpt_prompt, max_tokens=200)

    gpt_response = completion.choices[0].text
   
   
    # Step 5: Return the final GPT-generated summary
    return gpt_response



parameters = {
    "name": "search_restaurants",
    "description": "Search for flights based on user input",
    "parameters": {
        "type": "object",
        "properties": {
                    "departDate": {"type": "string", "description": "date of departure"},
                    "toEntityId": {"type": "string", "description": "Location of the airport you want to fly to"},
                    "fromEntityId": {"type": "string", "description": "Location of the airport you want to fly from"},
                   # "cabinClass": {"type": "number", "description": "Cabin class"},
                    "adults": {"type": "number", "description": "Number of adults"},
                    "children": {"type": "boolean", "description": "Number of children"},
                    "infants": {"type": "string", "description": "Number of infants"}
        },
        "required": ["departDate", "toEntityId", "fromEntityId"]
    }
}

tools = [
    {
         "type": "function",
        "function": {
            'name': 'search_restaurants', 
            'description': 'Search for restaurants based on user input', 
            'parameters': {
                "type": "object",
                "properties": {
                    "departDate": {"type": "string", "description": "date of departure"},
                    "toEntityId": {"type": "string", "description": "Location of the airport you want to fly to"},
                    "fromEntityId": {"type": "string", "description": "Location of the airport you want to fly from"},
                    #"cabinClass": {"type": "number", "description": "Cabin class"},
                    "adults": {"type": "number", "description": "Number of adults"},
                    "children": {"type": "boolean", "description": "Number of children"},
                    "infants": {"type": "string", "description": "Number of infants"}
                },
            "required": ["departDate", "toEntityId", "fromEntityId"]
             }
            }
    }
]

messages = []
messages.append({"role": "system", "content": "You are a helpful travel agent. Use the supplied tools to assist the user. Do not try to plan the entire trip, or anything outside of their flight."})

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get("user_input")
    messages.append({"role": "user", "content": user_input})
    
    # Get the GPT response based on the input message
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=messages,
        tools=tools,
    )

    finish_reason = response.choices[0].finish_reason
    assistant_response = ""

    if finish_reason == 'stop':
        assistant_response = response.choices[0].message.content
        messages.append({"role": "assistant", "content": assistant_response})
        
    elif finish_reason == 'tool_calls':
        tool_call = response.choices[0].message.tool_calls[0]
        arguments = json.loads(tool_call.function.arguments)

        arguments.setdefault("adults", 1)
        arguments.setdefault("children", 0)
        arguments.setdefault("infants", 0)

        # Call travel API
        result = travel_api(
            departDate=arguments["departDate"],
            toEntityId=arguments["toEntityId"],
            fromEntityId=arguments["fromEntityId"],
            adults=arguments["adults"],
            children=arguments["children"],
            infants=arguments["infants"]
        )

        # Evaluate options
        assistant_response = evaluate_trip_options(result)
        messages.append({"role": "assistant", "content": assistant_response})

    else:
        assistant_response = "I didn't understand that. Can you provide more details?"

    return jsonify({"response": assistant_response})

@app.route('/')
def index():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)
