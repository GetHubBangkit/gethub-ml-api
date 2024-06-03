from fastapi.responses import JSONResponse
from app.helpers.handler import show_model, show_list_model
from fastapi import Request, Query
from sqlalchemy import text
from configs.config import get_database_engine
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

engine = get_database_engine()

def fetch_users_from_database(request, profession=None):
    # Mock data for demonstration purposes
    with engine.connect() as conn:
        # Construct the SQL query with LIKE for partial matching of professions
        query = text("SELECT * FROM users WHERE is_visibility = 1")
        # Pass the profession parameter using bindparams
        result = conn.execute(query)
        users = result.fetchall()

        if not users:
            return show_model( 0, "No users found with the specified profession", data=None)

    # Get column names from the query result
    columns = result.keys()

    # Convert fetchall result to a list of dictionaries
    formatted_users = []
    for user in users:
        user_dict = dict(zip(columns, user))

        # Convert datetime values to strings
        user_dict["createdAt"] = str(user_dict["createdAt"])
        user_dict["updatedAt"] = str(user_dict["updatedAt"])

        user_dict.pop("role_id", None)
        user_dict.pop("password", None)
        user_dict.pop("phone", None)
        user_dict.pop("web", None)
        user_dict.pop("address", None)
        user_dict.pop("photo", None)
        user_dict.pop("expired_membership", None)
        user_dict.pop("about", None)
        user_dict.pop("qr_code", None)
        user_dict.pop("is_verify", None)
        user_dict.pop("is_complete_profile", None)
        user_dict.pop("is_premium", None)
        user_dict.pop("theme_hub", None)

        formatted_users.append(user_dict)

    users = formatted_users

    # Filter users by profession if specified
    if profession:
        if isinstance(profession, str):
            users = [user for user in users if user['profession'] and profession.lower() in user['profession'].lower()]
        else:  # Handle Query object
            users = [user for user in users if
                     user['profession'] and profession.default and profession.default.lower() in user[
                         'profession'].lower()]

    return users


# Function to create recommendation system based on profession
def create_profession_based_recommender(users, target_profession, similarity_threshold=0.5):
    professions = [user['profession'] for user in users if user['profession']]  # Filter out None values
    if not professions:
        return []

    # Initialize TF-IDF Vectorizer
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(professions + [target_profession])

    # Calculate cosine similarity between professions and target profession
    similarities = cosine_similarity(tfidf_matrix[:-1], tfidf_matrix)
    similar_users = []

    for user, sim in zip(users, similarities[0]):
        if sim > similarity_threshold:
            user_with_similarity = user.copy()  # Make a copy of the user dictionary
            user_with_similarity['similarity'] = sim  # Add 'similarity' field
            similar_users.append(user_with_similarity)

    return similar_users

def getlist(request: Request) -> JSONResponse:
    profession = request.query_params.get("profession")
    try:
        if profession is None:
            return show_model(404, "Profesi Wajib Di isi!", data=None)

        if profession == "":
            return show_model(404, "Profesi Wajib Di isi!", data=None)

        # Fetch users from database based on profession
        users = fetch_users_from_database(request, profession)

        if not users:
            return show_model(404, "No users found with the specified profession", data=None)

        # Get recommended users based on profession similarity
        similar_users = create_profession_based_recommender(users, profession)

        if not similar_users:
            return show_model(404, "No similar users found", data=None)

        return show_list_model(0, "Successfully Get Data", similar_users, len(similar_users))
    except Exception as e:
        return show_model(500, str(e), data=None)
