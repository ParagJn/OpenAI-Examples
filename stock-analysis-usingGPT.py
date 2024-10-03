"""
Stock Analysis Application

This application utilizes Streamlit for a web interface, yfinance for fetching historical stock data, and OpenAI's GPT-4 model for generating analyses based on the stock data. 
Users can input stock ticker symbols, set model parameters, and receive detailed analyses of stock trends, investment recommendations, and key statistics.

Modules:
- streamlit: For creating the web interface.
- pandas: For handling and manipulating the stock data.
- yfinance: For downloading historical stock data.
- openai_client: For interacting with OpenAI's GPT-4 model.
- tiktoken: For token counting related to the OpenAI API.

Functions:
- get_token_count(text): 
    Returns the number of tokens in the provided text using the GPT-4 encoding scheme.

- estimate_cost(token_count): 
    Estimates the cost of using the GPT-4 model based on the number of tokens processed, assuming a rate of $0.06 per 1000 tokens.

- generate_analysis(messages, temperature, max_tokens, agent_type="Stock Analyst"): 
    Generates an analysis of stock data by sending a prompt to the GPT-4 model. Returns the model's response or displays an error if the request fails.

- main(): 
    The main function that sets up the Streamlit application. It defines the user interface components, gathers user inputs, and manages the stock analysis workflow.

parag.jn@gmail.com
"""

import streamlit as st
import pandas as pd
import yfinance as yf
from openai_client import OpenAIClient
import tiktoken

# Set page config for wide mode
st.set_page_config(layout="wide")

# Initialize OpenAI Client
openai_client_obj = OpenAIClient()
client = openai_client_obj.get_client()

def get_token_count(text):
    encoding = tiktoken.encoding_for_model("gpt-4")
    return len(encoding.encode(text))

def estimate_cost(token_count):
    # Assuming $0.06 per 1K tokens for GPT-4
    return (token_count / 1000) * 0.06

def generate_analysis(messages, temperature, max_tokens, agent_type="Stock Analyst"):
    try:
        prepended_message = {
            "Expert Analyst": "You are an expert data analyst.",
        }.get(agent_type, "You are an expert stock market data analyst")

        messages.insert(0, {"role": "system", "content": prepended_message})

        response = client.chat.completions.create(
            model='gpt-4',
            messages=messages,
            max_tokens=max_tokens,
            n=1,
            stop=None,
            temperature=temperature,
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
    return None

def main():
    st.title("Stock Analysis App")

    # Sidebar for model parameters
    st.sidebar.header("Model Parameters")
    max_tokens = st.sidebar.slider("Max Tokens", 300, 3000, 1500)
    temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.7)

    # User inputs
    tickers = st.text_input("Enter ticker symbols (comma-separated)", "AAPL,MSFT,GOOGL").split(',')
    tickers = [ticker.strip().upper() for ticker in tickers]

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", pd.to_datetime("2022-01-01"))
    with col2:
        end_date = st.date_input("End Date", pd.to_datetime("2024-09-01"))

    if st.button("Analyze"):
        for ticker in tickers:
            st.subheader(f"Analysis for {ticker}")

            data_df = yf.download(ticker, start=start_date, end=end_date, interval="5d")

            if not data_df.empty:
                # data_df = data_df.drop(['Open', 'High', 'Low'], axis=1)
                data_df.index = pd.to_datetime(data_df.index).date

                # st.write("Stock Data:")
                # st.dataframe(data_df)

                prompt = f'''I have a dataset of historical stock prices for {ticker}.
The data is:
{data_df.to_string()}
The data is aggregated over a 5-day interval (weekly data) between {start_date} and {end_date}.
Analyze this data and provide the following information:
1. **Best months to invest**: List 2-3 specific month names that are historically best for investing, based on lowest average closing prices. Include the average closing price for each month.
2. **Best months to sell**: List 2-3 specific month names that are historically best for selling, based on highest average closing prices. Include the average closing price for each month.
3. **Stock trend**: In 1-2 sentences, describe the overall trend (bullish, bearish, or sideways) based on the price movement from {start_date} to {end_date}. Include the percentage change in closing price over this period.
4. **Key statistics**: Provide the following key stats:
   - Highest closing price (with date)
   - Lowest closing price (with date)
   - Average trading volume
Limit your response strictly to these points and keep it concise.
'''
                messages = [{"role": "user", "content": prompt}]
                with st.spinner("Working to build your analysis ..."):
                    model_response = generate_analysis(messages, temperature, max_tokens)

                if model_response:
                    model_response = model_response.replace('$','INR')
                    st.markdown("**Analysis Results:**")
                    
                    # Split the response into sections
                    sections = model_response.split('\n\n')
                    
                    for section in sections:
                        if ':' in section:
                            title, content = section.split(':', 1)
                            st.markdown(f"**{title.strip()}**")
                            st.write(content.strip())
                        else:
                            st.write(section)
                    # Calculate and display token count and estimated cost
                    token_count = get_token_count(model_response)
                    estimated_cost = estimate_cost(token_count)
                    st.markdown(f"<small>Token count: {token_count} | Estimated cost: ${estimated_cost:.4f}</small>", unsafe_allow_html=True)
                else:
                    st.warning(f"No data available for {ticker} in the specified date range.")

            st.markdown("---")

if __name__ == "__main__":
    main()
