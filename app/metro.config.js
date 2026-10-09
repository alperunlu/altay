// The game ships as a single .html asset (see scripts/sync-game.js), which is
// not an asset extension Metro knows about by default.
const { getDefaultConfig } = require('expo/metro-config');
const config = getDefaultConfig(__dirname);
config.resolver.assetExts.push('html');
module.exports = config;
