// fix-package.js
const fs = require('fs');
const path = require('path');

// Đọc file package.json
const packagePath = path.join(__dirname, 'package.json');
const packageData = JSON.parse(fs.readFileSync(packagePath, 'utf8'));

// Xóa dependency không mong muốn
if (packageData.dependencies && packageData.dependencies['jarvis-assistant']) {
  console.log('Đang xóa jarvis-assistant self-reference...');
  delete packageData.dependencies['jarvis-assistant'];
}

// Ghi lại file package.json
fs.writeFileSync(packagePath, JSON.stringify(packageData, null, 4), 'utf8');
console.log('Đã sửa package.json thành công!');
