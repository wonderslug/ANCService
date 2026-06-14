#pragma once
// Builds compact, valid JSON feed events for the ANCService web "repeater".
// Header-only; called from ESPHome YAML lambdas. Keeps each event small so the
// whole JSON string fits comfortably in a text_sensor state.
#include <string>
#include <cstdint>

namespace ancservice {

// Return the longest prefix of `in` that is <= max_bytes and does not split a
// UTF-8 multibyte sequence (so the result is always valid UTF-8).
inline std::string utf8_truncate(const std::string &in, size_t max_bytes) {
  if (in.size() <= max_bytes) return in;
  size_t cut = max_bytes;
  while (cut > 0 && (static_cast<unsigned char>(in[cut]) & 0xC0) == 0x80) cut--;
  return in.substr(0, cut);
}

// Escape a string for inclusion inside a JSON double-quoted value.
inline std::string json_escape(const std::string &in) {
  std::string out;
  out.reserve(in.size() + 8);
  for (char c : in) {
    switch (c) {
      case '"':  out += "\\\""; break;
      case '\\': out += "\\\\"; break;
      case '\n': out += "\\n"; break;
      case '\r': out += "\\r"; break;
      case '\t': out += "\\t"; break;
      default:
        if (static_cast<unsigned char>(c) < 0x20) {
          // drop other control chars
        } else {
          out += c;
        }
    }
  }
  return out;
}

// `max_bytes` bounds the *input* before escaping; escaping (e.g. " -> \") can
// grow the result slightly past max_bytes, so it is a budget, not a hard cap.
inline std::string json_field(const std::string &in, size_t max_bytes) {
  return json_escape(utf8_truncate(in, max_bytes));
}

inline std::string feed_notif_json(uint32_t uid, const std::string &phone,
                                   const std::string &app, const std::string &cat,
                                   const std::string &title, const std::string &msg,
                                   uint32_t ts) {
  std::string out = "{\"t\":\"notif\",\"ph\":\"";
  out += json_field(phone, 48);
  out += "\",\"uid\":" + std::to_string(uid);
  out += ",\"app\":\"" + json_field(app, 48) + "\"";
  out += ",\"cat\":\"" + json_field(cat, 24) + "\"";
  out += ",\"title\":\"" + json_field(title, 48) + "\"";
  out += ",\"msg\":\"" + json_field(msg, 80) + "\"";
  out += ",\"ts\":" + std::to_string(ts) + "}";
  return out;
}

inline std::string feed_removed_json(uint32_t uid, const std::string &phone) {
  std::string out = "{\"t\":\"removed\",\"ph\":\"";
  out += json_field(phone, 48);
  out += "\",\"uid\":" + std::to_string(uid) + "}";
  return out;
}

// connected=true -> {"t":"conn","ph":"<phone>"}; false -> {"t":"disconn","ph":"<phone>"}
inline std::string feed_conn_json(const std::string &phone, bool connected) {
  std::string out = "{\"t\":\"";
  out += connected ? "conn" : "disconn";
  out += "\",\"ph\":\"" + json_field(phone, 48) + "\"}";
  return out;
}

}  // namespace ancservice
