import requests

url = "https://dad-jokes.p.rapidapi.com/random/joke"

headers = {
	"x-rapidapi-key": "3ef4c71f12msh62a89801249c2c6p173cd4jsnc4c3f18f4087",
	"x-rapidapi-host": "dad-jokes.p.rapidapi.com"
}

response = requests.get(url, headers=headers)

print(response.json())