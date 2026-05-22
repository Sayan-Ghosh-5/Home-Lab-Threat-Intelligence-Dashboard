import pandas as pd
import psycopg2
import warnings
from sklearn.ensemble import IsolationForest # 1. Import the ML model

warnings.filterwarnings('ignore', category=UserWarning)

def extract_network_data():
    connection = None
    try:
        # Establish connection (Update port to 5433 if you changed it during debugging)
        connection = psycopg2.connect(
            dbname="homelab_db",
            user="admin",
            password="password123",
            host="localhost",
            port="5432" 
        )
        print("Successfully connected to the PostgreSQL database.\n")

        # Load data into DataFrame
        query = "SELECT * FROM network_traffic;"
        df = pd.read_sql(query, connection)
        
        # Ensure we actually have data before running ML
        if df.empty:
            print("No data found in the database. Please run your sniffer first.")
            return

        print(f"Loaded {len(df)} packets from the database.\n")
        
        # --- THE MACHINE LEARNING PIPELINE ---
        
        # 2. The Engineering: Group by IP and extract behavioral features
        print("Extracting behavioral features per Destination IP...")
        features_df = df.groupby('destination_ip')['packet_size'].agg(
            packet_count='count',
            avg_packet_size='mean',
            total_bytes='sum'
        ).reset_index()

        # 3. The Training: Initialize and fit the model
        # We tell the model to assume roughly 5% of our traffic is anomalous
        model = IsolationForest(contamination=0.05, random_state=42)
        
        # We drop the IP address string column because the model only understands numbers
        X = features_df[['packet_count', 'avg_packet_size', 'total_bytes']]
        model.fit(X)

        # 4. The Prediction: Label the data
        # Returns 1 for Normal, -1 for Anomaly
        features_df['anomaly'] = model.predict(X)

        # 5. The Output: Filter and display the threats
        anomalies = features_df[features_df['anomaly'] == -1]
        
        print("\n=== THREAT DETECTION REPORT ===")
        if anomalies.empty:
            print("No anomalies detected. Network traffic is normal.")
        else:
            print(f"WARNING: Detected {len(anomalies)} anomalous endpoints!")
            print("-" * 50)
            # Print the anomalies, dropping the '-1' label column for cleaner output
            print(anomalies.drop(columns=['anomaly']).to_string(index=False))
            print("-" * 50)

    except Exception as e:
        print(f"Pipeline failed: {e}")
        
    finally:
        if connection is not None:
            connection.close()

if __name__ == "__main__":
    extract_network_data()