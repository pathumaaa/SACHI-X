from flask import Flask, jsonify, request, render_template
import grpc
from xray_api.app.stats import command_pb2, command_pb2_grpc

app = Flask(__name__)

# Xray API client
class XrayAPI:
    def __init__(self, api_port):
        self.channel = grpc.insecure_channel(f"127.0.0.1:{api_port}")
        self.stats_client = command_pb2_grpc.StatsServiceStub(self.channel)

    def get_traffic(self, reset=False):
        try:
            response = self.stats_client.QueryStats(
                command_pb2.QueryStatsRequest(reset_=reset)
            return response.stat
        except grpc.RpcError as e:
            print(f"Error fetching traffic: {e}")
            return []

# Initialize Xray API
xray_api = XrayAPI(api_port=8080)  # Replace with your Xray API port

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user/traffic', methods=['GET'])
def get_user_traffic():
    uuid = request.args.get('uuid')
    if not uuid:
        return jsonify({"error": "UUID is required"}), 400

    # Fetch traffic data
    stats = xray_api.get_traffic(reset=False)
    for stat in stats:
        if stat.name == f"user>>>{uuid}>>>traffic>>>downlink":
            downlink = stat.value
        elif stat.name == f"user>>>{uuid}>>>traffic>>>uplink":
            uplink = stat.value

    if 'downlink' not in locals() or 'uplink' not in locals():
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "uuid": uuid,
        "downlink": downlink,
        "uplink": uplink
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
