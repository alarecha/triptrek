from openai import OpenAI
import os
import requests
import json

client = OpenAI(
  api_key="api-key",  # this is also the default, it can be omitted
)


# Define the URL and headers
def travel_api(departDate, toEntityId, fromEntityId, cabinClass="economy", adults=1, children=0, infants=0):
  url = "https://sky-scanner3.p.rapidapi.com/flights/search-multi-city"
  headers = {
      "Content-Type": "application/json",
      "x-rapidapi-host": "sky-scanner3.p.rapidapi.com",
      "x-rapidapi-key": "api-key2"  # Make sure to use a valid API key
  }

  # Define the data payload
  data = {
      "market": "US",
      "locale": "en-US",
      "currency": "USD",
      "adults":  adults,
      "children": children,
      "infants": infants,
      "cabinClass": cabinClass,
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
      print("Success!")
      result = response.json()
      #only take the first three results
      result = result["data"]["itineraries"][:3]
  else:
      print("Error:", response.status_code, response.text)

  return result

  

# Function to process user inputs and interact with GPT
def get_llm_response(user_messages, api_key):
    """
    Function to handle multiple user inputs, infer trip planning parameters,
    and call a travel API to fetch trip options based on GPT analysis.
    
    :param user_messages: List of messages from the user as a conversation.
    :param api_key: API key for the travel API (placeholder).
    :return: GPT response with trip suggestions and advice.
    """
    
    # Step 1: Combine user messages for GPT input
    conversation = "\n".join([f"User: {msg}" for msg in user_messages])
    
    # Step 2: Use GPT to infer trip details from the conversation
    gpt_prompt = f"""
    You are an AI travel assistant. Based on the following conversation, extract key trip parameters such as destination, travel dates, budget, flight preferences, and activity preferences:
    
    {conversation}
    
    Please output the extracted parameters in a structured format that we could insert into this function: travel_api(departDate, toEntityId, fromEntityId, cabinClass="economy", adults=1, children=0, infants=0)
    the format of date should be in the format of "YYYY-MM-DD"
    the toEntityID and fromEntityID should be the airport codes like DTW for Detroit Metro Airport

    
  Pass the parameter values in a dictionary and only that. Please include the paramater name and it's value and include all parameters from the call: travel_api(departDate, toEntityId, fromEntityId, cabinClass="economy", adults=1, children=0, infants=0), making the parameters you couldn't find out NA. Pass only the dictionary and nothing else, I must use this to turn into a dict. 
  An example dictionary would look like: 
  [departDate: "2024-07-15", toEntityId: "LAX", fromEntityId: "JFK", cabinClass: "economy", adults: 1, children: 0, infants: 0] but with curly brackets instead of the square brackets. Do not add any additional fields to the dictionary.
    """
    
    # Call GPT API to process the conversation
    completion1 = client.completions.create(model="gpt-3.5-turbo-instruct", prompt=gpt_prompt, max_tokens=200)

    gpt_response = completion1.choices[0].text
    print(json.loads(gpt_response))
    # Extract GPT's understanding of the trip parameters
    trip_parameters = json.loads(gpt_response)
    
    # Step 3: Placeholder for travel API call (use inferred parameters)
    # You would replace this with the actual API call once you've selected your travel API.
    # Here, we simulate an API call with a placeholder response.

    #travel_api_response = call_travel_api(trip_parameters, api_key)
    # make a placeholder response of three different flight options with prices and durations from CT to Portugal and back in json format
    travel_api_response = travel_api(departDate=trip_parameters["departDate"], toEntityId=trip_parameters["toEntityId"], fromEntityId=trip_parameters["fromEntityId"], cabinClass="economy", adults=trip_parameters["adults"], children=trip_parameters["children"], infants=trip_parameters["infants"])
    print(travel_api_response)

    # Step 4: Summarize options and provide advice using GPT
    gpt_summary_prompt = f"""
    Based on the following trip parameters and travel API results, highlight the possible trip options given from the response and provide some advice to the user. 
    I would like you to give the best 3 options in a format where you say Option 1: and list the info, and so on, and then provide the tag
    (Recommended Option) for the best one to fit the criteria:
    
    Trip Parameters:
    {trip_parameters}
    
    Travel API Results:
    {travel_api_response}
    
    Provide a helpful, conversational summary.
    """
    
    completion = client.completions.create(model="gpt-3.5-turbo-instruct", prompt=gpt_summary_prompt, max_tokens=200)
    
    # Step 5: Return the final GPT-generated summary
    print(completion.choices[0].text)



get_llm_response(["I want to go on a trip to LAX from JFK.", "I want to leave on july 1 2025.", "I have a budget of $2000.", "I want to save money if possible."], key)
