from fastapi.responses import JSONResponse
from app.helpers.handler import show_model, show_list_model
from fastapi import Request
from sqlalchemy import text
from configs.config import get_database_engine
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

engine = get_database_engine()


def fetch_data_from_database(request, profession=None):
    with engine.connect() as conn:
        query = text("SELECT * FROM informations")
        result = conn.execute(query)
        data_from_db = result.fetchall()

        if not data_from_db:
            return show_model(0, "No data found with the specified profession", data=None)

    columns = result.keys()
    results = []
    for row in data_from_db:
        user_dict = dict(zip(columns, row))
        user_dict["createdAt"] = str(user_dict["createdAt"])
        user_dict["updatedAt"] = str(user_dict["updatedAt"])
        results.append(user_dict)

    list_data = results

    if profession:
        if isinstance(profession, str):
            list_data = [row for row in list_data if row['title'] and profession.lower() in row['title'].lower()]
        else:
            list_data = [row for row in list_data if row['title'] and profession.default and profession.default.lower() in row['title'].lower()]

    return list_data


def create_content_based_recommender(list_of_data, target_profession, similarity_threshold=0.5):
    professions = [row['title'] for row in list_of_data if row['title']]
    if not professions:
        return []

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(professions + [target_profession])

    similarities = cosine_similarity(tfidf_matrix[:-1], tfidf_matrix)
    similar_users = []

    for row, sim in zip(list_of_data, similarities[0]):
        if sim > similarity_threshold:
            row_with_similarity = row.copy()
            row_with_similarity['similarity'] = sim
            similar_users.append(row_with_similarity)

    return similar_users


def getlist(request: Request) -> JSONResponse:
    profession = request.query_params.get("profession")
    try:
        if profession is None:
            return show_model(404, "Profesi Wajib Di isi!", data=None)

        if profession == "":
            return show_model(404, "Profesi Wajib Di isi!", data=None)

        data_from_db = fetch_data_from_database(request, profession)

        if isinstance(data_from_db, JSONResponse):
            return data_from_db

        if not data_from_db:
            return show_model(404, "No Data found with the specified profession", data=None)

        similar_users = create_content_based_recommender(data_from_db, profession)

        if not similar_users:
            return show_model(404, "No similar Data found", data=None)

        return show_list_model(0, "Successfully Get Data", similar_users, len(similar_users))
    except Exception as e:
        return show_model(500, str(e), data=None)
