"""
API calls module for fetching data from ZAgent APIs
"""
import requests
from logger_config import get_logger

logger = get_logger('api_calls')

# API configurations
ACCOUNT_IDS = ["86c3cb12-d1d1-5a0e-ab58-3230ec9fe11f", "8e9a3514-c5e8-52e7-842d-cb4e2a0a0cdb"]
API_KEY = "891f41ee454479c49e458c4a7c50dd1e"
BASE_URL = "https://config-store.zagent.stage.yavar.ai/api/v1/configs"


def fetch_chatbots():
    """Fetch chatbots from API"""
    logger.info(f"Fetching chatbots for {len(ACCOUNT_IDS)} accounts")
    chatbots = []
    headers = {'Content-Type': 'application/json', 'x-api-key': API_KEY}

    for acc_id in ACCOUNT_IDS:
        logger.debug(f"Fetching chatbots for account: {acc_id}")
        url = f'{BASE_URL}/chatbots/query/account_id/{acc_id}'

        try:
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    chatbot_count = len(data['data'])
                    chatbots.extend(data['data'])
                    logger.info(f"Retrieved {chatbot_count} chatbots for account {acc_id}")
                else:
                    logger.warning(f"No 'data' field in response for account {acc_id}")
            else:
                logger.error(f"Failed to fetch chatbots for account {acc_id}. Status: {response.status_code}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching chatbots for account {acc_id}: {str(e)}")

    logger.info(f"Total chatbots fetched: {len(chatbots)}")
    return chatbots


def fetch_settings():
    """Fetch settings from API"""
    logger.info("Fetching settings from API")
    url = f'{BASE_URL}/settings'
    headers = {'Content-Type': 'application/json', 'x-api-key': API_KEY}

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                logger.info(f"Retrieved {len(data)} settings")
                return data
            elif isinstance(data, dict) and 'data' in data:
                logger.info(f"Retrieved {len(data['data'])} settings from data field")
                return data['data']
            else:
                logger.info("Retrieved single setting object")
                return [data]
        else:
            logger.error(f"Failed to fetch settings. Status: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching settings: {str(e)}")
        return []


def fetch_languages():
    """Fetch languages from API"""
    logger.info("Fetching languages from API")
    url = f'{BASE_URL}/languages'
    headers = {'Content-Type': 'application/json', 'x-api-key': API_KEY}

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                logger.info(f"Retrieved {len(data)} languages")
                return data
            elif isinstance(data, dict) and 'data' in data:
                logger.info(f"Retrieved {len(data['data'])} languages from data field")
                return data['data']
            else:
                logger.info("Retrieved single language object")
                return [data]
        else:
            logger.error(f"Failed to fetch languages. Status: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching languages: {str(e)}")
        return []