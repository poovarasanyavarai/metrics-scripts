#!/usr/bin/env python3
"""
Main entry point for the chatbot metrics generator
"""
from datetime import datetime
import json
import logging
from api_calls import fetch_chatbots, fetch_settings, fetch_languages
from db_calls import fetch_all_data_optimized, get_db_connection, insert_metrics_direct
from static_data import (
    STATIC_FB_GEO,
    STATIC_FB_CHANNEL,
    STATIC_PERFORM_BY_GEO,
    STATIC_ALERTS,
    STATIC_TRENDS,
    STATIC_NET_IMPACT,
    STATIC_NET_IMPACT_GRAPH
)
from logger_config import setup_logger, get_logger

# Setup logging
logger = setup_logger('chatbot_metrics', logging.INFO)


def generate_json_data():
    """Main function to generate and save data to JSON file in INSERT format"""
    logger.info("="*50)
    logger.info("Starting Chatbot Metrics Generation")
    logger.info("="*50)

    # Get current timestamp
    snapshot_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # Include milliseconds
    logger.info(f"Snapshot time: {snapshot_time}")

    # Fetch all data
    logger.info("Step 1/4: Fetching data from APIs")
    chatbots = fetch_chatbots()
    settings = fetch_settings()
    languages = fetch_languages()

    if not chatbots:
        logger.error("No chatbots fetched. Exiting.")
        return

    # Create settings mapping
    settings_map = {s['id']: s for s in settings if 'id' in s}
    logger.info(f"Created settings map for {len(settings_map)} settings")

    # Create language ID to name mapping
    language_map = {}
    for lang in languages:
        if 'id' in lang and 'name' in lang:
            language_map[str(lang['id'])] = lang['name']
    logger.info(f"Created language map with {len(language_map)} languages")

    # Extract chatbot IDs
    chatbot_ids = [c.get('id', '') for c in chatbots if c.get('id')]
    chatbot_ids = [c_id for c_id in chatbot_ids if c_id]  # Remove empty IDs
    logger.info(f"Extracted {len(chatbot_ids)} valid chatbot IDs")

    # Connect to database and fetch data
    logger.info("Step 2/4: Connecting to database")
    try:
        conn = get_db_connection()

        # Fetch ALL data with optimized queries
        logger.info("Step 3/4: Fetching conversation, feedback, and leads data")
        today_conversations, yesterday_conversations, feedback_by_chatbot, today_leads, yesterday_leads = fetch_all_data_optimized(
            chatbot_ids, conn, language_map
        )
        conn.close()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Database operation failed: {str(e)}")
        return

    logger.info("Step 4/5: Generating data records")

    data_records = []

    for chatbot in chatbots:
        chatbot_id = chatbot.get('id', '')
        chatbot_name = chatbot.get('name', 'Unknown')
        bot_created_at = chatbot.get('created_at', snapshot_time)

        # Get profile URL from settings
        profile_url = ''
        settings_id = chatbot.get('settings_id')
        if settings_id and settings_id in settings_map:
            profile_url = settings_map[settings_id].get('profile_image_url', '')

        # Get conversation data
        today_data = today_conversations.get(chatbot_id, {
            'today_conversations': [],
            'languages': {},
            'platforms': {}
        })
        yesterday_data = yesterday_conversations.get(chatbot_id, {'yesterday_count': 0})

        today_count = len(today_data['today_conversations'])
        yesterday_count = yesterday_data['yesterday_count']
        conversation_diff = today_count - yesterday_count

        # Get leads data
        today_leads_count = today_leads.get(chatbot_id, 0)
        yesterday_leads_count = yesterday_leads.get(chatbot_id, 0)
        leads_diff = today_leads_count - yesterday_leads_count

        # Get feedback data
        feedback_data = feedback_by_chatbot.get(chatbot_id, {
            'feedback_total': 0, 'feedback_pos': 0, 'feedback_neg': 0, 'feedback_avg': 0, 'fb_channel': []
        })

        # Calculate AI CSAT
        feedback_total = feedback_data['feedback_total']
        feedback_pos = feedback_data['feedback_pos']
        ai_csat = round((feedback_pos / feedback_total) * 100, 2) if feedback_total > 0 else 0

        # Build data record matching INSERT structure
        record = {
            # Primary fields
            "snapshot_time": snapshot_time,
            "chatbot_id": chatbot_id,
            "profile_url": profile_url,

            # Status fields
            "active_status": True,
            "total_coversation": today_count,
            "coversation_diff": conversation_diff,
            "ai_resolved": today_count,
            "ai_resolved_diff": conversation_diff,
            "human_resolved": 0,
            "human_resolved_diff": 0,
            "leads": today_leads_count,
            "leads_diff": leads_diff,

            # CSAT fields
            "ai_csat": ai_csat,
            "human_csat": 0,

            # Platform as JSON string (e.g., {"WEB": 3})
            "platform": today_data['platforms'] if today_data['platforms'] else {"WEB": 0},

            # Queue fields
            "ongoing_calls": 0,
            "in_queue": 0,
            "unresolved": 0,

            # Feedback fields
            "feedback_total": feedback_total,
            "feedback_pos": feedback_pos,
            "feedback_neg": feedback_data['feedback_neg'],
            "feedback_avg": feedback_data['feedback_avg'],

            # Languages as JSON string (e.g., {"English": 3})
            "languages": today_data['languages'] if today_data['languages'] else {"English": 0},

            # Static JSON fields
            "alerts": STATIC_ALERTS,
            "fb_geo": STATIC_FB_GEO,
            "fb_channel": feedback_data.get('fb_channel', []),
            "trends": STATIC_TRENDS,
            "net_impact": STATIC_NET_IMPACT.get('efficiency_gain', 0),  # Use efficiency_gain from static data
            "net_impact_graph": STATIC_NET_IMPACT_GRAPH,

            # Name and timestamps
            "name": chatbot_name,
            "created_at": snapshot_time,
            "bot_created_at": bot_created_at,
            "chatbot_name": chatbot_name,

            # Perform by geo
            "perform_by_geo": STATIC_PERFORM_BY_GEO
        }

        data_records.append(record)

    # Create complete data structure for direct insertion
    json_data = {
        "chatbot_metrics": data_records,
        "metadata": {
            "total_chatbots": len(chatbots),
            "snapshot_time": snapshot_time,
            "total_today_conversations": sum(r['total_coversation'] for r in data_records),
            "total_yesterday_conversations": sum(yesterday_conversations.get(c.get('id'), {}).get('yesterday_count', 0) for c in chatbots),
            "total_feedback_records": sum(r['feedback_total'] for r in data_records),
            "total_today_leads": sum(r['leads'] for r in data_records),
            "total_yesterday_leads": sum(yesterday_leads.get(c.get('id'), 0) for c in chatbots),
            "database_queries_used": 5,  # Optimized to use 5 queries with IN operator (3 for convs/feedback + 2 for leads)
            "note": "Data formatted for direct INSERT INTO chatbot_metrics"
        }
    }

    # Insert data directly into database (no JSON file)
    logger.info("Step 5/5: Inserting metrics data directly into database")
    import time
    start_step = time.time()
    try:
        if insert_metrics_direct(json_data):
            end_step = time.time()
            logger.info(f"✅ Metrics data successfully inserted into database in {end_step - start_step:.2f} seconds")
        else:
            end_step = time.time()
            logger.error(f"❌ Failed to insert metrics data into database after {end_step - start_step:.2f} seconds")
    except Exception as e:
        end_step = time.time()
        logger.error(f"Error during database insertion after {end_step - start_step:.2f} seconds: {str(e)}")
        return

    # Summary logging
    logger.info("\n" + "="*50)
    logger.info("EXECUTION SUMMARY")
    logger.info("="*50)
    logger.info(f"✓ Total chatbots processed: {len(chatbots)}")
    logger.info(f"✓ Snapshot time: {snapshot_time}")
    logger.info(f"✓ Database queries used: 5 (optimized with IN operator)")
    logger.info(f"✓ Total today conversations: {json_data['metadata']['total_today_conversations']}")
    logger.info(f"✓ Total yesterday conversations: {json_data['metadata']['total_yesterday_conversations']}")
    logger.info(f"✓ Total feedback records: {json_data['metadata']['total_feedback_records']}")
    logger.info(f"✓ Total today leads: {json_data['metadata']['total_today_leads']}")
    logger.info(f"✓ Total yesterday leads: {json_data['metadata']['total_yesterday_leads']}")
    logger.info(f"✓ Direct insertion (no intermediate file)")
    logger.info("="*50)

  

if __name__ == "__main__":
    try:
        generate_json_data()
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)