import fs from "node:fs";
import path from "node:path";

const input = process.argv[2];
if (!input) throw new Error("usage: node validate_route_poster.mjs <route-poster.json>");
const file = path.resolve(input);
const data = JSON.parse(fs.readFileSync(file, "utf8"));
const errors = [];
const ids = new Set((data.points || []).map((point) => point.id));

if (!data.title) errors.push("missing title");
if (!(data.days || []).length) errors.push("missing days");
(data.days || []).forEach((day, index) => {
  if (!day.day || !day.date || !day.title) errors.push(`day ${index + 1} needs day/date/title`);
  if (index < data.days.length - 1 && !day.stayId) errors.push(`day ${day.day} is missing stayId`);
  if (day.stayId && !ids.has(day.stayId)) errors.push(`day ${day.day} has unknown stayId ${day.stayId}`);
});
(data.points || []).forEach((point) => {
  const [lat, lng] = point.coordinates || [];
  if (!point.id || !point.name) errors.push("a point needs id and name");
  if (!Number.isFinite(lat) || lat < -90 || lat > 90 || !Number.isFinite(lng) || lng < -180 || lng > 180) errors.push(`invalid coordinates for ${point.id}`);
  if (point.poster?.offset && (!Array.isArray(point.poster.offset) || point.poster.offset.length !== 2)) errors.push(`invalid poster offset for ${point.id}`);
});
for (const [key, optional] of [["segments", false], ["optionalSegments", true]]) {
  (data[key] || []).forEach((segment) => {
    if (!segment.id || !segment.name || !Number.isFinite(segment.day)) errors.push(`${key} item needs id/name/day`);
    if (!Array.isArray(segment.geometry) || segment.geometry.length < 2) errors.push(`${segment.id} needs route geometry`);
    if (optional && !segment.activation) errors.push(`${segment.id} needs activation conditions`);
  });
}
(data.insets || []).forEach((inset) => {
  if (!inset.id || !inset.title || !(inset.stops || []).length) errors.push("each inset needs id/title/stops");
  (inset.stops || []).forEach((stop) => { if (!ids.has(stop.pointId)) errors.push(`${inset.id} references unknown ${stop.pointId}`); });
});
if (errors.length) { console.error(errors.join("\n")); process.exit(1); }
console.log("route poster data valid");
