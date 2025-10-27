import time
import os
import re
from datetime import datetime
import pandas as pd
import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager



questions = [
    "What are the most popular tourist destinations in Meghalaya?",
    "How many days are ideal to explore Meghalaya properly?",
    "What is the best time of year to visit Meghalaya?",
    "Can you suggest a travel itinerary for a 5-day Meghalaya trip?",
    "What is Meghalaya famous for?",
    
]


# questions = [
#     "What are the most popular tourist destinations in Meghalaya?",
#     "How many days are ideal to explore Meghalaya properly?",
#     "What is the best time of year to visit Meghalaya?",
#     "Can you suggest a travel itinerary for a 5-day Meghalaya trip?",
#     "What is Meghalaya famous for?",
#     "How do I reach Meghalaya from Guwahati?",
#     "Do I need any travel permits to visit Meghalaya?",
#     "Is it safe to travel to Meghalaya at night?",
#     "How’s the weather in Meghalaya right now?",
#     "What are some offbeat places to visit in Meghalaya?"
#      "What are the top tourist places to visit in Meghalaya?",
#     "How can I reach Shillong from Guwahati?",
#     "What is the best time to visit Meghalaya?",
#     "Can you suggest some good homestays in Cherrapunji?",
#     "How far is Dawki from Shillong?",
#     "Is camping allowed near Dawki River?",
#     "What is the famous food of Meghalaya?",
#     "Are there any waterfalls near Shillong?",
#     "How can I book a hotel through the Meghalaya Tourism website?",
#     "What are the adventure activities available in Meghalaya?",
#     "Tell me something about Mawlynnong village.",
#     "Where is the Double Decker Root Bridge located?",
#     "Is there an entry fee for Nohkalikai Falls?",
#     "Can I rent a car for local sightseeing?",
#     "How to get a tourist guide in Meghalaya?",
#     "What are the timings of Ward’s Lake?",
#     "How safe is Meghalaya for solo travelers?",
#     "Are there any restrictions for visiting sacred groves?",
#     "What are the famous festivals of Meghalaya?",
#     "Can I find vegetarian restaurants in Shillong?",
#     "How can I reach the Living Root Bridge?",
#     "What is the distance between Shillong and Jowai?",
#     "How to explore the caves of Meghalaya?",
#     "Is online booking required for boating in Dawki?",
#     "Are pets allowed in Meghalaya hotels?",
#     "What are the local transport options available?",
#     "How is the mobile network connectivity in rural Meghalaya?",
#     "Can I visit Meghalaya during monsoon?",
#     "Are there any eco-resorts in the state?",
#     "How can I register my homestay on the Meghalaya Tourism portal?",
#     "Where can I get souvenirs in Shillong?",
#     "What languages are commonly spoken in Meghalaya?",
#     "Are there any wildlife sanctuaries in Meghalaya?",
#     "Can you share some photos of tourist destinations?",
#     "What are the famous waterfalls in Cherrapunji?",
#     "How can I plan a 3-day trip in Meghalaya?",
#     "Is there any government-approved tour package?",
#     "How can I contact Meghalaya Tourism support?",
#     "What are the COVID-19 travel guidelines in Meghalaya?",
#     "Does Meghalaya Tourism offer online permits for visitors?"
    
# ]


chrome_driver_path = ChromeDriverManager().install()
service = ChromeService(executable_path=chrome_driver_path)
options = webdriver.ChromeOptions()
options.add_argument("--log-level=3")
options.add_argument("--start-maximized")
options.add_argument("--disable-infobars")
options.add_argument("--disable-notifications")

driver = webdriver.Chrome(service=service, options=options)

now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
excel_path = os.path.join(os.getcwd(), f"Chatbot_Response_Report_{now}.xlsx")

df = pd.DataFrame({
    "Question": pd.Series(dtype="str"),
    "Bot Response": pd.Series(dtype="str"),
    "Response Time (s)": pd.Series(dtype="float"),
    "Links Found": pd.Series(dtype="str"),
    "Link Status": pd.Series(dtype="str")
})



st.set_page_config(page_title="Meghalaya Chatbot Dashboard", layout="wide")
st.title("🌄 Meghalaya Chatbot Report Dashboard")
st.write("Automated chatbot response testing for Meghalaya Tourism — powered by Selenium & Streamlit.")



#  Helper Function: Link Checker

def check_links_in_message(driver, bot_message):
    """
    Detects links in the bot message, opens them one by one,
    checks if they load successfully, and returns status.
    """
    url_pattern = r"(https?://[^\s]+)"
    links = re.findall(url_pattern, bot_message)
    link_status = "No Links"

    if not links:
        return None, link_status

    working_links = []
    broken_links = []

    for link in links:
        try:
            # Open link in new tab
            driver.execute_script(f"window.open('{link}', '_blank');")
            driver.switch_to.window(driver.window_handles[-1])

            # Wait for page to load or show visible content
            WebDriverWait(driver, 15).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )

            current_url = driver.current_url
            if current_url.startswith("http"):
                working_links.append(link)
            else:
                broken_links.append(link)

            # Close tab and switch back
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            time.sleep(1)

        except Exception:
            broken_links.append(link)
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

    if broken_links:
        link_status = f"Broken ({len(broken_links)} of {len(links)})"
    else:
        link_status = "All Working ✅"

    return ", ".join(links), link_status



# Main Automation Logic

try:
    driver.get("https://aware-emily-referring-evolution.trycloudflare.com")

    WebDriverWait(driver, 25).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="messageInput"]'))
    )

    for idx, question in enumerate(questions, start=1):
        st.info(f" Sending Question {idx}: {question}")
        time.sleep(1)

        try:
            bot_message_xpath = "//*[@class='message bot']"
            previous_count = len(driver.find_elements(By.XPATH, bot_message_xpath))

            input_field = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="messageInput"]'))
            )
            input_field.clear()
            input_field.send_keys(question)

            send_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="sendButton"]'))
            )
            start_time = time.monotonic()
            send_button.click()

            # Wait for new bot message
            WebDriverWait(driver, 40).until(
                lambda d: len(d.find_elements(By.XPATH, bot_message_xpath)) > previous_count
            )

            # Fetch last bot message
            last_bot_xpath = "(//*[@class='message bot'])[last()]"
            last_bot = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, last_bot_xpath))
            )
            WebDriverWait(driver, 15).until(lambda d: last_bot.text.strip() != "")

            bot_message = last_bot.text.strip()
            end_time = time.monotonic()
            response_time = round(end_time - start_time, 2)

            # Check for links inside bot message
            links_found, link_status = check_links_in_message(driver, bot_message)

            # Append data
            df = pd.concat([
                df,
                pd.DataFrame([{
                    "Question": question,
                    "Bot Response": bot_message,
                    "Response Time (s)": response_time,
                    "Links Found": links_found if links_found else "None",
                    "Link Status": link_status
                }])
            ], ignore_index=True)

        except Exception as e:
            st.error(f" Failed to get response for question {idx}: {e}")
            df = pd.concat([
                df,
                pd.DataFrame([{
                    "Question": question,
                    "Bot Response": "ERROR",
                    "Response Time (s)": None,
                    "Links Found": "None",
                    "Link Status": "ERROR"
                }])
            ], ignore_index=True)
            time.sleep(2)

    df.to_excel(excel_path, index=False)
    st.success(f"Excel report saved successfully at: {excel_path}")

except Exception as e:
    st.error(f" Fatal Error: {e}")
    df.to_excel(excel_path, index=False)

finally:
    driver.quit()



#Dashboard Visualization

if not df.empty:
    st.markdown("---")
    st.subheader("📊 Chatbot Responses Overview")

    response_times = df["Response Time (s)"].dropna()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Questions", len(df))
    col2.metric("Average Response Time (s)", f"{response_times.mean():.2f}" if not response_times.empty else "N/A")
    col3.metric("Max Response Time (s)", f"{response_times.max():.2f}" if not response_times.empty else "N/A")
    col4.metric("Links Found", df["Links Found"].apply(lambda x: x != "None").sum())

    st.markdown("### 🧾 Detailed Response Table")
    st.dataframe(df, use_container_width=True)

    if not response_times.empty:
        st.markdown("### ⏱️ Response Time Chart")
        st.bar_chart(df.set_index("Question")["Response Time (s)"])

    with open(excel_path, "rb") as file:
        st.download_button(
            label="⬇️ Download Excel Report",
            data=file,
            file_name=os.path.basename(excel_path),
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

else:
    st.warning("No chatbot data available yet.")
