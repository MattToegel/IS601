from flask import Blueprint, current_app, render_template, request
import requests
cats = Blueprint('cats', __name__, url_prefix='/',template_folder='templates')

@current_app.cache.cached(timeout=30)
def get_breeds():
    url = "https://api.thecatapi.com/v1/breeds"
    response = requests.get(url)

    if response.status_code == 200:
        breeds = response.json()
        return breeds
    else:
        print(f"Error: {response}")
        return []
    
@current_app.cache.cached(timeout=30, query_string=True)
def fetch_images_by_breed_id(breed_id, limit=12):
    
    url = f"https://api.thecatapi.com/v1/images/search?page=1&order=ASC"
    args = ""
    if breed_id:
        args = f"&breed_ids={breed_id}"
    args += f"&limit={limit}&api_key={current_app.api_key}"
    url += args
    print(url)
    response = requests.get(url)

    if response.status_code == 200:
        images = response.json()
        return images
    else:
        print(f"Error: {response}")
        return []
    
@cats.route("/cats")
def sample_live_list():
    breeds = get_breeds()
    breed_id = request.args.get("breed_id")
    cats = fetch_images_by_breed_id(breed_id)
    
    return render_template("cats.html", cats=cats, breeds=breeds)