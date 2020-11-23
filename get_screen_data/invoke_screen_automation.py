import boto3
import json
import pandas as pd

def lambda_handler(event,context):

   
    def honeyCodeClient():
        session = boto3.Session()
        honeycode_client = session.client('honeycode', region_name = 'us-west-2')
        return honeycode_client
        
    def invoke_screen_automation(honeycode_client,workbook_id,app_id,screen_id,screen_automation_id):
        response = honeycode_client.invoke_screen_automation(
            workbookId= workbook_id,
            appId=app_id,
            screenId=screen_id,
            screenAutomationId=screen_automation_id,
            variables={
                "fruit_key content": {"rawValue": "papayagr"}
            }
                    
            )
        return response
            
    workbook_id = '4c59292c-ed6e-4f48-831a-baa0f01979a5' 
    app_id = '94894a98-1da9-4de1-a064-3e137b1fe184' 
    screen_id = 'c129fe53-9d63-4e05-ad87-fecd61e8ea89' 
    screen_automation_id = 'f6934cd4-3b85-4089-91d0-954566188992'
    
    
    responseObject = invoke_screen_automation(honeyCodeClient(),workbook_id,app_id,screen_id,screen_automation_id)
    print(responseObject)
        
    
    
    