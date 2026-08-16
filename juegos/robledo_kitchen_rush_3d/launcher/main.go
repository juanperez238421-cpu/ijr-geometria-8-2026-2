package main

import (
	_ "embed"
	"flag"
	"fmt"
	"log"
	"net"
	"net/http"
	"os"
	"os/exec"
	"runtime"
	"sync"
	"time"
)

// game.html is replaced by the production build before this launcher is compiled.
//go:embed game.html
var gameHTML []byte

func openBrowser(url string) error {
	var cmd *exec.Cmd
	switch runtime.GOOS {
	case "windows":
		cmd = exec.Command("rundll32", "url.dll,FileProtocolHandler", url)
	case "darwin":
		cmd = exec.Command("open", url)
	default:
		cmd = exec.Command("xdg-open", url)
	}
	return cmd.Start()
}

func main() {
	requestedPort := flag.Int("port", 0, "local HTTP port; 0 selects a free port")
	noOpen := flag.Bool("no-open", false, "do not open a browser automatically")
	flag.Parse()

	addr := "127.0.0.1:0"
	if *requestedPort > 0 {
		addr = fmt.Sprintf("127.0.0.1:%d", *requestedPort)
	}
	ln, err := net.Listen("tcp", addr)
	if err != nil {
		log.Fatal(err)
	}
	defer ln.Close()

	var mu sync.Mutex
	lastHeartbeat := time.Now()
	hasHeartbeat := false
	touch := func() {
		mu.Lock()
		lastHeartbeat = time.Now()
		hasHeartbeat = true
		mu.Unlock()
	}

	mux := http.NewServeMux()
	mux.HandleFunc("/__health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Cache-Control", "no-store")
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte("OK"))
	})
	mux.HandleFunc("/__heartbeat", func(w http.ResponseWriter, r *http.Request) {
		touch()
		w.Header().Set("Cache-Control", "no-store")
		w.WriteHeader(http.StatusNoContent)
	})
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/html; charset=utf-8")
		w.Header().Set("Cache-Control", "no-store")
		w.Header().Set("Cross-Origin-Opener-Policy", "same-origin")
		w.Header().Set("X-Content-Type-Options", "nosniff")
		_, _ = w.Write(gameHTML)
	})

	server := &http.Server{Handler: mux, ReadHeaderTimeout: 5 * time.Second}
	go func() {
		if err := server.Serve(ln); err != nil && err != http.ErrServerClosed {
			log.Printf("server error: %v", err)
		}
	}()

	url := fmt.Sprintf("http://%s/?portable=1", ln.Addr().String())
	if !*noOpen {
		if err := openBrowser(url); err != nil {
			log.Printf("Could not open browser automatically: %v", err)
		}
	}

	if *noOpen {
		select {}
	}

	// Keep the tiny local launcher alive while the browser game is open.
	// The game pings /__heartbeat every 10 seconds when launched with ?portable=1.
	ticker := time.NewTicker(10 * time.Second)
	defer ticker.Stop()
	for range ticker.C {
		mu.Lock()
		age := time.Since(lastHeartbeat)
		seen := hasHeartbeat
		mu.Unlock()
		if seen && age > 45*time.Second {
			_ = server.Close()
			return
		}
		if !seen && age > 10*time.Minute {
			_ = server.Close()
			return
		}
	}

	_ = os.Stdout
}
