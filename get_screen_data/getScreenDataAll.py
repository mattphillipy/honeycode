import boto3
import json
import pandas as pd

def lambda_handler(event,context):

    def honeyCodeClient():
        session = boto3.Session()
        honeycode_client = session.client('honeycode', region_name = 'us-west-2')
        return honeycode_client
        
    def getScreenData(honeycode_client, workbook_id, app_id, screen_id, max_results):
        response = honeycode_client.get_screen_data(
            workbookId = workbook_id,
            appId = app_id,
            screenId = screen_id,
            maxResults=max_results,           
            )
        rows_list = response["results"]["fruit_metadata List"]["rows"]
        print(f'rows_list = {rows_list}')
        return (response)
        
    def getNextToken(response):
        keys = list(response.keys())
        next_token = ''
        if 'nextToken' in keys:
            next_token = response['nextToken']        
        else:
            next_token = 'no_token'
        return next_token
        
    def createFormattedValuesList(response):
        rows = response["results"]["fruit_metadata List"]["rows"]
        formatted_values = []
        for x in rows:
            row_values = []
            z = x['dataItems']
            for y in z:
                row_values.append(y['formattedValue'])
            formatted_values.append(row_values)   
    #     dataFrame = pd.DataFrame(formatted_values)
        return formatted_values
        
    def getNextPageData(honeycode_client,workbook_id, app_id, screen_id, max_results,next_token):
        response = honeycode_client.get_screen_data(
            workbookId = workbook_id,
            appId = app_id,
            screenId = screen_id,
            maxResults= max_results,
            nextToken=next_token        
        )
        return response
        
    def createHeaders(response):
        headers = response["results"]["fruit_metadata List"]['headers']
        
        columns = []
        for m in headers:
            columns.append(m['name'])
        print(columns)
        z = 0
        
        column_dictionary = {}
        for x in columns:
            column_dictionary[z] = x
            z+=1
        return column_dictionary  
        
    def extendFormattedValues(workbook_id, app_id, screen_id, max_results,next_token,formatted_values):
        n = 1 
        while next_token != 'no_token': 
            response = getNextPageData(honeyCodeClient(),workbook_id, app_id, screen_id, max_results,next_token) 
            next_token = getNextToken(response) 
            nextPageFormattedValuesList = createFormattedValuesList(response)
            print(f'nextPageFormattedValues list = {nextPageFormattedValuesList}')
            formatted_values.extend(nextPageFormattedValuesList)
            n+=1 
            print (f'Call #{n} next_token = {next_token}')
        return formatted_values
        
    workbook_id = '4c59292c-ed6e-4f48-831a-baa0f01979a5' 
    app_id = '94894a98-1da9-4de1-a064-3e137b1fe184' 
    screen_id = 'c129fe53-9d63-4e05-ad87-fecd61e8ea89' 
    max_results = 3
    
    # initialize token object to be passed as argument to additional calls to get_screen_data API 
    next_token = 'no_token' 
    
    # first call to get_screen_data API 
    response = getScreenData(honeyCodeClient(),workbook_id,app_id,screen_id,max_results) 
    next_token = getNextToken(response) 
    formatted_values = createFormattedValuesList(response) 
    print (f'Call #1 next_token = {next_token}') 
    
    # additional calls to get_screen_data API for rows in excess of max_results
    formatted_values = extendFormattedValues(workbook_id, app_id, screen_id, max_results,next_token, formatted_values)
    
    # create pandas Data Frame
    dataFrame = pd.DataFrame(formatted_values)
    
    dataFrame = dataFrame.rename(columns = createHeaders(response) )
    
    print('df_columns= ' + dataFrame.columns)
    
    dataFrame = dataFrame.rename(columns=
    {"fruit_key column data": "fruit_key",
    "fruit_name column data": "fruit_name",
    "fruit_family column data": "fruit_family",
    "list_price column data": "list_price"}
    )
    
    dataFrame.set_index("fruit_key",inplace=True)
    
    file_name = 'fruit_metadata_s3_lambda.csv'
    lambda_file_path = '/tmp/' + file_name
    
    bucket = 'my-honeycode-bucket'
    
    dataFrame.to_csv(lambda_file_path,index=True)
    
    s3 = boto3.resource('s3')
    
    s3.Object(bucket, file_name).upload_file(lambda_file_path)
    
    