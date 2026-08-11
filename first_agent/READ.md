
# Here is the text for deploying to cloud
adk deploy agent_engine \
  --project=agentic-ai-503915 \
  --region=us-central1 \
  --display_name=agent_app \
  first_agent

#region = eu and us not working properly use us-central1 like that FULL formate but few models are not working with the regions just change their version. eu is slow so use us or india mumbai. 
#once deployed check at Agent plateform -> Agents -> Deployments -> <app name> -> play groundd


#To install requirements.txt 
 pip install -r requirements.txt

 commands : 
 python3 -m venv .venv