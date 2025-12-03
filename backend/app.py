#!/usr/bin/env python3
from flask import Flask, jsonify, request
from flask_cors import CORS
from pathlib import Path
import os
from ssh_executor import SSHExecutor
from config import PiConfig, init_db

app = Flask(__name__, static_folder="../frontend/dist", static_url_path="")
CORS(app)

# Initialize database
init_db()

# All supported cities
CITIES = [
    "asker", "bergen", "bodø", "borås", "changzhou", "drammen", "eskilstuna",
    "fredrikstad", "göteborg", "halmstad", "helsingborg", "hämeenlinna", "helsinki",
    "hq", "joensuu", "jyväskylä", "karlstad", "kristiansand", "kuopio", "lahti",
    "lappeenranta", "linköping", "luleå", "malmö", "moss", "norrköping", "not used",
    "oslo", "oulu", "östersund", "örebro", "pori", "sandefjord", "seinäjoki",
    "shanghai", "skien", "stavanger", "sundsvall", "tampere", "trondheim", "tromsø",
    "turku", "umeå", "uppsala", "vaasa", "västeräs", "växjö"
]


# API Routes

@app.route("/api/pis", methods=["GET"])
def get_pis():
    """Get all Pi configurations"""
    pis = PiConfig.get_all()
    return jsonify(pis)


@app.route("/api/pis/<int:pi_id>", methods=["GET"])
def get_pi(pi_id):
    """Get single Pi configuration"""
    pi = PiConfig.get_by_id(pi_id)
    if not pi:
        return jsonify({"error": "Pi not found"}), 404
    return jsonify(pi)


@app.route("/api/pis/<int:pi_id>/status", methods=["GET"])
def get_pi_status(pi_id):
    """Get Pi status"""
    pi = PiConfig.get_by_id(pi_id)
    if not pi:
        return jsonify({"error": "Pi not found"}), 404

    try:
        with SSHExecutor(pi["ip"]) as ssh:
            result = ssh.get_status()
            status = result["output"].strip() if result["success"] else "offline"
            PiConfig.update_status(pi_id, status)
            return jsonify({
                "id": pi_id,
                "status": status,
                "success": result["success"]
            })
    except Exception as e:
        PiConfig.update_status(pi_id, "error")
        return jsonify({
            "id": pi_id,
            "status": "error",
            "error": str(e)
        }), 500


@app.route("/api/pis/<int:pi_id>/config", methods=["GET"])
def get_pi_env(pi_id):
    """Get Pi .env file"""
    pi = PiConfig.get_by_id(pi_id)
    if not pi:
        return jsonify({"error": "Pi not found"}), 404

    try:
        with SSHExecutor(pi["ip"]) as ssh:
            env = ssh.read_env()
            return jsonify({
                "id": pi_id,
                "env": env
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/pis/<int:pi_id>/config", methods=["POST"])
def update_pi_config(pi_id):
    """Update Pi configuration"""
    pi = PiConfig.get_by_id(pi_id)
    if not pi:
        return jsonify({"error": "Pi not found"}), 404

    data = request.json
    city = data.get("city", "")
    dashboard_mode = data.get("dashboard_mode", "operations")
    theme = data.get("theme", "")
    refresh_secs = data.get("refresh_secs", 300)

    # Validate city
    if city and city not in CITIES:
        return jsonify({"error": f"Invalid city: {city}"}), 400

    try:
        with SSHExecutor(pi["ip"]) as ssh:
            env_dict = ssh.read_env()
            env_dict["CITY"] = city
            env_dict["DASHBOARD_MODE"] = dashboard_mode
            env_dict["REFRESH_SECS"] = str(refresh_secs)
            if theme:
                env_dict["THEME"] = theme
            elif "THEME" in env_dict:
                del env_dict["THEME"]

            result = ssh.write_env(env_dict)
            if result["success"]:
                # Update local config
                PiConfig.update(pi_id, {
                    "city": city,
                    "dashboard_mode": dashboard_mode,
                    "theme": theme,
                    "refresh_secs": refresh_secs
                })
                return jsonify({
                    "success": True,
                    "message": "Configuration updated"
                })
            else:
                return jsonify({
                    "success": False,
                    "error": result["error"]
                }), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/pis/<int:pi_id>/restart", methods=["POST"])
def restart_pi_service(pi_id):
    """Restart Pi service"""
    pi = PiConfig.get_by_id(pi_id)
    if not pi:
        return jsonify({"error": "Pi not found"}), 404

    try:
        with SSHExecutor(pi["ip"]) as ssh:
            result = ssh.restart_service()
            return jsonify({
                "id": pi_id,
                "success": result["success"],
                "output": result["output"],
                "error": result["error"]
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/pis/<int:pi_id>/logs", methods=["GET"])
def get_pi_logs(pi_id):
    """Get Pi logs"""
    pi = PiConfig.get_by_id(pi_id)
    if not pi:
        return jsonify({"error": "Pi not found"}), 404

    lines = request.args.get("lines", 20, type=int)

    try:
        with SSHExecutor(pi["ip"]) as ssh:
            result = ssh.get_logs(lines)
            return jsonify({
                "id": pi_id,
                "logs": result["output"]
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/cities", methods=["GET"])
def get_cities():
    """Get list of all supported cities"""
    return jsonify({"cities": CITIES})


@app.route("/", methods=["GET"])
def index():
    """Serve React app"""
    return app.send_static_file("index.html")


@app.errorhandler(404)
def not_found(error):
    """Serve React app for non-API routes"""
    return app.send_static_file("index.html")


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
