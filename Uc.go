package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"x-ui-client-view/xray" // Adjust the import path to match your project structure
)

var xrayAPI *xray.XrayAPI

// Initialize the Xray API client
func initXrayAPI(apiPort int) {
	xrayAPI = &xray.XrayAPI{}
	err := xrayAPI.Init(apiPort)
	if err != nil {
		log.Fatalf("Failed to initialize Xray API: %v", err)
	}
}

// Handler to fetch user traffic by UUID
func getUserTraffic(w http.ResponseWriter, r *http.Request) {
	uuid := r.URL.Query().Get("uuid")
	if uuid == "" {
		http.Error(w, "UUID is required", http.StatusBadRequest)
		return
	}

	// Fetch traffic data
	traffic, clientTraffic, err := xrayAPI.GetTraffic(false)
	if err != nil {
		http.Error(w, "Failed to get traffic stats", http.StatusInternalServerError)
		return
	}

	// Find the user's traffic data
	for _, ct := range clientTraffic {
		if ct.Email == uuid { // Assuming UUID maps to email
			w.Header().Set("Content-Type", "application/json")
			json.NewEncoder(w).Encode(ct)
			return
		}
	}

	http.Error(w, "User not found", http.StatusNotFound)
}

func main() {
	// Initialize the Xray API client
	initXrayAPI(8080) // Replace with your Xray API port

	// Set up HTTP routes
	http.HandleFunc("/user/traffic", getUserTraffic)

	// Start the web server
	fmt.Println("Server started at :8081")
	log.Fatal(http.ListenAndServe(":8081", nil))
}
