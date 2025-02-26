I need to connect to an API endpoint after authenticating and acquiring and JWT.  Once the API call returns the JSON payload   

Here is what I have to authenticate on the Opendock Platform:

# Function to make an authenticated API call
def make_api_call( api_base_url, jwt_token):
    print("API URL:", api_base_url)  # Debugging line
    headers = {'Authorization': f'Bearer {jwt_token}'}
    try:
        response = requests.get(api_base_url, headers=headers)
        response.raise_for_status()
        api_response = response.json()
        #####print("API Response:", api_response)  # Debugging line
        return api_response
    except requests.RequestException as e:
        print(f"Error making API call")
        return None    



def get_jwt_token():
    api_url = 'https://neutron.opendock.com/auth/login'
    payload = {'email': 'nkrug@allendistribution.com', 'password': '@113nAPI$'}
    
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        data = response.json()
        
        if 'access_token' in data:
            return data['access_token']
        else:
            print("Error: 'token' key not found in JSON response.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error obtaining JWT token: {e}")
        return None

here is the API call that is made to the Opendockplatform to get all the records between 2 specified times and from specific warehouses:

https://neutron.opendock.com/appointment?s={ "lastChangedDateTime": {"$between": ["2024-04-29T12:10:00Z","2024-04-29T18:10:00Z"]}, "status": {"$notin": ["Cancelled", "Completed"] }, "dock.warehouseId":{"$in":["5dcc6a47-890f-40b9-9acd-ce07999ae589","a6671751-784a-44b2-b8df-3428d55062c4"]}}&join=dock||warehouseId,name&join=dock.warehouse||name

I need to iterate through the JSON extracting the confirmation numbers for each appointment.  The confirmationnumber will be used to create another JSON payload that will be POSTed to an endpoint on another platform (YMS).

If the record is found then the code will move on to the next confirmationnumber in the  JSON payload.  If the no record is found on the other YMS platform then a  JSON payload will need to be constructed to create a new appointment record on the YMS platform.



The second platform called Yard Management Systems or YMS for short, has a predefined bearer token to use with thier API   here are those details along with a sample endpoint

        url = "https://allen.api.ymshub.com/api/v2/appointments"

        # Bearer token for authentication and content type for YMS
        headers = {
            "Authorization": "Bearer 6|nLhEJXttzvwRJCOtpoAn8brtBOrXfaeyTp1v33jO",
            "Content-Type": "application/json",
            "Accept" : "application/json"
        }

When the YMS platform does not find a record with the confirmationnumber which we will know by the results of the api call -  If the appointment record is found we will receive a 204No Content result  if the record is not found will get a JSON result the looks like this 
{
    "success": false,
    "message": "",
    "data": "Resource not found."
}

Again, if the record is not found I must write some code that will build a JSON payload that we can submit to the YMS platform to create a new appointment. the code for this I will work on later so I need a placeholder in the code.  This will likely be a function in another script that we will call.

I hope all this makes sense.  Can you help me by generating the python code described to I can review and begin to make iterative adjustment with your continued help?
