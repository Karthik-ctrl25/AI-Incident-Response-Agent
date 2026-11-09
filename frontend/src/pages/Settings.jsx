
import React, { useState, useEffect } from "react";
import {
  Bell,
  BrainCircuit,
  Palette,
  ShieldCheck,
  Database,
  RotateCcw,
  CheckCircle2,
  AlertCircle,
} from "lucide-react";

const DEFAULT_SETTINGS = {
  emailNotifications: true,
  criticalAlerts: true,
  analysisNotifications: true,
  showActivity: true,
  compactView: false,
  analysisDepth: "Detailed",
};

export default function Settings() {
  const [settings, setSettings] = useState(() => {
    try {
      const saved = localStorage.getItem("incidentai-settings");

      return saved
        ? { ...DEFAULT_SETTINGS, ...JSON.parse(saved) }
        : DEFAULT_SETTINGS;
    } catch {
      return DEFAULT_SETTINGS;
    }
  });

  const [saved, setSaved] = useState(false);

  useEffect(() => {
    localStorage.setItem(
      "incidentai-settings",
      JSON.stringify(settings)
    );
  }, [settings]);

  const updateSetting = (key, value) => {
    setSettings((previous) => ({
      ...previous,
      [key]: value,
    }));
    setSaved(false);
  };

  const resetSettings = () => {
    setSettings({ ...DEFAULT_SETTINGS });
    setSaved(false);
  };

  const saveSettings = () => {
    localStorage.setItem(
      "incidentai-settings",
      JSON.stringify(settings)
    );
    setSaved(true);
  };

  const Toggle = ({ label, description, settingKey }) => (
    <div className="settings-option">
      <div className="settings-option-text">
        <h4>{label}</h4>
        <p>{description}</p>
      </div>

      <button
        type="button"
        className={`settings-toggle ${
          settings[settingKey] ? "active" : ""
        }`}
        onClick={() =>
          updateSetting(settingKey, !settings[settingKey])
        }
        aria-label={label}
        aria-pressed={settings[settingKey]}
      >
        <span />
      </button>
    </div>
  );

  return (
    <div className="settings-page">
      <div className="page-heading">
        <div>
          <h1>Settings</h1>
          <p>Manage your IncidentAI workspace preferences.</p>
        </div>

        <button
          className="settings-reset-btn"
          onClick={resetSettings}
        >
          <RotateCcw size={15} />
          Reset defaults
        </button>
      </div>

      <div className="settings-layout">
        <div className="settings-main">

          {/* Notifications */}
          <section className="settings-card">
            <div className="settings-section-heading">
              <div className="settings-icon">
                <Bell size={19} />
              </div>

              <div>
                <h3>Notifications</h3>
                <p>Manage your notification preferences.</p>
              </div>
            </div>

            <Toggle
              label="Email notifications"
              description="Preference for important email updates."
              settingKey="emailNotifications"
            />

            <Toggle
              label="Critical incident alerts"
              description="Preference for high-severity incident alerts."
              settingKey="criticalAlerts"
            />

            <Toggle
              label="Analysis notifications"
              description="Preference for completed analysis alerts."
              settingKey="analysisNotifications"
            />
          </section>

          {/* AI Analysis */}
          <section className="settings-card">
            <div className="settings-section-heading">
              <div className="settings-icon">
                <BrainCircuit size={19} />
              </div>

              <div>
                <h3>AI Analysis Preferences</h3>
                <p>Configure incident analysis preferences.</p>
              </div>
            </div>

            <div className="settings-option">
              <div className="settings-option-text">
                <h4>Analysis detail level</h4>
                <p>Select your preferred report detail level.</p>
              </div>

              <select
                className="settings-select"
                value={settings.analysisDepth}
                onChange={(event) =>
                  updateSetting(
                    "analysisDepth",
                    event.target.value
                  )
                }
              >
                <option value="Brief">Brief</option>
                <option value="Detailed">Detailed</option>
                <option value="Comprehensive">
                  Comprehensive
                </option>
              </select>
            </div>
          </section>

          {/* Appearance */}
          <section className="settings-card">
            <div className="settings-section-heading">
              <div className="settings-icon">
                <Palette size={19} />
              </div>

              <div>
                <h3>Appearance</h3>
                <p>Customize your dashboard preferences.</p>
              </div>
            </div>

            <div className="settings-option">
              <div className="settings-option-text">
                <h4>Application theme</h4>
                <p>Current workspace color scheme.</p>
              </div>

              <div className="theme-preview">
                <span className="theme-swatch" />
                <span>Emerald Dark</span>
                <CheckCircle2 size={16} />
              </div>
            </div>

            <Toggle
              label="Compact dashboard"
              description="Preference for a denser dashboard layout."
              settingKey="compactView"
            />

            <Toggle
              label="Show recent activity"
              description="Preference for displaying incident activity."
              settingKey="showActivity"
            />
          </section>

          {/* Memory */}
          <section className="settings-card">
            <div className="settings-section-heading">
              <div className="settings-icon">
                <Database size={19} />
              </div>

              <div>
                <h3>Data & Memory</h3>
                <p>Incident records and memory storage.</p>
              </div>
            </div>

            <div className="settings-info">
              <ShieldCheck size={18} />

              <div>
                <strong>Local demo storage</strong>
                <p>
                  Your preferences are stored in this browser.
                  Incident history and verified resolutions
                  currently use temporary frontend state.
                  Hindsight integration is pending.
                </p>
              </div>
            </div>
          </section>
        </div>

        {/* Right column */}
        <aside className="settings-side">

          <section className="settings-card system-card">
            <div className="settings-section-heading">
              <div className="settings-icon">
                <ShieldCheck size={19} />
              </div>

              <div>
                <h3>System Status</h3>
                <p>Application connection overview.</p>
              </div>
            </div>

            <div className="system-status-row">
              <span>Frontend</span>
              <span className="status-connected">
                <i /> Running
              </span>
            </div>

            <div className="system-status-row">
              <span>Backend API</span>
              <span className="status-demo">
                <i /> Demo mode
              </span>
            </div>

            <div className="system-status-row">
              <span>Hindsight Memory</span>
              <span className="status-demo">
                <i /> Not connected
              </span>
            </div>

            <div className="settings-info warning-info">
              <AlertCircle size={17} />
              <p>
                Backend AI analysis and Hindsight memory
                integration are not active yet.
              </p>
            </div>
          </section>

          <section className="settings-card about-card">
            <h3>About IncidentAI</h3>

            <p>
              AI-powered incident investigation and response.
            </p>

            <div className="about-version">
              <span>Application</span>
              <strong>IncidentAI</strong>
            </div>

            <div className="about-version">
              <span>Version</span>
              <strong>1.0.0</strong>
            </div>

            <div className="about-version">
              <span>Environment</span>
              <strong>Development</strong>
            </div>
          </section>
        </aside>
      </div>

      <div className="settings-footer">
        {saved && (
          <span className="settings-saved-message">
            <CheckCircle2 size={16} />
            Preferences saved
          </span>
        )}

        <button
          className="settings-save-btn"
          onClick={saveSettings}
        >
          Save preferences
        </button>
      </div>
    </div>
  );
}
