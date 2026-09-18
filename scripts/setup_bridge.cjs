'use strict';
// Legacy exports resolve only the runtime bundled with this skill.
const path = require('node:path');
function setupRoot() { return path.resolve(__dirname, '..'); }
function runtime() { return require('./node_runtime.cjs'); }
module.exports = {setupRoot, runtime};
