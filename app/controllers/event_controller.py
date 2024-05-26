from fastapi.responses import JSONResponse
from app.helpers.handler import show_model, show_list_model
from fastapi import Request
from sqlalchemy import text
from configs.config import get_database_engine
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

engine = get_database_engine()


def fetch_data_from_database(request, profession=None):
    # Mock data for demonstration purposes
    with engine.connect() as conn:
        # Construct the SQL query with LIKE for partial matching of professions
        query = text("SELECT * FROM informations")
        # Pass the profession parameter using bindparams
        result = conn.execute(query)
        data_from_db = result.fetchall()

        if not data_from_db:
            return show_model(0, "No data found with the specified profession", data=None)

    # Get column names from the query result
    columns = result.keys()

    # Convert fetchall result to a list of dictionaries
    results = []
    for row in data_from_db:
        user_dict = dict(zip(columns, row))

        # Convert datetime values to strings
        user_dict["createdAt"] = str(user_dict["createdAt"])
        user_dict["updatedAt"] = str(user_dict["updatedAt"])

        results.append(user_dict)

    list_data = results

    # Filter users by profession if specified
    if profession:
        if isinstance(profession, str):
            list_data = [row for row in list_data if
                         row['title'] and profession.lower() in row['title'].lower()]
        else:  # Handle Query object
            list_data = [row for row in list_data if
                         row['title'] and profession.default and profession.default.lower() in row[
                             'title'].lower()]

    return list_data


# Function to create recommendation system based on profession
def create_content_based_recommender(list_of_data, target_profession, similarity_threshold=0.5):
    professions = [row['title'] for row in list_of_data if row['title']]  # Filter out None values
    if not professions:
        return []

    # Initialize TF-IDF Vectorizer
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(professions + [target_profession])

    # Calculate cosine similarity between professions and target profession
    similarities = cosine_similarity(tfidf_matrix[:-1], tfidf_matrix)
    similar_users = []

    for row, sim in zip(list_of_data, similarities[0]):
        if sim > similarity_threshold:
            row_with_similarity = row.copy()  # Make a copy of the user dictionary
            row_with_similarity['similarity'] = sim  # Add 'similarity' field
            similar_users.append(row_with_similarity)

    return similar_users


def getlist(request: Request) -> JSONResponse:
    profession = request.query_params.get("profession")
    try:
        if profession is None:
            return show_model(500, "Profesi Wajib Di isi!", data=None)

        # Fetch users from database based on profession
        data_from_db = fetch_data_from_database(request, profession)

        if not data_from_db:
            return show_model(0, "No Data found with the specified profession", data=None)

        # Get recommended users based on profession similarity
        similar_users = create_content_based_recommender(data_from_db, profession)

        if not similar_users:
            return show_model(0, "No similar Data found", data=None)

        return show_list_model(0, "Successfully Get Data", similar_users, len(similar_users))
    except Exception as e:
        return show_model(500, str(e), data=None)
