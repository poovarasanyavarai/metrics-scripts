"""
Database calls module for fetching conversation and feedback data from PostgreSQL
"""
import psycopg2
import logging
import json
import os
from collections import defaultdict
from logger_config import get_logger

logger = get_logger('db_calls')

# Database connection from environment variable or default
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://z_agent_user:z_agent_password@localhost:5554/z_agent')


def get_db_connection():
    """Get database connection"""
    logger.debug("Establishing database connection")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        logger.info("Database connection established successfully")
        return conn
    except psycopg2.Error as e:
        logger.error(f"Failed to connect to database: {str(e)}")
        raise


def fetch_all_data_optimized(chatbot_ids, conn, language_map=None):
    """Fetch all data with just 5 queries using IN operator"""
    logger.info(f"Fetching optimized data for {len(chatbot_ids)} chatbots")
    cursor = conn.cursor()

    # Convert chatbot_ids to string for IN clause
    chatbot_ids_str = "', '".join(chatbot_ids)
    logger.debug(f"Executing 5 optimized queries for {len(chatbot_ids)} chatbots")

    # Query 1: Get all today's conversations (full data needed for language/platform analysis)
    today_conversations_query = f"""
        SELECT *
        FROM public.conversations
        WHERE chatbot_id IN ('{chatbot_ids_str}')
          AND deleted_at IS NULL
          AND created_at >= CURRENT_DATE
          AND created_at < CURRENT_DATE + INTERVAL '1 day'
        ORDER BY chatbot_id, created_at DESC
    """

    # Query 2: Get yesterday's conversation count
    yesterday_count_query = f"""
        SELECT chatbot_id, COUNT(*) AS yesterday_count
        FROM public.conversations
        WHERE chatbot_id IN ('{chatbot_ids_str}')
          AND deleted_at IS NULL
          AND created_at >= CURRENT_DATE - INTERVAL '1 day'
          AND created_at < CURRENT_DATE
        GROUP BY chatbot_id
    """

    # Query 3: Get all feedback with conversation channel information
    feedback_query = f"""
        SELECT
            f.chatbot_id,
            f.conversation_id,
            f.rating,
            f.feedback_text,
            COALESCE(c.conversation_via, 'WEB') as channel
        FROM public.conversation_overall_feedback f
        LEFT JOIN public.conversations c ON f.conversation_id = c.id
        WHERE f.chatbot_id IN ('{chatbot_ids_str}')
          AND f.deleted_at IS NULL
          AND f.rating IS NOT NULL
          AND f.created_at >= CURRENT_DATE
          AND f.created_at < CURRENT_DATE + INTERVAL '1 day'
        ORDER BY f.chatbot_id, f.created_at DESC
    """

    # Query 4: Get today's leads from event_scheduler
    today_leads_query = f"""
        SELECT chatbot_id, COUNT(*) AS today_leads_count
        FROM public.event_scheduler
        WHERE chatbot_id IN ('{chatbot_ids_str}')
          AND start_time >= CURRENT_DATE
          AND start_time < CURRENT_DATE + INTERVAL '1 day'
        GROUP BY chatbot_id
        ORDER BY chatbot_id
    """

    # Query 5: Get yesterday's leads from event_scheduler
    yesterday_leads_query = f"""
        SELECT chatbot_id, COUNT(*) AS yesterday_leads_count
        FROM public.event_scheduler
        WHERE chatbot_id IN ('{chatbot_ids_str}')
          AND start_time >= CURRENT_DATE - INTERVAL '1 day'
          AND start_time < CURRENT_DATE
        GROUP BY chatbot_id
        ORDER BY chatbot_id
    """

    try:
        # Execute today's conversations query
        logger.debug("Executing today's conversations query")
        cursor.execute(today_conversations_query)
        today_results = cursor.fetchall()
        today_columns = [desc[0] for desc in cursor.description]
        logger.info(f"Retrieved {len(today_results)} today's conversations")

        # Execute yesterday's count query
        logger.debug("Executing yesterday's count query")
        cursor.execute(yesterday_count_query)
        yesterday_results = cursor.fetchall()
        logger.info(f"Retrieved yesterday counts for {len(yesterday_results)} chatbots")

        # Execute feedback query
        logger.debug("Executing feedback query")
        cursor.execute(feedback_query)
        feedback_results = cursor.fetchall()
        logger.info(f"Retrieved {len(feedback_results)} feedback records")

        
        # Execute leads queries with separate connection to avoid transaction issues
        today_leads_results = []
        yesterday_leads_results = []

        try:
            # Create separate connection for leads queries
            leads_conn = get_db_connection()
            leads_cursor = leads_conn.cursor()

            # Execute today's leads query
            logger.debug("Executing today's leads query")
            leads_cursor.execute(today_leads_query)
            today_leads_results = leads_cursor.fetchall()
            logger.info(f"Retrieved today leads for {len(today_leads_results)} chatbots")

            # Execute yesterday's leads query
            logger.debug("Executing yesterday's leads query")
            leads_cursor.execute(yesterday_leads_query)
            yesterday_leads_results = leads_cursor.fetchall()
            logger.info(f"Retrieved yesterday leads for {len(yesterday_leads_results)} chatbots")

            leads_cursor.close()
            leads_conn.close()

        except psycopg2.Error as e:
            if "does not exist" in str(e):
                logger.warning("event_scheduler table does not exist, using 0 for all leads")
                # Leave results empty - will default to 0
            else:
                logger.warning(f"Leads query error (using 0 for leads): {str(e)}")
                # Leave results empty - will default to 0

        cursor.close()
    except psycopg2.Error as e:
        logger.error(f"Database query error: {str(e)}")
        cursor.close()
        raise

    # Initialize dictionaries
    today_conversations = {}
    yesterday_conversations = {}
    feedback_by_chatbot = {}

    # Process yesterday counts first
    for row in yesterday_results:
        chatbot_id, count = row
        yesterday_conversations[chatbot_id] = {'yesterday_count': count}

    # Process today's conversations
    for row in today_results:
        row_dict = dict(zip(today_columns, row))
        chatbot_id = row_dict['chatbot_id']

        if chatbot_id not in today_conversations:
            today_conversations[chatbot_id] = {
                'today_conversations': [],
                'languages': defaultdict(int),
                'platforms': defaultdict(int)
            }
        today_conversations[chatbot_id]['today_conversations'].append(row_dict)

        # Process language and platform for today's conversations
        lang_id = None
        if 'language_id' in row_dict and row_dict['language_id']:
            lang_id = str(row_dict['language_id'])

        # Map language ID to name
        lang_name = 'English'  # Default
        if lang_id and language_map and lang_id in language_map:
            lang_name = language_map[lang_id]

        today_conversations[chatbot_id]['languages'][lang_name] += 1

        # Process platform (conversation_via)
        platform = row_dict.get('conversation_via', 'WEB')
        if platform:
            today_conversations[chatbot_id]['platforms'][platform.upper()] += 1
        else:
            today_conversations[chatbot_id]['platforms']['WEB'] += 1

    # Convert defaultdicts to regular dicts for today's data
    for chatbot_id in today_conversations:
        today_conversations[chatbot_id]['languages'] = dict(today_conversations[chatbot_id]['languages'])
        today_conversations[chatbot_id]['platforms'] = dict(today_conversations[chatbot_id]['platforms'])

    # Process feedback with channel counting
    for row in feedback_results:
        # Since we're using custom SELECT, feedback_columns won't match,
        # so we need to build the dict manually
        chatbot_id = row[0]
        conversation_id = row[1]
        rating = row[2]
        feedback_text = row[3]
        channel = row[4].upper() if row[4] else 'WEB'

        if chatbot_id not in feedback_by_chatbot:
            feedback_by_chatbot[chatbot_id] = {
                'feedback': [],
                'feedback_total': 0,
                'feedback_pos': 0,
                'feedback_neg': 0,
                'feedback_avg': 0,
                'feedback_channels': defaultdict(int)  # Track feedback by channel
            }

        # Create feedback row dict
        feedback_row = {
            'chatbot_id': chatbot_id,
            'conversation_id': conversation_id,
            'rating': rating,
            'feedback_text': feedback_text,
            'channel': channel
        }

        feedback_by_chatbot[chatbot_id]['feedback'].append(feedback_row)
        feedback_by_chatbot[chatbot_id]['feedback_total'] += 1

        # Count by channel
        feedback_by_chatbot[chatbot_id]['feedback_channels'][channel] += 1

        rating = rating.lower() if rating else ''
        if rating == 'love it':
            feedback_by_chatbot[chatbot_id]['feedback_pos'] += 1
        elif rating == 'bad':
            feedback_by_chatbot[chatbot_id]['feedback_neg'] += 1
        elif rating == 'decent':
            feedback_by_chatbot[chatbot_id]['feedback_avg'] += 1

    # Convert feedback channel counts to array of objects format for fb_channel
    for chatbot_id in feedback_by_chatbot:
        if 'feedback_channels' in feedback_by_chatbot[chatbot_id]:
            # Convert dict to array of objects format
            channel_counts = feedback_by_chatbot[chatbot_id]['feedback_channels']
            fb_channel_array = []
            for channel, count in channel_counts.items():
                fb_channel_array.append({
                    "channel": channel.lower(),  # Convert to lowercase as in example
                    "count": count
                })
            feedback_by_chatbot[chatbot_id]['fb_channel'] = fb_channel_array
            # Remove the old feedback_channels dict
            del feedback_by_chatbot[chatbot_id]['feedback_channels']
        else:
            feedback_by_chatbot[chatbot_id]['fb_channel'] = []

    # Process leads data
    today_leads = {}
    yesterday_leads = {}

    # Process today's leads
    for row in today_leads_results:
        chatbot_id, count = row
        today_leads[chatbot_id] = count

    # Process yesterday's leads
    for row in yesterday_leads_results:
        chatbot_id, count = row
        yesterday_leads[chatbot_id] = count

    return today_conversations, yesterday_conversations, feedback_by_chatbot, today_leads, yesterday_leads


def insert_metrics_direct(data):
    """Insert metrics data directly into chatbot_metrics table without JSON file"""
    if 'chatbot_metrics' not in data:
        logger.error("Invalid data structure: 'chatbot_metrics' key not found")
        return False

    logger.info(f"Fast batch inserting {len(data['chatbot_metrics'])} metrics records")
    conn = None
    cursor = None
    inserted_count = 0

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Prepare insert query without id (auto-generated) - match actual table column order
        insert_query = """
        INSERT INTO chatbot_metrics (
            snapshot_time, chatbot_id, profile_url, active_status,
            total_coversation, coversation_diff, ai_resolved, ai_resolved_diff,
            human_resolved, human_resolved_diff, leads, leads_diff,
            ai_csat, human_csat, platform, ongoing_calls, in_queue,
            unresolved, feedback_total, feedback_pos, feedback_neg,
            feedback_avg, languages, alerts, fb_geo, fb_channel,
            trends, net_impact, net_impact_graph, name, created_at,
            bot_created_at, perform_by_geo
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s
        );
        """

        import time
        start_total = time.time()
        logger.info(f"Fast batch inserting {len(data['chatbot_metrics'])} metrics records")

        # Process metrics records
        values_list = []
        for metric in data['chatbot_metrics']:
            # Only process essential dynamic data, use empty strings for static JSON to avoid processing
            values = (
                metric.get('snapshot_time'),                    # 1
                metric.get('chatbot_id'),                       # 2
                metric.get('profile_url'),                      # 3
                metric.get('active_status', True),              # 4
                metric.get('total_coversation', 0),             # 5
                metric.get('coversation_diff', 0),              # 6
                metric.get('ai_resolved', 0),                   # 7
                metric.get('ai_resolved_diff', 0),              # 8
                metric.get('human_resolved', 0),                # 9
                metric.get('human_resolved_diff', 0),           # 10
                metric.get('leads', 0),                         # 11
                metric.get('leads_diff', 0),                    # 12
                metric.get('ai_csat', 0),                       # 13
                metric.get('human_csat', 0),                    # 14
                json.dumps(metric.get('platform', {})),         # 15
                metric.get('ongoing_calls', 0),                 # 16
                metric.get('in_queue', 0),                      # 17
                metric.get('unresolved', 0),                    # 18
                metric.get('feedback_total', 0),                # 19
                metric.get('feedback_pos', 0),                  # 20
                metric.get('feedback_neg', 0),                  # 21
                metric.get('feedback_avg', 0),                  # 22
                json.dumps(metric.get('languages', {})),        # 23
                json.dumps(metric.get('alerts', [])),  # 24 alerts - use actual static data
                json.dumps(metric.get('fb_geo', [])),  # 25 fb_geo - use actual static data
                json.dumps(metric.get('fb_channel', [])),       # 26
                json.dumps(metric.get('trends', [])),# 27 trends
                float(metric.get('net_impact', 0.0)),           # 28
                json.dumps(metric.get('net_impact_graph', {})),
                metric.get('name', ''),                         # 30
                metric.get('created_at'),                       # 31
                metric.get('bot_created_at', metric.get('snapshot_time')),  # 32
                json.dumps(metric.get('perform_by_geo', {}))

            )
            
            values_list.append(values)

        # Use executemany for batch insertion
        try:
            start_time = time.time()
            cursor.executemany(insert_query, values_list)
            logger.info(f"executemany completed, committing...")
            conn.commit()
            end_time = time.time()
            inserted_count = len(values_list)
            logger.info(f"Successfully batch inserted {inserted_count} metrics records in {end_time - start_time:.2f} seconds")
        except Exception as e:
            logger.error(f"Batch insert failed: {str(e)}")
            import traceback
            logger.error(f"Full error: {traceback.format_exc()}")
            conn.rollback()
            return False

        end_total = time.time()
        logger.info(f"Total insertion process took {end_total - start_total:.2f} seconds")
        return True

    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Database error during insertion: {str(e)}")
        return False

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        logger.info("Database connection closed")