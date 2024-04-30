from crewai import Task
from textwrap import dedent

class MarketingAnalysisTasks:
    def product_analysis(self, agent, product_website, product_details):
        expected_output = "A comprehensive analysis report identifying the product's key features, benefits, market appeal, and suggestions for enhancement or positioning."
        return Task(description=dedent(f"""\
            Analyze the provided product: {product_website}.
            Additional details provided by the customer: {product_details}.

            Focus on identifying unique features, benefits,
            and the overall narrative presented.

            Your final report should clearly articulate the
            product's key selling points, its market appeal,
            and suggestions for enhancement or positioning.
            Emphasize the aspects that make the product stand out.

            Attention to detail is crucial for a comprehensive analysis. It's currently 2024.
            """),
            agent=agent,
            expected_output=expected_output
        )

    def competitor_analysis(self, agent, product_details):
        expected_output = "A detailed comparison report between the provided product and its top 3 competitors, including analysis of strategies, market positioning, and customer perception."
        return Task(description=dedent(f"""\
            Explore competitors.
            Additional details provided by the customer: {product_details}.

            Identify the top 3 competitors and analyze their
            strategies, market positioning, and customer perception.

            Your final report MUST include a detailed comparison to its competitors.
            """),
            agent=agent,
            expected_output=expected_output
        )

    def campaign_development(self, agent, product_details):
        expected_output = "A detailed marketing campaign strategy with creative content ideas tailored to the product's target audience."
        return Task(description=dedent(f"""\
            Develop a targeted marketing campaign
            Additional details provided by the customer: {product_details}.

            Design a strategy and creative content ideas meticulously to captivate and engage
            the product's target audience.

            Your final answer MUST resonate with the audience and include ALL context about the product and the customer.
            """),
            agent=agent,
            expected_output=expected_output
        )

    def instagram_ad_copy(self, agent):
        expected_output = "Three engaging options for Instagram ad copy that inform, excite, and persuade the audience to take action. Also add this link ""https://aminutewithmary.com"" in the ad copy."
        return Task(description=dedent("""\
            Craft engaging Instagram post copy.
            The copy should be punchy, captivating, concise,
            and aligned with the product marketing strategy.

            Focus on creating a message that resonates with
            the target audience and highlights the product's
            unique selling points.

            Your ad copy must be attention-grabbing and should
            encourage viewers to take action, whether it's
            visiting the website, making a purchase, or learning
            more about the product.

            Your final answer MUST include 3 options for ad copy for Instagram.
             Also add the link "https://aminutewithmary.com" in the ad copy                          
            """),
            agent=agent,
            expected_output=expected_output
        )

    def take_photograph_task(self, agent, copy, product_details):
        expected_output = "Three options of photographs, each with a descriptive paragraph, capturing the audience's attention without showing the actual product."
        return Task(description=dedent(f"""\
            Take captivating photos for an Instagram post.
            You have the following copy: {copy}

            Additional details provided by the customer: {product_details}.

            Imagine and describe three options of photographs, each with a descriptive paragraph,
            capturing the audience's attention creatively without showing the actual product.
            """),
            agent=agent,
            expected_output=expected_output
        )

    def review_photo(self, agent, product_details):
        expected_output = "Three reviewed options of photographs, each with a descriptive paragraph, aligned with the product's goals."
        return Task(description=dedent(f"""\
            Review and approve photos for the Instagram post.
            Ensure they align with the product's goals.

            Additional details provided by the customer: {product_details}.

            Review the options of photographs provided and make decisions accordingly,
            ensuring they are aligned with the product's goals.
            """),
            agent=agent,
            expected_output=expected_output
        )
