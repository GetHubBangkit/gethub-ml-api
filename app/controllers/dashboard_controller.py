from fastapi.responses import JSONResponse
from app.helpers.handler import show_model
from fastapi import Request
from sqlalchemy import text
from configs.config import get_database_engine

engine = get_database_engine()

def get_dashboard(request: Request) -> JSONResponse:
    with engine.connect() as conn:
        # Construct the SQL query to count totals from different tables
        query_totals = text("""
            SELECT 'total_user' AS table_name, COUNT(*) AS total FROM users
            UNION ALL
            SELECT 'total_sponsor' AS table_name, COUNT(*) AS total FROM sponsors
            UNION ALL
            SELECT 'total_event' AS table_name, COUNT(*) AS total FROM informations
            UNION ALL
            SELECT 'total_project' AS table_name, COUNT(*) AS total FROM projects;
        """)

        result_totals = conn.execute(query_totals)
        totals = result_totals.fetchall()

        if not totals:
            return show_model(0, "No data found", data=None)

        # Create a dictionary to store the totals results
        result_dict = {total[0]: total[1] for total in totals}

        # Construct the SQL query for chart data
        query_chart = text("""
            SELECT 
                c.name, 
                COUNT(p.id) AS total
            FROM 
                categories c 
            INNER JOIN 
                projects p 
            ON 
                c.id = p.category_id 
            GROUP BY 
                c.id, c.name;
        """)

        result_chart = conn.execute(query_chart)
        chart_data = result_chart.fetchall()

        # Convert chart data to a list of dictionaries
        chart_list = [{"name": chart[0], "total": chart[1]} for chart in chart_data]

        # Add chart data to the result dictionary
        result_dict["chart"] = chart_list

    return show_model(0, "Dashboard Totals", result_dict)
