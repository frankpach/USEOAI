#!/bin/bash

echo "Instalando dependencias del frontend USEOAI..."
echo

echo "Limpiando cache de npm..."
npm cache clean --force

echo
echo "Instalando dependencias con legacy-peer-deps..."
npm install --legacy-peer-deps

echo
echo "Verificando instalacion..."
npm list --depth=0

echo
echo "Instalacion completada!"
echo "Para iniciar el servidor de desarrollo ejecuta: npm run dev" 