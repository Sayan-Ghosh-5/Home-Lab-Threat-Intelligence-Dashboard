import streamlit as st
import pandas as pd
import psycopg2
import warnings
import time  # Required for our refresh loop
from sklearn.ensemble import IsolationForest

warnings.filterwarnings('ignore', category=UserWarning)

# Set page config for a wider layout
st.set_page_config(page_title="SOC Dashboard", layout="wide")

# 1. No more caching! We need fresh data every loop.
def load_data():
    connection = None
    try:
        connection = psycopg2.connect(
            dbname="homelab_db",
            user="admin",
            password="password123",
            host="database",
            port="5432" 
        )
        # 2. The Rolling Window: Only pull the last 1 hour of traffic
        query = """
            SELECT * FROM network_traffic 
            WHERE captured_at >= NOW() - INTERVAL '60 minutes';
        """
        df = pd.read_sql(query, connection)
        return df
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return pd.DataFrame()
    finally:
        if connection is not None:
            connection.close()

# --- STREAMLIT UI LAYOUT ---

st.title("🛡️ Live Threat Intelligence (Active Monitor)")
st.markdown("Real-time network traffic analysis running on a 60-minute rolling window.")

# 3. Create the placeholder box
main_placeholder = st.empty()

# 4. The Infinite Refresh Loop
while True:
    # Everything inside this 'with' block gets overwritten every 5 seconds
    with main_placeholder.container():
        df = load_data()

        if df.empty:
            st.warning("No data found in the last hour. Ensure your Python sniffer is running.")
        else:
            st.subheader("Live Network Overview")
            st.metric(label="Packets Captured (Last 1 Hour)", value=f"{len(df):,}")

            st.markdown("---")
            st.subheader("🚨 Real-Time Threat Detection")

            # Engineer Features
            features_df = df.groupby('destination_ip')['packet_size'].agg(
                packet_count='count',
                avg_packet_size='mean',
                total_bytes='sum'
            ).reset_index()

            # Train Model on the current 1-hour window
            model = IsolationForest(contamination=0.05, random_state=42)
            X = features_df[['packet_count', 'avg_packet_size', 'total_bytes']]
            model.fit(X)

            # Predict Anomalies
            features_df['anomaly'] = model.predict(X)
            anomalies = features_df[features_df['anomaly'] == -1].copy()

            if anomalies.empty:
                st.success("✅ No anomalies detected in the current window.")
            else:
                st.error(f"⚠️ WARNING: Detected {len(anomalies)} anomalous endpoint(s)!")
                
                anomalies = anomalies.drop(columns=['anomaly'])
                anomalies = anomalies.rename(columns={
                    'destination_ip': 'Destination IP',
                    'packet_count': 'Packets Received',
                    'avg_packet_size': 'Avg Size (Bytes)',
                    'total_bytes': 'Total Bytes'
                })
                
                st.dataframe(anomalies, use_container_width=True, hide_index=True)
                
    # 5. Sleep for 5 seconds before wiping the placeholder and drawing again
    time.sleep(5)