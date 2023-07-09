from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

with open('Credentials.json','r') as credentials:
    credentials_info = json.load(credentials)
    API_KEY = credentials_info['API_KEY']
    ADDRESS = credentials_info['email']
    PASSWORD = credentials_info['password']
    
def connect_to_endpoint():
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'

    parameters = {
      'start':'1',
      'limit':'10',
      'convert':'USD'
    }
    headers = {
      'Accepts': 'application/json',
      'X-CMC_PRO_API_KEY': API_KEY,
    }
    
    session = Session()
    session.headers.update(headers)
    
    try:
      response = session.get(url, params=parameters)
      data = json.loads(response.text)
      return data
    except (ConnectionError, Timeout, TooManyRedirects) as e:
      print(e)
      
    
def write_csv_file(data):
    df = pd.json_normalize(data['data'])
    df['Date'] = pd.Timestamp('now').date()
    df = df.drop(['tags','platform','self_reported_circulating_supply','self_reported_market_cap','tvl_ratio','quote.USD.tvl','platform.id','platform.slug','platform.token_address','quote.USD.fully_diluted_market_cap','platform.name','platform.symbol'],axis=1)
    df = df.rename(columns={'num_market_pairs':'Market Pairs','date_added':'Date Added','max_supply':'Max Supply','total_supply':'Total Supply','infinite_supply':'Infinity Supply','cmc_rank':'CMC Rank','last_updated':'Last Updated','quote.USD.price':'Price USD','quote.USD.volume_24h':'Volume 24H(USD)','quote.USD.volume_change_24h':'Volumn change 24H(USD)','quote.USD.percent_change_1h':'Price change % 1H','quote.USD.percent_change_24h':'Price change % 24H','quote.USD.percent_change_7d':'Price change % 7D','quote.USD.percent_change_30d':'Price change % 30D','quote.USD.percent_change_60d':'Price change % 60D','quote.USD.percent_change_90d':'Price change % 90D','quote.USD.market_cap':'Market capitalization USD','quote.USD.market_cap_dominance':'Market capitalization dominance %','quote.USD.last_updated':'Last market updated'})
    df.to_csv('CriptoData.csv',header='column_names')
    send_data_email()

def send_data_email():
    sender_email = ADDRESS
    receiver_email = ADDRESS
    subject = 'Cripto Data Analysis CSV'
    body = 'CSV attachment of the Criptocurrencies Data information.'
    
    attachment_path = 'CriptoData.csv'
    
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = subject
    

    message.attach(MIMEText(body, 'plain'))
    
    with open(attachment_path, 'rb') as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
    
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename= {attachment_path}')
    
    message.attach(part)
    
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(ADDRESS, PASSWORD)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print("Error sending email:", str(e))

    
def main():
    json_response = connect_to_endpoint()
    write_csv_file(json_response)

if __name__ == "__main__":
    main()
