from django.contrib.auth.decorators import login_required
from google.cloud import bigquery
from django.shortcuts import render

#store in DB eventually, also allow superuser to query all available tables
USER_TABLE_MAP = {
    "jennyback": "icef-437920.views.data_pipeline_runs",
    "samuel.taylor": "icef-437920.views.data_pipeline_runs",
    # Add more users as needed
}

@login_required
def bigquery_table_view(request):

    username = request.user.username
    table = USER_TABLE_MAP.get(username)

    if not table:
        # Optionally, show an error page or message
        return render(request, 'sds_app/client_data_pipelines.html', {
            'data': [],
            'error': "No Data Pipeline Metadata table is configured for your account."
        })

    client = bigquery.Client()
    query = f"""
    SELECT *
    FROM `{table}`
    """
    query_job = client.query(query)
    rows = list(query_job.result())
    data = [dict(row) for row in rows]
    return render(request, 'sds_app/client_data_pipelines.html', {'data': data})

#Add the column in mySQL and make it dynamic to where you can click in and insert the link to the documentation .
#Also overlapping dropdowns on profile and requests is an issue. 