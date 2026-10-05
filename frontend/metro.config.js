// Carga la configuración desde el `.env` de la RAIZ del repositorio.
// Metro/Expo inlinizan `process.env.EXPO_PUBLIC_*` en tiempo de build; al
// cargarlo aquí, el frontend lee la misma configuración única que el backend.
const fs = require("fs");
const path = require("path");

const rootEnvPath = path.resolve(__dirname, "..", ".env");
if (fs.existsSync(rootEnvPath)) {
  const content = fs.readFileSync(rootEnvPath, "utf8");
  for (const line of content.split(/\r?\n/)) {
    const match = line.match(/^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$/);
    if (match && !(match[1] in process.env)) {
      process.env[match[1]] = match[2];
    }
  }
}

const { getDefaultConfig } = require("expo/metro-config");

module.exports = getDefaultConfig(__dirname);