#!/bin/bash
set -e

echo "🔄 Sincronizando artículos del agente..."

# Copiar artículos del agente al blog
cp /home/agent/agent-system/content/article_*.md src/content/blog/

echo "✅ Artículos copiados"

# Build
echo "🏗️  Haciendo build..."
npm run build

# Git
echo "📤 Pusheando a GitHub..."
git add -A
git commit -m "Nuevos artículos: $(date)" || echo "Sin cambios"
git push origin main

echo "🚀 ¡Listo! Netlify redeploya automáticamente"
