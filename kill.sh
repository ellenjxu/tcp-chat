# Check if port number argument is provided
if [ $# -eq 0 ]; then
    echo "Usage: ./script.sh <port>"
    exit 1
fi

# Assign the port number from the argument
port=$1

# Find the process IDs (PIDs) associated with the specified port
pids=$(lsof -t -i:"$port")

echo $(lsof -i :$port | awk '{print $1}')
# Check if any PIDs are founds
if [ -z "$pids" ]; then
    exit 0
fi

echo "Kill process on port $port (y/n)?"

# Terminate the processes using the found PIDs
#echo "Attempting to terminate processes running on port $port..."
#echo "$pids" | xargs -r kill

read answer

# Check the user's response
if [[ $answer =~ ^[Yy]$ ]]; then
    echo "$pids" | xargs -r kill
else
    echo "Process termination aborted."
fi