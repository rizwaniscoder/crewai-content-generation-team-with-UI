import streamlit as st
from io import StringIO
import logging
from dotenv import load_dotenv
from crewai import Agent, Crew
from openai import OpenAI
import os
import requests
from tasks import MarketingAnalysisTasks
from agents import MarketingAnalysisAgents
import re
import sys
# Load environment variables
load_dotenv()

tasks = MarketingAnalysisTasks()
agents = MarketingAnalysisAgents()


def post_on_facebook(image_url, caption):
    # You need to replace 'PAGE_ACCESS_TOKEN' with your actual Facebook Page Access Token
    page_access_token = 'PAGE_ACCESS_TOKEN'
    page_id = 'PAGE_ID'
    post_url = f"https://graph.facebook.com/{page_id}/photos"

    # Upload the image
    image_response = requests.post(post_url, data={'url': image_url}, params={'access_token': page_access_token})
    image_data = image_response.json()

    if 'id' in image_data:
        # Image uploaded successfully, now post the caption
        caption_response = requests.post(f"https://graph.facebook.com/{page_id}/feed",
                                         data={'message': caption, 'published': 'true', 'attached_media[0]': f"{'{'}'media_fbid': {image_data['id']}{'}'}"},
                                         params={'access_token': page_access_token})
        caption_data = caption_response.json()

        if 'id' in caption_data:
            return True
        else:
            return False
    else:
        return False

# Function to post on Instagram
def post_on_instagram(image_url, caption):
    # You need to replace 'INSTAGRAM_ACCESS_TOKEN' with your actual Instagram Access Token
    instagram_access_token = 'INSTAGRAM_ACCESS_TOKEN'
    # This endpoint is just a placeholder, actual Instagram posting mechanism is more complex and requires additional steps
    instagram_post_url = 'https://api.instagram.com/v1/media/upload/'

    # Upload the image
    image_response = requests.post(instagram_post_url, data={'url': image_url}, params={'access_token': instagram_access_token})
    image_data = image_response.json()

    if 'id' in image_data:
        # Image uploaded successfully, now post the caption
        caption_response = requests.post('https://api.instagram.com/v1/media/{0}/comments'.format(image_data['id']),
                                         data={'message': caption, 'published': 'true'},
                                         params={'access_token': instagram_access_token})
        caption_data = caption_response.json()

        if 'id' in caption_data:
            return True
        else:
            return False
    else:
        return False

# Function to post on Twitter
def post_on_twitter(image_url, caption):
    # You need to replace 'BEARER_TOKEN' with your actual Twitter Bearer Token
    bearer_token = 'BEARER_TOKEN'
    tweet_url = "https://api.twitter.com/2/tweets"

    # Prepare the tweet data
    tweet_data = {
        'text': caption,
        'media': {'media_url': image_url}
    }

    # Post the tweet
    headers = {"Authorization": f"Bearer {bearer_token}", "Content-Type": "application/json"}
    response = requests.post(tweet_url, json=tweet_data, headers=headers)

    if response.status_code == 200:
        return True
    else:
        return False

# Function to generate images using DALL·E 3
def generate_image(prompt, crewai_client):
    response = crewai_client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    return response.data[0].url


# StreamToExpander class for logging
class StreamToExpander:
    def __init__(self, expander):
        self.expander = expander
        self.buffer = []
        self.colors = ['red', 'green', 'blue', 'orange']  # Define a list of colors
        self.color_index = 0  # Initialize color index

    def write(self, data):
        # Filter out ANSI escape codes using a regular expression
        cleaned_data = re.sub(r'\x1B\[[0-9;]*[mK]', '', data)

        # Check if the data contains 'task' information
        task_match_object = re.search(r'\"task\"\s*:\s*\"(.*?)\"', cleaned_data, re.IGNORECASE)
        task_match_input = re.search(r'task\s*:\s*([^\n]*)', cleaned_data, re.IGNORECASE)
        task_value = None
        if task_match_object:
            task_value = task_match_object.group(1)
        elif task_match_input:
            task_value = task_match_input.group(1).strip()

        if task_value:
            st.toast(":robot_face: " + task_value)

        # Check if the text contains the specified phrase and apply color
        if "Entering new CrewAgentExecutor chain" in cleaned_data:
            # Apply different color and switch color index
            self.color_index = (self.color_index + 1) % len(self.colors)  # Increment color index and wrap around if necessary

            cleaned_data = cleaned_data.replace("Entering new CrewAgentExecutor chain", f":{self.colors[self.color_index]}[Entering new CrewAgentExecutor chain]")

        if "Market Research Analyst" in cleaned_data:
            # Apply different color 
            cleaned_data = cleaned_data.replace("Market Research Analyst", f":{self.colors[self.color_index]}[Market Research Analyst]")
        if "Business Development Consultant" in cleaned_data:
            cleaned_data = cleaned_data.replace("Business Development Consultant", f":{self.colors[self.color_index]}[Business Development Consultant]")
        if "Technology Expert" in cleaned_data:
            cleaned_data = cleaned_data.replace("Technology Expert", f":{self.colors[self.color_index]}[Technology Expert]")
        if "Finished chain." in cleaned_data:
            cleaned_data = cleaned_data.replace("Finished chain.", f":{self.colors[self.color_index]}[Finished chain.]")

        self.buffer.append(cleaned_data)
        if "\n" in data:
            self.expander.markdown(''.join(self.buffer), unsafe_allow_html=True)
            self.buffer = []

# Configure logging using StreamToExpander


# Streamlit app
def main():
    st.title("Marketing Crew for 'A Minute with Mary Cranston'")
    st.subheader("Generate Marketing Copy and Images")

    # Input OpenAI API key
    openai_api_key = st.text_input("Enter your OpenAI API key:", type="password")

    # Input fields
    product_website = st.text_input("Product Website", "https://aminutewithmary.com")
    product_details = st.text_area("Product Details")

    if st.button("Run Marketing Crew"):
        # Check if OpenAI API key is provided
        if not openai_api_key:
            st.error("Please enter your OpenAI API key.")
            return

        # Create OpenAI client with user-provided API key
        crewai_client = OpenAI(api_key=openai_api_key)

        # Create Agents
        product_competitor_agent = agents.product_competitor_agent()
        strategy_planner_agent = agents.strategy_planner_agent()
        creative_agent = agents.creative_content_creator_agent()

        # Create Tasks
        website_analysis = tasks.product_analysis(product_competitor_agent, product_website, product_details)
        market_analysis = tasks.competitor_analysis(product_competitor_agent, product_details)
        campaign_development = tasks.campaign_development(strategy_planner_agent, product_details)
        write_copy = tasks.instagram_ad_copy(creative_agent)

        # Create Crew responsible for Copy
        copy_crew = Crew(
            agents=[
                product_competitor_agent,
                strategy_planner_agent,
                creative_agent
            ],
            tasks=[
                website_analysis,
                market_analysis,
                campaign_development,
                write_copy
            ],
            verbose=True
        )
        
        log_expander = st.expander("Execution Logs", expanded=False)
        sys.stdout = StreamToExpander(log_expander)
        
        ad_copy = copy_crew.kickoff()
        st.subheader("Social Media Copy")
        st.write(ad_copy)

        # Log result
        st.write("Social Media Copy Generated.")

        # Create Crew responsible for Image
        senior_photographer = agents.senior_photographer_agent()

        image_crew = Crew(
            agents=[
                senior_photographer,
            ],
            tasks=[
                tasks.take_photograph_task(senior_photographer, ad_copy, product_details),
            ],
            verbose=True
        )

        image = image_crew.kickoff()

        # Display image generation result
        st.subheader("Graphics output from Design-Team")
        generated_image_url = generate_image(image, crewai_client)
        st.image(generated_image_url, caption="Generated Image")

        # Log result
        st.write("Image Generated.")

        # Prompt user for access tokens after everything is generated
        st.subheader("Post Results on Social Media")
        facebook_access_token = st.text_input("Enter your Facebook Page Access Token:")
        instagram_access_token = st.text_input("Enter your Instagram Access Token:")
        twitter_bearer_token = st.text_input("Enter your Twitter Bearer Token:")

        if st.button("Post on Social Media"):
            if facebook_access_token:
                st.write("Shared on Facebook.")
                post_on_facebook(crewai_client.images.generate_image(image), ad_copy, facebook_access_token)
            if instagram_access_token:
                st.write("Shared on Instagram.")
                post_on_instagram(crewai_client.images.generate_image(image), ad_copy, instagram_access_token)
            if twitter_bearer_token:
                st.write("Shared on Twitter.")
                post_on_twitter(crewai_client.images.generate_image(image), ad_copy, twitter_bearer_token)

if __name__ == "__main__":
    main()
