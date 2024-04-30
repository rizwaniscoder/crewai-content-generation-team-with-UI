import streamlit as st
from dotenv import load_dotenv
from crewai import Crew
from openai import OpenAI
import os
import requests
import re
import sys
from tasks import MarketingAnalysisTasks
from agents import MarketingAnalysisAgents

# Load environment variables
load_dotenv()

tasks = MarketingAnalysisTasks()
agents = MarketingAnalysisAgents()


def post_on_facebook(image_url, caption, page_access_token, page_id):
    post_url = f"https://graph.facebook.com/{page_id}/photos"
    image_response = requests.post(post_url, data={'url': image_url}, params={'access_token': page_access_token})
    image_data = image_response.json()

    if 'id' in image_data:
        caption_response = requests.post(f"https://graph.facebook.com/{page_id}/feed",
                                         data={'message': caption, 'published': 'true',
                                               'attached_media[0]': f"{'{'}'media_fbid': {image_data['id']}{'}'}"},
                                         params={'access_token': page_access_token})
        caption_data = caption_response.json()

        if 'id' in caption_data:
            return True
        else:
            return False
    else:
        return False


def post_on_instagram(image_url, caption, instagram_access_token):
    # Actual Instagram posting mechanism is more complex and requires additional steps
    st.warning("Instagram posting not implemented in this example.")
    return False


def post_on_twitter(image_url, caption, bearer_token):
    tweet_url = "https://api.twitter.com/2/tweets"
    tweet_data = {
        'text': caption,
        'media': {'media_url': image_url}
    }
    headers = {"Authorization": f"Bearer {bearer_token}", "Content-Type": "application/json"}
    response = requests.post(tweet_url, json=tweet_data, headers=headers)

    if response.status_code == 200:
        return True
    else:
        return False


class StreamToExpander:
    def __init__(self, expander):
        self.expander = expander
        self.buffer = []
        self.colors = ['red', 'green', 'blue', 'orange']
        self.color_index = 0

    def write(self, data):
        cleaned_data = re.sub(r'\x1B\[[0-9;]*[mK]', '', data)

        task_match_object = re.search(r'\"task\"\s*:\s*\"(.*?)\"', cleaned_data, re.IGNORECASE)
        task_match_input = re.search(r'task\s*:\s*([^\n]*)', cleaned_data, re.IGNORECASE)
        task_value = None
        if task_match_object:
            task_value = task_match_object.group(1)
        elif task_match_input:
            task_value = task_match_input.group(1).strip()

        if task_value:
            st.toast(":robot_face: " + task_value)

        if "Entering new CrewAgentExecutor chain" in cleaned_data:
            self.color_index = (self.color_index + 1) % len(self.colors)

            cleaned_data = cleaned_data.replace("Entering new CrewAgentExecutor chain",
                                                f":{self.colors[self.color_index]}[Entering new CrewAgentExecutor chain]")

        if "Market Research Analyst" in cleaned_data:
            cleaned_data = cleaned_data.replace("Market Research Analyst",
                                                f":{self.colors[self.color_index]}[Market Research Analyst]")
        if "Business Development Consultant" in cleaned_data:
            cleaned_data = cleaned_data.replace("Business Development Consultant",
                                                f":{self.colors[self.color_index]}[Business Development Consultant]")
        if "Technology Expert" in cleaned_data:
            cleaned_data = cleaned_data.replace("Technology Expert",
                                                f":{self.colors[self.color_index]}[Technology Expert]")
        if "Finished chain." in cleaned_data:
            cleaned_data = cleaned_data.replace("Finished chain.", f":{self.colors[self.color_index]}[Finished chain.]")

        self.buffer.append(cleaned_data)
        if "\n" in data:
            self.expander.markdown(''.join(self.buffer), unsafe_allow_html=True)
            self.buffer = []
def generate_image(prompt, crewai_client):
    response = crewai_client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    return response.data[0].url


def main():
    st.title("Authentication Required")

    # Prompt user for password
    entered_password = st.text_input("Enter the password:", type="password")

    # Retrieve password from environment variable
    correct_password = os.getenv('STREAMLIT_APP_PASSWORD')

    if entered_password == correct_password:
        st.success("Authentication successful! You can now access the app.")

        st.subheader("Marketing Crew for 'A Minute with Mary Cranston'")
        st.subheader("Generate Marketing Copy and Images")

        # Retrieve OpenAI API key from environment variables
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not openai_api_key:
            st.error("Please set your OpenAI API key in the environment variables.")
            return

        # Input fields
        product_website = st.text_input("Product Website", "https://aminutewithmary.com")
        product_details = st.text_area("Product Details")

        if st.button("Run Marketing Crew"):
            crewai_client = OpenAI(api_key=openai_api_key)

            product_competitor_agent = agents.product_competitor_agent()
            strategy_planner_agent = agents.strategy_planner_agent()
            creative_agent = agents.creative_content_creator_agent()

            website_analysis = tasks.product_analysis(product_competitor_agent, product_website, product_details)
            market_analysis = tasks.competitor_analysis(product_competitor_agent, product_details)
            campaign_development = tasks.campaign_development(strategy_planner_agent, product_details)
            write_copy = tasks.instagram_ad_copy(creative_agent)

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

            st.write("Social Media Copy Generated.")

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

            st.subheader("Graphics output from Design-Team")
            generated_image_url = generate_image(image, crewai_client)
            st.image(generated_image_url, caption="Generated Image")

            st.write("Image Generated.")

            st.subheader("Post Results on Social Media")
            facebook_access_token = st.text_input("Enter your Facebook Page Access Token:")
            instagram_access_token = st.text_input("Enter your Instagram Access Token:")
            twitter_bearer_token = st.text_input("Enter your Twitter Bearer Token:")

            if st.button("Post on Social Media"):
                if facebook_access_token:
                    st.write("Shared on Facebook.")
                    post_on_facebook(generated_image_url, ad_copy, facebook_access_token, 'PAGE_ID')
                if instagram_access_token:
                    st.write("Shared on Instagram.")
                    post_on_instagram(generated_image_url, ad_copy, instagram_access_token)
                if twitter_bearer_token:
                    st.write("Shared on Twitter.")
                    post_on_twitter(generated_image_url, ad_copy, twitter_bearer_token)

    else:
        if entered_password:
            st.error("Incorrect password. Please try again.")


if __name__ == "__main__":
    main()
