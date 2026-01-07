import { useState } from "react";
import { Shield, Save, RefreshCw } from "lucide-react";
import { Link } from "react-router-dom";

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    requestThreshold: 100,
    timeWindow: 60,
    blockDuration: 3600,
    autoBlock: true,
    emailAlerts: true,
    suspiciousIPThreshold: 50,
    ddosProtectionLevel: "medium",
    rateLimitPerIP: 100,
  });

  const [saved, setSaved] = useState(false);

  const handleChange = (field, value) => {
    setSettings((prev) => ({
      ...prev,
      [field]: value,
    }));
    setSaved(false);
  };

  const handleSave = () => {
    // Here you would typically send settings to your backend
    console.log("Saving settings:", settings);
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const handleReset = () => {
    setSettings({
      requestThreshold: 100,
      timeWindow: 60,
      blockDuration: 3600,
      autoBlock: true,
      emailAlerts: true,
      suspiciousIPThreshold: 50,
      ddosProtectionLevel: "medium",
      rateLimitPerIP: 100,
    });
    setSaved(false);
  };

  return (
    <div className="min-h-screen bg-black text-white">
      <style>
        {`
          .text-gradient {
            background: linear-gradient(135deg, #00ffaa 0%, #00ccff 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
          }
          .btn-gradient {
            background: linear-gradient(135deg, #00ffaa 0%, #00ccff 100%);
          }
          .card-gradient {
            background: linear-gradient(135deg, rgba(0, 255, 170, 0.05) 0%, rgba(0, 204, 255, 0.05) 100%);
          }
          .border-gradient {
            border-color: rgba(0, 255, 170, 0.2);
          }
          input[type="range"]::-webkit-slider-thumb {
            background: linear-gradient(135deg, #00ffaa 0%, #00ccff 100%);
          }
          input[type="range"]::-moz-range-thumb {
            background: linear-gradient(135deg, #00ffaa 0%, #00ccff 100%);
          }
        `}
      </style>

      {/* Header */}
      <header className="bg-black bg-opacity-95 backdrop-blur-lg shadow-lg border-b border-gradient">
        <div className="max-w-7xl mx-auto px-4 py-5 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Shield className="w-8 h-8" style={{ color: "#00ffaa" }} />
              <h1 className="text-3xl font-bold text-gradient">
                CWatch Settings
              </h1>
            </div>
            <div className="flex gap-4">
              <button
                onClick={handleReset}
                className="flex items-center space-x-2 px-6 py-3 bg-gray-800 text-white rounded-full hover:bg-gray-700 transition-all duration-300 font-bold border border-gray-700"
              >
                <RefreshCw className="w-4 h-4" />
                <span>Reset</span>
              </button>
              <button
                onClick={handleSave}
                className="flex items-center space-x-2 px-6 py-3 btn-gradient text-black rounded-full hover:scale-105 transition-all duration-300 font-bold shadow-lg"
                style={{ boxShadow: "0 10px 30px rgba(0, 255, 170, 0.3)" }}
              >
                <Save className="w-4 h-4" />
                <span>{saved ? "Saved!" : "Save Changes"}</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
        {/* DDoS Protection Settings */}
        <div className="card-gradient rounded-3xl border border-gradient p-8 mb-8 shadow-xl">
          <h2 className="text-2xl font-bold text-gradient mb-6">
            DDoS Protection Settings
          </h2>

          <div className="space-y-8">
            {/* Request Threshold */}
            <div>
              <label className="block text-sm font-bold text-gray-300 mb-3">
                Request Threshold (requests per time window)
              </label>
              <div className="flex items-center gap-6">
                <input
                  type="range"
                  min="10"
                  max="500"
                  value={settings.requestThreshold}
                  onChange={(e) =>
                    handleChange("requestThreshold", parseInt(e.target.value))
                  }
                  className="flex-1 h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
                />
                <span className="text-2xl font-bold text-cyan-400 min-w-[80px] text-right">
                  {settings.requestThreshold}
                </span>
              </div>
              <p className="text-xs text-gray-500 mt-2">
                Number of requests allowed from a single IP before triggering
                protection
              </p>
            </div>

            {/* Time Window */}
            <div>
              <label className="block text-sm font-bold text-gray-300 mb-3">
                Time Window (seconds)
              </label>
              <div className="flex items-center gap-6">
                <input
                  type="range"
                  min="10"
                  max="300"
                  value={settings.timeWindow}
                  onChange={(e) =>
                    handleChange("timeWindow", parseInt(e.target.value))
                  }
                  className="flex-1 h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
                />
                <span className="text-2xl font-bold text-cyan-400 min-w-[80px] text-right">
                  {settings.timeWindow}s
                </span>
              </div>
              <p className="text-xs text-gray-500 mt-2">
                Time period to monitor request frequency
              </p>
            </div>

            {/* Block Duration */}
            <div>
              <label className="block text-sm font-bold text-gray-300 mb-3">
                Block Duration (seconds)
              </label>
              <div className="flex items-center gap-6">
                <input
                  type="range"
                  min="60"
                  max="86400"
                  step="60"
                  value={settings.blockDuration}
                  onChange={(e) =>
                    handleChange("blockDuration", parseInt(e.target.value))
                  }
                  className="flex-1 h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
                />
                <span className="text-2xl font-bold text-cyan-400 min-w-[80px] text-right">
                  {settings.blockDuration >= 3600
                    ? `${Math.floor(settings.blockDuration / 3600)}h`
                    : `${Math.floor(settings.blockDuration / 60)}m`}
                </span>
              </div>
              <p className="text-xs text-gray-500 mt-2">
                How long to block suspicious IPs
              </p>
            </div>

            {/* Protection Level */}
            <div>
              <label className="block text-sm font-bold text-gray-300 mb-3">
                DDoS Protection Level
              </label>
              <div className="grid grid-cols-3 gap-4">
                {["low", "medium", "high"].map((level) => (
                  <button
                    key={level}
                    onClick={() => handleChange("ddosProtectionLevel", level)}
                    className={`py-4 px-6 rounded-2xl font-bold text-sm uppercase transition-all duration-300 ${
                      settings.ddosProtectionLevel === level
                        ? "btn-gradient text-black shadow-lg"
                        : "bg-gray-800 text-gray-400 hover:bg-gray-700"
                    }`}
                  >
                    {level}
                  </button>
                ))}
              </div>
              <p className="text-xs text-gray-500 mt-2">
                Low: Minimal filtering | Medium: Balanced protection | High:
                Aggressive filtering
              </p>
            </div>

            {/* Rate Limit Per IP */}
            <div>
              <label className="block text-sm font-bold text-gray-300 mb-3">
                Rate Limit Per IP (requests/minute)
              </label>
              <div className="flex items-center gap-6">
                <input
                  type="range"
                  min="10"
                  max="1000"
                  step="10"
                  value={settings.rateLimitPerIP}
                  onChange={(e) =>
                    handleChange("rateLimitPerIP", parseInt(e.target.value))
                  }
                  className="flex-1 h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
                />
                <span className="text-2xl font-bold text-cyan-400 min-w-[80px] text-right">
                  {settings.rateLimitPerIP}
                </span>
              </div>
              <p className="text-xs text-gray-500 mt-2">
                Maximum requests per minute allowed per IP address
              </p>
            </div>
          </div>
        </div>

        {/* Advanced Settings */}
        <div className="card-gradient rounded-3xl border border-gradient p-8 mb-8 shadow-xl">
          <h2 className="text-2xl font-bold text-gradient mb-6">
            Advanced Settings
          </h2>

          <div className="space-y-6">
            {/* Auto Block Toggle */}
            <div className="flex items-center justify-between p-4 bg-black bg-opacity-30 rounded-2xl">
              <div>
                <h3 className="text-lg font-bold text-white">
                  Auto-Block Suspicious IPs
                </h3>
                <p className="text-sm text-gray-400 mt-1">
                  Automatically block IPs that exceed the threshold
                </p>
              </div>
              <button
                onClick={() => handleChange("autoBlock", !settings.autoBlock)}
                className={`relative w-16 h-8 rounded-full transition-all duration-300 ${
                  settings.autoBlock
                    ? "bg-gradient-to-r from-cyan-500 to-green-500"
                    : "bg-gray-700"
                }`}
              >
                <div
                  className={`absolute top-1 left-1 w-6 h-6 bg-white rounded-full transition-transform duration-300 ${
                    settings.autoBlock ? "transform translate-x-8" : ""
                  }`}
                />
              </button>
            </div>

            {/* Email Alerts Toggle */}
            <div className="flex items-center justify-between p-4 bg-black bg-opacity-30 rounded-2xl">
              <div>
                <h3 className="text-lg font-bold text-white">Email Alerts</h3>
                <p className="text-sm text-gray-400 mt-1">
                  Receive notifications when threats are detected
                </p>
              </div>
              <button
                onClick={() =>
                  handleChange("emailAlerts", !settings.emailAlerts)
                }
                className={`relative w-16 h-8 rounded-full transition-all duration-300 ${
                  settings.emailAlerts
                    ? "bg-gradient-to-r from-cyan-500 to-green-500"
                    : "bg-gray-700"
                }`}
              >
                <div
                  className={`absolute top-1 left-1 w-6 h-6 bg-white rounded-full transition-transform duration-300 ${
                    settings.emailAlerts ? "transform translate-x-8" : ""
                  }`}
                />
              </button>
            </div>

            {/* Geo-Blocking Toggle */}
            {/* <div className="flex items-center justify-between p-4 bg-black bg-opacity-30 rounded-2xl">
              <div>
                <h3 className="text-lg font-bold text-white">Geographic Blocking</h3>
                <p className="text-sm text-gray-400 mt-1">
                  Block traffic from specific countries
                </p>
              </div>
              <button
                onClick={() => handleChange('geoBlocking', !settings.geoBlocking)}
                className={`relative w-16 h-8 rounded-full transition-all duration-300 ${
                  settings.geoBlocking ? 'bg-gradient-to-r from-cyan-500 to-green-500' : 'bg-gray-700'
                }`}
              >
                <div
                  className={`absolute top-1 left-1 w-6 h-6 bg-white rounded-full transition-transform duration-300 ${
                    settings.geoBlocking ? 'transform translate-x-8' : ''
                  }`}
                />
              </button>
            </div> */}

            {/* Geo-Blocking Toggle */}
            {/* <div className="flex items-center justify-between p-4 bg-black bg-opacity-30 rounded-2xl">
              <div>
                <h3 className="text-lg font-bold text-white">Geographic Blocking</h3>
                <p className="text-sm text-gray-400 mt-1">
                  Block traffic from specific countries
                </p>
              </div>
              <button
                onClick={() => handleChange('geoBlocking', !settings.geoBlocking)}
                className={`relative w-16 h-8 rounded-full transition-all duration-300 ${
                  settings.geoBlocking ? 'bg-gradient-to-r from-cyan-500 to-green-500' : 'bg-gray-700'
                }`}
              >
                <div
                  className={`absolute top-1 left-1 w-6 h-6 bg-white rounded-full transition-transform duration-300 ${
                    settings.geoBlocking ? 'transform translate-x-8' : ''
                  }`}
                />
              </button>
            </div> */}

            {/* Suspicious IP Threshold */}
            <div>
              <label className="block text-sm font-bold text-gray-300 mb-3">
                Suspicious IP Alert Threshold
              </label>
              <div className="flex items-center gap-6">
                <input
                  type="range"
                  min="10"
                  max="200"
                  value={settings.suspiciousIPThreshold}
                  onChange={(e) =>
                    handleChange(
                      "suspiciousIPThreshold",
                      parseInt(e.target.value)
                    )
                  }
                  className="flex-1 h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
                />
                <span className="text-2xl font-bold text-cyan-400 min-w-[80px] text-right">
                  {settings.suspiciousIPThreshold}
                </span>
              </div>
              <p className="text-xs text-gray-500 mt-2">
                Request count to flag an IP as suspicious (but not blocked)
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
