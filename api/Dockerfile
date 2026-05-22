# Start from a lightweight Go environment
FROM golang:alpine

# Set the working directory inside the container
WORKDIR /app

# Copy your Go files into the container
COPY go.mod ./
# (If you created a go.sum file, copy that too: COPY go.mod go.sum ./)
COPY main.go ./

# Download the PostgreSQL driver
RUN go mod tidy

# Compile the Go application
RUN go build -o api-server main.go

# Expose the API port
EXPOSE 8080

# Run the compiled binary when the container starts
CMD ["./api-server"]