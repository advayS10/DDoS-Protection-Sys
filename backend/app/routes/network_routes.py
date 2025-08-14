from flask import Blueprint, jsonify
from ..services.network_monitor import start_packet_capture

network_bp = Blueprint("network", __name__)

processor = start_packet_capture()

@network_bp.route("/api/network-stats", methods=["GET"])
def get_network_stats():
    df = processor.get_dataframe()
    return jsonify(df.to_dict(orient="records"))
