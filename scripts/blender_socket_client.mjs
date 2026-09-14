import net from "node:net";
import fs from "node:fs";

const host = process.env.BLENDER_HOST || "127.0.0.1";
const port = Number(process.env.BLENDER_PORT || 9876);
const mode = process.argv[2] || "get_scene_info";

let request;
if (mode === "execute_file") {
  const file = process.argv[3];
  if (!file) throw new Error("Usage: execute_file <python-file>");
  request = { type: "execute_code", params: { code: fs.readFileSync(file, "utf8") } };
} else if (mode === "json") {
  request = JSON.parse(process.argv[3]);
} else {
  request = { type: mode, params: {} };
}

const socket = net.createConnection({ host, port });
let buffer = "";

socket.setTimeout(900_000);
socket.on("connect", () => socket.write(JSON.stringify(request)));
socket.on("data", (chunk) => {
  buffer += chunk.toString("utf8");
  try {
    const response = JSON.parse(buffer);
    process.stdout.write(`${JSON.stringify(response, null, 2)}\n`);
    socket.end();
  } catch {
    // The Blender add-on sends one JSON response without a delimiter.
  }
});
socket.on("timeout", () => socket.destroy(new Error("Blender response timed out")));
socket.on("error", (error) => {
  process.stderr.write(`${error.stack || error.message}\n`);
  process.exitCode = 1;
});
