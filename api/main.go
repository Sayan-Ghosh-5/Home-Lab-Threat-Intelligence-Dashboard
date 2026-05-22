package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"

	_ "github.com/lib/pq"
)

// The Global DB: Declared at the top so the handler can access it
var db *sql.DB

type Packet struct {
	SourceIP      string `json:"source_ip"`
	DestinationIP string `json:"destination_ip"`
	PacketSize    int    `json:"packet_size"`
}

func packetHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method Not Allowed", http.StatusMethodNotAllowed)
		return
	}

	var p Packet
	err := json.NewDecoder(r.Body).Decode(&p)
	if err != nil {
		http.Error(w, "Bad Request: Invalid JSON", http.StatusBadRequest)
		return
	}

	// Insert the data into the newly defined network_traffic table
	insertSQL := `
		INSERT INTO network_traffic (source_ip, destination_ip, packet_size)
		VALUES ($1, $2, $3)`
	
	_, err = db.Exec(insertSQL, p.SourceIP, p.DestinationIP, p.PacketSize)
	if err != nil {
		log.Printf("Failed to insert data: %v", err)
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		return
	}

	fmt.Printf("Logged to DB: %s -> %s (%d bytes)\n", p.SourceIP, p.DestinationIP, p.PacketSize)
	w.WriteHeader(http.StatusCreated)
}

func main() {
	var err error
	
	// The Connection string provided in the requirements
	connStr := "postgres://admin:password123@database:5432/homelab_db?sslmode=disable"
	
	// Open the connection
	db, err = sql.Open("postgres", connStr)
	if err != nil {
		log.Fatalf("Error opening database connection: %v\n", err)
	}
	defer db.Close()

	// Ping it. If it fails, log.Fatal() will kill the server
	err = db.Ping()
	if err != nil {
		log.Fatalf("Cannot connect to the database. Is it running? Error: %v\n", err)
	}
	fmt.Println("Successfully connected to PostgreSQL!")

	// The Schema: Create the table using db.Exec()
	createTableSQL := `
		CREATE TABLE IF NOT EXISTS network_traffic (
			id SERIAL PRIMARY KEY,
			source_ip INET NOT NULL,
			destination_ip INET NOT NULL,
			packet_size INTEGER NOT NULL,
			captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		);`
	
	_, err = db.Exec(createTableSQL)
	if err != nil {
		log.Fatalf("Failed to execute schema creation: %v\n", err)
	}
	fmt.Println("Database schema verified!")

	// Start the server
	http.HandleFunc("/api/packets", packetHandler)

	fmt.Println("Server is listening on port 8080...")
	err = http.ListenAndServe(":8080", nil)
	if err != nil {
		log.Fatalf("Server failed to start: %v\n", err)
	}
}